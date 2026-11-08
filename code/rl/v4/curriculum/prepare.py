#!/usr/bin/env python3
"""Restore archived boundaries; differential Java checks; live recovery screening."""
import argparse
import json
import time
from common import ROOT, OUT, BASE, Oracle, now, save, sha
from native import Simulator, Network
from state import digest, validate

ARCHIVE = ROOT / 'experiments/rl/2026-11-07-ppo-v3/live-submission'
MAPS = ROOT / 'experiments/rl/2026-11-06-ppo-v2/maps-2000.json'
B2M = ROOT / 'experiments/rl/2026-11-07-ppo-v3/seed-b/step-02000416/weights.txt'
OLDER = ROOT / 'experiments/rl/2026-11-06-ppo-v1/training/weights.txt'


def same(actual, expected, context, java=False):
    # Java does not expose a parse-error counter. Never fabricate a Java zero.
    # That native telemetry is not a mechanical field; preserve it separately.
    if java:
        def physical(value):
            if isinstance(value, list):
                return [physical(v) for v in value]
            if isinstance(value, dict):
                return {k: physical(v) for k, v in value.items() if k != 'errors'}
            return value
        actual, expected = physical(actual), physical(expected)
    if actual != expected:
        save(OUT / f'restoration-mismatch-{time.time_ns()}.json', {'context': context, 'actual': actual, 'expected': expected})
        raise AssertionError(f'Restoration mismatch: {context}')


def archived():
    battles = json.loads((ARCHIVE / 'battles-009.json').read_text())['battles']
    records = []
    for battle in sorted(battles, key=lambda row: row['game_id']):
        path = ARCHIVE / 'games' / f"{battle['game_id']}.json"
        raw = json.loads(path.read_text())
        log = raw.get('log', raw)
        seat = next(a['index'] for a in log['agents'] if a.get('me'))
        options = dict(line.split('=', 1) for line in log['game_options'].splitlines() if '=' in line)
        board = {key: [[int(v) for v in row.split(',')] for row in options[key].split('_') if row]
                 for key in ('nodes', 'units', 'edges')}
        commands = [[f['stdout'] for f in log['frames'] if f.get('agent') == p and 'stdout' in f] for p in (0, 1)]
        actions = [list(pair) for pair in zip(*commands)]
        records.append({'game_id': log['game_id'], 'seat': seat, 'category': 'win' if battle['my_position'] == 0 else 'loss',
                        'map': board, 'map_hash': digest(board), 'actions': actions, 'final_score': log['scores'],
                        'source': str(path.relative_to(ROOT)), 'source_sha256': sha(path),
                        'legacy_hash': digest({k: options[k] for k in ('nodes', 'units', 'edges')})})
    return records


def parity():
    target = OUT / 'restoration.json'
    assert not target.exists()
    start = time.monotonic()
    records = archived()
    checks = snapshots = transitions = 0
    with Oracle() as oracle:
        for record in records:
            expected = oracle.run(dict(record['map'], actions=record['actions']))
            sim = Simulator(record['map'])
            record['snapshots'] = {}
            for turn, state in enumerate(expected):
                actual = sim.state()
                same(actual, state, {'game': record['game_id'], 'turn': turn, 'mode': 'sequential'}, java=True)
                checks += 1
                if turn in (2, 4, 6, 8, 10):
                    validate(actual)
                    restored = Simulator(snapshot=actual)
                    same(restored.state(), actual, {'game': record['game_id'], 'turn': turn, 'mode': 'native_restore'})
                    direct = oracle.run({'snapshot': actual, 'actions': []})[0]
                    same(direct, actual, {'game': record['game_id'], 'turn': turn, 'mode': 'java_restore'}, java=True)
                    record['snapshots'][str(turn)] = actual
                    restored.close()
                    snapshots += 1
                if turn < len(record['actions']):
                    sim.step(record['actions'][turn])
                    transitions += 1
            assert sim.state()['done'] and sim.state()['score'] == record['final_score']
            record['native_parse_counters'] = sim.state()['errors']
            sim.close()
            if len(record['snapshots']) != 5:
                raise AssertionError('Unexpected early-terminal archival game')
    save(OUT / 'archive-boundaries.json', records)
    result = {'as_of': now(), 'passed': True, 'games': len(records), 'sequential_full_states': checks,
              'joint_transitions': transitions, 'native_direct_restores': snapshots, 'java_direct_restores': snapshots,
              'mismatches': 0, 'archive_boundary_sha256': sha(OUT / 'archive-boundaries.json'),
              'fields': [k for k in records[0]['snapshots']['2'] if k != 'errors'],
              'native_archival_parse_counters': {str(r['game_id']): r['native_parse_counters'] for r in records if any(r['native_parse_counters'])},
              'diagnostic_note': 'Java has no parse counter. Physical fields are compared exactly; native archival parser counters are retained separately. Eligible starts and generated live plans still require zero errors.',
              'wall_seconds': time.monotonic() - start,
              'external_spend': 0, 'scope': 'Archived development games, not new independent evaluation.'}
    save(target, result)
    print(json.dumps(result), flush=True)


def continue_live(snapshot, seat, learner, opponent):
    sim = Simulator(snapshot=snapshot)
    states, actions = [sim.state()], []
    while not states[-1]['done']:
        pair = [None, None]
        pair[seat] = learner.act(sim, seat)
        pair[1 - seat] = opponent.act(sim, 1 - seat)
        sim.step(pair)
        states.append(sim.state())
        actions.append(pair)
    scores = states[-1]['score']
    outcome = 1 if scores[seat] > scores[1 - seat] else -1 if scores[seat] < scores[1 - seat] else 0
    sim.close()
    return {'outcome': outcome, 'actions': actions, 'states': states}


def bank():
    target = OUT / 'bank.json'
    assert not target.exists() and json.loads((OUT / 'restoration.json').read_text())['passed']
    assert sha(OUT / 'archive-boundaries.json') == json.loads((OUT / 'restoration.json').read_text())['archive_boundary_sha256']
    start = time.monotonic()
    records = json.loads((OUT / 'archive-boundaries.json').read_text())
    selected = [r for r in records if r['category'] == 'loss'][:24] + [r for r in records if r['category'] == 'win'][:12]
    paths = [BASE / 'weights.txt', B2M, OLDER]
    for path in paths:
        assert path.exists(), str(path)
    networks = [Network(path) for path in paths]
    training = json.loads(MAPS.read_text())['training']
    fresh_records = []
    # Fresh trajectories on known TRAINING maps; never branch dev maps.
    for i, row in enumerate(training[:16]):
        sim = Simulator(row['map'])
        actions, snapshots = [], {}
        while not sim.state()['done'] and sim.state()['turn'] < 10:
            pair = [networks[0].act(sim, 0), networks[i % 2].act(sim, 1)]
            sim.step(pair)
            actions.append(pair)
            state = sim.state()
            if state['turn'] in (2, 4, 6, 8, 10) and not state['done']:
                snapshots[str(state['turn'])] = state
        fresh_records.append({'game_id': f'fresh-{i}', 'seat': i % 2, 'category': 'fresh', 'map': row['map'],
                              'map_hash': digest(row['map']), 'source': str(MAPS.relative_to(ROOT)),
                              'source_sha256': sha(MAPS), 'actions': actions, 'snapshots': snapshots,
                              'max_turn': 2 + 2 * (i % 5)})
        sim.close()
    selected += fresh_records
    save(OUT / 'bank-screen-plan.json', {'as_of': now(), 'game_ids': [r['game_id'] for r in selected],
         'policy_weights_sha256': {str(p.relative_to(ROOT)): sha(p) for p in paths},
         'rule': 'Latest eligible turn <= maximum in 10,8,6,4,2 with at least one win in four live greedy continuations.'})
    accepted, screens, java_states = [], [], 0
    with Oracle() as oracle:
        for record in selected:
            chosen = None
            for turn in (10, 8, 6, 4, 2):
                if turn > record.get('max_turn', 10) or str(turn) not in record['snapshots']:
                    continue
                snapshot = record['snapshots'][str(turn)]
                prefix = record['actions'][:turn]
                round_results = []
                for learner in (0, 1):
                    for opponent in (0, 2):
                        played = continue_live(snapshot, record['seat'], networks[learner], networks[opponent])
                        direct = oracle.run({'snapshot': snapshot, 'actions': played['actions']})
                        sequential = oracle.run(dict(record['map'], actions=prefix + played['actions']))[turn:]
                        same(played['states'], direct, {'game': record['game_id'], 'turn': turn, 'mode': 'live_direct_java'}, java=True)
                        same(played['states'], sequential, {'game': record['game_id'], 'turn': turn, 'mode': 'live_sequential_java'}, java=True)
                        java_states += len(direct) + len(sequential)
                        item = {'game_id': record['game_id'], 'category': record['category'], 'turn': turn,
                                'learner': learner, 'opponent': opponent, **played}
                        screens.append(item)
                        round_results.append(played['outcome'])
                if max(round_results) == 1:
                    chosen = {'game_id': record['game_id'], 'category': record['category'], 'seat': record['seat'],
                              'map': record['map'], 'map_hash': record['map_hash'], 'snapshot': snapshot,
                              'prefix': prefix, 'source': record['source'], 'source_sha256': record['source_sha256'],
                              'screen_outcomes': round_results, 'snapshot_hash': digest(snapshot)}
                    break
            if chosen:
                accepted.append(chosen)
            save(OUT / 'bank-screen-progress.json', {'as_of': now(), 'processed': record['game_id'],
                 'accepted': len(accepted), 'screen_games': len(screens), 'java_states': java_states})
            print(json.dumps({'game': record['game_id'], 'category': record['category'], 'chosen_turn': chosen['snapshot']['turn'] if chosen else None,
                              'accepted': len(accepted), 'screen_games': len(screens)}), flush=True)
    for net in networks:
        net.close()
    assert all(any(r['category'] == category and r['seat'] == seat for r in accepted) for category in ('loss', 'win', 'fresh') for seat in (0, 1))
    save(OUT / 'bank-screen-records.json', screens)
    save(target, {'as_of': now(), 'records': accepted, 'provenance': 'PROJECT_REPORTED',
                 'selection': 'Development/training bank screened using live frozen policies; not independent test.'})
    result = {'as_of': now(), 'passed': True, 'eligible_source_games': len(selected), 'accepted_states': len(accepted),
              'categories': {c: sum(r['category'] == c for r in accepted) for c in ('loss', 'win', 'fresh')},
              'start_turns': {str(t): sum(r['snapshot']['turn'] == t for r in accepted) for t in (2, 4, 6, 8, 10)},
              'screen_games': len(screens), 'java_full_states': java_states, 'mismatches': 0,
              'bank_sha256': sha(target), 'screen_records_sha256': sha(OUT / 'bank-screen-records.json'),
              'wall_seconds': time.monotonic() - start, 'external_spend': 0}
    save(OUT / 'bank-verification.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('phase', choices=['parity', 'bank'])
    args = ap.parse_args()
    {'parity': parity, 'bank': bank}[args.phase]()
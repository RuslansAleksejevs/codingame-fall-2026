#!/usr/bin/env python3
"""Untimed native search-quality screen; never mistaken for a timed arena."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from run_matches import BASE, REPO, java_home
from rl.sim.native import Simulator
from rl.search.native import Search
from rl.data.replays import read
from rl.train.ppo import save, sha
from rl.eval.analyze import interval

STOP = datetime(2026, 11, 8, 4, tzinfo=timezone.utc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    assert datetime.now(timezone.utc) < STOP
    args.out.mkdir(parents=True, exist_ok=False)
    experiment = BASE / 'experiments/rl/2026-11-07-ppo-v3'
    actor = BASE / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt'
    critic = experiment / 'search/frozen-critic/critic.txt'
    opponent_paths = {'league3m': actor,
                      'long3m': BASE / 'experiments/rl/2026-11-06-ppo-v2/control-long/step-03002813/weights.txt',
                      'extended': BASE / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-04836947/weights.txt'}
    enemies = list(opponent_paths.values())
    candidates = {'greedy': Search(actor, critic, enemies, candidates=1, budget_ms=0),
                  'search1': Search(actor, critic, enemies, depth=1, candidates=4, budget_ms=0),
                  'search2': Search(actor, critic, enemies, depth=2, candidates=4, budget_ms=0)}
    opponents = {name: Search(p, critic, enemies, candidates=1, budget_ms=0) for name, p in opponent_paths.items()}
    manifest = {'as_of': datetime.now(timezone.utc).isoformat(), 'provenance': 'PROJECT_REPORTED',
                'mode': 'Untimed native simulator, deterministic greedy opponents and unlimited-time search',
                'seeds': list(range(30001, 30013)), 'under_training_load': True,
                'timing_claim': False, 'independent_opponent_evidence': False,
                'limitation': 'All three opponents are also response models. Passing only permits an external-opponent screen; it is not promotion evidence.',
                'source_sha256': {str(p.relative_to(BASE)): sha(p) for p in (BASE / 'code/rl/search').glob('*') if p.is_file()},
                'weights_sha256': {str(p.relative_to(BASE)): sha(p) for p in [actor, critic, *enemies]},
                'binary_sha256': sha(BASE / 'code/build/libtryangle_search.dylib'), 'external_spend': 0}
    save(args.out / 'manifest.json', manifest)
    cp = str(BASE / 'code/build') + ':' + str(REPO / 'target/classes') + ':' + (REPO / 'classpath.txt').read_text().strip()
    oracle = subprocess.Popen([str(java_home() / 'bin/java'), '-Xmx1g', '-cp', cp, 'Oracle'],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    rows = []
    states_compared = 0
    started = time.monotonic()
    try:
        for seed in manifest['seeds']:
            source = experiment / 'baseline-dev' / f'league3m-vs-lacoz-seed{seed}-seat0.json.gz'
            board = read(source)['map']
            for name, policy in candidates.items():
                for opponent, enemy in opponents.items():
                    for seat in (0, 1):
                        assert datetime.now(timezone.utc) < STOP, 'Search pilot time cap reached'
                        campaign = json.loads((experiment / 'campaign-status.json').read_text())
                        assert (campaign['stage'] == 'running' and campaign.get('label', '').startswith('train-')) or campaign['stage'] == 'first_blocks_finished', 'Timed campaign phase started; stop this untimed scout'
                        sim = Simulator(board)
                        actions, states, diagnostics = [], [sim.state()], []
                        try:
                            while not states[-1]['done']:
                                own, info = policy.act(sim, seat)
                                other = enemy.act(sim, 1-seat)[0]
                                pair = [own, other] if seat == 0 else [other, own]
                                sim.step(pair)
                                actions.append(pair)
                                states.append(sim.state())
                                diagnostics.append(info)
                                assert not any(states[-1]['errors'])
                            scores = states[-1]['score']
                        finally:
                            sim.close()
                        oracle.stdin.write(json.dumps(dict(board, actions=actions)) + '\n')
                        oracle.stdin.flush()
                        reference = json.loads(oracle.stdout.readline())
                        assert len(reference) == len(states)
                        assert all(all(a[k] == b[k] for k in ('turn', 'score', 'units', 'edges', 'triangles', 'done')) for a, b in zip(states, reference))
                        states_compared += len(states)
                        outcome = 'win' if scores[seat] > scores[1-seat] else 'loss' if scores[seat] < scores[1-seat] else 'draw'
                        row = {'candidate': name, 'opponent': opponent, 'seed': seed, 'seat': seat,
                               'outcome': outcome, 'scores': scores, 'turns': len(actions),
                               'changes': sum(d['selected'] > 0 for d in diagnostics),
                               'mean_candidates': statistics.mean(d['complete_candidates'] for d in diagnostics),
                               'max_plan_us_under_load': max(d['plan_us'] for d in diagnostics)}
                        rows.append(row)
                        with (args.out / 'matches.jsonl').open('a') as f:
                            f.write(json.dumps(row) + '\n')
                        stem = f'{name}-vs-{opponent}-seed{seed}-seat{seat}'
                        with gzip.GzipFile(filename=str(args.out / (stem + '.json.gz')), mode='wb', mtime=0) as f:
                            f.write(json.dumps({'map': board, 'actions': actions, 'states': states, 'search': diagnostics, 'row': row}).encode())
                        if len(rows) % 6 == 0:
                            print(json.dumps({'games': len(rows), 'expected': 216, 'last': row, 'wall_seconds': time.monotonic()-started}), flush=True)
    finally:
        oracle.stdin.close()
        oracle.wait(timeout=20)
        for policy in [*candidates.values(), *opponents.values()]:
            policy.close()
    value = lambda row: {'win': 1., 'draw': .5, 'loss': 0.}[row['outcome']]
    groups = {}
    for candidate in candidates:
        groups[candidate] = {}
        for opponent in opponents:
            selected = [r for r in rows if r['candidate'] == candidate and r['opponent'] == opponent]
            groups[candidate][opponent] = {'games': len(selected), 'results': dict(Counter(r['outcome'] for r in selected)),
                'score_rate': statistics.mean(map(value, selected)),
                'map_cluster_95_percent': interval([[value(r) for r in selected if r['seed'] == seed] for seed in manifest['seeds']])}
    assert groups['greedy']['league3m']['score_rate'] == .5
    gates = {}
    base_mean = statistics.mean(g['score_rate'] for g in groups['greedy'].values())
    for candidate in ('search1', 'search2'):
        mean = statistics.mean(g['score_rate'] for g in groups[candidate].values())
        direct = groups[candidate]['league3m']['score_rate']
        regressions = {o: groups[candidate][o]['score_rate'] - groups['greedy'][o]['score_rate'] for o in opponents}
        gates[candidate] = {'mean_gain_pp': 100*(mean-base_mean), 'direct_score': direct,
                            'per_opponent_gain_pp': {o: 100*d for o, d in regressions.items()},
                            'permits_external_screen_only': mean-base_mean >= .05 and direct >= .55 and min(regressions.values()) >= -.05}
    result = {'passed_contracts': True, 'games': len(rows), 'java_full_states_compared': states_compared,
              'joint_transitions': states_compared-len(rows), 'technical_errors': 0, 'groups': groups,
              'preliminary_gate': gates, 'wall_seconds': time.monotonic()-started, 'external_spend': 0,
              'scope': manifest['mode'], 'limitations': manifest['limitation']}
    save(args.out / 'summary.json', result)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
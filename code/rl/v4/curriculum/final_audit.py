#!/usr/bin/env python3
"""Read-only recomputation of saved development results; no games or training."""
from collections import Counter, defaultdict
import json
import math
import statistics
from common import ROOT, OUT, BUILD, now, save, sha
from rl.eval.analyze import interval


def load(path):
    return json.loads(path.read_text())


def main():
    target = OUT / 'final-data-audit.json'
    assert not target.exists()
    panel = OUT / 'screen'
    analysis = load(panel / 'analysis.json')
    strict = load(OUT / 'screen-strict-decision.json')
    manifest = load(panel / 'manifest.json')
    spec = load(panel / 'panel-spec.json')
    freeze = load(OUT / 'screen-analysis-freeze.json')
    rows = [json.loads(line) for line in (panel / 'matches.jsonl').read_text().splitlines()]
    assert len(rows) == 264
    assert all(r['valid'] and r['returncode'] == 0 and not r['own_action_errors']
               and not r['opponent_action_errors'] for r in rows)
    assert set(r['seed'] for r in rows) == set(range(61001, 61013))
    indexed = {(r['candidate'], r['opponent'], r['seed'], r['seat']): r for r in rows}
    assert len(indexed) == len(rows)
    assert len(spec['pairs']) == 11
    for candidate, opponent in spec['pairs']:
        for seed in spec['seeds']:
            for seat in (0, 1):
                assert (candidate, opponent, seed, seat) in indexed
    value = {'win': 1.0, 'draw': .5, 'loss': 0.0}
    groups = {}
    for candidate, opponent in spec['pairs']:
        subset = [r for r in rows if (r['candidate'], r['opponent']) == (candidate, opponent)]
        maps = defaultdict(list)
        for row in subset:
            maps[row['seed']].append(value[row['outcome']])
        key = f'{candidate}_vs_{opponent}'
        got = {'games': len(subset), 'results': dict(Counter(r['outcome'] for r in subset)),
               'score_rate': statistics.mean(value[r['outcome']] for r in subset),
               'score_95_percent': interval(list(maps.values()))}
        expected = analysis['groups'][key]
        assert got['games'] == expected['games'] == expected['clean_games'] == 24
        assert got['results'] == expected['clean_results']
        assert got['score_rate'] == expected['score_rate']
        assert got['score_95_percent'] == expected['score_95_percent']
        groups[key] = got
    paired = {}
    for before in ('control', 'base'):
        paired[before] = {}
        pooled = defaultdict(list)
        for opponent in ('lacoz', 'khoufou', 'b2m'):
            maps = defaultdict(list)
            for seed in sorted(spec['seeds']):
                for seat in (0, 1):
                    a = indexed['curriculum', opponent, seed, seat]
                    b = indexed[before, opponent, seed, seat]
                    assert a['map_content_sha256'] == b['map_content_sha256']
                    delta = value[a['outcome']] - value[b['outcome']]
                    maps[seed].append(delta)
                    pooled[seed].append(delta)
            values = [v for cluster in maps.values() for v in cluster]
            got = {'clean_pairs': len(values), 'gain_pp': 100 * statistics.mean(values),
                   'paired_95_pp': interval(list(maps.values()))}
            expected = analysis['paired_curriculum_minus'][before][opponent]
            assert all(got[k] == expected[k] for k in got)
            paired[before][opponent] = got
        values = [v for cluster in pooled.values() for v in cluster]
        got = {'gain_pp': 100 * statistics.mean(values), 'paired_95_pp': interval(list(pooled.values()))}
        assert got == analysis['paired_curriculum_minus'][before]['pooled']
        paired[before]['pooled'] = got
    assert all(sha(ROOT / path) == expected for path, expected in freeze['source_sha256'].items())
    assert all(sha(ROOT / path) == expected for path, expected in strict['frozen_baseline_preservation'].items())
    arms = {}
    for arm in ('control', 'curriculum'):
        path = OUT / f'pilot-{arm}'
        run, summary, audit = (load(path / name) for name in ('run-000000.json', 'summary.json', 'technical-audit.json'))
        sources = load(path / 'source-sha256.json')
        assert all(sha(ROOT / name) == digest for name, digest in sources.items())
        assert sha(BUILD / 'libcurriculum.dylib') == run['binary_sha256']
        assert sha(path / 'weights.txt') == summary['weights_sha256'] == manifest['policy_weights_sha256'][arm]
        assert sha(path / 'checkpoint.pt') == summary['checkpoint_sha256']
        assert audit['passed'] and audit['partial_episodes_used'] == 0 and audit['java_mismatches'] == 0
        arms[arm] = {'summary': summary, 'runtime': run, 'technical_audit': audit}
    native, java = load(panel / 'native-verification.json'), load(panel / 'java-verification.json')
    assert java['passed'] and not java['mismatches'] and java['panel_games'] == 264
    assert native['games'] == 264 and not native['native_replay_mismatches'] and not native['map_overlap_seeds']
    assert native['native_joint_transitions'] == java['joint_transitions']
    primary = paired['control']
    gate_parts = {
        'pooled_point_gain_positive': primary['pooled']['gain_pp'] > 0,
        'no_opponent_point_loss_worse_than_10pp': all(primary[o]['gain_pp'] >= -10 for o in ('lacoz', 'khoufou', 'b2m')),
        'direct_score_strictly_above_half': groups['curriculum_vs_control']['score_rate'] > .5,
        'at_least_90_percent_clean_pairs': all(primary[o]['clean_pairs'] >= math.ceil(.9 * 24) for o in ('lacoz', 'khoufou', 'b2m')),
        'all_technical_checks': analysis['technical_passed'],
    }
    gate = all(gate_parts.values())
    assert gate == analysis['continuation_gate_passed'] == strict['strict_gate'] == False
    events = [json.loads(line) for line in (ROOT / '.context/rl4-compute/events.jsonl').read_text().splitlines()]
    own_events = [event for event in events if event['owner'] == 'curriculum']
    paths = ['screen/analysis.json', 'screen/matches.jsonl', 'screen/manifest.json',
             'screen/native-verification.json', 'screen/java-verification.json',
             'screen-analysis-freeze.json', 'screen-strict-decision.json',
             'bank.json', 'restoration.json', 'bank-verification.json', 'matched-pair-audit.json']
    result = {'as_of': now(), 'passed': True, 'method': 'Recomputed all W/L/D, score rates, paired gains and bootstrap intervals from saved matches; checked actual source, DLL, checkpoint and policy hashes.',
              'groups': groups, 'paired_curriculum_minus': paired, 'gate_components': gate_parts,
              'continuation_gate_passed': gate, 'arms': arms,
              'java': java, 'native': {k: v for k, v in native.items() if not k.startswith('new_')},
              'evidence_sha256': {name: sha(OUT / name) for name in paths},
              'source_freeze': freeze, 'versions': {k: manifest[k] for k in ('compiler', 'java_version', 'referee_commit')},
              'curriculum_compute_events': own_events,
              'heavy_seconds_at_audit': sum(e['seconds'] for e in own_events if e['event'] == 'finished'),
              'external_spend': 0, 'scope': 'Saved development evidence only. No new games, training or promotion.'}
    save(target, result)
    print(json.dumps({'as_of': result['as_of'], 'passed': True,
                      'paired_curriculum_minus': paired, 'gate_components': gate_parts,
                      'direct_vs_control': groups['curriculum_vs_control'], 'direct_vs_base': groups['curriculum_vs_base'],
                      'java_states': java['full_states_compared'], 'transitions': java['joint_transitions'],
                      'heavy_seconds_at_audit': result['heavy_seconds_at_audit'], 'audit_sha256': sha(target)}), flush=True)


if __name__ == '__main__':
    main()
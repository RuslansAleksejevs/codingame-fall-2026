#!/usr/bin/env python3
"""Apply the predeclared final promotion gates; never change the deployed policy.

Only one previously frozen candidate, all 100 reserved maps, and independently
verified original-referee records are accepted. This script does not generate
maps, play games, tune a policy, or submit a bot.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'code'))
from rl.eval.analyze import clean, value, interval

EXTERNAL = ('lacoz', 'khoufou2', 'khoufou', 'v6', 'bc')
SEEDS = tuple(range(40001, 40101))
BASE_HASH = 'dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_game(row):
    return clean(row) and not row['returncode']


def evidence(rows, candidate):
    assert candidate != 'league3m'
    pairs = [('league3m', o) for o in EXTERNAL] + [(candidate, o) for o in (*EXTERNAL, 'league3m')]
    expected = {(c, o, seed, seat) for c, o in pairs for seed in SEEDS for seat in (0, 1)}
    actual = {(r['candidate'], r['opponent'], r['seed'], r['seat']) for r in rows}
    assert len(rows) == len(expected) == 2200 and actual == expected, 'Incomplete/duplicate/wrong final panel'
    groups, paired, paired_differences = {}, {}, {}
    for name, opponent in pairs:
        group = [r for r in rows if r['candidate'] == name and r['opponent'] == opponent]
        good = [r for r in group if clean_game(r)]
        by_map = [[value(r) for r in good if r['seed'] == seed] for seed in SEEDS]
        groups[f'{name}_vs_{opponent}'] = {
            'games': len(group), 'all_results': dict(Counter(r['outcome'] for r in group)),
            'clean_games': len(good), 'clean_results': dict(Counter(r['outcome'] for r in good)),
            'score_rate': statistics.mean(map(value, good)) if good else None,
            'map_cluster_95_percent': interval([v for v in by_map if v]),
            'own_error_games': sum(bool(r['own_action_errors']) for r in group),
            'opponent_error_games': sum(bool(r['opponent_action_errors']) for r in group),
            'invalid_or_process_failure_games': sum(not r['valid'] or bool(r['returncode']) for r in group)}
    for opponent in EXTERNAL:
        a = {(r['seed'], r['seat']): r for r in rows if r['candidate'] == candidate and r['opponent'] == opponent}
        b = {(r['seed'], r['seat']): r for r in rows if r['candidate'] == 'league3m' and r['opponent'] == opponent}
        assert a.keys() == b.keys()
        assert all(a[k]['map_content_sha256'] == b[k]['map_content_sha256'] for k in a)
        keys = [k for k in a if clean_game(a[k]) and clean_game(b[k])]
        differences = {k: value(a[k])-value(b[k]) for k in keys}
        paired_differences[opponent] = differences
        by_map = [[d for (s, _), d in differences.items() if s == seed] for seed in SEEDS]
        paired[opponent] = {'clean_pairs': len(keys),
                            'candidate_results': dict(Counter(a[k]['outcome'] for k in keys)),
                            'base_results': dict(Counter(b[k]['outcome'] for k in keys)),
                            'score_gain_pp': 100*statistics.mean(differences.values()) if keys else None,
                            'map_cluster_95_pp': interval([v for v in by_map if v]),
                            'excluded_keys': [list(k) for k in a if k not in differences]}
    direct = groups[f'{candidate}_vs_league3m']
    complete_maps = []
    for seed in SEEDS:
        if all((seed, seat) in paired_differences[o] for o in EXTERNAL for seat in (0, 1)):
            complete_maps.append([paired_differences[o][seed, seat] for o in EXTERNAL for seat in (0, 1)])
    all_estimated = all(p['score_gain_pp'] is not None for p in paired.values())
    mean_gain = statistics.mean(p['score_gain_pp'] for p in paired.values()) if all_estimated else None
    own_failures = sum(bool(r['own_action_errors']) or not r['valid'] or bool(r['returncode'])
                       for r in rows if r['candidate'] == candidate)
    gates = {'direct_score_at_least_55_percent': direct['score_rate'] is not None and direct['score_rate'] >= .55,
             'direct_map_lower_95_above_50_percent': direct['map_cluster_95_percent'] is not None and direct['map_cluster_95_percent'][0] > 50,
             'equal_external_gain_at_least_3_pp': mean_gain is not None and mean_gain >= 3,
             'no_external_matchup_drop_over_5_pp': all_estimated and min(p['score_gain_pp'] for p in paired.values()) >= -5,
             'zero_candidate_technical_failure': own_failures == 0,
             'adequate_clean_coverage': direct['clean_games'] >= 180 and all(p['clean_pairs'] >= 180 for p in paired.values())}
    promoted = all(gates.values())
    return {'candidate': candidate, 'games': len(rows), 'unique_maps': len(SEEDS), 'groups': groups,
            'paired_candidate_minus_base': paired, 'equal_weight_external_gain_pp': mean_gain,
            'complete_composite_maps': len(complete_maps),
            'complete_map_composite_gain_95_pp': interval(complete_maps),
            'composite_interval_scope': 'Maps with all ten paired external outcomes; individual matchup point estimates use all paired clean games.',
            'gates': gates, 'promotion_evidence_passed': promoted,
            'local_recommendation': candidate if promoted else 'league3m',
            'fallback_rule': 'A failed or uncertain candidate is not an established improvement. Retain base; no final-set tuning.',
            'bootstrap': {'replicates': 10000, 'seed': 20261106, 'unit': 'whole map, both seats together',
                          'scope': 'Map/game uncertainty for the selected run; not training-seed variance.',
                          'caveat': 'Degenerate empirical intervals at all wins/losses are not certainty of the underlying probability.'}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--panel', type=Path, required=True)
    ap.add_argument('--freeze', type=Path, required=True)
    ap.add_argument('--native-verification', type=Path, required=True)
    ap.add_argument('--java-verification', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    assert args.out.resolve().is_relative_to(ROOT / 'experiments') and not args.out.exists()
    freeze = json.loads(args.freeze.read_text())
    manifest = json.loads((args.panel / 'manifest.json').read_text())
    spec = json.loads((args.panel / 'panel-spec.json').read_text())
    native = json.loads(args.native_verification.read_text())
    java = json.loads(args.java_verification.read_text())
    name = freeze['candidate_name']
    assert datetime.fromisoformat(freeze['as_of']) < datetime.fromisoformat(manifest['as_of'])
    assert manifest['purpose'] == spec['purpose'] == 'confirmation'
    assert tuple(manifest['seeds']) == tuple(spec['seeds']) == SEEDS
    assert manifest['policy_weights_sha256'][name] == freeze['weights_sha256']
    assert manifest['policy_weights_sha256']['league3m'] == BASE_HASH
    assert sha(ROOT / freeze['weights_path']) == freeze['weights_sha256']
    for packaged_name, package in freeze['packages'].items():
        assert manifest['policy_variants'][packaged_name] == 'packaged'
        assert sha(ROOT / package['manifest_path']) == package['manifest_sha256']
        assert sha(ROOT / package['source_path']) == package['source_sha256']
        assert manifest['source_sha256'][f'packaged/{packaged_name}.cpp'] == package['source_sha256']
    for source, digest in freeze['frozen_sources'].items():
        assert sha(ROOT / source) == digest, 'Source/criteria changed after freezing: '+source
        snapshot = source.removeprefix('code/')
        if snapshot in manifest['source_sha256']:
            assert manifest['source_sha256'][snapshot] == digest
    prepared = json.loads((args.freeze.parent / 'prepared.json').read_text())
    assert prepared['freeze_sha256'] == sha(args.freeze)
    assert prepared['spec_sha256'] == sha(args.panel / 'panel-spec.json')
    assert prepared['registry_sha256'] == sha(args.freeze.parent / 'map-registry.json')
    for report in (native, java):
        assert report['panel_manifest_sha256'] == sha(args.panel / 'manifest.json')
        assert report['panel_matches_sha256'] == sha(args.panel / 'matches.jsonl')
        assert report['panel_spec_sha256'] == sha(args.panel / 'panel-spec.json')
    assert native['source_freeze_verified'] and native['games'] == 2200 and native['unique_maps'] == 100
    assert native['policy_weights_sha256'] == manifest['policy_weights_sha256']
    assert not native['map_overlap_seeds'] and not native['native_replay_mismatches']
    assert java['passed'] and java['panel_games'] == 2200 and not java['mismatches']
    assert java['clean_games_replayed'] + len(java['technical_records_excluded']) == 2200
    rows = [json.loads(line) for line in (args.panel / 'matches.jsonl').read_text().splitlines()]
    excluded = {f'{r["candidate"]}-vs-{r["opponent"]}-seed{r["seed"]}-seat{r["seat"]}.json.gz'
                for r in rows if not clean_game(r)}
    assert excluded == set(java['technical_records_excluded']) == set(native['technical_records_excluded_from_native_replay'])
    result = evidence(rows, name)
    result.update({'as_of': datetime.now(timezone.utc).isoformat(), 'provenance': 'PROJECT_REPORTED',
                   'freeze_sha256': sha(args.freeze), 'panel_manifest_sha256': sha(args.panel / 'manifest.json'),
                   'native_verification_sha256': sha(args.native_verification),
                   'java_verification_sha256': sha(args.java_verification), 'analysis_sha256': sha(Path(__file__)),
                   'no_map_overlap': True, 'no_policy_changed': True, 'live_submission': False, 'external_spend': 0})
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('groups', 'paired_candidate_minus_base')}, indent=2))


if __name__ == '__main__':
    main()
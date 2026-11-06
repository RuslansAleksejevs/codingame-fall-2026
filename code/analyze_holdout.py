#!/usr/bin/env python3
"""Apply the frozen v3/v6 promotion gate and verify fresh map contents."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path

from analyze_incremental import clean


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text())


def source_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def map_content(path):
    result = json.loads(gzip.decompress(path.read_bytes()))
    parameters = {}
    for block in result['gameParameters']:
        for line in block.splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                parameters[key] = value
    assert {'nodes', 'edges', 'units', 'seed'} <= parameters.keys(), path
    seed = int(parameters.pop('seed'))
    # Exclude the seed itself: different seeds alone do not prove different maps.
    digest = hashlib.sha256(json.dumps(parameters, sort_keys=True).encode()).hexdigest()
    return seed, digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment', type=Path, required=True)
    parser.add_argument('--out', type=Path, help='Default: selection.json inside the experiment')
    args = parser.parse_args()
    folder = args.experiment.resolve()
    plan = read(folder / 'plan.json')
    comparison = read(folder / 'comparison.json')
    audit = read(folder / 'audit.json')
    completion = read(folder / 'run/completion.json')
    assert plan['source_changes_during_run'] is False
    assert plan['optional_stopping'] is False
    assert comparison['increments'][0]['before'] == 'v3'
    assert comparison['increments'][0]['after'] == 'v6'
    expected = {(o, s, t) for o in plan['opponents'] for s in plan['seeds'] for t in plan['seats']}
    rows = {}
    technical = []
    verified_sources = {}
    for label, filename in [('v3', 'v3-multispawn.cpp'), ('v6', 'v6-attack.cpp')]:
        run = folder / 'run' / label
        manifest = read(run / 'manifest.json')
        assert datetime.fromisoformat(plan['created_at']) < datetime.fromisoformat(manifest['as_of'])
        assert manifest['map_context'] == 'fresh'
        assert manifest['seeds'] == plan['seeds']
        path = 'code/variants/' + filename
        digest = source_hash(run / 'snapshots/candidate.cpp')
        assert digest == plan['source_sha256'][path] == source_hash(ROOT / path)
        assert digest == comparison['runs'][label]['source_sha256']
        verified_sources[label] = digest
        rr = [json.loads(line) for line in (run / 'matches.jsonl').read_text().splitlines()]
        assert len(rr) == len(expected)
        assert {(r['opponent'], r['seed'], r['seat']) for r in rr} == expected
        assert all(r['valid'] and r['returncode'] == 0 for r in rr)
        rows[label] = rr
        checked = [v for k, v in audit['runs'].items() if Path(k).name == label]
        assert len(checked) == 1
        assert sum(v['games'] for v in checked[0].values()) == len(rr)
        assert sum(v['validated_decisions'] for v in checked[0].values()) == sum(r['own_decisions'] for r in rr)
        for r in rr:
            if not clean(r):
                technical.append({
                    'variant': label, 'opponent': r['opponent'], 'seed': r['seed'], 'seat': r['seat'],
                    'outcome': r['outcome'], 'own_errors': r['own_action_errors'],
                    'opponent_errors': r['opponent_action_errors'],
                })

    count = sum(len(rr) for rr in rows.values())
    assert count == completion['games'] == plan['planned_games']
    paired = comparison['increments'][0]['paired_without_errors']
    common = {}
    for opponent in plan['opponents']:
        indexed = {label: {(r['seed'], r['seat']): r for r in rr if r['opponent'] == opponent}
                   for label, rr in rows.items()}
        keys = [k for k in indexed['v3'] if all(clean(indexed[label][k]) for label in rows)]
        assert len(keys) == paired[opponent]['paired_games']
        common[opponent] = {
            'pairs': len(keys),
            'fraction_of_planned_pairs': len(keys) / (len(plan['seeds']) * len(plan['seats'])),
            'results': {label: dict(Counter(indexed[label][k]['outcome'] for k in keys)) for label in rows},
            'paired_map_estimate': paired[opponent],
        }

    # Every current pair is already checked by analyze_incremental. Compare its
    # underlying map content with one archived record for every historical seed.
    history = read(folder / 'historical-maps.json')
    historical = {int(k): v for k, v in history['maps'].items()}
    historical_manifests = history['manifests']
    historical_seeds = set()
    for item in historical_manifests:
        manifest_path = ROOT / item['path']
        assert source_hash(manifest_path) == item['sha256']
        metadata = read(manifest_path)
        assert datetime.fromisoformat(metadata['as_of']) < datetime.fromisoformat(plan['created_at'])
        historical_seeds.update(metadata['seeds'])
    assert historical_seeds == set(historical)
    for seed, item in historical.items():
        actual_seed, digest = map_content(ROOT / item['record'])
        assert actual_seed == seed and digest == item['content_sha256']
    assert len(historical_manifests) == plan['historical_manifest_count']
    assert len(historical) == plan['previously_used_seed_count']
    old_hashes = {r['content_sha256'] for r in historical.values()}
    current = {}
    for seed in plan['seeds']:
        record = folder / 'run/v3' / f'khoufou-seed{seed}-seat0.json.gz'
        actual_seed, digest = map_content(record)
        assert actual_seed == seed
        current[seed] = digest
    overlap = sorted(set(current) & set(historical))
    content_overlap = [seed for seed, digest in current.items() if digest in old_hashes]
    assert not overlap and not content_overlap
    assert len(set(current.values())) == plan['maps']

    gates = {
        'complete_valid_schedule_and_raw_record_audit': True,
        'sources_match_pre_run_plan': True,
        'fresh_seeds_and_map_contents': True,
        'no_own_errors_or_timeouts': all(not r['own_errors'] for r in technical),
        'at_least_95_percent_shared_clean_pairs_per_opponent': all(v['fraction_of_planned_pairs'] >= .95 for v in common.values()),
        'khoufou_positive_95_percent_lower_bound': paired['khoufou']['paired_map_bootstrap_95_percent_interval'][0] > 0,
        'lacoz_no_lower_observed_paired_score': paired['lacoz']['score_change_percentage_points'] >= 0,
    }
    promote = all(gates.values())
    result = {
        'as_of': datetime.now(timezone.utc).isoformat(), 'provenance': 'PROJECT_REPORTED',
        'pre_run_plan_sha256': source_hash(folder / 'plan.json'),
        'plan_created_before_both_run_manifests': True,
        'games': count, 'source_sha256': verified_sources,
        'map_novelty': {
            'definition': 'SHA256 of sorted game-parameter fields excluding seed; includes node coordinates, edges and initial units; not graph-isomorphism equivalence.',
            'historical_manifest_count': len(historical_manifests),
            'historical_seeds': len(historical), 'historical_unique_contents': len(old_hashes),
            'new_unique_contents': len(set(current.values())),
            'seed_overlap': overlap, 'content_overlap_seeds': content_overlap,
            'historical_index': 'historical-maps.json',
            'historical_index_sha256': source_hash(folder / 'historical-maps.json'),
            'new_content_sha256_by_seed': current,
        },
        'shared_clean_comparison': common,
        'technical_outcomes': technical, 'promotion_gate_results': gates,
        'promote_v6': promote, 'selected_baseline': 'v6' if promote else 'v3',
        'match_process_wall_seconds': sum(r['wall_seconds'] for rr in rows.values() for r in rr),
        'external_spend': 0, 'contest_submission': False,
        'limitations': [
            'Confirmation uses this fresh set alone, without pooling older outcomes.',
            'Lacoz gate checks observed score, not formal statistical non-inferiority.',
            'Bootstrap uncertainty is conditional on the frozen opponents and observed runs.',
            'Time-limited opponent search can vary on replay; technical outcomes are preserved and excluded from clean pairs.',
        ],
    }
    (args.out or folder / 'selection.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('games', 'shared_clean_comparison', 'technical_outcomes', 'promotion_gate_results', 'promote_v6', 'selected_baseline')}, indent=2))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Preclaimed fresh whole-game maps, original-referee panel and paired analysis."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from common import ROOT, OUT, BASE, Oracle, now, save, sha
from state import digest
from rl.eval.analyze import interval, value

CAMPAIGN = ROOT / 'experiments/rl/2026-11-08-rl4'
REGISTRY = CAMPAIGN / 'map-registry-base.json'
B2M = ROOT / 'experiments/rl/2026-11-07-ppo-v3/seed-b/step-02000416/weights.txt'


def exclusions(include_own=True):
    paths = [REGISTRY]
    for lane in ('exploiters', 'curriculum', 'search-teacher'):
        if lane == 'curriculum' and not include_own:
            continue
        for name in ('map-contribution.json', 'map-registry-claim.json'):
            path = CAMPAIGN / lane / name
            if path.exists():
                paths.append(path)
    canonical, legacy, sources = set(), set(), {}
    assert sha(REGISTRY) == '6185ddba8c2eac022e1f2201ae4b669e7c1e7dc962f1bc6636c805609b6c3702'
    for path in paths:
        data = json.loads(path.read_text())
        canonical.update(data['canonical'])
        legacy.update(data.get('legacy', []))
        sources[str(path.relative_to(ROOT))] = sha(path)
    return {'as_of': now(), 'canonical': sorted(canonical), 'legacy': sorted(legacy), 'sources': sources}


def prepare_maps(stage, seeds):
    path = OUT / f'{stage}-maps.json'
    assert not path.exists()
    seen = exclusions()
    generated = []
    with Oracle('MapGenerator') as generator:
        for seed in seeds:
            assert 61001 <= seed <= 61060
            properties = generator.run(seed)
            board = {k: [[int(v) for v in row.split(',')] for row in properties[k].split('_') if row]
                     for k in ('nodes', 'units', 'edges')}
            canonical = digest(board)
            legacy = hashlib.sha256(json.dumps(properties, sort_keys=True).encode()).hexdigest()
            assert canonical not in seen['canonical'] and legacy not in seen['legacy'], f'Content overlap at {seed}'
            assert canonical not in {r['hash'] for r in generated}, f'Duplicate development map at {seed}'
            generated.append({'seed': seed, 'map': board, 'hash': canonical, 'legacy_hash': legacy})
    # Reread other lanes before claiming: no reliance on seed identity alone.
    fresh = exclusions()
    assert not ({r['hash'] for r in generated} & set(fresh['canonical']))
    assert not ({r['legacy_hash'] for r in generated} & set(fresh['legacy']))
    save(OUT / f'{stage}-exclusions.json', fresh)
    save(path, {'as_of': now(), 'purpose': 'development, not global final', 'records': generated})
    prior_path = OUT / 'map-contribution.json'
    prior = json.loads(prior_path.read_text()) if prior_path.exists() else {'canonical': [], 'legacy': [], 'sources': {}, 'seed_mapping': {}}
    contribution = {'as_of': now(), 'lane': 'curriculum', 'purpose': 'Whole-game development evaluation only',
                    'canonical': sorted(set(prior['canonical']) | {r['hash'] for r in generated}),
                    'legacy': sorted(set(prior['legacy']) | {r['legacy_hash'] for r in generated}),
                    'sources': {**prior['sources'], str(path.relative_to(ROOT)): sha(path)},
                    'seed_mapping': {**prior['seed_mapping'], **{str(r['seed']): {'canonical': r['hash'], 'legacy': r['legacy_hash'], 'stage': stage} for r in generated}}}
    save(prior_path, contribution)
    save(OUT / 'map-registry-claim.json', contribution)
    return generated


def run(command, log):
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    with log.open('x') as output:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            line = line.replace(str(ROOT), '${PROJECT_ROOT}').replace(str(Path.home()), '${HOME}')
            output.write(line)
            output.flush()
            print(line, end='', flush=True)
        code = process.wait()
    assert code == 0, (command[2:], code)


def clean(row):
    return row['valid'] and row['returncode'] == 0 and not row['own_action_errors'] and not row['opponent_action_errors']


def analyze(panel):
    rows = [json.loads(line) for line in (panel / 'matches.jsonl').read_text().splitlines()]
    groups, comparisons = {}, {}
    for candidate, opponent in sorted({(r['candidate'], r['opponent']) for r in rows}):
        subset = [r for r in rows if r['candidate'] == candidate and r['opponent'] == opponent]
        valid = [r for r in subset if clean(r)]
        maps = defaultdict(list)
        for row in valid:
            maps[row['seed']].append(value(row))
        groups[f'{candidate}_vs_{opponent}'] = {'games': len(subset), 'clean_games': len(valid),
              'clean_results': dict(Counter(r['outcome'] for r in valid)),
              'score_rate': statistics.mean(value(r) for r in valid) if valid else None,
              'score_95_percent': interval(list(maps.values())),
              'own_error_games': sum(bool(r['own_action_errors']) for r in subset),
              'opponent_error_games': sum(bool(r['opponent_action_errors']) for r in subset)}
    for before in ('control', 'base'):
        comparisons[before] = {}
        pooled = defaultdict(list)
        for opponent in ('lacoz', 'khoufou', 'b2m'):
            a = {(r['seed'], r['seat']): r for r in rows if r['candidate'] == 'curriculum' and r['opponent'] == opponent}
            b = {(r['seed'], r['seat']): r for r in rows if r['candidate'] == before and r['opponent'] == opponent}
            assert a.keys() == b.keys()
            maps = defaultdict(list)
            excluded = []
            for key in sorted(a):
                assert a[key]['map_content_sha256'] == b[key]['map_content_sha256']
                if clean(a[key]) and clean(b[key]):
                    delta = value(a[key]) - value(b[key])
                    maps[key[0]].append(delta)
                    pooled[key[0]].append(delta)
                else:
                    excluded.append(list(key))
            values = [v for cluster in maps.values() for v in cluster]
            comparisons[before][opponent] = {'clean_pairs': len(values), 'excluded': excluded,
                 'gain_pp': 100 * statistics.mean(values) if values else None, 'paired_95_pp': interval(list(maps.values()))}
        pooled_values = [v for cluster in pooled.values() for v in cluster]
        comparisons[before]['pooled'] = {'gain_pp': 100 * statistics.mean(pooled_values), 'paired_95_pp': interval(list(pooled.values()))}
    own_errors = sum(bool(r['own_action_errors']) for r in rows)
    invalid = sum(not r['valid'] or r['returncode'] != 0 for r in rows)
    primary = comparisons['control']
    technical = json.loads((panel / 'java-verification.json').read_text())['passed']
    native = json.loads((panel / 'native-verification.json').read_text())
    technical &= not native['native_replay_mismatches'] and not native['map_overlap_seeds'] and own_errors == 0 and invalid == 0
    minimum_pairs = int(.9 * len(json.loads((panel / 'panel-spec.json').read_text())['seeds']) * 2)
    coverage = all(primary[o]['clean_pairs'] >= minimum_pairs for o in ('lacoz', 'khoufou', 'b2m'))
    gate = bool(technical and coverage and primary['pooled']['gain_pp'] > 0 and
                all(primary[o]['gain_pp'] >= -10 for o in ('lacoz', 'khoufou', 'b2m')) and
                groups['curriculum_vs_control']['score_rate'] > .5)
    result = {'as_of': now(), 'groups': groups, 'paired_curriculum_minus': comparisons,
              'technical_passed': technical, 'own_error_games': own_errors, 'invalid_games': invalid,
              'coverage_passed': coverage, 'continuation_gate_passed': gate, 'external_spend': 0,
              'bootstrap': '10000 resamples of whole maps, keeping both seats and opponent pairing; fixed seed20261106',
              'scope': 'One training seed. Adaptive development screen, not independent global final or training-seed replication.'}
    save(panel / 'analysis.json', result)
    print(json.dumps(result), flush=True)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('stage', choices=['screen', 'expand'])
    args = ap.parse_args()
    if args.stage == 'expand':
        assert json.loads((OUT / 'screen/analysis.json').read_text())['continuation_gate_passed']
    assert json.loads((OUT / 'contracts/summary.json').read_text())['passed']
    from audit_arm import audit, audit_pair
    for arm in ('control', 'curriculum'):
        path = OUT / f'pilot-{arm}/technical-audit.json'
        if not path.exists():
            print(json.dumps(audit(arm)), flush=True)
        assert json.loads(path.read_text())['passed']
    if not (OUT / 'matched-pair-audit.json').exists():
        print(json.dumps(audit_pair()), flush=True)
    policies = {'curriculum': OUT / 'pilot-curriculum/weights.txt', 'control': OUT / 'pilot-control/weights.txt',
                'base': BASE / 'weights.txt', 'b2m': B2M}
    for name in ('curriculum', 'control'):
        summary = json.loads((policies[name].parent / 'summary.json').read_text())
        assert summary['stop'] == 'sample_target' and summary['weights_sha256'] == sha(policies[name])
    seeds = list(range(61001, 61013)) if args.stage == 'screen' else list(range(61013, 61041))
    maps = prepare_maps(args.stage, seeds)
    pairs = [[candidate, opponent] for opponent in ('lacoz', 'khoufou', 'b2m') for candidate in ('curriculum', 'control', 'base')]
    pairs += [['curriculum', 'control'], ['curriculum', 'base']]
    spec = {'purpose': 'development', 'seeds': seeds, 'policies': {k: str(v.relative_to(ROOT)) for k, v in policies.items()},
            'pairs': pairs, 'rotate_order': True, 'require_new_maps': True, 'stop_at': '2026-11-09T02:00:00Z',
            'exclude_map_hash_files': [str((OUT / f'{args.stage}-exclusions.json').relative_to(ROOT))]}
    spec_path = OUT / f'{args.stage}-spec.json'
    save(spec_path, spec)
    panel = OUT / args.stage
    commands = [
        [sys.executable, '-B', 'code/rl/eval/panel.py', '--spec', str(spec_path.relative_to(ROOT)), '--out', str(panel.relative_to(ROOT))],
        [sys.executable, '-B', 'code/rl/eval/verify_panel.py', str(panel.relative_to(ROOT)), '--out', str((panel / 'native-verification.json').relative_to(ROOT))],
        [sys.executable, '-B', 'code/rl/eval/verify_java_panel.py', str(panel.relative_to(ROOT)), '--out', str((panel / 'java-verification.json').relative_to(ROOT))],
    ]
    save(OUT / f'{args.stage}-commands.json', [['${PYTHON}', *command[1:]] for command in commands])
    for index, command in enumerate(commands):
        run(command, OUT / f'{args.stage}-command{index}.log')
    claimed = {str(r['seed']): r['hash'] for r in maps}
    assert json.loads((panel / 'map-hashes.json').read_text()) == claimed
    analyze(panel)


if __name__ == '__main__':
    main()
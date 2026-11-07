#!/usr/bin/env python3
"""Audit named-policy panels, frozen inputs, map novelty and native replays."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from run_matches import BASE
from analyze_holdout import map_content
from rl.data.replays import read
from rl.sim.native import Simulator


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def old_maps(spec):
    historical = json.loads((BASE / 'experiments/2026-11-06-attack-holdout/historical-maps.json').read_text())['maps']
    legacy = {row['content_sha256'] for row in historical.values()}
    legacy.update(json.loads((BASE / 'experiments/2026-11-06-attack-holdout/selection.json').read_text())['map_novelty']['new_content_sha256_by_seed'].values())
    for experiment in ('bc-v1', 'ppo-v1'):
        path = BASE / f'experiments/rl/2026-11-06-{experiment}/verification.json'
        legacy.update(json.loads(path.read_text())['new_legacy_hashes_by_seed'].values())
    canonical = set()
    for relative in spec.get('exclude_map_manifests', []):
        manifest = json.loads((BASE / relative).read_text())
        for split in ('training', 'selection'):
            for row in manifest.get(split, []):
                canonical.add(row['hash'])
                if 'legacy_hash' in row:
                    legacy.add(row['legacy_hash'])
    return legacy, canonical


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    run = args.run
    manifest = json.loads((run / 'manifest.json').read_text())
    spec = json.loads((run / 'panel-spec.json').read_text())
    rows = [json.loads(line) for line in (run / 'matches.jsonl').read_text().splitlines()]
    expected = {(c, o, s, p) for c, o in manifest['pairs'] for s in manifest['seeds'] for p in manifest['seats']}
    assert len(rows) == len(expected)
    assert {(r['candidate'], r['opponent'], r['seed'], r['seat']) for r in rows} == expected
    for relative, digest in manifest['source_sha256'].items():
        assert sha(run / 'snapshots' / relative) == digest, relative
    for name, digest in manifest['policy_weights_sha256'].items():
        assert sha(run / 'snapshots/weights' / (name + '.txt')) == digest, name
    assert sha(run / 'snapshots/v6.cpp') == sha(BASE / 'code/bot.cpp') == sha(BASE / 'code/variants/v6-attack.cpp')
    old_legacy, old_canonical = old_maps(spec)
    new_legacy, new_canonical = {}, {}
    overlaps, errors, technical = [], [], []
    turns = 0
    for row in rows:
        path = run / f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}.json.gz'
        seed, digest = map_content(path)
        record = read(path)
        canonical = hashlib.sha256(json.dumps(record['map'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        assert seed == row['seed']
        assert canonical == row['map_content_sha256']
        assert seed not in new_legacy or new_legacy[seed] == digest
        assert seed not in new_canonical or new_canonical[seed] == canonical
        new_legacy[seed], new_canonical[seed] = digest, canonical
        if digest in old_legacy or canonical in old_canonical:
            overlaps.append(seed)
        if not row['valid'] or row['returncode'] or row['own_action_errors'] or row['opponent_action_errors'] or record['errors']:
            technical.append(path.name)
            continue
        sim = Simulator(record['map'])
        for turn, decision in enumerate(record['decisions']):
            if sim.state()['units'] != decision['units']:
                errors.append({'record': path.name, 'turn': turn, 'kind': 'viewer_units'})
                break
            sim.step(decision['actions'])
            turns += 1
        state = sim.state()
        scores = [record['scores'][str(p)] for p in (0, 1)]
        if any(state['errors']):
            errors.append({'record': path.name, 'kind': 'native_parse', 'counts': state['errors']})
        if not state['done'] or state['score'] != scores:
            errors.append({'record': path.name, 'kind': 'terminal', 'native': state['score'], 'original': scores})
        sim.close()
    assert len(set(new_legacy.values())) == len(manifest['seeds'])
    assert len(set(new_canonical.values())) == len(manifest['seeds'])
    report = {
        'verifier_sha256': sha(Path(__file__)), 'purpose': manifest['purpose'],
        'games': len(rows), 'source_freeze_verified': True,
        'policy_weights_sha256': manifest['policy_weights_sha256'],
        'v6_source_sha256': sha(BASE / 'code/bot.cpp'),
        'previous_unique_legacy_maps': len(old_legacy),
        'previous_unique_canonical_maps': len(old_canonical),
        'unique_maps': len(new_legacy), 'map_overlap_seeds': sorted(set(overlaps)),
        'new_legacy_hashes_by_seed': new_legacy, 'new_canonical_hashes_by_seed': new_canonical,
        'native_joint_transitions': turns, 'native_replay_mismatches': errors,
        'technical_records_excluded_from_native_replay': technical,
        'own_error_games': sum(bool(r['own_action_errors']) for r in rows),
        'opponent_error_games': sum(bool(r['opponent_action_errors']) for r in rows),
        'wall_seconds': time.monotonic() - started,
    }
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if not k.endswith('_by_seed')}, indent=2))
    assert not errors, 'Native replay differs from original referee'
    if manifest['purpose'] == 'confirmation':
        assert not overlaps, 'Confirmation contains previously inspected maps'


if __name__ == '__main__':
    main()

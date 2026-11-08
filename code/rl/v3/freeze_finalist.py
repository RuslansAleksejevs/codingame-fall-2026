#!/usr/bin/env python3
"""Freeze exactly one full-development finalist before reserved maps are opened.

Creates frozen weights, a content-exclusion registry and the 2,200-game spec.
It never starts the panel, promotes a policy, or changes selected-policy.json.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'code'))
from rl.train.ppo import save, sha
from rl.v3.map_registry import build
from rl.v3.final_evidence import EXTERNAL, SEEDS, BASE_HASH

EXP = ROOT / 'experiments/rl/2026-11-07-ppo-v3'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ranking', type=Path, required=True)
    ap.add_argument('--candidate', required=True)
    ap.add_argument('--research-complete', action='store_true',
                    help='Explicitly confirm that all learning/evaluation processes have exited and no more selection is planned')
    args = ap.parse_args()
    assert args.research_complete, 'Finish research and inspect process status first'
    assert datetime.now(timezone.utc) < datetime(2026, 11, 9, 7, tzinfo=timezone.utc), 'Final evaluation start window closed'
    rank_path = args.ranking.resolve()
    assert rank_path.parent == EXP and re.fullmatch(r'full-dev-block\d+-ranking\.json', rank_path.name)
    tag = rank_path.name.removesuffix('-ranking.json')
    assert json.loads((EXP / (tag+'-status.json')).read_text())['stage'] == 'finished'
    assert json.loads((EXP / 'campaign-status.json').read_text())['stage'] == 'first_blocks_finished'
    assert (EXP / 'search/decision.json').exists(), 'Record the bounded-search outcome before freezing'
    out = EXP / 'finalist'
    assert not out.exists() and not (EXP / 'final-confirmation').exists(), 'Never reselect after a finalist/holdout is opened'
    ranking = json.loads(rank_path.read_text())
    eligible = [r for r in ranking['ranking'] if r['safeguards_pass']]
    assert eligible and eligible[0]['candidate'] == args.candidate, 'Use the frozen full-development ranking, not an untested choice'
    chosen = eligible[0]
    panel = EXP / tag
    manifest = json.loads((panel / 'manifest.json').read_text())
    assert manifest['purpose'] == 'development' and manifest['seeds'] == list(range(30001, 30041))
    weights = ROOT / chosen['weights']
    assert sha(weights) == manifest['policy_weights_sha256'][args.candidate]
    native_path, java_path = EXP / (tag+'-verification.json'), EXP / (tag+'-java.json')
    native, java = json.loads(native_path.read_text()), json.loads(java_path.read_text())
    assert native['source_freeze_verified'] and not native['native_replay_mismatches']
    assert java['passed'] and java['clean_games_replayed'] + len(java['technical_records_excluded']) == native['games']
    base = ROOT / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt'
    assert sha(base) == BASE_HASH
    assert sha(ROOT / 'submissions/ppo-v2-league3m.cpp') == '199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1'
    independent_runs = {}
    for arm, seed in [('a', 202611074), ('b', 202611075)]:
        run = EXP / ('seed-'+arm)
        config = json.loads((run / 'config.json').read_text())
        summary = json.loads((run / 'summary.json').read_text())
        assert config['seed'] == seed and config['initial_weights_sha256'] == BASE_HASH
        assert summary['additional_steps'] > 0 and not summary['teacher']['errors']
        independent_runs[arm] = {'seed': seed, 'additional_steps': summary['additional_steps'],
                                 'config_sha256': sha(run / 'config.json'), 'summary_sha256': sha(run / 'summary.json')}
    frozen_sources = {str(p.relative_to(ROOT)): sha(p) for p in [
        ROOT / 'code/rl/models/policy.hpp', ROOT / 'code/rl/sim/simulator.hpp',
        ROOT / 'code/rl/export/bot.cpp', ROOT / 'code/rl/export/inference.hpp',
        ROOT / 'code/rl/export/package.py', ROOT / 'code/rl/v3/verify_package.py',
        ROOT / 'code/rl/eval/panel.py', ROOT / 'code/rl/eval/verify_panel.py',
        ROOT / 'code/rl/eval/verify_java_panel.py', ROOT / 'code/rl/v3/run_final.py',
        Path(__file__).resolve(), ROOT / 'code/rl/v3/final_evidence.py', EXP / 'PROTOCOL.md', EXP / 'FINAL_GATES.md']}
    out.mkdir(exist_ok=False)
    shutil.copy2(weights, out / 'weights.txt')
    packages = {}
    for name, path, digest in [('ppo3', out / 'weights.txt', sha(out / 'weights.txt')),
                               ('league3m', base, BASE_HASH)]:
        package_dir = out / ('package-'+name)
        command = [sys.executable, str(ROOT / 'code/rl/export/package.py'), '--weights', str(path),
                   '--sha256', digest, '--out', str(package_dir)]
        with (out / ('package-'+name+'.log')).open('x') as log:
            subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        metadata = json.loads((package_dir / 'package.json').read_text())
        packages[name] = {'manifest_path': str((package_dir / 'package.json').relative_to(ROOT)),
                          'manifest_sha256': sha(package_dir / 'package.json'),
                          'source_path': metadata['source_path'], 'source_sha256': metadata['source_sha256']}
    freeze = {'as_of': datetime.now(timezone.utc).isoformat(), 'provenance': 'PROJECT_REPORTED',
              'candidate_name': 'ppo3', 'development_name': args.candidate,
              'weights_path': str((out / 'weights.txt').relative_to(ROOT)), 'weights_sha256': sha(out / 'weights.txt'),
              'original_weights_path': str(weights.relative_to(ROOT)), 'ranking_sha256': sha(rank_path),
              'development_manifest_sha256': sha(panel / 'manifest.json'), 'development_result': chosen,
              'native_verification_sha256': sha(native_path), 'java_verification_sha256': sha(java_path),
              'independent_runs': independent_runs, 'frozen_sources': frozen_sources, 'packages': packages,
              'development_panel_path': str(panel.relative_to(ROOT)),
              'scope': 'One fixed candidate before final maps; no promotion/submission. Base remains deployed.',
              'no_more_training_or_final_set_tuning': True}
    save(out / 'freeze.json', freeze)
    registry = build(out / 'map-registry.json')
    save(out / 'map-registry.json', registry)
    spec = {'purpose': 'confirmation', 'seeds': list(SEEDS), 'rotate_order': True,
            'require_new_maps': True, 'stop_at': '2026-11-09T07:00:00Z',
            'policies': {'ppo3': freeze['weights_path'], 'league3m': str(base.relative_to(ROOT)),
                         'bc': 'experiments/rl/2026-11-06-bc-v1/training/weights.txt'},
            'policy_variants': {'ppo3': 'packaged', 'league3m': 'packaged'},
            'packaged_configs': {name: {'manifest': p['manifest_path']} for name, p in packages.items()},
            'pairs': [['league3m', o] for o in EXTERNAL] + [['ppo3', o] for o in (*EXTERNAL, 'league3m')],
            'exclude_map_hash_files': [str((out / 'map-registry.json').relative_to(ROOT))]}
    save(out / 'panel-spec.json', spec)
    save(out / 'prepared.json', {'as_of': datetime.now(timezone.utc).isoformat(),
         'freeze_sha256': sha(out / 'freeze.json'), 'spec_sha256': sha(out / 'panel-spec.json'),
         'registry_sha256': sha(out / 'map-registry.json'), 'known_canonical_maps': len(registry['canonical']),
         'known_legacy_maps': len(registry['legacy']), 'planned_games': 2200,
         'reserved_maps_generated_or_read_by_this_script': 0})
    print(json.dumps(freeze, indent=2))


if __name__ == '__main__':
    main()
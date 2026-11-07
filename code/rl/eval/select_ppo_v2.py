#!/usr/bin/env python3
"""Freeze the predeclared PPO-v2 development winner before opening final maps."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from run_matches import BASE


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('experiment', type=Path)
    args = parser.parse_args()
    root = args.experiment
    run = root / 'dev-finalists'
    assert not (root / 'selection.json').exists(), 'Selection is immutable'
    assert not (root / 'confirmation').exists(), 'Final maps must remain unopened'
    spec = read(run / 'panel-spec.json')
    manifest = read(run / 'manifest.json')
    inputs = read(root / 'dev-finalists-inputs.json')
    native = read(root / 'dev-finalists-verification.json')
    java = read(root / 'dev-finalists-java-verification.json')
    assert spec['purpose'] == 'development'
    assert native['source_freeze_verified'] and not native['native_replay_mismatches']
    assert java['passed'] and not java['mismatches']
    rows = [json.loads(line) for line in (run / 'matches.jsonl').read_text().splitlines()]
    expected = {(c, o, s, p) for c, o in spec['pairs'] for s in spec['seeds'] for p in (0, 1)}
    assert len(rows) == len(expected) == 1150
    assert {(r['candidate'], r['opponent'], r['seed'], r['seat']) for r in rows} == expected
    assert manifest['policy_weights_sha256'] == inputs['policy_weights_sha256']
    assert java['clean_games_replayed'] == len(rows) - len(java['technical_records_excluded'])
    opponents = ('lacoz', 'khoufou', 'v6', 'ppo1')
    groups = {}
    for candidate, opponent in spec['pairs']:
        group = [r for r in rows if r['candidate'] == candidate and r['opponent'] == opponent]
        clean = [r for r in group if r['valid'] and not r['returncode']
                 and not r['own_action_errors'] and not r['opponent_action_errors']]
        groups[f'{candidate}_vs_{opponent}'] = {
            'games': len(group), 'clean_games': len(clean),
            'results': dict(Counter(r['outcome'] for r in group)),
            'clean_results': dict(Counter(r['outcome'] for r in clean)),
            'score_rate': sum({'win': 1, 'draw': .5, 'loss': 0}[r['outcome']] for r in clean) / len(clean) if clean else None,
            'own_error_games': sum(bool(r['own_action_errors']) for r in group),
            'opponent_error_games': sum(bool(r['opponent_action_errors']) for r in group),
            'invalid_games': sum(not r['valid'] or bool(r['returncode']) for r in group),
        }
    candidates = []
    for name in inputs['additional_steps']:
        metrics = {opponent: groups[f'{name}_vs_{opponent}'] for opponent in opponents}
        guards = {
            opponent: metrics[opponent]['score_rate'] is not None
            and metrics[opponent]['score_rate'] + 1e-12 >= groups[f'ppo1_vs_{opponent}']['score_rate'] - .06
            for opponent in ('khoufou', 'v6')
        }
        guards['direct_ppo1'] = metrics['ppo1']['score_rate'] is not None and metrics['ppo1']['score_rate'] >= .60
        guards['complete_clean_panel'] = all(g['clean_games'] == 50 for g in metrics.values())
        candidates.append({
            'name': name, 'guards': guards, 'eligible': all(guards.values()),
            'lacoz_score_rate': metrics['lacoz']['score_rate'],
            'four_opponent_mean_score_rate': sum(g['score_rate'] or 0 for g in metrics.values()) / 4,
            'additional_steps': inputs['additional_steps'][name],
            'training_elapsed_seconds': inputs['training_elapsed_seconds'][name],
        })
    eligible = sorted((r for r in candidates if r['eligible']),
                      key=lambda r: (-r['lacoz_score_rate'], -r['four_opponent_mean_score_rate'], r['training_elapsed_seconds']))
    assert eligible, 'No candidate satisfies the predeclared safeguards'
    winner = eligible[0]['name']
    weights = spec['policies'][winner]
    variant = spec.get('policy_variants', {}).get(winner, 'standard')
    assert sha(BASE / weights) == manifest['policy_weights_sha256'][winner]
    selected = {
        'as_of': datetime.now(timezone.utc).isoformat(), 'provenance': 'PROJECT_REPORTED',
        'status': 'frozen_before_confirmation', 'confirmation_maps_opened': False,
        'selection_rule': inputs['selection_rule'], 'selected': winner,
        'weights': weights, 'weights_sha256': sha(BASE / weights),
        'checkpoint': str(Path(weights).with_name('checkpoint.pt')),
        'checkpoint_sha256': sha(BASE / Path(weights).with_name('checkpoint.pt')),
        'policy_variant': variant, 'inference_style': 3 if variant == 'roads' else 2,
        'additional_steps': inputs['additional_steps'][winner],
        'common_initialization_steps': 752998,
        'training_elapsed_seconds': inputs['training_elapsed_seconds'][winner],
        'candidates': candidates, 'eligible_ranking': [r['name'] for r in eligible],
        'groups': groups, 'development_manifest_sha256': sha(run / 'manifest.json'),
        'source_sha256': manifest['source_sha256'],
        'selection_script_sha256': sha(Path(__file__)),
        'caveat': 'Selection on reused maps, not independent confirmation. Repeated development panels are not pooled.',
    }
    confirmation = {
        'purpose': 'confirmation',
        'policies': {
            'ppo2': weights,
            'ppo1': 'experiments/rl/2026-11-06-ppo-v1/training/weights.txt',
            'bc': 'experiments/rl/2026-11-06-bc-v1/training/weights.txt',
        },
        'policy_variants': {'ppo2': variant},
        'pairs': [[c, o] for o in ('lacoz', 'khoufou', 'v6', 'bc') for c in ('ppo2', 'ppo1')] + [['ppo2', 'ppo1']],
        'seeds': list(range(9001, 9101)), 'rotate_order': True,
        'exclude_map_manifests': spec['exclude_map_manifests'],
        'selection_sha256': None,
    }
    (root / 'selection.json').write_text(json.dumps(selected, indent=2) + '\n')
    confirmation['selection_sha256'] = sha(root / 'selection.json')
    (root / 'confirmation-spec.json').write_text(json.dumps(confirmation, indent=2) + '\n')
    print(json.dumps({k: selected[k] for k in ('selected', 'weights_sha256', 'additional_steps', 'eligible_ranking', 'candidates')}, indent=2))


if __name__ == '__main__':
    main()

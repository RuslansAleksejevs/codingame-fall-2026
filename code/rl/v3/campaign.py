#!/usr/bin/env python3
"""Supervised first blocks: A, isolated screening, B, isolated screening.

This bounded driver never submits, publishes, changes Git refs, or opens final maps.
It stops on any failed contract and records each command in a separate new log.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'code'))
from rl.train.ppo import sha, save
from rl.eval.analyze import clean, value

EXP = Path('experiments/rl/2026-11-07-ppo-v3')
BASE_POLICY = Path('experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173')
CUTOFF = datetime(2026, 11, 9, 2, tzinfo=timezone.utc)
EXTERNAL = ['lacoz', 'khoufou2', 'khoufou', 'v6', 'bc']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arms', nargs='+', choices=['a', 'b'], default=['a', 'b'])
    args = ap.parse_args()
    os.chdir(ROOT)
    assert json.loads((EXP / 'v3-tests-2/summary.json').read_text())['passed']
    pilot = json.loads((EXP / 'pilot-v3/summary.json').read_text())
    assert pilot['additional_steps'] >= 20000 and not pilot['teacher']['errors']
    baseline = json.loads((EXP / 'baseline-dev-verification.json').read_text())
    assert baseline['games'] == 400 and not baseline['native_replay_mismatches'] and not baseline['map_overlap_seeds']
    assert not baseline['own_error_games']
    assert sha(BASE_POLICY / 'checkpoint.pt') == '9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663'
    assert sha(BASE_POLICY / 'weights.txt') == 'dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb'
    assert sha(Path('submissions/ppo-v2-league3m.cpp')) == '199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1'

    def event(stage, **values):
        record = {'as_of': datetime.now(timezone.utc).isoformat(), 'pid': os.getpid(), 'stage': stage, **values}
        save(EXP / 'campaign-status.json', record)
        with (EXP / 'campaign-events.jsonl').open('a') as f:
            f.write(json.dumps(record) + '\n')
        print(json.dumps(record), flush=True)

    def run(command, label):
        assert datetime.now(timezone.utc) < CUTOFF, 'Research cutoff reached; no new stages'
        path = EXP / (label + '.log')
        public_command = [str(x).replace(str(ROOT), '${PROJECT_ROOT}') for x in command]
        event('running', label=label, command=public_command, log=str(path))
        with path.open('x') as log:
            process = subprocess.run([str(x) for x in command], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        event('stage_finished', label=label, returncode=process.returncode, log=str(path))
        assert process.returncode == 0, f'Failed stage {label}; inspect preserved log'

    for arm in args.arms:
        training = EXP / f'seed-{arm}'
        assert not training.exists(), 'Existing run requires explicit resume review; never overwrite'
        seed = {'a': 202611074, 'b': 202611075}[arm]
        run([sys.executable, 'code/rl/v3/train.py', '--maps', 'experiments/rl/2026-11-06-ppo-v2/maps-2000.json',
             '--init', BASE_POLICY / 'checkpoint.pt', '--initial-weights', BASE_POLICY / 'weights.txt',
             '--opponents', EXP / 'training-opponents.json', '--out', training, '--steps', '2000000',
             '--minutes', '120', '--seed', str(seed)], f'train-{arm}-block1')
        summary = json.loads((training / 'summary.json').read_text())
        assert not summary['teacher']['errors'] and summary['additional_steps'] > 0
        assert datetime.now(timezone.utc) < CUTOFF, 'Research cutoff reached after training'
        snapshots = sorted(training.glob('step-*/checkpoint.pt'))
        indexed = [(int(p.parent.name.split('-')[1]), p) for p in snapshots]
        chosen = {min((pair for pair in indexed if pair[0] >= target), default=indexed[-1])
                  for target in (500000, 1000000, 1500000, summary['additional_steps'])}
        policies = {'league3m': str(BASE_POLICY / 'weights.txt'),
                    'bc': 'experiments/rl/2026-11-06-bc-v1/training/weights.txt'}
        candidates = []
        for step, checkpoint in sorted(chosen):
            name = f'{arm}{step}'
            candidates.append(name)
            policies[name] = str(checkpoint.parent / 'weights.txt')
        if len(snapshots) >= 3:
            averaged = training / 'average-block1'
            run([sys.executable, 'code/rl/v3/average.py', '--checkpoints', *snapshots[-3:], '--out', averaged], f'average-{arm}-block1')
            candidates.append(f'{arm}average')
            policies[f'{arm}average'] = str(averaged / 'weights.txt')
        for candidate in candidates:
            run([sys.executable, 'code/rl/export/verify.py', '--training', Path(policies[candidate]).parent,
                 '--data', 'code/build/rl-cache/bc-v1-clean', '--out', EXP / f'export-{candidate}.json'], f'export-{candidate}')
        spec = {'purpose': 'development', 'seeds': list(range(30001, 30013)), 'rotate_order': True,
                'policies': policies, 'pairs': [['league3m', o] for o in EXTERNAL] +
                [[c, o] for c in candidates for o in EXTERNAL + ['league3m']],
                'exclude_map_hash_files': [str(EXP / 'map-registry-initial.json')]}
        spec_path = EXP / f'screen-{arm}-block1-spec.json'
        save(spec_path, spec)
        panel = EXP / f'screen-{arm}-block1'
        run([sys.executable, 'code/rl/eval/panel.py', '--spec', spec_path, '--out', panel], f'screen-{arm}-block1')
        run([sys.executable, 'code/rl/eval/verify_panel.py', panel, '--out', EXP / f'screen-{arm}-block1-verification.json'], f'verify-{arm}-block1')
        verification = json.loads((EXP / f'screen-{arm}-block1-verification.json').read_text())
        assert not verification['native_replay_mismatches'] and not verification['own_error_games']
        rows = [json.loads(line) for line in (panel / 'matches.jsonl').read_text().splitlines()]
        def score(candidate, opponent):
            games = [r for r in rows if r['candidate'] == candidate and r['opponent'] == opponent and clean(r)]
            return statistics.mean(map(value, games)) if games else None
        ranking = []
        for candidate in candidates:
            scores = {o: score(candidate, o) for o in EXTERNAL + ['league3m']}
            assert all(v is not None for v in scores.values())
            admissible = all(scores[o] >= score('league3m', o) - .05 for o in ('v6', 'bc'))
            ranking.append({'candidate': candidate, 'weights': policies[candidate], 'scores': scores,
                            'primary_mean': statistics.mean(scores[o] for o in ('lacoz', 'khoufou2', 'khoufou', 'league3m')),
                            'safeguards_pass': admissible})
        # Within one percentage point, prefer the earlier raw checkpoint; the
        # average was appended last. Repeat within each admissibility group.
        ordered = []
        for admissible in (True, False):
            remaining = [r for r in ranking if r['safeguards_pass'] == admissible]
            while remaining:
                best = max(r['primary_mean'] for r in remaining)
                chosen = next(r for r in remaining if r['primary_mean'] >= best - .01)
                ordered.append(chosen)
                remaining.remove(chosen)
        ranking = ordered
        save(EXP / f'screen-{arm}-block1-ranking.json', {'ranking': ranking,
             'shortlist': [r['candidate'] for r in ranking if r['safeguards_pass']][:2],
             'scope': 'Adaptive development screen only, not independent improvement evidence. Full 40-map evaluation remains.'})
        event('arm_screened', arm=arm, steps=summary['additional_steps'], ranking=ranking)
    event('first_blocks_finished', arms=args.arms, required_next='Full development finalists, bounded search pilot, possible continuation, frozen independent final panel and packaging/platform verification. No submission authorized.')


if __name__ == '__main__':
    main()
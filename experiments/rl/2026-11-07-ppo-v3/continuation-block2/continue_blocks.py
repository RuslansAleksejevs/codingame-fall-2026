#!/usr/bin/env python3
"""Resume both independent trajectories for one bounded block, then compare.

The frozen trainer is unchanged. Earlier checkpoints and latest-file backups are
preserved. Each seed's preceding full-development champion remains a screened
incumbent; at most one new challenger joins it in the next full panel.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'code'))
from rl.train.ppo import save, sha
from rl.v3.full_development import statistics_for, rank, EXTERNAL, CUTOFF

EXP = ROOT / 'experiments/rl/2026-11-07-ppo-v3'
BASE = ROOT / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173'
BASE_CHECKPOINT = '9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663'
BASE_WEIGHTS = 'dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb'
FALLBACK = '199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1'


def block_limits(summary):
    steps, elapsed = summary['additional_steps'], summary['elapsed_seconds']
    assert 0 < steps < 8_000_000 and 0 < elapsed < 480 * 60
    return min(8_000_000, steps + 2_000_000), min(480., elapsed / 60 + 120.)


def choose_snapshots(indexed, start, end):
    assert indexed and all(step > start for step, _ in indexed)
    targets = [start + d for d in (500_000, 1_000_000, 1_500_000)] + [end]
    # Checkpoint thresholds use a global250k grid, whereas each block can end
    # a batch past its target. Nearest avoids accidentally skipping a whole
    # quarter-million checkpoint because of that harmless small overshoot.
    return sorted({min(indexed, key=lambda pair: (abs(pair[0] - t), pair[0])) for t in targets})


def screen_selection(rows, policies, incumbent):
    results = []
    for name, weights in policies.items():
        if name in ('league3m', 'bc'):
            continue
        result = statistics_for(rows, name)
        complete = all(v is not None for v in result['scores'].values())
        result['safeguards_pass'] = bool(
            complete and not result['own_or_invalid_games']
            and min(result['clean_paired_games'].values()) >= 22
            and min(result['paired_gain_pp'][o] for o in ('v6', 'bc')) >= -5)
        results.append(dict(result, weights=weights))
    ordered = rank(results)
    previous = next(r for r in ordered if r['candidate'] == incumbent)
    # Preserve the broad-panel champion, while using the cheap screen only to
    # choose its challenger. A failed incumbent is not silently discarded.
    assert previous['safeguards_pass'], 'Incumbent failed screen safeguards; inspect preserved evidence'
    new = [r['candidate'] for r in ordered
           if r['candidate'] != incumbent and r['safeguards_pass']]
    return ordered, [incumbent] + new[:1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--block', type=int, required=True)
    args = ap.parse_args()
    assert args.block == 2, 'This reviewed driver is limited to the second A/B block'
    assert datetime.now(timezone.utc) < CUTOFF
    assert not (EXP / 'finalist').exists() and not (EXP / 'final-confirmation').exists()
    assert json.loads((EXP / 'campaign-status.json').read_text())['stage'] == 'first_blocks_finished'
    assert json.loads((EXP / 'search/decision.json').read_text())['status'] == 'not_confirmed'
    previous_tag = f'full-dev-block{args.block - 1}'
    assert json.loads((EXP / (previous_tag + '-status.json')).read_text())['stage'] == 'finished'
    ranking_path = EXP / (previous_tag + '-ranking.json')
    previous = json.loads(ranking_path.read_text())
    manifest_path = EXP / previous_tag / 'manifest.json'
    matches_path = EXP / previous_tag / 'matches.jsonl'
    manifest = json.loads(manifest_path.read_text())
    assert manifest['seeds'] == list(range(30001, 30041))
    for suffix in ('verification', 'java'):
        report = json.loads((EXP / (previous_tag + '-' + suffix + '.json')).read_text())
        assert report['panel_manifest_sha256'] == sha(manifest_path)
        assert report['panel_matches_sha256'] == sha(matches_path)
        if suffix == 'java':
            assert report['passed']
        else:
            assert report['source_freeze_verified'] and not report['native_replay_mismatches']
    assert sha(BASE / 'checkpoint.pt') == BASE_CHECKPOINT
    assert sha(BASE / 'weights.txt') == BASE_WEIGHTS
    assert sha(ROOT / 'submissions/ppo-v2-league3m.cpp') == FALLBACK

    incumbents, summaries, sources = {}, {}, {}
    for arm in ('a', 'b'):
        incumbent = next(r for r in previous['ranking']
                         if r['candidate'].startswith(arm) and r['safeguards_pass'])
        assert incumbent['external_gain_pp'] > 0
        assert incumbent['scores']['league3m'] > .5
        assert min(incumbent['paired_gain_pp'][o] for o in EXTERNAL) >= -5
        assert sha(ROOT / incumbent['weights']) == manifest['policy_weights_sha256'][incumbent['candidate']]
        incumbents[arm] = incumbent
        training = EXP / ('seed-' + arm)
        summaries[arm] = json.loads((training / 'summary.json').read_text())
        assert not summaries[arm]['teacher']['errors']
        block_limits(summaries[arm])
        sources[arm] = json.loads((training / 'source-sha256.json').read_text())
        assert all(sha(ROOT / path) == digest for path, digest in sources[arm].items())
        assert not (EXP / f'screen-{arm}-block{args.block}').exists()

    tag = f'continuation-block{args.block}'
    archive = EXP / tag
    archive.mkdir(exist_ok=False)
    for path in (Path(__file__).resolve(), ROOT / 'code/rl/v3/full_development.py',
                 EXP / 'CONTINUATION.md'):
        shutil.copy2(path, archive / path.name)
    save(archive / 'decision.json', {'as_of': datetime.now(timezone.utc).isoformat(),
         'previous_ranking_sha256': sha(ranking_path), 'incumbents': incumbents,
         'implementation_sha256': {p.name: sha(p) for p in archive.iterdir() if p.is_file()},
         'frozen_training_source_sha256': sources,
         'limits': {a: {'target_steps': block_limits(s)[0], 'cumulative_minutes': block_limits(s)[1]}
                    for a, s in summaries.items()},
         'scope': 'One additional bounded block per independent seed, serial screens/full development; no final maps.',
         'incumbent_rule': 'Keep the prior full-panel champion plus at most one admissible new screen leader per seed.',
         'external_spend': 0})

    def event(stage, **values):
        record = {'as_of': datetime.now(timezone.utc).isoformat(), 'pid': os.getpid(), 'stage': stage, **values}
        save(EXP / (tag + '-status.json'), record)
        with (EXP / (tag + '-events.jsonl')).open('a') as f:
            f.write(json.dumps(record) + '\n')
        print(json.dumps(record), flush=True)

    def run(command, label):
        assert datetime.now(timezone.utc) < CUTOFF, 'Research cutoff reached'
        path = EXP / (label + '.log')
        event('running', label=label, command=[str(x).replace(str(ROOT), '${PROJECT_ROOT}') for x in command],
              log=str(path.relative_to(ROOT)))
        with path.open('x') as log:
            result = subprocess.run([str(x) for x in command], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        event('stage_finished', label=label, returncode=result.returncode)
        assert result.returncode == 0, 'Failed stage; preserve evidence and inspect ' + label

    try:
        for arm, seed in [('a', 202611074), ('b', 202611075)]:
            training = EXP / ('seed-' + arm)
            before = summaries[arm]
            backup = archive / ('before-' + arm)
            backup.mkdir(exist_ok=False)
            for name in ('final.pt', 'weights.txt', 'summary.json', 'history.jsonl', 'source-sha256.json'):
                shutil.copy2(training / name, backup / name)
            save(backup / 'sha256.json', {p.name: sha(p) for p in backup.iterdir() if p.is_file()})
            target, minutes = block_limits(before)
            run([sys.executable, 'code/rl/v3/train.py', '--maps',
                 'experiments/rl/2026-11-06-ppo-v2/maps-2000.json', '--init', BASE / 'checkpoint.pt',
                 '--initial-weights', BASE / 'weights.txt', '--opponents', EXP / 'training-opponents.json',
                 '--out', training, '--resume', backup / 'final.pt', '--steps', target,
                 '--minutes', minutes, '--seed', seed], f'train-{arm}-block{args.block}')
            summary = json.loads((training / 'summary.json').read_text())
            assert summary['additional_steps'] > before['additional_steps'] and not summary['teacher']['errors']
            save(archive / ('after-' + arm + '.json'), summary)
            snapshots = sorted(p for p in training.glob('step-*/checkpoint.pt')
                               if int(p.parent.name.split('-')[1]) > before['additional_steps'])
            indexed = [(int(p.parent.name.split('-')[1]), p) for p in snapshots]
            chosen = choose_snapshots(indexed, before['additional_steps'], summary['additional_steps'])
            incumbent = incumbents[arm]
            policies = {'league3m': str((BASE / 'weights.txt').relative_to(ROOT)),
                        'bc': 'experiments/rl/2026-11-06-bc-v1/training/weights.txt',
                        incumbent['candidate']: incumbent['weights']}
            for step, path in sorted(chosen):
                policies[f'{arm}{step}'] = str((path.parent / 'weights.txt').relative_to(ROOT))
            if len(snapshots) >= 3:
                averaged = training / f'average-block{args.block}'
                run([sys.executable, 'code/rl/v3/average.py', '--checkpoints', *snapshots[-3:], '--out', averaged],
                    f'average-{arm}-block{args.block}')
                policies[f'{arm}average{args.block}'] = str((averaged / 'weights.txt').relative_to(ROOT))
            candidates = [name for name in policies if name not in ('league3m', 'bc')]
            for name in candidates:
                run([sys.executable, 'code/rl/export/verify.py', '--training', (ROOT / policies[name]).parent,
                     '--data', 'code/build/rl-cache/bc-v1-clean', '--out', EXP / f'export-{name}-block{args.block}.json'],
                    f'export-{name}-block{args.block}')
            screen_tag = f'screen-{arm}-block{args.block}'
            panel = EXP / screen_tag
            spec_path = EXP / (screen_tag + '-spec.json')
            assert not spec_path.exists()
            spec = {'purpose': 'development', 'seeds': list(range(30001, 30013)), 'rotate_order': True,
                    'policies': policies, 'pairs': [['league3m', o] for o in EXTERNAL] +
                    [[c, o] for c in candidates for o in (*EXTERNAL, 'league3m')],
                    'stop_at': CUTOFF.isoformat(),
                    'exclude_map_hash_files': [str((EXP / 'map-registry-initial.json').relative_to(ROOT))]}
            save(spec_path, spec)
            run([sys.executable, 'code/rl/eval/panel.py', '--spec', spec_path, '--out', panel], screen_tag)
            run([sys.executable, 'code/rl/eval/verify_panel.py', panel, '--out', EXP / (screen_tag+'-verification.json')],
                screen_tag + '-verify')
            run([sys.executable, 'code/rl/eval/verify_java_panel.py', panel, '--out', EXP / (screen_tag+'-java.json')],
                screen_tag + '-java')
            rows = [json.loads(line) for line in (panel / 'matches.jsonl').read_text().splitlines()]
            assert len(rows) == len(spec['pairs']) * 24
            ordered, shortlist = screen_selection(rows, policies, incumbent['candidate'])
            save(EXP / (screen_tag + '-ranking.json'), {'ranking': ordered, 'shortlist': shortlist,
                 'incumbent': incumbent['candidate'], 'rule': 'Retain previous full-development champion plus best new admissible challenger.',
                 'scope': 'Adaptive screening, not independent confirmation; at most two per seed advance.'})
            event('arm_screened', arm=arm, steps=summary['additional_steps'], shortlist=shortlist)
        run([sys.executable, 'code/rl/v3/full_development.py', '--block', args.block], f'full-dev-block{args.block}-driver')
        event('finished', required_next='Review full development before any further training or a single finalist freeze. Platform OAuth pending; no submission authorized.')
    except Exception as error:
        event('failed', error=str(error), required_next='Inspect preserved logs; never silently restart or overwrite a partial block.')
        raise


if __name__ == '__main__':
    main()
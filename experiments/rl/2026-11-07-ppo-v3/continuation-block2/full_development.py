#!/usr/bin/env python3
"""Compare at most two screened policies per independent seed on all 40 dev maps.

This produces provisional rankings only. It never opens the final holdout,
changes the selected/deployed policy, resumes training, or submits anything.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'code'))
from rl.eval.analyze import clean, value, interval
from rl.train.ppo import save, sha

EXP = ROOT / 'experiments/rl/2026-11-07-ppo-v3'
EXTERNAL = ('lacoz', 'khoufou2', 'khoufou', 'v6', 'bc')
PRIMARY = ('lacoz', 'khoufou2', 'khoufou', 'league3m')
CUTOFF = datetime(2026, 11, 9, 2, tzinfo=timezone.utc)


def statistics_for(rows, name):
    scores, gains, counts, intervals = {}, {}, {}, {}
    for opponent in EXTERNAL:
        a = {(r['seed'], r['seat']): r for r in rows
             if r['candidate'] == name and r['opponent'] == opponent and clean(r)}
        b = {(r['seed'], r['seat']): r for r in rows
             if r['candidate'] == 'league3m' and r['opponent'] == opponent and clean(r)}
        keys = a.keys() & b.keys()
        assert all(a[k]['map_content_sha256'] == b[k]['map_content_sha256'] for k in keys)
        counts[opponent] = len(keys)
        scores[opponent] = statistics.mean(value(a[k]) for k in keys) if keys else None
        gains[opponent] = statistics.mean(value(a[k])-value(b[k]) for k in keys) if keys else None
        intervals[opponent] = interval([[value(a[k])-value(b[k]) for k in keys if k[0] == seed]
                                        for seed in sorted({k[0] for k in keys})])
    direct = [r for r in rows if r['candidate'] == name and r['opponent'] == 'league3m' and clean(r)]
    scores['league3m'] = statistics.mean(map(value, direct)) if direct else None
    gains['league3m'] = scores['league3m']-.5 if direct else None
    counts['league3m'] = len(direct)
    own_errors = sum(bool(r['own_action_errors']) or not r['valid'] or bool(r['returncode'])
                     for r in rows if r['candidate'] == name)
    complete = all(v is not None for v in scores.values())
    safeguards = (complete and not own_errors and min(counts.values()) >= 72
                  and all(gains[o] >= -.05 for o in ('v6', 'bc')))
    return {'candidate': name, 'scores': scores,
            'paired_gain_pp': {o: 100*g if g is not None else None for o, g in gains.items()},
            'clean_paired_games': counts, 'paired_map_95_pp': intervals,
            'primary_mean': statistics.mean(scores[o] for o in PRIMARY) if complete else None,
            'external_gain_pp': 100*statistics.mean(gains[o] for o in EXTERNAL) if complete else None,
            'own_or_invalid_games': own_errors, 'safeguards_pass': bool(safeguards)}


def rank(results):
    # Prefer earlier raw snapshots within one percentage point; average last.
    def complexity(row):
        number = re.search(r'\d+', row['candidate'])
        return ('average' in row['candidate'], int(number.group()) if number else 10**10, row['candidate'])
    ordered = []
    for safe in (True, False):
        remaining = sorted([r for r in results if r['safeguards_pass'] == safe], key=complexity)
        while remaining:
            eligible = [r for r in remaining if r['primary_mean'] is not None]
            if not eligible:
                ordered.extend(remaining)
                break
            best = max(r['primary_mean'] for r in eligible)
            chosen = next(r for r in eligible if r['primary_mean'] >= best-.01)
            ordered.append(chosen)
            remaining.remove(chosen)
    return ordered


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--block', type=int, default=1)
    args = ap.parse_args()
    assert args.block >= 1
    assert datetime.now(timezone.utc) < CUTOFF
    state = json.loads((EXP / 'campaign-status.json').read_text())
    assert state['stage'] == 'first_blocks_finished', 'Do not overlap the A/B driver'
    search_end = EXP / 'search/decision.json'
    assert search_end.exists(), 'Close/record the bounded search branch first; never overlap timed panels'
    assert json.loads(search_end.read_text())['status'] in (
        'rejected_external_screen', 'time_cap_before_confirmation', 'confirmed_teacher', 'not_confirmed',
        'time_cap_before_external', 'failed_validation', 'time_cap_during_external')
    tag = f'full-dev-block{args.block}'
    out = EXP / tag
    assert not out.exists(), 'Do not overwrite a completed or partial panel'
    policies = {'league3m': 'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt',
                'bc': 'experiments/rl/2026-11-06-bc-v1/training/weights.txt'}
    candidates = []
    provenance = {}
    for arm in ('a', 'b'):
        source = EXP / f'screen-{arm}-block{args.block}-ranking.json'
        ranking = json.loads(source.read_text())
        assert len(ranking['shortlist']) <= 2
        manifest = json.loads((EXP / f'screen-{arm}-block{args.block}/manifest.json').read_text())
        for name in ranking['shortlist']:
            row = next(r for r in ranking['ranking'] if r['candidate'] == name)
            assert row['safeguards_pass']
            assert sha(ROOT / row['weights']) == manifest['policy_weights_sha256'][name]
            policies[name] = row['weights']
            candidates.append(name)
        provenance[str(source.relative_to(ROOT))] = sha(source)
    assert candidates, 'No candidate passed the screening safeguards; retain base and inspect failures'
    spec = {'purpose': 'development', 'seeds': list(range(30001, 30041)), 'rotate_order': True,
            'policies': policies, 'pairs': [['league3m', o] for o in EXTERNAL] +
            [[name, o] for name in candidates for o in (*EXTERNAL, 'league3m')],
            'stop_at': CUTOFF.isoformat(),
            'exclude_map_hash_files': [str((EXP / 'map-registry-initial.json').relative_to(ROOT))]}
    spec_path = EXP / (tag + '-spec.json')
    assert not spec_path.exists(), 'Existing prepared spec requires manual inspection, not replacement'
    save(spec_path, spec)
    save(EXP / (tag + '-selection-input.json'), {'as_of': datetime.now(timezone.utc).isoformat(),
         'candidates': candidates, 'screen_hashes': provenance, 'spec_sha256': sha(spec_path),
         'scope': 'Adaptive development only; final holdout unopened.'})
    def run(command, label):
        assert datetime.now(timezone.utc) < CUTOFF
        log_path = EXP / (label + '.log')
        status = {'as_of': datetime.now(timezone.utc).isoformat(), 'stage': label, 'pid': os.getpid(),
                  'log': str(log_path.relative_to(ROOT))}
        save(EXP / (tag + '-status.json'), status)
        print(json.dumps(status), flush=True)
        with log_path.open('x') as log:
            subprocess.run([str(x) for x in command], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)

    run([sys.executable, 'code/rl/eval/panel.py', '--spec', spec_path, '--out', out], tag)
    run([sys.executable, 'code/rl/eval/verify_panel.py', out, '--out', EXP / (tag + '-verification.json')], tag + '-verify')
    run([sys.executable, 'code/rl/eval/verify_java_panel.py', out, '--out', EXP / (tag + '-java.json')], tag + '-java')
    rows = [json.loads(line) for line in (out / 'matches.jsonl').read_text().splitlines()]
    results = rank([dict(statistics_for(rows, name), weights=policies[name]) for name in candidates])
    save(EXP / (tag + '-ranking.json'), {'as_of': datetime.now(timezone.utc).isoformat(), 'ranking': results,
         'scope': 'Adaptive development ranking, not independent effect evidence or final promotion.',
         'next': 'Review both seeds and broad gains before another bounded block or freezing one finalist.'})
    save(EXP / (tag + '-status.json'), {'as_of': datetime.now(timezone.utc).isoformat(), 'stage': 'finished',
                                     'candidates': candidates, 'games': len(rows)})
    print(json.dumps(results, indent=2), flush=True)


if __name__ == '__main__':
    main()
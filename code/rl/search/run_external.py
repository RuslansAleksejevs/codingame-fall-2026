#!/usr/bin/env python3
"""Run bounded external search validation only after heavy PPO first blocks exit."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'code'))
from rl.train.ppo import save, sha
from rl.eval.analyze import clean, value, interval

EXP = ROOT / 'experiments/rl/2026-11-07-ppo-v3'
OUT = EXP / 'search'
STOP = datetime(2026, 11, 8, 4, tzinfo=timezone.utc)
EXTERNAL = ('lacoz', 'khoufou2', 'khoufou')


def run(command, label):
    assert datetime.now(timezone.utc) < STOP, 'Search pilot cutoff reached'
    path = OUT / (label + '.log')
    with path.open('x') as log:
        subprocess.run([str(x) for x in command], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)


def evaluate(panel, name):
    rows = [json.loads(line) for line in (panel / 'matches.jsonl').read_text().splitlines()]
    scores = {}
    gains = {}
    paired_counts = {}
    for opponent in (*EXTERNAL, 'league3m'):
        chosen = [r for r in rows if r['candidate'] == name and r['opponent'] == opponent and clean(r)]
        control = [r for r in rows if r['candidate'] == 'greedy' and r['opponent'] == opponent and clean(r)]
        scores[opponent] = statistics.mean(map(value, chosen)) if chosen else None
        a = {(r['seed'], r['seat']): r for r in chosen}
        b = {(r['seed'], r['seat']): r for r in control}
        keys = a.keys() & b.keys()
        assert all(a[k]['map_content_sha256'] == b[k]['map_content_sha256'] for k in keys)
        paired_counts[opponent] = len(keys)
        gains[opponent] = statistics.mean(value(a[k])-value(b[k]) for k in keys) if keys else None
    errors = sum(bool(r['own_action_errors']) or not r['valid'] or bool(r['returncode'])
                 for r in rows if r['candidate'] in (name, 'greedy'))
    assert all(v is not None for v in [*scores.values(), *gains.values()])
    external_mean = statistics.mean(scores[o] for o in EXTERNAL)
    gain = statistics.mean(gains[o] for o in EXTERNAL)
    baseline = {(r['opponent'], r['seed'], r['seat']): r for r in rows if r['candidate'] == 'greedy' and clean(r)}
    candidate = {(r['opponent'], r['seed'], r['seat']): r for r in rows if r['candidate'] == name and clean(r)}
    seeds = sorted({r['seed'] for r in rows})
    clusters = []
    retained = []
    for seed in seeds:
        keys = [(opponent, seed, seat) for opponent in EXTERNAL for seat in (0, 1)]
        if all(key in candidate and key in baseline for key in keys):
            clusters.append([value(candidate[key]) - value(baseline[key]) for key in keys])
            retained.append(seed)
    direct = [r for r in rows if r['candidate'] == name and r['opponent'] == 'league3m' and clean(r)]
    direct_clusters = [[value(r) for r in direct if r['seed'] == seed] for seed in seeds]
    direct_clusters = [group for group in direct_clusters if group]
    external_ci, direct_ci = interval(clusters), interval(direct_clusters)
    preliminary = gain >= .05 and scores['league3m'] >= .55 and min(gains[o] for o in EXTERNAL) >= -.05 and not errors
    confirmed = (preliminary and len(retained) >= 20 and external_ci is not None and external_ci[0] > 0
                 and direct_ci is not None and direct_ci[0] > 50)
    return {'candidate': name, 'scores': scores, 'external_mean': external_mean,
            'gain_pp': 100*gain, 'per_opponent_gain_pp': {o: 100*g for o, g in gains.items()},
            'clean_paired_games': paired_counts,
            'own_or_control_technical_games': errors, 'complete_composite_maps': len(retained),
            'external_gain_paired_95_pp': external_ci, 'direct_score_95_percent': direct_ci,
            'preliminary_gate': preliminary, 'confirmed_teacher_gate': bool(confirmed)}


def panel(spec, name):
    path = OUT / name
    run([sys.executable, 'code/rl/eval/panel.py', '--spec', spec, '--out', path], name)
    run([sys.executable, 'code/rl/eval/verify_panel.py', path, '--out', OUT / (name + '-verification.json')], name + '-verify')
    run([sys.executable, 'code/rl/eval/verify_java_panel.py', path, '--out', OUT / (name + '-java.json')], name + '-java')
    return path


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    state = json.loads((EXP / 'campaign-status.json').read_text())
    assert state['stage'] == 'first_blocks_finished', 'Wait for the complete A/B driver, not a gap between its stages'
    protocol = json.loads((OUT / 'protocol-absolute-order/summary.json').read_text())
    assert protocol['passed'] and protocol['plans_checked'] >= 600
    assert protocol['binary_sha256'] == sha(ROOT / 'code/build/search-bot')
    assert all(sha(ROOT / path) == digest for path, digest in protocol['source_sha256'].items()
               if path.endswith(('.hpp', '.cpp'))), 'Search implementation changed after parity verification'
    assert (STOP-datetime.now(timezone.utc)).total_seconds() >= 1800, 'Insufficient pilot window; do not start'
    assert not (OUT / 'external-started.json').exists(), 'Never rerun an existing search panel silently'
    save(OUT / 'external-started.json', {'as_of': datetime.now(timezone.utc).isoformat(),
                                       'spec_sha256': sha(OUT / 'external-spec.json')})
    preliminary = panel(OUT / 'external-spec.json', 'external-screen')
    results = [evaluate(preliminary, name) for name in ('search1', 'search2')]
    save(OUT / 'external-screen-gates.json', results)
    eligible = [r for r in results if r['preliminary_gate']]
    if not eligible:
        save(OUT / 'decision.json', {'as_of': datetime.now(timezone.utc).isoformat(), 'status': 'rejected_external_screen',
                                   'teacher_strength_gate_passed': False, 'results': results})
        print(json.dumps(results, indent=2))
        return
    best = max(r['external_mean'] for r in eligible)
    selected = next(r for r in eligible if r['external_mean'] >= best-.01)
    name = selected['candidate']
    spec = json.loads((OUT / 'external-spec.json').read_text())
    spec['seeds'] = list(range(30013, 30041))
    spec['policies'] = {k: v for k, v in spec['policies'].items() if k in ('greedy', name, 'league3m')}
    spec['policy_variants'] = {k: v for k, v in spec['policy_variants'].items() if k in spec['policies']}
    spec['search_configs'] = {k: v for k, v in spec['search_configs'].items() if k in spec['policies']}
    spec['pairs'] = [pair for pair in spec['pairs'] if pair[0] in ('greedy', name)]
    spec_path = OUT / 'external-confirm-spec.json'
    save(spec_path, spec)
    save(OUT / 'external-selection.json', {'as_of': datetime.now(timezone.utc).isoformat(), 'selected': name,
         'screen_results': results, 'expanded_seeds_unplayed_by_search': [30013, 30040], 'spec_sha256': sha(spec_path)})
    if (STOP-datetime.now(timezone.utc)).total_seconds() < 1200:
        save(OUT / 'decision.json', {'as_of': datetime.now(timezone.utc).isoformat(), 'status': 'time_cap_before_confirmation',
                                   'teacher_strength_gate_passed': False, 'selected': name})
        return
    confirmation = panel(spec_path, 'external-confirm')
    result = evaluate(confirmation, name)
    run([sys.executable, 'code/rl/eval/analyze.py', confirmation, '--before', 'greedy', '--after', name,
         '--opponents', *EXTERNAL, 'league3m', '--out', OUT / 'external-confirm-comparison.json'], 'external-confirm-analysis')
    decision = {'as_of': datetime.now(timezone.utc).isoformat(), 'status': 'confirmed_teacher' if result['confirmed_teacher_gate'] else 'not_confirmed',
                'teacher_strength_gate_passed': result['confirmed_teacher_gate'], 'selected': name, 'result': result,
                'scope': '28-map independent-from-search-selection local confirmation, not final contest evidence or a deployable five-network package.',
                'external_spend': 0}
    save(OUT / 'decision.json', decision)
    print(json.dumps(decision, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if (OUT / 'external-started.json').exists() and not (OUT / 'decision.json').exists():
            save(OUT / 'decision.json', {'as_of': datetime.now(timezone.utc).isoformat(),
                 'status': 'time_cap_during_external' if datetime.now(timezone.utc) >= STOP else 'failed_validation',
                 'teacher_strength_gate_passed': False, 'error': str(error),
                 'scope': 'Incomplete/failed evidence preserved; no teacher data or silent rerun.'})
        raise
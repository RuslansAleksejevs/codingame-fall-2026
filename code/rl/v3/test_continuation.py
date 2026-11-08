#!/usr/bin/env python3
"""Synthetic continuation-limit and incumbent-selection checks; no real games."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'code'))
from rl.v3.continue_blocks import block_limits, choose_snapshots, screen_selection, EXTERNAL


def main():
    target, minutes = block_limits({'additional_steps': 2_001_950, 'elapsed_seconds': 3328.352366332896})
    assert target == 4_001_950 and abs(minutes - 175.4725394388816) < 1e-9
    assert block_limits({'additional_steps': 7_500_000, 'elapsed_seconds': 470*60}) == (8_000_000, 480)
    points = [(n, str(n)) for n in (2250300, 2500100, 2750900, 3000200, 3250100, 3500300, 3750500, 4002500)]
    assert [p[0] for p in choose_snapshots(points, 2001950, 4002500)] == [2500100, 3000200, 3500300, 4002500]
    assert choose_snapshots(points[:1], 2001950, 2250300) == points[:1]
    for summary in ({'additional_steps': 8_000_000, 'elapsed_seconds': 100},
                    {'additional_steps': 1, 'elapsed_seconds': 480*60}):
        try:
            block_limits(summary)
        except AssertionError:
            pass
        else:
            raise AssertionError('Exhausted budget accepted')
    policies = {'league3m': 'base', 'bc': 'bc', 'a1501957': 'old', 'a2501950': 'new1',
                'a3001950': 'new2', 'aaverage2': 'average'}
    rows = []
    for name in policies:
        if name == 'bc':
            continue
        for opponent in EXTERNAL if name == 'league3m' else (*EXTERNAL, 'league3m'):
            for seed in range(30001, 30013):
                for seat in (0, 1):
                    wins = {'league3m': 6, 'a1501957': 8, 'a2501950': 10, 'a3001950': 11, 'aaverage2': 11}[name]
                    rows.append({'candidate': name, 'opponent': opponent, 'seed': seed, 'seat': seat,
                                 'map_content_sha256': 'SYNTHETIC-' + str(seed),
                                 'outcome': 'win' if seed-30001 < wins else 'loss', 'valid': True,
                                 'returncode': 0, 'own_action_errors': [], 'opponent_action_errors': []})
    _, selected = screen_selection(rows, policies, 'a1501957')
    assert selected == ['a1501957', 'a3001950'], 'Incumbent retention / raw-average tie failed'
    next(r for r in rows if r['candidate'] == 'a1501957')['own_action_errors'] = ['synthetic timeout']
    try:
        screen_selection(rows, policies, 'a1501957')
    except AssertionError:
        pass
    else:
        raise AssertionError('Failed incumbent silently discarded')
    print('PASS: cumulative limits, global caps, exhausted budgets, nearest checkpoints, short block, incumbent retention, raw tie, error stop; no real games')


if __name__ == '__main__':
    main()
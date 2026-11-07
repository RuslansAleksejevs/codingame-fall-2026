#!/usr/bin/env python3
"""Replay the frozen Gold panel and describe losses; this is not a new evaluation."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys

BASE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BASE / 'code/rl/sim'))
from native import Simulator


def compact(state, seat):
    return {
        'turn': state['turn'], 'score': state['score'][seat],
        'opponent_score': state['score'][1-seat],
        'army': sum(u[seat] for u in state['units']),
        'opponent_army': sum(u[1-seat] for u in state['units']),
        'triangles': sum(t[3] == seat for t in state['triangles']),
        'opponent_triangles': sum(t[3] == 1-seat for t in state['triangles']),
    }


def replay(path, battle):
    data = json.loads(gzip.decompress(path.read_bytes()))
    log = data.get('log', data)
    seat = next(a['index'] for a in log['agents'] if a.get('me'))
    options = dict(x.split('=', 1) for x in log['game_options'].splitlines() if '=' in x)
    board = {k: [[int(z) for z in row.split(',')] for row in options[k].split('_')]
             for k in ('nodes', 'units', 'edges')}
    commands = [[f for f in log['frames'] if f.get('agent') == p and 'stdout' in f]
                for p in range(2)]
    sim = Simulator(board)
    timeline, checks, mismatches, times = [], 0, [], []
    totals = [Counter(), Counter()]
    try:
        for turn in range(min(map(len, commands))):
            state = sim.state()
            if state['done']:
                mismatches.append({'turn': turn, 'reason': 'commands_after_native_terminal'})
                break
            row = compact(state, seat)
            timeline.append(row)
            frame = commands[seat][turn]
            match = re.search(r'turn=(\d+) units=(\d+) triangles=(\d+) plan_us=(\d+)', frame.get('stderr', ''))
            if match:
                declared_turn, army, triangles, micros = map(int, match.groups())
                checks += 1
                times.append(micros)
                if (declared_turn, army, triangles) != (turn+1, row['army'], row['triangles']):
                    mismatches.append({'turn': turn, 'reason': 'own_observation',
                                       'expected': [declared_turn, army, triangles],
                                       'replayed': [turn+1, row['army'], row['triangles']]})
            actions = [commands[p][turn]['stdout'] for p in range(2)]
            for p in range(2):
                totals[p].update(c.strip().split()[0] for c in actions[p].split(';') if c.strip())
            sim.step(actions)
        final = sim.state()
        if final['score'] != log['scores'] or not final['done']:
            mismatches.append({'reason': 'terminal', 'native_score': final['score'],
                               'platform_score': log['scores'], 'native_done': final['done']})
        # Platform logs retain one last, unpaired output on the terminal frame.
        # It is not executed: all paired turns already reproduce the final scores.
        extra = [len(commands[p])-len(timeline) for p in range(2)]
        if sum(extra) > 1 or (sum(extra) and not final['done']):
            mismatches.append({'reason': 'unpaired_commands', 'counts': list(map(len, commands))})
        expected_win = log['scores'][seat] > log['scores'][1-seat]
        if expected_win != (battle['my_position'] == 0):
            mismatches.append({'reason': 'battle_outcome_disagrees'})
        return {
            'game_id': log['game_id'], 'log_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'win': expected_win, 'seat': seat, 'turns': final['turn'],
            'observation_checks': checks, 'mismatches': mismatches,
            'ignored_terminal_unpaired_outputs': extra,
            'max_plan_us': max(times, default=0),
            'own_commands': dict(totals[seat]), 'opponent_commands': dict(totals[1-seat]),
            'timeline': timeline, 'final': compact(final, seat),
        }
    finally:
        sim.close()


def summarize(games):
    result = {'games': len(games), 'median_turns': statistics.median(g['turns'] for g in games),
              'max_plan_us': max(g['max_plan_us'] for g in games)}
    for side in ('own', 'opponent'):
        result[side + '_command_counts'] = dict(sum((Counter(g[side+'_commands']) for g in games), Counter()))
        for action in ('ATTACK', 'ADD_PATH', 'REMOVE_PATH'):
            result[f'{side}_games_with_{action}'] = sum(g[side+'_commands'].get(action, 0) > 0 for g in games)
    for t in (5, 10, 15, 20):
        states = [g['timeline'][t] for g in games if len(g['timeline']) > t]
        result[f'after_{t}_turns'] = {
            'surviving_games': len(states),
            'median_army_gap': statistics.median(s['army']-s['opponent_army'] for s in states) if states else None,
            'median_income_gap': statistics.median(s['triangles']-s['opponent_triangles'] for s in states) if states else None,
            'behind_in_army': sum(s['army'] < s['opponent_army'] for s in states),
        }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    source = BASE / 'experiments/rl/2026-11-06-live-ppo-v2'
    battles = json.loads((source/'battles-final.json').read_text())
    games = [replay(source/'games'/f"{b['game_id']}.json.gz", b) for b in battles['battles'] if b['done']]
    result = {
        'provenance': 'PROJECT_REPORTED', 'as_of': '2026-11-07',
        'source': str(source.relative_to(BASE)), 'submission_id': battles['submission_id'],
        'method': 'Replay saved commands, compare own per-turn army/income and final scores. No new games or training.',
        'limitations': 'Observational, selected matchmaking sample. Correlations are not causal. Late-turn summaries exclude finished games.',
        'replay_mismatch_games': sum(bool(g['mismatches']) for g in games),
        'observation_checks': sum(g['observation_checks'] for g in games),
        'all': summarize(games), 'wins': summarize([g for g in games if g['win']]),
        'losses': summarize([g for g in games if not g['win']]), 'games': games,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(result, indent=2)+'\n').encode()
    args.out.write_bytes(gzip.compress(payload, mtime=0) if args.out.suffix == '.gz' else payload)
    print(json.dumps({k:v for k,v in result.items() if k != 'games'}, indent=2))
    if result['replay_mismatch_games']:
        raise SystemExit('Replay disagreement: inspect mismatches before using the aggregates.')


if __name__ == '__main__':
    main()

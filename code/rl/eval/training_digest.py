#!/usr/bin/env python3
"""Compact learning diagnostics; training win rates are not tournament estimates."""
import argparse
import json
from pathlib import Path


def digest(folder, window):
    rows = [json.loads(line) for line in (folder / 'history.jsonl').read_text().splitlines()]
    last = rows[-1]
    recent = rows[-window:]
    kinds = []
    for index in range(len(last['rollout']['kinds'])):
        games = sum(row['rollout']['kinds'][index]['games'] for row in recent)
        wins = sum(row['rollout']['kinds'][index]['learner_seat_wins'] for row in recent)
        draws = sum(row['rollout']['kinds'][index]['draws'] for row in recent)
        kinds.append({'kind': index, 'games': games, 'wins': wins, 'draws': draws,
                      'score_rate': (wins + .5 * draws) / games if games else None})
    return {'run': folder.name, 'additional_steps': last['steps'], 'games': last['games'],
            'minutes': last['elapsed_seconds'] / 60, 'recent_iterations': len(recent),
            'recent_training_kinds': kinds,
            'recent_mean_kl': sum(row['update']['final_rollout_kl'] for row in recent) / len(recent),
            'max_native_logp_error': max(row['update']['max_old_logp_error'] for row in rows),
            'actor_early_stop_batches': sum(row['update']['actor_early_stopped'] for row in rows),
            'note': 'Sampled training policies and changing opponents; not a fixed-opponent evaluation.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('folders', nargs='+', type=Path)
    parser.add_argument('--window', type=int, default=50)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = [digest(folder, args.window) for folder in args.folders]
    text = json.dumps(result, indent=2) + '\n'
    if args.out:
        args.out.write_text(text)
    print(text)


if __name__ == '__main__':
    main()

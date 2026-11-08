#!/usr/bin/env python3
"""Compare complete native/Java states for every clean archived panel game."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from run_matches import BASE, REPO, COMMIT, java_home
from rl.data.replays import read
from rl.sim.native import Simulator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    rows = [json.loads(line) for line in (args.run / 'matches.jsonl').read_text().splitlines()]
    cp = str(BASE / 'code/build') + ':' + str(REPO / 'target/classes') + ':' + (REPO / 'classpath.txt').read_text().strip()
    oracle = subprocess.Popen([str(java_home() / 'bin/java'), '-Xmx1g', '-cp', cp, 'Oracle'],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    started = time.monotonic()
    games = transitions = states = 0
    excluded, mismatches = [], []
    try:
        for row in rows:
            name = f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}.json.gz'
            record = read(args.run / name)
            if not row['valid'] or row['returncode'] or row['own_action_errors'] or row['opponent_action_errors'] or record['errors']:
                excluded.append(name)
                continue
            actions = [turn['actions'] for turn in record['decisions']]
            oracle.stdin.write(json.dumps(dict(record['map'], actions=actions)) + '\n')
            oracle.stdin.flush()
            line = oracle.stdout.readline()
            assert line, 'Original Java oracle exited'
            expected = json.loads(line)
            assert len(expected) == len(actions) + 1
            native = Simulator(record['map'])
            for turn, reference in enumerate(expected):
                actual = native.state()
                differences = [key for key in ('turn', 'score', 'units', 'edges', 'triangles', 'done') if actual[key] != reference[key]]
                if differences:
                    mismatches.append({'record': name, 'turn': turn, 'fields': differences,
                                       'native': actual, 'original_java': reference})
                    break
                states += 1
                if turn < len(actions):
                    native.step(actions[turn])
                    transitions += 1
            native.close()
            games += 1
            if games % 100 == 0:
                print(json.dumps({'games': games, 'transitions': transitions, 'mismatches': len(mismatches)}), flush=True)
            if mismatches:
                break
    finally:
        oracle.stdin.close()
        oracle.wait(timeout=30)
    report = {'passed': not mismatches, 'panel_games': len(rows), 'clean_games_replayed': games,
              'panel_manifest_sha256': hashlib.sha256((args.run / 'manifest.json').read_bytes()).hexdigest(),
              'panel_matches_sha256': hashlib.sha256((args.run / 'matches.jsonl').read_bytes()).hexdigest(),
              'panel_spec_sha256': hashlib.sha256((args.run / 'panel-spec.json').read_bytes()).hexdigest(),
              'full_states_compared': states, 'joint_transitions': transitions,
              'fields': ['turn', 'score', 'units', 'edges', 'triangles', 'done'],
              'technical_records_excluded': excluded, 'mismatches': mismatches,
              'referee_commit': COMMIT,
              'oracle_sha256': hashlib.sha256((BASE / 'code/rl/sim/Oracle.java').read_bytes()).hexdigest(),
              'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'wall_seconds': time.monotonic() - started}
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'mismatches'}, indent=2))
    assert not mismatches, 'Complete native state disagrees with original Java'


if __name__ == '__main__':
    main()

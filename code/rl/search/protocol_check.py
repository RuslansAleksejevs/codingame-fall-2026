#!/usr/bin/env python3
"""Check native search against standalone stdin/stdout on both absolute seats."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'code'))
from rl.data.replays import read
from rl.league.rollout import LIB as LEAGUE
from rl.search.native import Search
from rl.sim.native import Simulator
from rl.train.ppo import save, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seed', type=int, default=30001, choices=range(30001, 30013))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    exp = ROOT / 'experiments/rl/2026-11-07-ppo-v3'
    actor = ROOT / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt'
    critic = exp / 'search/frozen-critic/critic.txt'
    enemies = [actor, ROOT / 'experiments/rl/2026-11-06-ppo-v2/control-long/step-03002813/weights.txt',
               ROOT / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-04836947/weights.txt']
    binary = ROOT / 'code/build/search-bot'
    streams = []
    mismatches = []
    total = 0
    for opponent in ('lacoz', 'khoufou2', 'khoufou'):
        for recorded_seat in (0, 1):
            path = exp / 'baseline-dev' / f'league3m-vs-{opponent}-seed{args.seed}-seat{recorded_seat}.json.gz'
            record = read(path)
            for player in (0, 1):
                for depth, candidates in ((1, 1), (1, 4), (2, 4)):
                    policy = Search(actor, critic, enemies, depth=depth, candidates=candidates, budget_ms=0)
                    sim = Simulator(record['map'])
                    inputs, expected = [], []
                    try:
                        for turn, decision in enumerate(record['decisions']):
                            inputs.append(LEAGUE.league_observation(sim.ptr, player, int(turn == 0)))
                            expected.append(policy.act(sim, player)[0])
                            sim.step(decision['actions'])
                    finally:
                        sim.close()
                        policy.close()
                    stdin = b''.join(inputs)
                    result = subprocess.run([str(p) for p in [binary, actor, critic, *enemies, depth, candidates, 0]],
                                            input=stdin, capture_output=True, timeout=90, check=False)
                    actual = result.stdout.decode().splitlines()
                    differences = [i for i, (a, b) in enumerate(zip(expected, actual)) if a != b]
                    difference_count = len(differences) + abs(len(expected)-len(actual))
                    details = {'record': str(path.relative_to(ROOT)), 'player': player, 'depth': depth,
                               'candidates': candidates, 'turns': len(expected), 'mismatches': difference_count,
                               'returncode': result.returncode, 'input_sha256': hashlib.sha256(stdin).hexdigest(),
                               'output_sha256': hashlib.sha256(result.stdout).hexdigest()}
                    streams.append(details)
                    total += len(expected)
                    if difference_count or result.returncode:
                        mismatches.append(dict(details, samples=[{'turn': i, 'expected': expected[i], 'actual': actual[i]}
                                                               for i in differences[:3]],
                                               stderr_tail=result.stderr.decode()[-2000:]))
    report = {'as_of': datetime.now(timezone.utc).isoformat(), 'passed': not mismatches,
              'seed': args.seed,
              'streams': streams, 'plans_checked': total, 'mismatching_streams': len(mismatches),
              'mismatches': mismatches, 'binary_sha256': sha(binary),
              'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'code/rl/search').glob('*') if p.is_file()},
              'note': 'Untimed same-input action parity on both absolute seats; not strength/timing evidence.'}
    save(args.out / 'summary.json', report)
    print(json.dumps({k: v for k, v in report.items() if k not in ('streams', 'mismatches', 'source_sha256')}, indent=2))
    if mismatches:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
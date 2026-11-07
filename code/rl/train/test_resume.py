#!/usr/bin/env python3
"""Check interrupted/resumed training against uninterrupted deterministic training."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import torch

ROOT = Path(__file__).resolve().parents[3]


def equal(a, b):
    if isinstance(a, torch.Tensor):
        return isinstance(b, torch.Tensor) and torch.equal(a, b)
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    return a == b


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--recipes', nargs='+', choices=('long', 'league', 'roads'), default=['long', 'league'])
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    results = []
    for recipe in args.recipes:
        base = [sys.executable, str(ROOT / f'code/rl/train/ppo_{recipe}.py'),
                '--maps', str(ROOT / 'experiments/rl/2026-11-06-ppo-v1/maps.json'),
                '--init', str(ROOT / 'experiments/rl/2026-11-06-ppo-v1/training/checkpoint.pt'),
                '--initial-weights', str(ROOT / 'experiments/rl/2026-11-06-ppo-v1/training/weights.txt'),
                '--minutes', '5', '--pilot']
        if recipe in ('league', 'roads'):
            base += ['--teacher', 'none']
        full, split = args.out / f'{recipe}-full', args.out / f'{recipe}-split'
        commands = [base + ['--out', str(full), '--steps', '10000'],
                    base + ['--out', str(split), '--steps', '1'],
                    base + ['--out', str(split), '--steps', '10000', '--resume', str(split / 'final.pt')]]
        for index, command in enumerate(commands):
            with (args.out / f'{recipe}-{index}.log').open('w') as log:
                subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        a, b = [torch.load(folder / 'final.pt', weights_only=False, map_location='cpu') for folder in (full, split)]
        fields = ('actor', 'critic', 'actor_optimizer', 'critic_optimizer', 'numpy_rng',
                  'pool', 'pool_steps', 'next_pool', 'steps', 'iteration', 'games')
        checks = {field: bool(equal(a[field], b[field])) for field in fields}
        hashes = [hashlib.sha256((folder / 'weights.txt').read_bytes()).hexdigest() for folder in (full, split)]
        checks['export_identical'] = hashes[0] == hashes[1]
        # Torch RNG is serialized but temporary module construction consumes values on
        # resume. Current optimization uses no Torch randomness; sampling/shuffling
        # use restored native/NumPy seeds. Test actual tensors, not unused RNG bytes.
        result = {'recipe': recipe, 'passed': all(checks.values()), 'checks': checks,
                  'steps': a['steps'], 'weights_sha256': hashes[0],
                  'wall_timed_teacher_enabled': False,
                  'torch_rng_bytes_identical': torch.equal(a['torch_rng'], b['torch_rng'])}
        results.append(result)
        (args.out / 'summary.json').write_text(json.dumps(results, indent=2) + '\n')
        print(json.dumps(result), flush=True)
        assert result['passed'], result


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Inference-only arithmetic average of nearby compatible actor checkpoints."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from run_matches import BASE
from rl.train.bc import Policy, export
from rl.train.ppo import sha, save


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--checkpoints', required=True, nargs='+', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--max-span', default=600000, type=int)
    args = ap.parse_args()
    assert 2 <= len(args.checkpoints) <= 3
    paths = [p.resolve() for p in args.checkpoints]
    assert len(set(p.parent.parent for p in paths)) == 1, 'Never average independent trajectories'
    assert len(set(paths)) == len(paths)
    checkpoints = [torch.load(p, map_location='cpu', weights_only=False) for p in paths]
    assert all(c['config'] == checkpoints[0]['config'] for c in checkpoints)
    steps = [c['steps'] for c in checkpoints]
    assert max(steps) - min(steps) <= args.max_span
    states = [c['actor'] for c in checkpoints]
    assert all(s.keys() == states[0].keys() for s in states)
    average = {}
    for name in states[0]:
        tensors = [s[name] for s in states]
        assert all(t.shape == tensors[0].shape and torch.isfinite(t).all() for t in tensors)
        average[name] = torch.stack([t.double() for t in tensors]).mean(0).to(tensors[0].dtype)
    actor = Policy()
    actor.load_state_dict(average)
    out = args.out.resolve()
    assert out.is_relative_to(BASE / 'experiments')
    out.mkdir(parents=True, exist_ok=False)
    export(actor, out / 'weights.txt')
    torch.save({'actor': average, 'inference_only': True, 'kind': 'nearby_arithmetic_actor_average',
                'config': checkpoints[0]['config'], 'source_steps': steps}, out / 'checkpoint.pt')
    result = {'as_of': datetime.now(timezone.utc).isoformat(), 'inference_only': True, 'source_steps': steps,
              'sources': {str(p.relative_to(BASE)): sha(p) for p in paths},
              'weights_sha256': sha(out / 'weights.txt'), 'external_spend': 0}
    save(out / 'manifest.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
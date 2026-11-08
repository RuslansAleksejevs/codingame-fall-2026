#!/usr/bin/env python3
"""Export the frozen existing critic for search; no training or policy change."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from run_matches import BASE
from rl.train.bc import Policy, export
from rl.train.ppo import sha, save

ap = argparse.ArgumentParser()
ap.add_argument('--checkpoint', required=True, type=Path)
ap.add_argument('--out', required=True, type=Path)
args = ap.parse_args()
args.out.mkdir(parents=True, exist_ok=False)
checkpoint = torch.load(args.checkpoint, map_location='cpu', weights_only=False)
critic = Policy()
critic.load_state_dict(checkpoint['critic'])
export(critic, args.out / 'critic.txt')
save(args.out / 'manifest.json', {'as_of': datetime.now(timezone.utc).isoformat(),
     'source': str(args.checkpoint.resolve().relative_to(BASE)), 'source_sha256': sha(args.checkpoint),
     'critic_sha256': sha(args.out / 'critic.txt'), 'training_performed': False, 'external_spend': 0})
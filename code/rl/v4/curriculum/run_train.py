#!/usr/bin/env python3
"""One finite pilot arm and export check; the CPU lease is held by the caller."""
import argparse
import json
import sys
import time
from common import ROOT, OUT, BUILD, now, save, sha
from evaluate import run

ap = argparse.ArgumentParser()
ap.add_argument('arm', choices=['control', 'curriculum'])
args = ap.parse_args()
out = OUT / f'pilot-{args.arm}'
if args.arm == 'curriculum':
    frozen = json.loads((OUT / 'pilot-control/source-sha256.json').read_text())
    assert all(sha(ROOT / path) == expected for path, expected in frozen.items()), 'Control training source freeze changed'
    assert sha(BUILD / 'libcurriculum.dylib') == json.loads((OUT / 'pilot-control/run-000000.json').read_text())['binary_sha256']
commands = [
    [sys.executable, '-B', 'code/rl/v4/curriculum/train.py', '--out', str(out.relative_to(ROOT)),
     '--fraction', '0' if args.arm == 'control' else '.15', '--steps', '100000', '--minutes', '12', '--seed', '202611081'],
    [sys.executable, '-B', 'code/rl/export/verify.py', '--training', str(out.relative_to(ROOT)),
     '--data', 'code/build/rl-cache/bc-v1-clean', '--out', str((out / 'export-verification.json').relative_to(ROOT))],
]
if args.arm == 'curriculum':
    commands.insert(0, [sys.executable, '-B', 'code/rl/v4/curriculum/test_changed_topology.py'])
if not (OUT / 'preflight-evidence.tar.gz').exists():
    commands.insert(0, [sys.executable, '-B', 'code/rl/v4/curriculum/archive.py'])
started = time.monotonic()
save(OUT / f'pilot-{args.arm}-commands.json', [['${PYTHON}', *command[1:]] for command in commands])
for i, command in enumerate(commands):
    run(command, OUT / f'pilot-{args.arm}-command{i}.log')
save(OUT / f'pilot-{args.arm}-execution.json', {'as_of': now(), 'wall_seconds': time.monotonic() - started,
     'passed': True, 'external_spend': 0})
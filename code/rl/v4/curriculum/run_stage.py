#!/usr/bin/env python3
"""A logged finite stage; invoke only through the shared compute-slot wrapper."""
import argparse
import os
import subprocess
import sys
import time
from common import ROOT, OUT, now, save

ap = argparse.ArgumentParser()
ap.add_argument('stage', choices=['restore', 'bank', 'contracts', 'smoke'])
ap.add_argument('--attempt', type=int, default=1)
args = ap.parse_args()
scripts = {'restore': [('build.py',), ('prepare.py', 'parity')],
           'bank': [('prepare.py', 'bank')], 'contracts': [('contracts.py',)],
           'smoke': [('build.py',), ('prepare.py', 'parity'), ('prepare.py', 'bank'), ('contracts.py',)]}[args.stage]
started = time.monotonic()
events = []
for stage_index, parts in enumerate(scripts):
    command = [sys.executable, '-B', 'code/rl/v4/curriculum/' + parts[0], *parts[1:]]
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    stamp = now()
    with (OUT / f'{args.stage}-{stage_index}-{parts[0]}-attempt{args.attempt}.log').open('x') as log:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        print(f'{stamp} stage={args.stage} child_pid={process.pid} command={parts}', flush=True)
        for line in process.stdout:
            clean = line.replace(str(ROOT), '${PROJECT_ROOT}').replace(str(__import__('pathlib').Path.home()), '${HOME}')
            log.write(clean)
            log.flush()
            print(clean, end='', flush=True)
        code = process.wait()
    events.append({'command': ['${PYTHON}', '-B', command[2], *command[3:]], 'as_of': stamp, 'returncode': code})
    save(OUT / f'{args.stage}-execution-attempt{args.attempt}.json', {'as_of': now(), 'events': events, 'seconds': time.monotonic() - started,
         'external_spend': 0, 'completed': code == 0 and parts == scripts[-1]})
    if code:
        raise SystemExit(code)
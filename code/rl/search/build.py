#!/usr/bin/env python3
"""Build isolated experimental search binaries; do not replace PPO libraries."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
for source, output, shared in [('api.cpp', 'libtryangle_search.dylib', True), ('bot.cpp', 'search-bot', False)]:
    command = ['clang++', '-std=c++17', '-O3', '-Wall', '-Wextra', '-Wpedantic', '-pthread']
    if shared:
        command += ['-shared', '-fPIC']
    command += [str(ROOT / 'code/rl/search' / source), '-o', str(ROOT / 'code/build' / output)]
    subprocess.run(command, check=True)
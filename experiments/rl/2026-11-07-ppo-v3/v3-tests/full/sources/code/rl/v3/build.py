#!/usr/bin/env python3
"""Build PPO-v3 separately; never replace a running legacy rollout library."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
subprocess.run(['clang++', '-std=c++17', '-O3', '-Wall', '-Wextra', '-Wpedantic',
                '-shared', '-fPIC', '-pthread', str(ROOT / 'code/rl/league/rollout_league.cpp'),
                '-o', str(ROOT / 'code/build/libtryangle_v3.dylib')], check=True)
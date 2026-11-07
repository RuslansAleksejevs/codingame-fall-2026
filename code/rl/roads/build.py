#!/usr/bin/env python3
"""Build the isolated road-observation collector and diagnostic interface."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
subprocess.run(['clang++', '-std=c++17', '-O3', '-Wall', '-Wextra', '-Wpedantic',
                '-shared', '-fPIC', '-pthread', str(ROOT / 'code/rl/roads/rollout_roads.cpp'),
                '-o', str(ROOT / 'code/build/libtryangle_roads.dylib')], check=True)

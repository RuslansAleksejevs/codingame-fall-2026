#!/usr/bin/env python3
"""Build only inside the exclusive branch directory; requires shared CPU slot."""
import subprocess
from common import BUILD, HERE, ROOT, classpath, java_home, now, save, sha

BUILD.mkdir(exist_ok=True)
commands = [
    ['clang++', '-std=c++17', '-O3', '-Wall', '-Wextra', '-Wpedantic', '-shared', '-fPIC', '-pthread',
     str(HERE / 'native.cpp'), '-o', str(BUILD / 'libcurriculum.dylib')],
    [str(java_home() / 'bin/javac'), '-cp', classpath(), '-d', str(BUILD), str(HERE / 'RestoreOracle.java')],
]
for command in commands:
    subprocess.run(command, check=True)
save(BUILD / 'manifest.json', {'as_of': now(), 'commands': [[a.replace(str(ROOT), '${PROJECT_ROOT}') for a in c] for c in commands],
     'sources': {str(p.relative_to(ROOT)): sha(p) for p in [HERE / 'native.cpp', HERE / 'state.hpp', HERE / 'RestoreOracle.java',
                 ROOT / 'code/rl/sim/simulator.hpp', ROOT / 'code/rl/models/policy.hpp', ROOT / 'code/rl/league/rollout_league.cpp']},
     'binary_sha256': sha(BUILD / 'libcurriculum.dylib'), 'external_spend': 0})
"""One new build, under the existing exclusive CPU lease."""
import platform
import subprocess
import sys
from common import *


def main():
    guard(); target = build_dir(); target.mkdir(parents=True, exist_ok=False)
    jobs = [('bot', CODE/'bot.cpp', []), ('api.dylib', CODE/'api.cpp', ['-shared', '-fPIC', '-pthread']),
            ('league3m', ROOT/'submissions/ppo-v2-league3m.cpp', []),
            ('b2m', ROOT/'experiments/rl/2026-11-07-ppo-v3/handoff-b2m/bot.cpp', []),
            ('v6', ROOT/'code/variants/v6-attack.cpp', []),
            ('bc', ROOT/'code/rl/export/bot.cpp', [])]
    for name, source, flags in jobs:
        command = ['clang++', '-std=c++17', '-O3', '-Wall', '-Wextra', '-Wpedantic', *flags,
                   rel(source), '-o', rel(target/name)]
        start = time.monotonic(); p = subprocess.run(command, capture_output=True, text=True)
        save(OUT/f'build-{name}-result.json', {'as_of': now(), 'command': command, 'seconds': time.monotonic()-start,
             'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr,
             'binary_sha256': sha(target/name) if p.returncode == 0 else None})
        print(json.dumps({'built': name, 'returncode': p.returncode}), flush=True); p.check_returncode()
    save(OUT/'build-manifest.json', {'as_of': now(), 'sources': sources(),
        'weights': {rel(p): sha(p) for p in {ACTOR, CRITIC, *ENEMIES}}, 'protected': guard(),
        'binaries': {rel(target/n): sha(target/n) for n, _, _ in jobs},
        'python': sys.version, 'machine': platform.machine(), 'platform': platform.platform(),
        'compiler': subprocess.run(['clang++', '--version'], capture_output=True, text=True).stdout,
        'budget': budget(), 'external_spend': 0})


if __name__ == '__main__': main()
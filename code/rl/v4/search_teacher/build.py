"""Build only the branch-local diagnostic library; never touch shared caches."""
import subprocess
import argparse
from common import CODE, OUT, ROOT, check_preserved, now, relative, save, sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--attempt',type=int,default=1)
    args=parser.parse_args();assert args.attempt in (1,2)
    preserved = check_preserved()
    build = OUT / 'build'
    build.mkdir(exist_ok=args.attempt>1)
    assert not (build/'diagnostic.dylib').exists(), 'Never overwrite a built diagnostic'
    command = ['clang++', '-std=c++17', '-O3', '-Wall', '-Wextra', '-Wpedantic',
               '-pthread', '-shared', '-fPIC', relative(CODE / 'diagnostic.cpp'),
               '-o', relative(build / 'diagnostic.dylib')]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    print(result.stdout, result.stderr, end='')
    save(OUT / ('build-manifest.json' if args.attempt==1 else f'build-manifest-{args.attempt}.json'), {
        'as_of': now(), 'command': command, 'returncode': result.returncode,
        'compiler': subprocess.run(['clang++', '--version'], capture_output=True, text=True).stdout,
        'stdout': result.stdout, 'stderr': result.stderr, 'preserved': preserved,
        'sources': {relative(p): sha(p) for p in [CODE / 'diagnostic.cpp',
             ROOT / 'code/rl/search/search.hpp', ROOT / 'code/rl/league/rollout_league.cpp',
             ROOT / 'code/rl/models/policy.hpp', ROOT / 'code/rl/sim/simulator.hpp',
             ROOT / 'code/rl/export/inference.hpp']},
        'binary_sha256': sha(build / 'diagnostic.dylib') if result.returncode == 0 else None,
        'external_spend': 0,
    })
    result.check_returncode()


if __name__ == '__main__':
    main()
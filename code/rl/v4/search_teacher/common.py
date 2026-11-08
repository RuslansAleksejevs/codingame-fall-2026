"""Read-only shared dependencies and branch-local evidence helpers."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
CODE = ROOT / 'code/rl/v4/search_teacher'
OUT = ROOT / 'experiments/rl/2026-11-08-rl4/search-teacher'
sys.path.insert(0, str(ROOT / 'code'))
ACTOR = ROOT / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt'
CRITIC = ROOT / 'experiments/rl/2026-11-07-ppo-v3/search/frozen-critic/critic.txt'
ENEMIES = [ACTOR,
           ROOT / 'experiments/rl/2026-11-06-ppo-v2/control-long/step-03002813/weights.txt',
           ROOT / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-04836947/weights.txt']
STOP = datetime(2026, 11, 9, 2, tzinfo=timezone.utc)
EXTERNAL = ('lacoz', 'khoufou2', 'khoufou')


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def check_preserved():
    paths = {
        ACTOR: 'dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb',
        ACTOR.with_name('checkpoint.pt'): '9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663',
        ROOT / 'submissions/ppo-v2-league3m.cpp': '199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1',
        ROOT / 'code/rl/search/bot.cpp': 'da6a29bf0c204d4add3a94eb26a0acebe6d0e15c3cc96595882a4befba364d1f',
    }
    for path, expected in paths.items():
        assert sha(path) == expected, relative(path)
    # Once compilation succeeds, bind every later stage to those exact sources.
    manifest = OUT / 'build-manifest-2.json'
    if manifest.exists():
        frozen = json.loads(manifest.read_text())
        assert frozen['returncode']==0
        for source, digest in frozen['sources'].items():
            assert sha(ROOT/source)==digest, 'Source changed after pilot: '+source
    diagnostic = OUT/'diagnostic/summary.json'
    if diagnostic.exists():
        for source,digest in json.loads(diagnostic.read_text())['weights'].items():
            assert sha(ROOT/source)==digest, 'Frozen teacher weight changed: '+source
    assert datetime.now(timezone.utc) < STOP, 'Research hard stop reached'
    return {relative(path): digest for path, digest in paths.items()}


def checked_seeds(seeds):
    assert seeds and len(set(seeds)) == len(seeds)
    assert all(62001 <= seed <= 62060 for seed in seeds), 'Outside branch development allocation'
    return seeds
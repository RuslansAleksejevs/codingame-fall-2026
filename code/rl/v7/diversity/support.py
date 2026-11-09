"""Small new allocation adapter; frozen v5 mechanics are imported read-only."""
from datetime import datetime, timezone
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
CODE = ROOT / 'code/rl/v7/diversity'
OUT = ROOT / 'experiments/rl/2026-11-09-rl7/diversity'
V5 = ROOT / 'experiments/rl/2026-11-08-rl5/deadline-search'
V5CODE = ROOT / 'code/rl/v5/deadline_search'
BUILD = V5 / 'build/attempt1'
sys.path.insert(0, str(ROOT / 'code'))
sys.path.append(str(V5CODE))
import common as old_common
from run_matches import java_home
from maps import classpath

ACTOR = old_common.ACTOR
CRITIC = old_common.CRITIC
ENEMIES = old_common.ENEMIES
PROTECTED = old_common.PROTECTED
TRAIN = list(range(73001, 73065))
LABELDEV = list(range(73201, 73217))
GAMEDEV = list(range(73301, 73317))
FINAL = list(range(73401, 73441))
OPPONENTS = ('lacoz', 'khoufou2', 'khoufou', 'league3m', 'b2m')
COLLECTION_OPPONENTS = ('lacoz', 'khoufou2', 'khoufou', 'b2m')
SEEDS = (20261109, 20261110)
ARMS = ('narrow1', 'broad1', 'narrow2', 'broad2', 'base')
PYTHON = 'code/arena/.venv-rl/bin/python'
now, sha, rel, clean = old_common.now, old_common.sha, old_common.rel, old_common.clean


def save(path, value):
    path = Path(path)
    assert path.resolve().is_relative_to(OUT), path
    old_common.save(path, value)


def budget():
    ledger = ROOT / '.context/rl7-compute/events.jsonl'
    records = [json.loads(s) for s in ledger.read_text().splitlines()] if ledger.exists() else []
    spent = sum(r['seconds'] for r in records if r['event'] == 'finished' and r['owner'] == 'diversity')
    return {'completed_seconds': spent, 'cap_seconds': 7200, 'cutoff': '2026-11-09T06:00:00Z'}


def guard():
    assert datetime.now(timezone.utc) < datetime(2026, 11, 9, 6, tzinfo=timezone.utc)
    assert budget()['completed_seconds'] < 7200
    for path, digest in PROTECTED.items():
        assert sha(path) == digest, rel(path)
    return {rel(p): h for p, h in PROTECTED.items()}


def teacher_guard():
    guard()
    assert sha(V5 / 'freeze.json') == '3a8a360441013efe735d7f2f3d27e4bdd11e66b84b83323938991bf36987f532'
    frozen = json.loads((V5 / 'freeze.json').read_text())
    identities = {**frozen['sources'], **frozen['weights'], **frozen['binaries'], **frozen['dependencies']}
    previous = json.loads((V5 / 'student/data-training-freeze.json').read_text())
    identities.update(previous['identities'])
    for path, digest in identities.items():
        assert sha(ROOT / path) == digest, path
    return identities


def sources():
    paths = list(CODE.glob('*.py')) + [OUT / 'PROTOCOL.md', ROOT / 'code/rl/train/bc.py',
        ROOT / 'code/rl/export/package.py', ROOT / 'code/rl/v3/verify_package.py']
    if (OUT/'AMENDMENT_A1.md').exists(): paths.append(OUT/'AMENDMENT_A1.md')
    return {rel(p): sha(p) for p in sorted(paths)}


def check_freeze(name='data-freeze.json'):
    if name == 'data-freeze.json' and (OUT/'data-freeze-a1.json').exists():
        name = 'data-freeze-a1.json'
    frozen = json.loads((OUT / name).read_text())
    for path, digest in frozen['identities'].items():
        assert sha(ROOT / path) == digest, path
    guard()
    return frozen


def run(command, name, timeout=1200):
    guard()
    start = time.monotonic()
    result = subprocess.run([str(c) for c in command], cwd=ROOT, capture_output=True, timeout=timeout)
    with (OUT / (name + '.log')).open('x') as stream:
        stream.write(clean((result.stdout + result.stderr).decode(errors='replace')))
    save(OUT / (name + '-command.json'), {'as_of': now(), 'command': list(map(str, command)),
         'seconds': time.monotonic()-start, 'returncode': result.returncode, 'external_spend': 0})
    result.check_returncode()


def commands():
    # All dependencies already compiled and hash-bound. No legacy build calls.
    result = {name: [rel(BUILD/name)] for name in ('league3m', 'b2m')}
    result['base'] = result['league3m']
    result['lacoz'] = ['code/arena/.venv-lacoz/bin/python', '-B', '-u',
                      'code/opponents/public/lacoz-7f190183/bot.py']
    for name in ('khoufou', 'khoufou2'):
        result[name] = [str(java_home()/'bin/java'), '-cp', rel(BUILD/name), 'Player']
    for arm in ARMS[:-1]:
        result[arm] = [rel(OUT/'models'/arm/'verify/packaged')]
    return result


def panel(name, schedule, hashes):
    module = importlib.import_module('panel')
    module.OUT = OUT
    module.SCRATCH = OUT / 'build/specs'
    module.guard = guard
    module.budget = budget
    module.sources = sources
    module.commands = commands
    return module.panel(name, schedule, hashes, 'rl7_diversity_' + name)


def verify(name):
    module = importlib.import_module('verify')
    module.OUT = OUT
    module.verify(name)
    return json.loads((OUT/(name+'-verification.json')).read_text())


def teacher_stream(inputs, name):
    command = [rel(BUILD/'bot'), *[rel(p) for p in [ACTOR, CRITIC, *ENEMIES]], '4', '16']
    data = b''.join(inputs)
    result = subprocess.run(command, input=data, capture_output=True, cwd=ROOT, timeout=90)
    lines = result.stdout.decode().splitlines()
    logs = [json.loads(s.split('=', 1)[1]) for s in result.stderr.decode().splitlines() if s.startswith('deadline=')]
    save(OUT/'teacher-streams'/(name+'.json'), {'as_of': now(), 'command': command,
        'returncode': result.returncode, 'input_sha256': hashlib.sha256(data).hexdigest(),
        'outputs': lines, 'stderr': result.stderr.decode(), 'inference_calls': len(logs),
        'emergencies': sum(s['search']['emergency'] for s in logs)})
    assert result.returncode == 0 and len(lines) == len(inputs) == len(logs), name
    assert [s['turn'] for s in logs] == list(range(1, len(inputs)+1)), name
    assert not any(s['search']['emergency'] for s in logs), ('teacher emergency', name)
    return lines, logs


def registry(name):
    from rl.v3.map_registry import build
    result = build()
    canonical, legacy = set(result['canonical']), set(result['legacy'])
    bindings = dict(result['sources'])

    def visit(value):
        if isinstance(value, list):
            for item in value: visit(item)
        elif isinstance(value, dict):
            if all(k in value for k in ('nodes', 'units', 'edges')):
                data = {k: value[k] for k in ('nodes', 'units', 'edges')}
                if all(isinstance(v, str) for v in data.values()):
                    legacy.add(hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest())
                    data = {k: [list(map(int, r.split(','))) for r in v.split('_') if r] for k, v in data.items()}
                if all(isinstance(v, list) for v in data.values()):
                    canonical.add(hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest())
            for key, item in value.items():
                if key in ('gameParameters', 'game_options'):
                    text = ''.join(item) if isinstance(item, list) else item
                    if isinstance(text, str): visit(dict(line.split('=', 1) for line in text.splitlines() if '=' in line))
                if key in ('canonical', 'legacy') and isinstance(item, list):
                    (canonical if key == 'canonical' else legacy).update(item)
                if key in ('map_content_sha256', 'map_hash') and isinstance(item, str): canonical.add(item)
                if key == 'legacy_hash' and isinstance(item, str): legacy.add(item)
                visit(item)

    paths = set()
    for pattern in ('*-maps.json', '*-map-hashes.json', '*map-contribution*.json', '*map-registry-claim*.json'):
        paths.update((ROOT/'experiments').rglob(pattern))
    for folder in ('2026-11-07-ppo-v3/platform', '2026-11-07-ppo-v3/live-submission', '2026-11-08-leaderboard-recheck'):
        paths.update((ROOT/'experiments/rl'/folder).rglob('*log*.json*'))
    for path in sorted(paths):
        raw = path.read_bytes()
        value = json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)
        visit(value)
        if path.name.endswith('-map-hashes.json'): canonical.update(value.values())
        bindings[rel(path)] = sha(path)
    assert all(len(h) == 64 for h in canonical | legacy)
    result = {'as_of': now(), 'canonical': sorted(canonical), 'legacy': sorted(legacy), 'sources': bindings}
    save(OUT/(name+'-registry.json'), result)
    return result


def prepare(name, seeds):
    assert set(seeds) <= set(TRAIN+LABELDEV+GAMEDEV+FINAL)
    check_freeze()
    if set(seeds) & set(FINAL):
        assert json.loads((OUT/'gamedev-decision.json').read_text())['promise']
        check_freeze('final-freeze.json')
    prior = registry(name)
    known, old = set(prior['canonical']), set(prior['legacy'])
    proc = subprocess.Popen([str(java_home()/'bin/java'), '-Xmx1g', '-cp', classpath(), 'MapGenerator'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    entries, hashes, collisions = [], {}, []
    try:
        for seed in seeds:
            proc.stdin.write(str(seed)+'\n'); proc.stdin.flush()
            props = json.loads(proc.stdout.readline())
            board = {k: [list(map(int, r.split(','))) for r in props[k].split('_') if r] for k in ('nodes', 'units', 'edges')}
            digest = hashlib.sha256(json.dumps(board, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            previous = hashlib.sha256(json.dumps(props, sort_keys=True).encode()).hexdigest()
            if digest in known or previous in old or digest in hashes.values(): collisions.append(seed)
            hashes[str(seed)] = digest
            entries.append({'seed': seed, 'hash': digest, 'legacy_hash': previous, 'map': board})
    finally:
        proc.stdin.close(); proc.wait(timeout=20)
    save(OUT/(name+'-maps.json'), {'as_of': now(), 'maps': entries, 'collisions': collisions})
    save(OUT/(name+'-map-hashes.json'), hashes)
    save(OUT/(name+'-novelty.json'), {'passed': not collisions, 'seeds': seeds, 'collisions': collisions,
        'previous_canonical': len(known), 'previous_legacy': len(old), 'registry_sha256': sha(OUT/(name+'-registry.json'))})
    assert not collisions, 'Content collision: no replacement'
    return hashes


def game_schedule(seeds, arms):
    result = []
    for i, seed in enumerate(seeds):
        for j, opponent in enumerate(OPPONENTS[i%5:] + OPPONENTS[:i%5]):
            for seat in (i%2, 1-i%2):
                order = arms if (i+j+seat)%2 == 0 else tuple(reversed(arms))
                result.extend({'candidate': arm, 'opponent': opponent, 'seed': seed, 'seat': seat} for arm in order)
    return result
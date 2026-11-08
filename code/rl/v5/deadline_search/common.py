"""Isolated evidence helpers and immutable dependency identities."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
CODE = ROOT / 'code/rl/v5/deadline_search'
OUT = ROOT / 'experiments/rl/2026-11-08-rl5/deadline-search'
SCRATCH = ROOT / '.context/rl5-deadline-search'
sys.path.insert(0, str(ROOT / 'code'))
ACTOR = ROOT / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt'
CRITIC = ROOT / 'experiments/rl/2026-11-07-ppo-v3/search/frozen-critic/critic.txt'
ENEMIES = [ACTOR, ROOT / 'experiments/rl/2026-11-06-ppo-v2/control-long/step-03002813/weights.txt',
           ROOT / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-04836947/weights.txt']
OLD = ROOT / 'experiments/rl/2026-11-08-rl4/search-teacher'
INITIAL_SPENT = 1379.5969817093574
STOP = datetime(2026, 11, 9, 2, tzinfo=timezone.utc)
PROTECTED = {
    ACTOR: 'dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb',
    ACTOR.with_name('checkpoint.pt'): '9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663',
    ROOT / 'submissions/ppo-v2-league3m.cpp': '199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1',
    ROOT / 'experiments/rl/2026-11-07-ppo-v3/handoff-b2m/bot.cpp': 'b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214',
}


def now(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rel(path): return str(Path(path).resolve().relative_to(ROOT))


def clean(value):
    if isinstance(value, str): return value.replace(str(ROOT), '${PROJECT_ROOT}').replace(str(Path.home()), '${HOME}')
    if isinstance(value, list): return [clean(v) for v in value]
    if isinstance(value, dict): return {k: clean(v) for k, v in value.items()}
    return value


def save(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream: json.dump(clean(data), stream, indent=2); stream.write('\n')


def budget():
    records = [json.loads(line) for line in (ROOT / '.context/rl4-compute/events.jsonl').read_text().splitlines()]
    spent = sum(r['seconds'] for r in records if r.get('event') == 'finished' and r['owner'] == 'search-teacher')
    current = json.loads((ROOT / '.context/rl4-compute/slot.lock').read_text())
    active = max(0, (datetime.now(timezone.utc)-datetime.fromisoformat(current['as_of'])).total_seconds()) if current.get('event') == 'started' and current['owner'] == 'search-teacher' else 0
    return {'as_of': now(), 'initial_owner_seconds': INITIAL_SPENT, 'owner_completed_seconds': spent,
            'phase_completed_seconds': spent-INITIAL_SPENT, 'active_elapsed_seconds': active,
            'phase_remaining_seconds': min(10800-(spent-INITIAL_SPENT)-active, 14400-spent-active),
            'seconds_to_research_stop': (STOP-datetime.now(timezone.utc)).total_seconds()}


def guard():
    for path, expected in PROTECTED.items(): assert sha(path) == expected, rel(path)
    b = budget(); assert b['phase_remaining_seconds'] > 0 and b['seconds_to_research_stop'] > 0
    return {rel(p): h for p, h in PROTECTED.items()}


def sources():
    paths = list(CODE.glob('*.py')) + list(CODE.glob('*.cpp')) + list(CODE.glob('*.hpp'))
    paths += [ROOT / p for p in ('code/rl/search/search.hpp', 'code/rl/search/bot.cpp',
        'code/rl/league/rollout_league.cpp', 'code/rl/models/policy.hpp', 'code/rl/sim/simulator.hpp',
        'code/rl/export/inference.hpp', 'code/arena/BenchmarkMatch.java', 'code/benchmark_public.py',
        'code/run_matches.py', 'code/rl/data/replays.py', 'code/rl/sim/Oracle.java',
        'code/rl/v4/compute_slot.py')]
    return {rel(p): sha(p) for p in sorted(paths)}


def run(command, name, timeout=1200):
    guard(); command = [str(x) for x in command]; start = time.monotonic()
    with (OUT / (name + '.log')).open('x') as stream:
        proc = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        try:
            for line in proc.stdout: stream.write(clean(line)); stream.flush()
            code = proc.wait(timeout=timeout)
        except BaseException:
            proc.terminate(); proc.wait(timeout=10); raise
    save(OUT / (name + '-command.json'), {'as_of': now(), 'command': command, 'returncode': code,
        'seconds': time.monotonic()-start, 'budget': budget(), 'external_spend': 0})
    print(json.dumps({'stage': name, 'returncode': code, 'seconds': time.monotonic()-start}), flush=True)
    if code: raise RuntimeError('Stage failed: '+name)


def build_dir():
    return OUT / 'build/attempt1'
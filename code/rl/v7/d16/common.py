"""New D16 lane paths; no mutation of historical experiment modules or ledgers."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
CODE = ROOT / 'code/rl/v7/d16'
OUT = ROOT / 'experiments/rl/2026-11-09-rl7/d16'
V5 = ROOT / 'experiments/rl/2026-11-08-rl5/deadline-search'
V5CODE = ROOT / 'code/rl/v5/deadline_search'
V6 = ROOT / 'experiments/rl/2026-11-08-rl6/compact-d16'
V6CODE = ROOT / 'code/rl/v6/compact_d16'
SCRATCH = OUT / 'build/specs'
STOP = datetime(2026, 11, 9, 6, tzinfo=timezone.utc)
ACTOR = ROOT / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt'
CRITIC = ROOT / 'experiments/rl/2026-11-07-ppo-v3/search/frozen-critic/critic.txt'
ENEMIES = [ACTOR, ROOT / 'experiments/rl/2026-11-06-ppo-v2/control-long/step-03002813/weights.txt', ROOT / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-04836947/weights.txt']
PROTECTED = {
    ACTOR: 'dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb',
    ACTOR.with_name('checkpoint.pt'): '9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663',
    ROOT / 'submissions/ppo-v2-league3m.cpp': '199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1',
    ROOT / 'experiments/rl/2026-11-07-ppo-v3/handoff-b2m/bot.cpp': 'b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214',
    V6 / 'package-attempt2/b9/bot.cpp': '22ccbbe3fedd8cdb7bae8c232b62269ee5b7cde838b23afb4405692b92e5a5c9',
}
sys.path.insert(0, str(ROOT / 'code'))

def now(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rel(path): return str(Path(path).resolve().relative_to(ROOT))
def build_dir(): return OUT / 'build/attempt1'

def clean(value):
    if isinstance(value, str): return value.replace(str(ROOT), '${PROJECT_ROOT}').replace(str(Path.home()), '${HOME}')
    if isinstance(value, list): return [clean(v) for v in value]
    if isinstance(value, dict): return {k: clean(v) for k, v in value.items()}
    return value

def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f: json.dump(clean(value), f, indent=2); f.write('\n')

def budget():
    path = ROOT / '.context/rl7-compute/events.jsonl'
    events = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    return {'as_of': now(), 'owner': 'd16', 'completed_seconds': sum(e.get('seconds', 0) for e in events if e.get('event') == 'finished' and e.get('owner') == 'd16'), 'cap_seconds': 5400, 'cutoff': STOP.isoformat()}

def guard():
    for p, h in PROTECTED.items(): assert sha(p) == h, rel(p)
    assert datetime.now(timezone.utc) < STOP
    assert budget()['completed_seconds'] < 5400
    return {rel(p): h for p, h in PROTECTED.items()}

def sources():
    return {rel(p): sha(p) for p in sorted(CODE.glob('*')) if p.suffix in ('.py', '.cpp', '.hpp')}

def run(command, name, timeout=1200):
    guard(); command = list(map(str, command)); began = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=timeout)
    log = OUT / (name + '.log'); log.parent.mkdir(parents=True, exist_ok=True)
    with log.open('x') as f: f.write(clean(result.stdout.decode(errors='replace') + result.stderr.decode(errors='replace')))
    save(OUT / (name + '-command.json'), {'as_of': now(), 'command': command, 'returncode': result.returncode, 'seconds': time.monotonic() - began, 'budget': budget(), 'external_spend': 0})
    assert result.returncode == 0, name
    return result

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path); obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj; spec.loader.exec_module(obj); return obj
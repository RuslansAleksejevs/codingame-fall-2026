"""Isolated v6 paths, immutable inputs and the original exclusive budget ledger."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
CODE=ROOT/'code/rl/v6/compact_d16'
OUT=ROOT/'experiments/rl/2026-11-08-rl6/compact-d16'
V5=ROOT/'experiments/rl/2026-11-08-rl5/deadline-search'
V5CODE=ROOT/'code/rl/v5/deadline_search'
SCRATCH=ROOT/'.context/rl6-compact-d16'
sys.path.insert(0,str(ROOT/'code'))
ACTOR=ROOT/'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt'
CRITIC=ROOT/'experiments/rl/2026-11-07-ppo-v3/search/frozen-critic/critic.txt'
ENEMIES=[ACTOR,ROOT/'experiments/rl/2026-11-06-ppo-v2/control-long/step-03002813/weights.txt',ROOT/'experiments/rl/2026-11-06-ppo-v2/league-a/step-04836947/weights.txt']
WEIGHTS=[ACTOR,CRITIC,*ENEMIES[1:]]
INITIAL_SPENT=4569.00871229358
STOP=datetime(2026,11,9,2,tzinfo=timezone.utc)
PROTECTED={
 ACTOR:'dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb',
 ACTOR.with_name('checkpoint.pt'):'9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663',
 ROOT/'submissions/ppo-v2-league3m.cpp':'199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1',
 ROOT/'experiments/rl/2026-11-07-ppo-v3/handoff-b2m/bot.cpp':'b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214'}


def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rel(path):return str(Path(path).resolve().relative_to(ROOT))
def build_dir():return OUT/'build/attempt2'


def clean(value):
    if isinstance(value,str):return value.replace(str(ROOT),'${PROJECT_ROOT}').replace(str(Path.home()),'${HOME}')
    if isinstance(value,list):return [clean(v) for v in value]
    if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
    return value


def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(clean(value),f,indent=2);f.write('\n')


def budget():
    records=[json.loads(s) for s in (ROOT/'.context/rl4-compute/events.jsonl').read_text().splitlines()]
    total=sum(r['seconds'] for r in records if r.get('event')=='finished' and r['owner']=='search-teacher')
    current=json.loads((ROOT/'.context/rl4-compute/slot.lock').read_text())
    active=max(0,(datetime.now(timezone.utc)-datetime.fromisoformat(current['as_of'])).total_seconds()) if current.get('event')=='started' and current['owner']=='search-teacher' else 0
    return {'as_of':now(),'initial_owner_seconds':INITIAL_SPENT,'owner_completed_seconds':total,
        'phase_completed_seconds':total-INITIAL_SPENT,'active_seconds':active,
        'phase_remaining_seconds':min(9000-total+INITIAL_SPENT-active,14400-total-active),
        'seconds_to_cutoff':(STOP-datetime.now(timezone.utc)).total_seconds()}


def guard():
    for p,h in PROTECTED.items():assert sha(p)==h,rel(p)
    frozen=json.loads((V5/'freeze.json').read_text())
    for p,h in {**frozen['sources'],**frozen['weights'],**frozen['binaries'],**frozen['dependencies']}.items():assert sha(ROOT/p)==h,p
    assert sha(V5/'PROTOCOL.md')==frozen['protocol_sha256']
    b=budget();assert b['phase_remaining_seconds']>0 and b['seconds_to_cutoff']>0
    return {rel(p):h for p,h in PROTECTED.items()}


def sources():
    files=[p for p in CODE.iterdir() if p.suffix in ('.py','.cpp','.hpp')]
    return {rel(p):sha(p) for p in sorted(files)}


def run(command,name,timeout=1200):
    guard();command=list(map(str,command));start=time.monotonic()
    result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=timeout)
    log=OUT/(name+'.log');log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('x') as f:f.write(clean(result.stdout.decode(errors='replace')+result.stderr.decode(errors='replace')))
    save(OUT/(name+'-command.json'),{'as_of':now(),'command':command,'returncode':result.returncode,
        'seconds':time.monotonic()-start,'budget':budget(),'external_spend':0})
    print(json.dumps({'stage':name,'returncode':result.returncode,'seconds':time.monotonic()-start}),flush=True)
    assert result.returncode==0,name
    return result


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec)
    sys.modules[name]=result;spec.loader.exec_module(result);return result
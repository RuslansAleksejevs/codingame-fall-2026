#!/usr/bin/env python3
"""Full-state differential replay plus independent archived-viewer unit checks."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE, REPO, java_home
from rl.sim.native import Simulator
from rl.data.replays import read, sources

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--games',type=int,default=100);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    paths=sources(BASE);stride=max(1,len(paths)//args.games);paths=paths[::stride][:args.games]
    cp=str(BASE/'code/build')+':'+str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()
    java=subprocess.Popen([str(java_home()/'bin/java'),'-Xmx1g','-cp',cp,'Oracle'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    total=0;counts=Counter();began=time.monotonic();native_seconds=0;checked=[];mismatches=[];terminal_checks=0
    try:
        for i,path in enumerate(paths):
            rec=read(path)
            if rec['errors']:continue
            job=dict(rec['map'],actions=[d['actions'] for d in rec['decisions']])
            java.stdin.write(json.dumps(job)+'\n');java.stdin.flush()
            line=java.stdout.readline()
            if not line:raise RuntimeError('Java oracle stopped')
            expected=json.loads(line);sim=Simulator(rec['map'])
            actual=[sim.state()]
            for d in rec['decisions']:
                if sim.state()['units']!=d['units']:
                    mismatches.append({'file':str(path.relative_to(BASE)),'turn':len(actual)-1,'kind':'viewer','actual':sim.state(),'expected_units':d['units']});break
                for a in d['actions']:
                    counts.update(c.strip().split()[0] for c in a.split(';') if c.strip())
                start=time.perf_counter();sim.step(d['actions']);native_seconds+=time.perf_counter()-start
                actual.append(sim.state());total+=1
            for turn,(a,e) in enumerate(zip(actual,expected)):
                for key in ('turn','score','units','edges','triangles','done'):
                    if a[key]!=e[key]:mismatches.append({'file':str(path.relative_to(BASE)),'turn':turn,'kind':key,'actual':a,'expected':e});break
                if mismatches:break
            if actual[-1]['done'] and not mismatches:
                terminal_checks+=1
                archived=[rec['scores'][str(p)] for p in (0,1)]
                if actual[-1]['score']!=archived:mismatches.append({'file':str(path.relative_to(BASE)),'kind':'archived_terminal_score','actual':actual[-1]['score'],'expected':archived})
            checked.append({'path':str(path.relative_to(BASE)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'turns':len(actual)-1})
            if mismatches:break
            if (i+1)%20==0:print(f'{i+1} games, {total} transitions, zero mismatches',flush=True)
    finally:
        java.stdin.close();java.wait(timeout=20)
    summary={'games':len(checked),'joint_transitions':total,'archived_terminal_score_checks':terminal_checks,'mismatches':mismatches,'command_counts':dict(counts),
             'native_step_seconds':native_seconds,'joint_steps_per_second':total/native_seconds if native_seconds else 0,
             'wall_seconds':time.monotonic()-began,'records':checked,'scope':'Exact Java Board/TaskManager transitions; archived viewer pre-decision unit states; maps from historical development records.'}
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='records'},indent=2))
    if mismatches:raise SystemExit(1)
if __name__=='__main__':main()

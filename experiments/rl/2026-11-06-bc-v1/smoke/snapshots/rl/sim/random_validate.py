#!/usr/bin/env python3
"""Stress simultaneous spends and road edits from synthetic populated maps."""
import argparse
from collections import Counter
import ctypes
import json
from pathlib import Path
import random
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE,REPO,java_home
from rl.sim.native import Simulator,LIB
from rl.data.replays import read,sources

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    LIB.sim_random.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_uint];LIB.sim_random.restype=ctypes.c_char_p
    rng=random.Random(20261106);paths=sources(BASE)[::16];cp=str(BASE/'code/build')+':'+str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()
    java=subprocess.Popen([str(java_home()/'bin/java'),'-Xmx1g','-cp',cp,'Oracle'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    cases=[];commands=Counter();mismatches=[];turns=0;start=time.monotonic()
    try:
        for path in paths:
            data=read(path)['map'];data['units']=[[rng.randint(1,4),0] if x<960 else [0,rng.randint(1,4)] for x,y in data['nodes']]
            sim=Simulator(data);states=[sim.state()];actions=[]
            for t in range(50):
                pair=[LIB.sim_random(sim.ptr,p,rng.randrange(2**32)).decode() for p in (0,1)]
                for line in pair:commands.update(cmd.split()[0] for cmd in line.split(';'))
                sim.step(pair);actions.append(pair);states.append(sim.state());turns+=1
                if states[-1]['done']:break
            job=dict(data,actions=actions);java.stdin.write(json.dumps(job)+'\n');java.stdin.flush();line=java.stdout.readline()
            if not line:raise RuntimeError('Oracle stopped')
            expected=json.loads(line)
            for i,(a,e) in enumerate(zip(states,expected)):
                if any(a[k]!=e[k] for k in ('turn','score','units','edges','triangles','done')):
                    mismatches.append({'case':len(cases),'turn':i,'actual':a,'expected':e});break
            cases.append(job)
            if mismatches:break
    finally:java.stdin.close();java.wait(timeout=20)
    report={'seed':20261106,'cases':len(cases),'joint_transitions':turns,'commands':dict(commands),'mismatches':mismatches,'wall_seconds':time.monotonic()-start}
    args.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    if mismatches:
        args.out.with_suffix('.failure.json').write_text(json.dumps(cases[-1],indent=2)+'\n');raise SystemExit(1)
if __name__=='__main__':main()

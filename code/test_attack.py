#!/usr/bin/env python3
"""Protocol checks for ATTACK resource accounting and v3 fallback behavior."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def state(mine, enemy, owner=0, distant=False):
    edges=[(0,1),(1,2),(2,0),(2,3),(3,4)]
    if not distant: edges.append((1,4))
    lines=['5']+[f'{v} {v*100} 0' for v in range(5)]
    lines+=['0 0']+[f'{v} {mine[v]} {enemy[v]}' for v in range(5)]
    lines+=[str(len(edges))]+[f'{a} {b}' for a,b in edges]
    lines+=['1',f'0 1 2 {owner} {int(owner!=0)} 1','0']
    return '\n'.join(lines)+'\n'

def run(binary, data):
    p=subprocess.run([binary],input=data,text=True,capture_output=True,check=True)
    return p.stdout.strip().split(';'),p.stderr

with tempfile.TemporaryDirectory() as tmp:
    binaries=[]
    for name in ['v3-multispawn','v6-attack']:
        binary=str(Path(tmp)/name)
        subprocess.run(['clang++','-std=c++17','-O2','-Wall','-Wextra','-Wpedantic',
                        str(ROOT/'code/variants'/f'{name}.cpp'),'-o',binary],check=True)
        binaries.append(binary)
    attack,stderr=run(binaries[1],state([2,2,2,0,0],[0,0,0,0,4]))
    assert attack[0]=='ATTACK 0 1 2 4',attack
    assert sum(c.startswith('ATTACK') for c in attack)==1
    assert not any(c.startswith('SPAWN') for c in attack), 'Spent triangle reused'
    outgoing=[0]*5
    for c in attack:
        parts=c.split()
        if parts[0]=='MOVE':outgoing[int(parts[1])]+=int(parts[3])
    assert all(outgoing[v]<=1 for v in [0,1,2]), 'Consumed units also moved'
    assert 'units=6 triangles=1' in stderr, 'Telemetry must describe observed input'
    for data in [
        state([2,2,2,0,0],[0,0,0,0,3]),
        state([0,3,3,0,0],[0,0,0,0,8]),
        state([1,1,1,0,0],[0,0,0,0,8]),
        state([2,2,2,0,0],[0,0,0,0,8],owner=1),
        state([2,2,2,0,0],[0,0,0,0,8],distant=True),
    ]:
        before,_=run(binaries[0],data);after,_=run(binaries[1],data)
        assert before==after,(before,after)
    commands,_=run(binaries[1],state([2,2,2,0,0],[0,0,0,5,8]))
    assert commands[0]=='ATTACK 0 1 2 4',commands
print('PASS: attack threshold, legality, resource accounting, largest target and v3 fallback')

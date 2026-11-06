#!/usr/bin/env python3
"""Audit teacher-plan normalization against the recorded joint transition."""
import argparse
import ctypes
import json
from pathlib import Path
import re
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE
from rl.sim.native import Simulator,LIB
from rl.data.replays import sources,read

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    LIB.sim_clone.argtypes=[ctypes.c_void_p];LIB.sim_clone.restype=ctypes.c_void_p
    LIB.sim_labels.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_char_p];LIB.sim_label_plan.restype=ctypes.c_char_p
    total=0;differences=[];start=time.monotonic();families={};rejected=[]
    for i,path in enumerate(sources(BASE)):
        rec=read(path)
        if rec['errors']:continue
        p=1-int(re.search(r'seat(\d)',path.name)[1]);style=int('khoufou' in path.name);sim=Simulator(rec['map'])
        for turn,d in enumerate(rec['decisions']):
            if sim.state()['done']:break
            ng=LIB.sim_labels(sim.ptr,p,style,d['actions'][p].encode())
            if ng<0:rejected.append({'record':str(path.relative_to(BASE)),'turn':turn,'reason':LIB.sim_error().decode()});sim.step(d['actions']);continue
            normalized=LIB.sim_label_plan().decode();copy=LIB.sim_clone(sim.ptr);pair=d['actions'].copy();pair[p]=normalized
            if LIB.sim_step(copy,pair[0].encode(),pair[1].encode()):raise RuntimeError(LIB.sim_error().decode())
            expected=json.loads(LIB.sim_state(copy));LIB.sim_delete(copy);sim.step(d['actions']);actual=sim.state();total+=1
            if any(actual[k]!=expected[k] for k in ('score','units','edges','triangles','done')):
                differences.append({'record':str(path.relative_to(BASE)),'turn':turn,'original':d['actions'][p],'normalized':normalized,'changed_fields':[k for k in ('score','units','edges','triangles','done') if actual[k]!=expected[k]]})
        if (i+1)%400==0:print(f'{i+1} games: {total} plans, {len(differences)} transition differences',flush=True)
    report={'plans':total,'transition_equivalent_plans':total-len(differences),'transition_equivalence':1-len(differences)/max(1,total),'differences':differences,'rejections':rejected,'wall_seconds':time.monotonic()-start,'method':'Normalize nonadjacent moves to one step, split unit amounts, order triangle choices and unit moves canonically; replay with the actual opposing plan. This checks observed joint effects, not equivalence against every possible opposing plan.'}
    args.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('differences','rejections')},indent=2))
if __name__=='__main__':main()

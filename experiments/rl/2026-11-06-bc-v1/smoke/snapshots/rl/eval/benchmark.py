#!/usr/bin/env python3
"""Measure complete native policy calls on archived observations, not MLP-only FLOPs."""
import argparse
import ctypes
import json
from pathlib import Path
import statistics
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE
from rl.sim.native import Simulator,LIB
from rl.data.replays import read,sources

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--weights',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);args=ap.parse_args()
    LIB.net_new.argtypes=[ctypes.c_char_p];LIB.net_new.restype=ctypes.c_void_p;LIB.net_act.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int];LIB.net_act.restype=ctypes.c_char_p;LIB.net_delete.argtypes=[ctypes.c_void_p]
    LIB.sim_clone.argtypes=[ctypes.c_void_p];LIB.sim_clone.restype=ctypes.c_void_p
    net=LIB.net_new(str(args.weights.resolve()).encode());times=[];errors=0;units=[]
    if not net:raise RuntimeError('Cannot load model')
    for path in sources(BASE)[::16]:
        rec=read(path)
        if rec['errors']:continue
        sim=Simulator(rec['map'])
        for d in rec['decisions']:
            s=sim.state()
            if s['done']:break
            for p in (0,1):
                start=time.perf_counter();plan=LIB.net_act(net,sim.ptr,p,2).decode();times.append(time.perf_counter()-start);units.append(sum(v[p] for v in s['units']))
                copy=LIB.sim_clone(sim.ptr);pair=d['actions'].copy();pair[p]=plan;LIB.sim_step(copy,pair[0].encode(),pair[1].encode());after=json.loads(LIB.sim_state(copy));errors+=after['errors'][p]-s['errors'][p];LIB.sim_delete(copy)
            sim.step(d['actions'])
            if len(times)>=2000:break
        if len(times)>=2000:break
    LIB.net_delete(net);ordered=sorted(times)
    report={'decisions':len(times),'total_policy_seconds':sum(times),'complete_decisions_per_second':len(times)/sum(times),'p50_us':statistics.median(times)*1e6,'p95_us':ordered[int(.95*(len(ordered)-1))]*1e6,'max_us':max(times)*1e6,'max_units':max(units),'parse_errors':errors,'scope':'Single C++ policy call, including all feature encoding, legal candidates and sequential decoding; archived development states, both players. Excludes environment step and process I/O.'}
    args.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()

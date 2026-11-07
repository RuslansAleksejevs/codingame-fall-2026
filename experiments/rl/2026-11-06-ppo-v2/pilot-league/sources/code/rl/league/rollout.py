"""Threaded C++ rollouts with zero-copy NumPy views until the next collect call."""
import ctypes as C
import json
from pathlib import Path
import numpy as np
from rl.sim.native import map_text

ROOT=Path(__file__).resolve().parents[3]
LIB=C.CDLL(str(ROOT/'code/build/libtryangle_league.dylib'))
LIB.league_new.argtypes=[C.c_char_p];LIB.league_new.restype=C.c_void_p
LIB.league_delete.argtypes=[C.c_void_p]
LIB.league_error.restype=C.c_char_p
LIB.league_add_map.argtypes=[C.c_void_p,C.c_char_p]
LIB.league_set_actor.argtypes=[C.c_void_p,C.POINTER(C.c_float)]
LIB.league_add_pool.argtypes=[C.c_void_p];LIB.league_clear_pool.argtypes=[C.c_void_p]
LIB.league_collect.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_ulonglong,C.c_double,C.c_int]
for name in ('league_stats','league_records'):
    getattr(LIB,name).argtypes=[C.c_void_p];getattr(LIB,name).restype=C.c_char_p
LIB.league_float.argtypes=[C.c_void_p,C.c_int];LIB.league_float.restype=C.POINTER(C.c_float)
LIB.league_int.argtypes=[C.c_void_p,C.c_int];LIB.league_int.restype=C.POINTER(C.c_int)
LIB.league_episodes.argtypes=[C.c_void_p]
LIB.league_greedy_game.argtypes=[C.c_void_p,C.c_char_p,C.c_int]

def flatten(model):
    return np.concatenate([v.detach().cpu().numpy().ravel() for v in model.parameters()]).astype(np.float32)

class Rollout:
    def __init__(self,weights,maps):
        self.ptr=LIB.league_new(str(Path(weights).resolve()).encode())
        if not self.ptr:raise RuntimeError(LIB.league_error().decode())
        for data in maps:LIB.league_add_map(self.ptr,map_text(data).encode())
    def set_actor(self,model):
        flat=flatten(model);LIB.league_set_actor(self.ptr,flat.ctypes.data_as(C.POINTER(C.c_float)))
    def add_pool(self):LIB.league_add_pool(self.ptr)
    def collect(self,games,workers,seed,temperature=.7,audit=0):
        if LIB.league_collect(self.ptr,games,workers,seed,temperature,audit):raise RuntimeError(LIB.league_error().decode())
        stats=json.loads(LIB.league_stats(self.ptr));n=stats['controlled_decisions'];g=stats['groups'];c=stats['candidates'];e=LIB.league_episodes(self.ptr)
        f=lambda which,shape:np.ctypeslib.as_array(LIB.league_float(self.ptr,which),shape=shape)
        i=lambda which,size:np.ctypeslib.as_array(LIB.league_int(self.ptr,which),shape=(size,))
        return {'x':f(0,(c*128,)).reshape(c,128),'value_x':f(1,(n*128,)).reshape(n,128),'old_logp':f(2,(n,)),'old_entropy':f(3,(n,)),'reward':f(4,(n,)),
                'group_offsets':i(0,g+1),'choices':i(1,g),'turn_offsets':i(2,n+1),'episode_offsets':i(3,e+1),'game_ids':i(4,n),'players':i(5,n),'stats':stats}
    def records(self):return json.loads(LIB.league_records(self.ptr))
    def evaluate(self,maps):
        results=[]
        for data in maps:
            for seat in (0,1):
                r=LIB.league_greedy_game(self.ptr,map_text(data).encode(),seat)
                if r==-9:raise RuntimeError(LIB.league_error().decode())
                results.append(r)
        return {'games':len(results),'wins':results.count(1),'draws':results.count(0),'losses':results.count(-1),'score_rate':sum((v+1)/2 for v in results)/len(results),'results':results}
    def close(self):
        if self.ptr:LIB.league_delete(self.ptr);self.ptr=None
    def __del__(self):self.close()

EXTERNAL=C.CFUNCTYPE(C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_char_p)
LIB.league_set_external.argtypes=[C.c_void_p,EXTERNAL]
LIB.league_set_anchor.argtypes=[C.c_void_p,C.POINTER(C.c_float)]
LIB.league_observation.argtypes=[C.c_void_p,C.c_int,C.c_int];LIB.league_observation.restype=C.c_char_p

def set_anchor(collector,model):
    flat=flatten(model);LIB.league_set_anchor(collector.ptr,flat.ctypes.data_as(C.POINTER(C.c_float)))

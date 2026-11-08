"""Explicit stopped-prefix selection and hidden-state contract, disclosed roots only."""
from diagnose import Native
from common import *
from rl.data.replays import read
from rl.sim.native import Simulator
from rl.league.rollout import LIB as LEAGUE
import ctypes as C


def main():
    guard();target=build_dir()/'contracts.dylib';assert not target.exists()
    run(['clang++','-std=c++17','-O3','-shared','-fPIC','-pthread',rel(CODE/'contracts.cpp'),'-o',rel(target)],'contracts-build')
    native=Native();lib=C.CDLL(str(target))
    lib.ds_contract.argtypes=[C.c_void_p,C.c_void_p,C.c_int,C.c_char_p];lib.ds_contract.restype=C.c_char_p
    lib.ds_error.restype=C.c_char_p
    rows=[]
    try:
        for seed,opp in [(62041,'v6'),(62044,'lacoz'),(62046,'lacoz')]:
            record=read(OLD/f'confirm3/search2-vs-{opp}-seed{seed}-seat0.json.gz')
            sim=Simulator(record['map'])
            try:
                for decision in record['decisions']:sim.step(decision['actions'])
                for p in (0,1):
                    result=lib.ds_contract(native.ptr,sim.ptr,p,LEAGUE.league_observation(sim.ptr,p,1))
                    assert result,lib.ds_error()
                    rows.append({'seed':seed,'player':p,**json.loads(result)})
            finally:sim.close()
    finally:native.close()
    save(OUT/'contracts.json',{'as_of':now(),'passed':True,'roots':rows,'cap_probes':sum(len(r['caps']) for r in rows),
        'candidate_binary_unchanged':sha(build_dir()/'bot'),'sources':sources(),'budget':budget()})
    print(json.dumps({'passed':True,'roots':len(rows),'cap_probes':sum(len(r['caps']) for r in rows)}))


if __name__=='__main__':main()
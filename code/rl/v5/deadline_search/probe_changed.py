"""Fixed maximum three changed-plan disclosed roots, to exercise nonbaseline stops."""
import ctypes as C
from common import *
from diagnose import Native
from rl.sim.native import Simulator
from rl.data.replays import read
from rl.league.rollout import LIB as LEAGUE


def main():
    native=Native();lib=C.CDLL(str(build_dir()/'contracts.dylib'))
    lib.ds_contract.argtypes=[C.c_void_p,C.c_void_p,C.c_int,C.c_char_p];lib.ds_contract.restype=C.c_char_p
    lib.ds_error.restype=C.c_char_p;rows=[];inspected=0
    try:
        for seed,opp in [(62041,'v6'),(62044,'lacoz'),(62046,'lacoz')]:
            record=read(OLD/f'confirm3/search2-vs-{opp}-seed{seed}-seat0.json.gz');sim=Simulator(record['map'])
            try:
                for turn,d in enumerate(record['decisions']):
                    for p in (0,1):
                        if len(rows)==3:break
                        _,stats=native.act(sim,p);inspected+=1
                        if stats['selected']>0:
                            result=lib.ds_contract(native.ptr,sim.ptr,p,LEAGUE.league_observation(sim.ptr,p,1))
                            assert result,lib.ds_error()
                            rows.append({'seed':seed,'turn':turn,'player':p,'unlimited_selected':stats['selected'],**json.loads(result)})
                    if len(rows)==3:break
                    sim.step(d['actions'])
            finally:sim.close()
            if len(rows)==3:break
    finally:native.close()
    assert rows and any(c['selected']>0 for r in rows for c in r['caps'])
    save(OUT/'changed-plan-contracts.json',{'as_of':now(),'passed':True,'roots_inspected':inspected,'roots':rows,
        'cap_probes':sum(len(r['caps']) for r in rows),'scope':'Disclosed prefix contract coverage, no strength selection.'})
    print(json.dumps({'passed':True,'roots':len(rows),'cap_probes':sum(len(r['caps']) for r in rows)}))


if __name__=='__main__':main()
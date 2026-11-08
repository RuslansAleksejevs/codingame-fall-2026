"""Exactly60 disclosed-root original-30ms calls; no strength claim or source edits."""
import ctypes as C
from common import *
from diagnose import Native
from rl.data.replays import read
from rl.sim.native import Simulator


def main():
    guard();native=Native();lib=native.lib
    lib.search_info.argtypes=[C.c_void_p];lib.search_info.restype=C.c_char_p
    weights=[str(x).encode() for x in [ACTOR,CRITIC,*ENEMIES]]
    old=lib.search_new(*weights,2,4,30);assert old
    rows=[]
    try:
        for seed,opp in [(62041,'v6'),(62044,'lacoz'),(62046,'lacoz')]:
            record=read(OLD/f'confirm3/search2-vs-{opp}-seed{seed}-seat0.json.gz');sim=Simulator(record['map'])
            try:
                for d in record['decisions']:sim.step(d['actions'])
                before=sim.state()
                for p in (0,1):
                    for repeat in range(10):
                        start=time.perf_counter();action=lib.search_act(old,sim.ptr,p)
                        elapsed=(time.perf_counter()-start)*1e6;assert action
                        info=json.loads(lib.search_info(old))
                        rows.append({'seed':seed,'player':p,'repeat':repeat,'external_call_us':elapsed,
                                     'action':action.decode(),'original_search_info':info})
                        assert sim.state()==before
            finally:sim.close()
    finally:lib.search_delete(old);native.close()
    save(OUT/'legacy-timing.json',{'as_of':now(),'calls':len(rows),
        'max_external_call_us':max(r['external_call_us'] for r in rows),
        'max_internal_plan_us':max(r['original_search_info']['plan_us'] for r in rows),
        'calls_above_nominal_30ms':sum(r['original_search_info']['plan_us']>30000 for r in rows),
        'calls_above_50ms':sum(r['external_call_us']>50000 for r in rows),
        'protocol_sha256':sha(OUT/'LEGACY_TIMING_CHECK.md'),'rows':rows,
        'scope':'Native-call timing on disclosed old roots, not referee/platform deadline or fresh strength.'})
    print(json.dumps({'calls':len(rows),'max_external_call_us':max(r['external_call_us'] for r in rows),
                     'calls_above_nominal_30ms':sum(r['original_search_info']['plan_us']>30000 for r in rows)}),flush=True)


if __name__=='__main__':main()
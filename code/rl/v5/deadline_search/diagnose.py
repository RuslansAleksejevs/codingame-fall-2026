"""Finite disclosed-root timing, deterministic parity and input restoration checks."""
import ctypes as C
import gzip
import subprocess
from common import *
from rl.data.replays import read
from rl.sim.native import Simulator
from rl.league.rollout import LIB as LEAGUE


class Native:
    def __init__(self):
        self.lib = C.CDLL(str(build_dir()/'api.dylib'))
        lib=self.lib
        lib.ds_new.argtypes=[C.c_char_p]*5;lib.ds_new.restype=C.c_void_p
        lib.ds_delete.argtypes=[C.c_void_p];lib.ds_error.restype=C.c_char_p
        lib.ds_act.argtypes=[C.c_void_p,C.c_void_p,C.c_int,C.c_double,C.c_int,C.c_int,C.c_double];lib.ds_act.restype=C.c_char_p
        lib.ds_stats.argtypes=[C.c_void_p];lib.ds_stats.restype=C.c_char_p
        lib.ds_restore.argtypes=[C.c_char_p,C.c_int,C.c_int];lib.ds_restore.restype=C.c_char_p
        lib.search_act.argtypes=[C.c_void_p,C.c_void_p,C.c_int];lib.search_act.restype=C.c_char_p
        lib.search_new.argtypes=[C.c_char_p]*5+[C.c_int,C.c_int,C.c_double];lib.search_new.restype=C.c_void_p
        lib.search_delete.argtypes=[C.c_void_p]
        weights=[str(x).encode() for x in [ACTOR,CRITIC,*ENEMIES]]
        self.ptr=lib.ds_new(*weights);self.old=lib.search_new(*weights,2,4,0)
        assert self.ptr and self.old
    def act(self, sim, p, ms=0, count=4, cap=0, elapsed=0):
        result=self.lib.ds_act(self.ptr,sim.ptr,p,ms,count,cap,elapsed)
        assert result, self.lib.ds_error()
        return result.decode(),json.loads(self.lib.ds_stats(self.ptr))
    def close(self):self.lib.ds_delete(self.ptr);self.lib.search_delete(self.old)


def main():
    guard(); native=Native();directory=OUT/'diagnostic';directory.mkdir(exist_ok=False)
    fixtures=[(62041,'v6',24),(62044,'lacoz',24),(62046,'lacoz',3)]
    roots=[];streams=[];timings=[];commands=0
    try:
        for seed,opp,failed in fixtures:
            path=OLD/f'confirm3/search2-vs-{opp}-seed{seed}-seat0.json.gz'
            raw=json.loads(gzip.decompress(path.read_bytes()));record=read(path)
            raw_late=[s for s in raw['errors']['0'] if s][-1]
            assert len(record['decisions']) == failed-1
            for p in (0,1):
                sim=Simulator(record['map']);inputs=[];expected=[]
                try:
                    for turn in range(failed):
                        original=sim.state()
                        complete_input=LEAGUE.league_observation(sim.ptr,p,1)
                        restored=native.lib.ds_restore(complete_input,turn,p)
                        assert restored,native.lib.ds_error()
                        assert json.loads(restored)==original, (seed,p,turn,'restore')
                        observation=LEAGUE.league_observation(sim.ptr,p,int(turn==0));inputs.append(observation)
                        old=native.lib.search_act(native.old,sim.ptr,p).decode()
                        new,stats=native.act(sim,p);again,again_stats=native.act(sim,p)
                        assert old==new==again,(seed,p,turn,'unlimited')
                        assert stats['values']==again_stats['values']
                        assert sim.state()==original
                        expected.append(new);commands+=1
                        if turn==failed-1:
                            baseline,_=native.act(sim,p,count=1)
                            emergency,es=native.act(sim,p,ms=16,cap=20000,elapsed=17000)
                            assert emergency=='WAIT' and es['emergency']==1 and es['selected']==0
                            capped,cs=native.act(sim,p,cap=stats['forwards'] if stats['forwards'] else 1)
                            assert sim.state()==original
                            for repeat in range(10):
                                begin=time.perf_counter();action,t=native.act(sim,p,ms=16,cap=20000)
                                timings.append({'seed':seed,'player':p,'turn':failed,'repeat':repeat,
                                    'call_us':(time.perf_counter()-begin)*1e6,'action':action,'stats':t})
                                assert not t['emergency']
                                if t['selected']==0:assert action==baseline
                            roots.append({'seed':seed,'opponent':opp,'player':p,'failed_reported_turn':failed,
                                'source':rel(path),'source_sha256':sha(path),'old_raw_late_stderr':raw_late,
                                'state':original,'baseline':baseline,'unlimited_selected':new,
                                'unlimited_stats':stats,'cap_probe':cs})
                        if turn<len(record['decisions']):sim.step(record['decisions'][turn]['actions'])
                    command=[str(build_dir()/'bot'),*[str(x) for x in [ACTOR,CRITIC,*ENEMIES]],'4','0']
                    result=subprocess.run(command,input=b''.join(inputs),capture_output=True,timeout=60)
                    actual=result.stdout.decode().splitlines()
                    save(directory/f'stream-{seed}-{p}.json',{'command':command,'returncode':result.returncode,
                        'expected':expected,'actual':actual,'stderr':result.stderr.decode()})
                    assert result.returncode==0 and expected==actual
                    streams.append({'seed':seed,'player':p,'turns':len(expected),'mismatches':0})
                finally:sim.close()
        save(directory/'roots.json',roots);save(directory/'timings.json',timings)
        save(directory/'summary.json',{'as_of':now(),'passed':True,'fixtures':len(fixtures),'roots':len(roots),
            'unlimited_parity_commands':commands,'standalone_parity_commands':commands,'streams':streams,
            'timed_root_calls':len(timings),'maximum_timed_call_us':max(t['call_us'] for t in timings),
            'scope':'Disclosed regression roots, not fresh strength evidence; call time excludes bot I/O.',
            'sources':sources(),'budget':budget()})
        print(json.dumps({'passed':True,'commands':commands,'timed_calls':len(timings),
                          'maximum_timed_call_us':max(t['call_us'] for t in timings)}))
    finally:native.close()


if __name__=='__main__':main()
"""Finite disclosed-stream, mandatory-baseline and delayed-input contracts."""
import ctypes as C
import gzip
import selectors
from common import *
from rl.data.replays import read
from rl.sim.native import Simulator
from rl.league.rollout import LIB as LEAGUE

class Native:
    def __init__(self, path):
        self.lib = C.CDLL(str(path)); lib = self.lib
        lib.ds_new.argtypes = [C.c_char_p] * 5; lib.ds_new.restype = C.c_void_p
        lib.ds_delete.argtypes = [C.c_void_p]; lib.ds_error.restype = C.c_char_p
        lib.ds_act.argtypes = [C.c_void_p, C.c_void_p, C.c_int, C.c_double, C.c_int, C.c_int, C.c_double]; lib.ds_act.restype = C.c_char_p
        lib.ds_stats.argtypes = [C.c_void_p]; lib.ds_stats.restype = C.c_char_p
        lib.ds_restore.argtypes = [C.c_char_p, C.c_int, C.c_int]; lib.ds_restore.restype = C.c_char_p
        lib.ds_contract.argtypes = [C.c_void_p, C.c_void_p, C.c_int, C.c_char_p]; lib.ds_contract.restype = C.c_char_p
        self.ptr = lib.ds_new(*[b'0'] * 5); assert self.ptr, lib.ds_error()
    def act(self, sim, p, ms=0, cap=0, count=4, elapsed=0):
        result = self.lib.ds_act(self.ptr, sim.ptr, p, ms, count, cap, elapsed)
        assert result, self.lib.ds_error()
        action = result.decode(); return action, json.loads(self.lib.ds_stats(self.ptr))
    def close(self): self.lib.ds_delete(self.ptr)

def stored(path, value):
    with path.open('xb') as f: f.write(gzip.compress(json.dumps(clean(value)).encode(), mtime=0))

def invariants(st):
    return {k: st[k] for k in ('selected', 'generated', 'complete', 'transitions', 'stopped', 'emergency', 'forwards', 'choices', 'checks', 'values')}

def delayed(directory, inputs, expected):
    outcomes = []
    for delay in (.020, .030):
        for label, binary in [('repaired', build_dir()/'candidate'), ('original_b9', V6/'build/attempt2/candidate')]:
            name = f'delay{int(delay*1000)}-{label}'; outputs = []; began = time.monotonic()
            with (directory/(name+'-stderr.log')).open('xb') as err:
                process = subprocess.Popen([str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err)
                selector = selectors.DefaultSelector(); selector.register(process.stdout, selectors.EVENT_READ)
                try:
                    for turn, text in enumerate(inputs):
                        if turn == len(inputs)-1:
                            first, rest = text.split(b' ', 1)
                            process.stdin.write(first+b' '); process.stdin.flush(); time.sleep(delay)
                            process.stdin.write(rest); process.stdin.flush()
                        else: process.stdin.write(text); process.stdin.flush()
                        assert selector.select(5), ('No output', name, turn)
                        line = process.stdout.readline().decode().strip(); assert line
                        outputs.append(line)
                    process.stdin.close(); process.wait(timeout=5)
                    extra = process.stdout.read().decode(); assert not extra
                finally:
                    selector.close()
                    if process.poll() is None: process.kill(); process.wait()
            stderr = (directory/(name+'-stderr.log')).read_text()
            timings = [json.loads(s.split('=',1)[1]) for s in stderr.splitlines() if s.startswith('deadline=')]
            stored(directory/(name+'.json.gz'), {'inputs':[x.decode() for x in inputs], 'outputs':outputs, 'stderr':stderr, 'returncode':process.returncode})
            assert process.returncode == 0 and len(timings) == len(inputs)
            last = timings[-1]
            assert last['parse_us'] >= delay*1e6-2500, ('Input delay not measured', last)
            assert last['through_flush_us'] >= last['parse_us']
            if label == 'repaired':
                assert outputs[-1] == expected and last['search']['baseline_complete'] == 1
                assert last['search']['emergency'] == 0 and last['search']['stopped'] == 1
                assert last['through_flush_us'] < 40000
            else: assert outputs[-1] == 'WAIT' and last['search']['emergency'] == 1
            outcomes.append({'label':label, 'delay_ms':delay*1000, 'output':outputs[-1], 'expected_greedy':expected, 'timing':last, 'seconds':time.monotonic()-began})
    return outcomes

def main():
    guard(); directory = OUT/'contracts'; directory.mkdir(exist_ok=False); began=time.monotonic()
    old_manifest=json.loads((V6/'contracts/manifest.json').read_text())
    paths=[ROOT/r['path'] for r in old_manifest['games'][:16]]
    v4=ROOT/'experiments/rl/2026-11-08-rl4/search-teacher/confirm3'
    paths += [v4/'search2-vs-v6-seed62041-seat0.json.gz', v4/'search2-vs-lacoz-seed62044-seat0.json.gz', v4/'search2-vs-lacoz-seed62046-seat0.json.gz', V6/'confirm2/candidate-vs-league3m-seed40016-seat1.json.gz']
    assert len(paths)==20
    save(directory/'manifest.json', {'as_of':now(),'games':[{'path':rel(p),'sha256':sha(p)} for p in paths], 'selection':'First16 old v6 technical fixtures plus3 original v4 failures and original v6 emergency; no outcome-based search', 'source_sha256':sha(OUT/'package-attempt1/bot.cpp')})
    old=Native(V6/'build/attempt2/quantized.dylib'); new=Native(build_dir()/'candidate.dylib')
    roots=streams=hidden=forced=nonbaseline=0; results=[]; caps=[]; baseline_max=0; delayed_inputs=None; delayed_expected=None
    try:
        for index,path in enumerate(paths):
            record=read(path); sim=Simulator(record['map']); inputs=[[],[]]; expected=[[],[]]
            try:
                count=len(record['decisions']) + (1 if record['errors'] else 0)
                for turn in range(count):
                    before=sim.state()
                    for p in (0,1):
                        observation=LEAGUE.league_observation(sim.ptr,p,int(turn==0)); inputs[p].append(observation)
                        full=LEAGUE.league_observation(sim.ptr,p,1)
                        restored=new.lib.ds_restore(full,turn,p); assert restored,new.lib.ds_error()
                        assert json.loads(restored)==before; hidden+=1
                        a,ast=old.act(sim,p); b,bst=new.act(sim,p)
                        assert a==b and invariants(ast)==invariants(bst),(index,turn,p,'Unlimited policy changed')
                        assert bst['baseline_complete']==1 and sim.state()==before
                        expected[p].append(a); roots+=1
                        if turn in (count//2,count-1) or (index==19 and turn==26):
                            baseline,base=new.act(sim,p,count=1); baseline_max=max(baseline_max,base['baseline_us'])
                            detail=new.lib.ds_contract(new.ptr,sim.ptr,p,full); assert detail,new.lib.ds_error()
                            detail=json.loads(detail); nonbaseline+=sum(x['selected']>0 for x in detail['caps'])
                            force=[]
                            for ms,cap,elapsed in [(0,1,0),(16,20000,17774.5),(16,20000,30000),(.000001,20000,0)]:
                                action,st=new.act(sim,p,ms=ms,cap=cap,elapsed=elapsed)
                                assert action==baseline and st['baseline_complete']==1 and not st['emergency']
                                assert st['generated']==1 and st['selected']==0 and st['stopped']==1
                                force.append({'ms':ms,'cap':cap,'elapsed_us':elapsed,'action':action,'stats':st});forced+=1
                            caps.append({'game':index,'turn':turn,'seat':p,'greedy':baseline,'prefix_contract':detail,'forced':force})
                            if index==19 and turn==26 and p==1:
                                delayed_inputs=list(inputs[p]);delayed_expected=baseline
                        assert sim.state()==before
                    if turn<len(record['decisions']):sim.step(record['decisions'][turn]['actions'])
                for p in (0,1):
                    for label,binary in [('original_b9',V6/'build/attempt2/candidate-diagnostic'),('repaired',build_dir()/'diagnostic')]:
                        command=[str(binary),'0','0','4']; result=subprocess.run(command,input=b''.join(inputs[p]),capture_output=True,timeout=60)
                        actual=result.stdout.decode().splitlines()
                        stored(directory/f'game{index:02d}-seat{p}-{label}.json.gz',{'command':command,'returncode':result.returncode,'expected':expected[p],'actual':actual,'stderr':result.stderr.decode()})
                        assert result.returncode==0 and actual==expected[p],(index,p,label)
                        streams+=len(actual)
                results.append({'source':rel(path),'roots':count*2,'original_errors':record['errors'],'passed':True})
                print(json.dumps({'stage':'contracts','games':index+1,'roots':roots,'seconds':time.monotonic()-began}),flush=True)
            finally:sim.close()
        assert nonbaseline>0 and delayed_inputs and delayed_expected!='WAIT'
        injection=delayed(directory,delayed_inputs,delayed_expected)
    finally:old.close();new.close()
    save(directory/'cap-contracts.json',caps);save(directory/'games.json',results)
    save(OUT/'contracts.json',{'as_of':now(),'passed':True,'saved_games':20,'roots':roots,'stream_commands':streams,'hidden_restore_roots':hidden,'forced_baseline_cases':forced,'nonbaseline_partial_stops':nonbaseline,'baseline_us_max_sample':baseline_max,'delayed_input_tests':injection,'seconds':time.monotonic()-began,'source_sha256':sha(OUT/'package-attempt1/bot.cpp'),'sources':sources(),'budget':budget()})

if __name__=='__main__':main()
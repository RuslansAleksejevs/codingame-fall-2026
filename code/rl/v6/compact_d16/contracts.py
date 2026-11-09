"""Saved-game technical contracts, never evidence of fresh strength."""
import ctypes as C
import gzip
import subprocess
import numpy as np
from common import *
from package import function,compile_one,emit
from rl.data.replays import read
from rl.sim.native import Simulator
from rl.league.rollout import LIB as LEAGUE

EXTRA=r'''
extern "C" const char* ds_logits(void* pointer,void* state,int player){
    try{auto& search=*static_cast<deadline::Search*>(pointer);auto& root=*static_cast<rl::State*>(state);
        rl::Decoder d(root,player,2);std::vector<rl::Candidate> choices;
        for(auto& t:root.ts)if(t->owner==player){auto cs=d.spend(t);choices.insert(choices.end(),cs.begin(),cs.end());}
        for(int a=0;a<root.n;++a)if(d.available[a]>0){choices.push_back({0,a,a,nullptr});
            for(int b=0;b<root.n;++b)if(root.adj[a][b])choices.push_back({1,a,b,nullptr});}
        std::ostringstream out;out<<'[';bool first=true;
        const rl::FastNetwork* nets[]={search.policy.get(),search.value.get(),search.responses[0].get(),search.responses[1].get(),search.responses[2].get()};
        for(const auto& c:choices){auto x=d.features(c);for(auto net:nets){float v=net->evaluate(x);
            if(!std::isfinite(v))throw std::runtime_error("Nonfinite logit");
            unsigned int bits;std::memcpy(&bits,&v,4);if(!first)out<<',';first=false;out<<bits;}}
        out<<']';result=out.str();return result.c_str();
    }catch(const std::exception& e){error=e.what();return nullptr;}
}
'''

def build_apis(package):
    target=OUT/'contract-build';target.mkdir(exist_ok=False)
    old=(V5CODE/'api.cpp').read_text();old='\n'.join(line for line in old.splitlines() if not line.startswith('#include'))
    contracts=(V5CODE/'contracts.cpp').read_text().replace('#include "api.cpp"','')
    sample=function((ROOT/'code/rl/search/search.hpp').read_text(),'std::string sampled(')
    for label,path in [('quantized',ROOT/package['source']),('fp32',OUT/'package-attempt2/b32/bot.cpp')]:
        value='#define main packaged_program_main\n#include "'+str(path.relative_to(ROOT))+'"\n#undef main\n'
        value+='namespace searchpilot{'+sample+'}\n'+old+contracts+EXTRA
        source=target/(label+'.cpp');emit(source,value)
        compile_one(source,build_dir()/(label+'.dylib'),'compile-'+label+'-api',['-shared','-fPIC','-pthread','-I.'])
    source=target/'reference.cpp';emit(source,'#include <cstring>\n#include "code/rl/v5/deadline_search/contracts.cpp"\n'+EXTRA)
    compile_one(source,build_dir()/'reference.dylib','compile-reference-api',['-shared','-fPIC','-pthread','-I.'])

class Native:
    def __init__(self,path,weights):
        self.lib=C.CDLL(str(path));lib=self.lib
        lib.ds_new.argtypes=[C.c_char_p]*5;lib.ds_new.restype=C.c_void_p
        lib.ds_delete.argtypes=[C.c_void_p];lib.ds_error.restype=C.c_char_p
        lib.ds_act.argtypes=[C.c_void_p,C.c_void_p,C.c_int,C.c_double,C.c_int,C.c_int,C.c_double];lib.ds_act.restype=C.c_char_p
        lib.ds_stats.argtypes=[C.c_void_p];lib.ds_stats.restype=C.c_char_p
        lib.ds_restore.argtypes=[C.c_char_p,C.c_int,C.c_int];lib.ds_restore.restype=C.c_char_p
        lib.ds_contract.argtypes=[C.c_void_p,C.c_void_p,C.c_int,C.c_char_p];lib.ds_contract.restype=C.c_char_p
        lib.ds_logits.argtypes=[C.c_void_p,C.c_void_p,C.c_int];lib.ds_logits.restype=C.c_char_p
        self.ptr=lib.ds_new(*[str(w).encode() for w in weights]);assert self.ptr,lib.ds_error()
    def act(self,sim,p,cap=0,count=4,ms=0,elapsed=0):
        result=self.lib.ds_act(self.ptr,sim.ptr,p,ms,count,cap,elapsed);assert result,self.lib.ds_error()
        return result.decode(),json.loads(self.lib.ds_stats(self.ptr))
    def extra(self,name,sim,p,*args):
        result=getattr(self.lib,name)(self.ptr,sim.ptr,p,*args);assert result,self.lib.ds_error();return json.loads(result)
    def close(self):self.lib.ds_delete(self.ptr)

def invariant(stats):
    return {k:stats[k] for k in ('selected','generated','complete','transitions','stopped','emergency','forwards','choices','checks','values')}

def main():
    guard();package=json.loads((OUT/'package-attempt2.json').read_text());assert sha(ROOT/package['source'])==package['source_sha256']
    build_apis(package);directory=OUT/'contracts';directory.mkdir(exist_ok=False)
    paths=sorted((V5/'confirm1').glob('search-*.json.gz'),key=lambda p:(read(p)['seed'],p.name))[:100]
    assert len(paths)==100
    save(directory/'manifest.json',{'as_of':now(),'games':[{'path':rel(p),'sha256':sha(p)} for p in paths],
         'selection':'First100 v5 confirm1 search records sorted by(seed,filename); both seats of every trajectory, no outcome filtering',
         'source_sha256':package['source_sha256'],'scope':'Technical replay only; disclosed old maps','sources':sources()})
    quant=OUT/f'package-attempt2/b{package["selected_width"]}';qw=[quant/f'weights{i}.txt' for i in (0,1,0,2,3)]
    fw=[ACTOR,CRITIC,*ENEMIES]
    original=Native(build_dir()/'reference.dylib',fw);fp32=Native(build_dir()/'fp32.dylib',fw)
    textref=Native(build_dir()/'reference.dylib',qw);packed=Native(build_dir()/'quantized.dylib',qw)
    records=[];caps=[];logits=commands=changed=nonbaseline=stream_commands=hidden=0;max_logit_error=0.
    began=time.monotonic()
    try:
        for index,path in enumerate(paths):
            guard();record=read(path);assert not record['errors'];sim=Simulator(record['map']);inputs=[[],[]];expected=[[[],[]],[[],[]]]
            try:
                for turn,decision in enumerate(record['decisions']):
                    before=sim.state()
                    for p in (0,1):
                        observation=LEAGUE.league_observation(sim.ptr,p,int(turn==0));inputs[p].append(observation)
                        full_input=LEAGUE.league_observation(sim.ptr,p,1)
                        restored=packed.lib.ds_restore(full_input,turn,p);assert restored,packed.lib.ds_error()
                        assert json.loads(restored)==before;hidden+=1
                        a,ast=original.act(sim,p);b,bst=fp32.act(sim,p);c,cst=textref.act(sim,p);d,dst=packed.act(sim,p)
                        assert a==b and invariant(ast)==invariant(bst),(index,turn,p,'FP32 storage parity')
                        assert c==d and invariant(cst)==invariant(dst),(index,turn,p,'quantized packed parity')
                        assert sim.state()==before,(index,turn,p,'root mutation')
                        expected[0][p].append(a);expected[1][p].append(c);commands+=1;changed+=a!=c
                        if turn in (0,len(record['decisions'])//2):
                            aa=original.extra('ds_logits',sim,p);bb=fp32.extra('ds_logits',sim,p)
                            cc=textref.extra('ds_logits',sim,p);dd=packed.extra('ds_logits',sim,p)
                            assert aa==bb and cc==dd and len(aa)==len(cc)
                            va=np.asarray(aa,dtype=np.uint32).view(np.float32);vc=np.asarray(cc,dtype=np.uint32).view(np.float32)
                            assert np.isfinite(va).all() and np.isfinite(vc).all();logits+=len(aa)
                            max_logit_error=max(max_logit_error,float(np.max(np.abs(va-vc))) if len(va) else 0)
                        if turn==len(record['decisions'])//2:
                            detail=packed.extra('ds_contract',sim,p,full_input)
                            baseline,base=packed.act(sim,p,count=1)
                            for cap in sorted(set([1,base['forwards']+1,max(1,cst['forwards']//2),max(1,cst['forwards']-1)])):
                                ca,cs=textref.act(sim,p,cap=cap);da,ds=packed.act(sim,p,cap=cap)
                                assert ca==da and invariant(cs)==invariant(ds),(index,p,cap,'cap parity')
                            emergency,es=packed.act(sim,p,ms=16,cap=20000,elapsed=17000)
                            assert emergency=='WAIT' and es['emergency']==1
                            nonbaseline+=sum(x['selected']>0 for x in detail['caps'])
                            caps.append({'game':index,'turn':turn,'player':p,'contract':detail})
                    sim.step(decision['actions'])
                assert sim.state()['done'] and sim.state()['score']==[record['scores'][str(p)] for p in (0,1)]
                for p in (0,1):
                    for label,binary,weights,wanted in [('original',V5/'build/attempt1/bot',fw,expected[0][p]),('fp32',build_dir()/'fp32-diagnostic',None,expected[0][p]),('textref',V5/'build/attempt1/bot',qw,expected[1][p]),('packed',build_dir()/'candidate-diagnostic',None,expected[1][p])]:
                        cmd=[str(binary),*[str(w) for w in weights],'4','0'] if weights else [str(binary),'0','0','4']
                        result=subprocess.run(cmd,input=b''.join(inputs[p]),capture_output=True,timeout=60)
                        actual=result.stdout.decode().splitlines()
                        with (directory/f'game{index:03d}-seat{p}-{label}.json.gz').open('xb') as f:
                            f.write(gzip.compress(json.dumps(clean({'command':cmd,'returncode':result.returncode,'expected':wanted,'actual':actual,'stderr':result.stderr.decode()})).encode(),mtime=0))
                        assert result.returncode==0 and actual==wanted,(index,p,label,'stream parity')
                        stream_commands+=len(actual)
                records.append({'game':index,'source':rel(path),'seed':record['seed'],'turns':len(record['decisions']),'both_seats':True,'passed':True})
                print(json.dumps({'stage':'contracts','completed_games':len(records),'total_games':100,'commands':commands,'seconds':time.monotonic()-began}),flush=True)
            finally:sim.close()
    finally:
        for obj in (original,fp32,textref,packed):obj.close()
    assert nonbaseline>0,'No nonbaseline partial-stop case exercised'
    save(directory/'cap-contracts.json',caps);save(directory/'games.json',records)
    save(OUT/'contracts.json',{'as_of':now(),'passed':True,'saved_games':len(records),'both_seat_roots':commands,'full_stream_commands':stream_commands,'hidden_restore_roots':hidden,'bitexact_logit_pairs':logits,'original_quantized_changed_plans':changed,'maximum_original_quantized_logit_difference':max_logit_error,'nonbaseline_partial_stop_cases':nonbaseline,'cap_root_contracts':len(caps),'seconds':time.monotonic()-began,'sources':sources(),'budget':budget(),'scope':'Old exposed technical fixtures; no new strength evidence'})

if __name__=='__main__':main()
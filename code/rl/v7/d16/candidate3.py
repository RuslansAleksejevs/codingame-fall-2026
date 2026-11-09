"""One A3 implementation; preserve A1/A2 and run the fixed old-fixture contracts."""
import ctypes as C
import selectors
from common import *
from build import codec, replace_once, trimmed
from contracts import Native, stored
from rl.data.replays import read
from rl.sim.native import Simulator
from rl.league.rollout import LIB as LEAGUE

A2_SHA='d36aba4daa02580b1a20e5e1d000954cea330a852d8adbae1bb8f593572c9d15'
AMENDMENT=ROOT/'experiments/rl/2026-11-09-d16-live/AMENDMENT_A3.md'
BUILD=OUT/'build/attempt3'
TARGET=OUT/'package-attempt3'
ATTEMPT=sys.argv[1] if len(sys.argv)>1 else 'initial'

def prepare():
    guard();assert sha(OUT/'package-attempt2/bot.cpp')==A2_SHA
    old=(OUT/'package-attempt1/search-readable.hpp').read_text();new=old
    start=new.index('    std::string act_checked(');end=new.index('\n};',start)
    new=new[:start]+(CODE/'act_a3.inc').read_text().rstrip()+new[end:]
    new=replace_once(new,'Stats stats;','Stats stats;\n    std::vector<std::array<int,4>> boundaries;')
    new=replace_once(new,'int selected=0, generated=0, complete=0, transitions=0, stopped=0;',
                     'int selected=0, generated=0, complete=0, transitions=0, stopped=0, shallow_complete=0, selected_tier=0;')
    new=replace_once(new,'std::vector<double> values;','std::vector<double> values, shallow_values;')
    new=replace_once(new,'<<",\\\"complete\\\":"<<complete',
                     '<<",\\\"shallow_complete\\\":"<<shallow_complete<<",\\\"selected_tier\\\":"<<selected_tier<<",\\\"paired\\\":"<<(shallow_complete>=2||complete>=2)<<",\\\"complete\\\":"<<complete')
    new=replace_once(new,'o<<"]}";return o.str();',
                     'o<<"],\\\"shallow_values\\\":[";for(size_t i=0;i<shallow_values.size();++i){if(i)o<<\',\';o<<shallow_values[i];}o<<"]}";return o.str();')
    source=(OUT/'package-attempt2/bot.cpp').read_text()
    source=replace_once(source,codec.minify(trimmed(old)).strip(),codec.minify(trimmed(new)).strip())
    source='#include <ctime>\n'+source
    source=replace_once(source,'auto began=deadline::Clock::now();','auto began=deadline::Clock::now();auto cpu_began=std::clock();')
    source=replace_once(source,'total_us=deadline::us(began);','total_us=deadline::us(began);double process_cpu_us=1e6*double(std::clock()-cpu_began)/CLOCKS_PER_SEC;')
    source=replace_once(source,'<<",\\\"through_flush_us\\\":"<<total_us','<<",\\\"process_cpu_us\\\":"<<process_cpu_us<<",\\\"through_flush_us\\\":"<<total_us')
    TARGET.mkdir(exist_ok=True);BUILD.mkdir(exist_ok=True)
    for path,text in [(TARGET/'bot.cpp',source),(TARGET/'search-readable.hpp',new)]:
        if path.exists():assert path.read_text()==text,('Candidate change prohibited',rel(path))
        else:
            with path.open('x') as f:f.write(text)
    units=len(source.encode('utf-16-le'))//2;assert units<98000,units
    oldsearch=(ROOT/'code/rl/search/search.hpp').read_text();begin=oldsearch.index('std::string sampled(');opening=oldsearch.index('{',begin);depth=1;end=opening+1
    while depth:depth+=(oldsearch[end]=='{')-(oldsearch[end]=='}');end+=1
    oldapi='\n'.join(s for s in (V5CODE/'api.cpp').read_text().splitlines() if not s.startswith('#include'))
    api='#define main packaged_main\n#include "'+rel(TARGET/'bot.cpp')+'"\n#undef main\nnamespace searchpilot{'+oldsearch[begin:end]+'}\n'+oldapi+'\n'+(CODE/'contracts_a3.cpp').read_text()
    with (TARGET/('api-'+ATTEMPT+'.cpp')).open('x') as f:f.write(api)
    return units

def delayed(directory,inputs,expected):
    results=[]
    for delay in (.020,.030):
        name=f'delay{int(delay*1000)}';outputs=[]
        with (directory/(name+'-stderr.log')).open('xb') as err:
            proc=subprocess.Popen([str(BUILD/'candidate')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err)
            selector=selectors.DefaultSelector();selector.register(proc.stdout,selectors.EVENT_READ)
            try:
                for i,text in enumerate(inputs):
                    if i==len(inputs)-1:
                        first,rest=text.split(b' ',1);proc.stdin.write(first+b' ');proc.stdin.flush();time.sleep(delay);proc.stdin.write(rest)
                    else:proc.stdin.write(text)
                    proc.stdin.flush();assert selector.select(5),(name,i);outputs.append(proc.stdout.readline().decode().strip())
                proc.stdin.close();proc.wait(timeout=5);extra=proc.stdout.read();assert not extra
            finally:
                selector.close()
                if proc.poll() is None:proc.kill();proc.wait()
        stderr=(directory/(name+'-stderr.log')).read_text();records=[json.loads(s.split('=',1)[1]) for s in stderr.splitlines() if s.startswith('deadline=')]
        stored(directory/(name+'.json.gz'),{'inputs':[x.decode() for x in inputs],'outputs':outputs,'stderr':stderr,'returncode':proc.returncode})
        last=records[-1];assert proc.returncode==0 and len(records)==len(inputs)
        assert last['parse_us']>=delay*1e6-2500 and last['through_flush_us']<40000
        assert outputs[-1]==expected and last['search']['baseline_complete']==1 and last['search']['emergency']==0 and last['search']['selected_tier']==0
        results.append({'delay_ms':delay*1000,'timing':last,'output':outputs[-1],'greedy':expected})
    return results

def main():
    began=time.monotonic();units=prepare()
    for name,flags in [('candidate',[]),('diagnostic',['-DD16_DIAGNOSTIC']),('dump',['-DD16_WEIGHT_DUMP'])]:
        if not (BUILD/name).exists():
            run(['clang++','-std=c++17','-O3','-Wall','-Wextra','-Wpedantic',*flags,rel(TARGET/'bot.cpp'),'-o',rel(BUILD/name)],'a3-compile-'+name,90)
        else:assert json.loads((OUT/('a3-compile-'+name+'-command.json')).read_text())['returncode']==0
    run(['clang++','-std=c++17','-O3','-shared','-fPIC','-pthread','-I.',rel(TARGET/('api-'+ATTEMPT+'.cpp')),'-o',rel(BUILD/'candidate.dylib')],'a3-'+ATTEMPT+'-compile-api',90)
    expected_bytes=(V6/'package-attempt2/b9/expected-f32.bin').read_bytes();dump=subprocess.run([str(BUILD/'dump')],capture_output=True,timeout=20)
    assert dump.returncode==0 and dump.stdout==expected_bytes
    directory=OUT/'candidate3-contracts';directory.mkdir(exist_ok=False)
    previous=json.loads((OUT/'contracts/manifest.json').read_text());paths=[ROOT/r['path'] for r in previous['games']];assert len(paths)==20
    save(directory/'manifest.json',{'as_of':now(),'games':previous['games'],'source_sha256':sha(TARGET/'bot.cpp'),'reference_a2_sha256':A2_SHA,'amendment_sha256':sha(AMENDMENT)})
    old=Native(OUT/'build/attempt2/candidate.dylib');new=Native(BUILD/'candidate.dylib')
    new.lib.ds_a3_oracle.argtypes=[C.c_void_p,C.c_void_p,C.c_int];new.lib.ds_a3_oracle.restype=C.c_char_p
    roots=streams=forced=0;cap_records=[];oracle_records=[];games=[];delay_inputs=None;delay_expected=None
    try:
        for index,path in enumerate(paths):
            assert sha(path)==previous['games'][index]['sha256'];record=read(path);sim=Simulator(record['map']);inputs=[[],[]];plans=[[],[]]
            try:
                count=len(record['decisions'])+(1 if record['errors'] else 0)
                for turn in range(count):
                    before=sim.state()
                    for p in (0,1):
                        full=LEAGUE.league_observation(sim.ptr,p,1);inputs[p].append(LEAGUE.league_observation(sim.ptr,p,int(turn==0)))
                        restored=new.lib.ds_restore(full,turn,p);assert restored and json.loads(restored)==before
                        a,sa=old.act(sim,p);b,sb=new.act(sim,p)
                        assert a==b and sa['values']==sb['values'] and sa['complete']==sb['complete'] and sa['selected']==sb['selected'],(index,turn,p,'Unlimited D2 parity')
                        assert sb['baseline_complete']==1 and sb['shallow_complete']==sb['complete'];plans[p].append(a);roots+=1
                        oracle=new.lib.ds_a3_oracle(new.ptr,sim.ptr,p);assert oracle,new.lib.ds_error()
                        oracle_records.append({'game':index,'turn':turn,'seat':p,'independent':json.loads(oracle),'deep_values':sb['values'],'selected':sb['selected']})
                        if turn in (count//2,count-1) or (index==19 and turn==26):
                            baseline,base=new.act(sim,p,count=1);detail=new.lib.ds_contract(new.ptr,sim.ptr,p,full);assert detail,new.lib.ds_error();cases=[]
                            for ms,cap,elapsed in [(0,1,0),(16,20000,17774.5),(16,20000,30000),(.000001,20000,0)]:
                                action,st=new.act(sim,p,ms=ms,cap=cap,elapsed=elapsed)
                                assert action==baseline and st['baseline_complete']==1 and not st['emergency'] and st['selected_tier']==0 and st['stopped']==1
                                cases.append({'ms':ms,'cap':cap,'elapsed_us':elapsed,'action':action,'stats':st});forced+=1
                            cap_records.append({'game':index,'turn':turn,'seat':p,'prefix_contract':json.loads(detail),'forced':cases})
                            if index==19 and turn==26 and p==1:delay_inputs=list(inputs[p]);delay_expected=baseline
                        assert sim.state()==before
                    if turn<len(record['decisions']):sim.step(record['decisions'][turn]['actions'])
                for p in (0,1):
                    command=[str(BUILD/'diagnostic'),'0','0','4'];result=subprocess.run(command,input=b''.join(inputs[p]),capture_output=True,timeout=60)
                    actual=result.stdout.decode().splitlines();stderr=result.stderr.decode()
                    stored(directory/f'game{index:02d}-seat{p}-candidate3.json.gz',{'command':command,'returncode':result.returncode,'inputs':[x.decode() for x in inputs[p]],'expected_a2':plans[p],'actual':actual,'stderr':stderr})
                    assert result.returncode==0 and actual==plans[p];streams+=len(actual)
                    records=[json.loads(s.split('=',1)[1]) for s in stderr.splitlines() if s.startswith('deadline=')]
                    assert len(records)==len(actual) and all(r['process_cpu_us']>=0 for r in records)
                games.append({'path':rel(path),'roots':count*2,'passed':True});print(json.dumps({'stage':'a3-contracts','games':index+1,'roots':roots,'seconds':time.monotonic()-began}),flush=True)
            finally:sim.close()
        assert delay_inputs and delay_expected!='WAIT';injections=delayed(directory,delay_inputs,delay_expected)
    finally:old.close();new.close()
    save(directory/'oracle.json',oracle_records);save(directory/'caps.json',cap_records);save(directory/'games.json',games)
    caps=[c for r in cap_records for c in r['prefix_contract']['caps']]
    coverage={'shallow_selected':sum(c['tier']==1 and c['selected']>0 for c in caps),'deep_selected':sum(c['tier']==2 and c['selected']>0 for c in caps),'deep_baseline_only':sum(c['deep_complete']==1 and c['shallow_complete']>=2 for c in caps),'incomplete_shallow':sum(c['shallow_complete']==0 for c in caps)}
    assert all(coverage.values()),coverage
    assert roots==streams==1156 and sha(OUT/'package-attempt2/bot.cpp')==A2_SHA
    for p,h in json.loads((OUT/'candidate2-package.json').read_text())['binaries'].items():assert sha(ROOT/p)==h
    package={'as_of':now(),'passed':True,'source':rel(TARGET/'bot.cpp'),'source_sha256':sha(TARGET/'bot.cpp'),'source_utf16':units,'source_bytes':(TARGET/'bot.cpp').stat().st_size,'decoded_bytes':len(expected_bytes),'decoded_sha256':hashlib.sha256(dump.stdout).hexdigest(),'reference_a2_sha256':A2_SHA,'amendment':rel(AMENDMENT),'amendment_sha256':sha(AMENDMENT),'timed_policy_change':'Complete three-model depth1 incumbent then original depth2; same16ms cumulative origin and20000cap','contracts':{'saved_games':20,'both_seat_roots':roots,'actual_stream_commands':streams,'forced_baseline_cases':forced,'oracle_roots':len(oracle_records),'interruption_cases':len(caps),'coverage':coverage,'delayed_input':injections},'binaries':{rel(p):sha(p) for p in BUILD.iterdir() if p.is_file()},'implementation_bindings':{rel(p):sha(p) for p in [CODE/'candidate3.py',CODE/'act_a3.inc',CODE/'contracts_a3.cpp',TARGET/'search-readable.hpp']},'compiler':subprocess.run(['clang++','--version'],capture_output=True,text=True).stdout,'seconds':time.monotonic()-began,'budget':budget(),'protected':guard(),'platform_ready_for_fixed_tests':True,'local_96_game_guard_pending':True,'process_cpu_scope':'std::clock from first score token through stdout flush; excludes startup/initial map/pre-first-token/final stderr, not official chargedCPU'}
    save(OUT/'candidate3-package.json',package);print(json.dumps(package),flush=True)

if __name__=='__main__':main()
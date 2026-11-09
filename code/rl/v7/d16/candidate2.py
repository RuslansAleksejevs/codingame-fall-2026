"""A2: exact GCC-O3 prelude only, plus old/new numerical and stop contracts."""
import gzip
from common import *
from contracts import Native, invariants, stored
from rl.data.replays import read
from rl.sim.native import Simulator
from rl.league.rollout import LIB as LEAGUE

OLD_SHA='aba2d6f2ae4bcd92eb79f38fd6bd643be9973b714b135c7b532a3e9fd9a80701'

def main():
    guard();began=time.monotonic();old_cpp=OUT/'package-attempt1/bot.cpp';assert sha(old_cpp)==OLD_SHA
    old_package=json.loads((OUT/'package.json').read_text())
    old_build=build_dir();new_build=OUT/'build/attempt2';target=OUT/'package-attempt2'
    target.mkdir(exist_ok=False);new_build.mkdir(exist_ok=False)
    reference=(ROOT/'submissions/ppo-v2-league3m.cpp').read_text()
    begin=reference.index('#if defined(__GNUC__) && !defined(__clang__)\n')
    end=reference.index('#endif\n',begin)+len('#endif\n');prelude=reference[begin:end]
    assert prelude=='#if defined(__GNUC__) && !defined(__clang__)\n#pragma GCC optimize("O3")\n#endif\n'
    body=old_cpp.read_bytes();source=prelude.encode()+body;cpp=target/'bot.cpp'
    with cpp.open('xb') as f:f.write(source)
    assert cpp.read_bytes()[len(prelude.encode()):]==body
    units=len(source.decode().encode('utf-16-le'))//2;assert units<=98000
    compiler=subprocess.run(['clang++','--version'],capture_output=True,text=True).stdout
    assert compiler==old_package['versions']['compiler'],'Local compiler version changed'
    run(['clang++','-std=c++17','-O3','-Wall','-Wextra','-Wpedantic','-DD16_DIAGNOSTIC',rel(old_cpp),'-o',rel(new_build/'candidate1-control-diagnostic')],'a2-compile-unchanged-control',180)
    for name,flags in [('candidate',[]),('diagnostic',['-DD16_DIAGNOSTIC']),('dump',['-DD16_WEIGHT_DUMP'])]:
        run(['clang++','-std=c++17','-O3','-Wall','-Wextra','-Wpedantic',*flags,rel(cpp),'-o',rel(new_build/name)],'a2-compile-'+name,180)
    api=(OUT/'package-attempt1/api.cpp').read_text();old_include=rel(old_cpp);assert api.count(old_include)==1
    with (target/'api.cpp').open('x') as f:f.write(api.replace(old_include,rel(cpp)))
    run(['clang++','-std=c++17','-O3','-shared','-fPIC','-pthread','-I.',rel(target/'api.cpp'),'-o',rel(new_build/'candidate.dylib')],'a2-compile-api',180)
    dump=subprocess.run([str(new_build/'dump')],capture_output=True,timeout=20)
    expected=(V6/'package-attempt2/b9/expected-f32.bin').read_bytes();assert dump.returncode==0 and dump.stdout==expected
    directory=OUT/'candidate2-contracts';directory.mkdir(exist_ok=False)
    previous=json.loads((OUT/'contracts/manifest.json').read_text());paths=[ROOT/r['path'] for r in previous['games']]
    assert len(paths)==20
    save(directory/'manifest.json',{'as_of':now(),'original_manifest_sha256':sha(OUT/'contracts/manifest.json'),'old_source_sha256':OLD_SHA,'new_source_sha256':sha(cpp),'amendment_sha256':sha(OUT/'AMENDMENT_A2.md'),'games':previous['games'],'scope':'Old disclosed technical fixtures only, no new games or strength inference'})
    old=Native(old_build/'candidate.dylib');new=Native(new_build/'candidate.dylib')
    roots=streams=forced=nonbaseline=0;cap_records=[];game_records=[]
    try:
        for index,path in enumerate(paths):
            assert sha(path)==previous['games'][index]['sha256']
            record=read(path);sim=Simulator(record['map']);inputs=[[],[]];expected_plans=[[],[]]
            try:
                count=len(record['decisions'])+(1 if record['errors'] else 0)
                for turn in range(count):
                    before=sim.state()
                    for p in (0,1):
                        text=LEAGUE.league_observation(sim.ptr,p,int(turn==0));full=LEAGUE.league_observation(sim.ptr,p,1);inputs[p].append(text)
                        restored=new.lib.ds_restore(full,turn,p);assert restored and json.loads(restored)==before
                        a,ast=old.act(sim,p);b,bst=new.act(sim,p)
                        assert a==b and invariants(ast)==invariants(bst) and ast['baseline_complete']==bst['baseline_complete']==1
                        expected_plans[p].append(a);roots+=1
                        if turn in (count//2,count-1):
                            baseline,base=new.act(sim,p,count=1)
                            da=old.lib.ds_contract(old.ptr,sim.ptr,p,full);assert da,old.lib.ds_error();da=json.loads(da)
                            db=new.lib.ds_contract(new.ptr,sim.ptr,p,full);assert db,new.lib.ds_error();db=json.loads(db)
                            assert da==db;nonbaseline+=sum(x['selected']>0 for x in db['caps'])
                            cases=[]
                            for ms,cap,elapsed in [(0,1,0),(16,20000,17774.5),(16,20000,30000),(.000001,20000,0)]:
                                aa,sa=old.act(sim,p,ms=ms,cap=cap,elapsed=elapsed);bb,sb=new.act(sim,p,ms=ms,cap=cap,elapsed=elapsed)
                                assert aa==bb==baseline and invariants(sa)==invariants(sb)
                                assert sa['baseline_complete']==sb['baseline_complete']==1 and sa['emergency']==sb['emergency']==0
                                cases.append({'ms':ms,'cap':cap,'elapsed_us':elapsed,'action':bb,'old_stats':sa,'new_stats':sb});forced+=1
                            cap_records.append({'game':index,'turn':turn,'seat':p,'prefix_contract':db,'forced':cases})
                        assert sim.state()==before
                    if turn<len(record['decisions']):sim.step(record['decisions'][turn]['actions'])
                for p in (0,1):
                    for label,binary in [('candidate1',new_build/'candidate1-control-diagnostic'),('candidate2',new_build/'diagnostic')]:
                        command=[str(binary),'0','0','4'];result=subprocess.run(command,input=b''.join(inputs[p]),capture_output=True,timeout=60)
                        actual=result.stdout.decode().splitlines()
                        stored(directory/f'game{index:02d}-seat{p}-{label}.json.gz',{'command':command,'returncode':result.returncode,'inputs':[x.decode() for x in inputs[p]],'expected':expected_plans[p],'actual':actual,'stderr':result.stderr.decode()})
                        assert result.returncode==0 and actual==expected_plans[p];streams+=len(actual)
                game_records.append({'source':rel(path),'sha256':sha(path),'roots':count*2,'original_errors':record['errors'],'passed':True})
                print(json.dumps({'stage':'candidate2-contracts','games':index+1,'roots':roots,'seconds':time.monotonic()-began}),flush=True)
            finally:sim.close()
    finally:old.close();new.close()
    assert nonbaseline>0
    save(directory/'cap-contracts.json',cap_records);save(directory/'games.json',game_records)
    for p,h in old_package['binaries'].items():assert sha(ROOT/p)==h,('Original candidate1 binary changed',p)
    package={'as_of':now(),'passed':True,'source':rel(cpp),'source_sha256':sha(cpp),'source_utf16':units,'source_bytes':len(source),'old_source_sha256':OLD_SHA,'body_exactly_equal':True,'only_change':'Exact guarded GCC optimize O3 prelude copied from protected submitted league3m','prelude':prelude,'decoded_bytes':len(expected),'decoded_sha256':hashlib.sha256(dump.stdout).hexdigest(),'codec_exact':True,
        'same_local_compiler_flags':['clang++','-std=c++17','-O3','-Wall','-Wextra','-Wpedantic'],'compiler':compiler,'fresh_unchanged_control_diagnostic_sha256':sha(new_build/'candidate1-control-diagnostic'),
        'binary_equal_to_candidate1':{name:sha(new_build/name)==sha(old_build/name) for name in ('candidate','diagnostic','dump','candidate.dylib')},
        'binaries':{rel(p):sha(p) for p in new_build.iterdir() if p.is_file()},'contracts':{'saved_games':20,'both_seat_roots':roots,'stream_commands':streams,'forced_old_new_baseline_cases':forced,'nonbaseline_partial_stop_cases':nonbaseline,'hidden_restore_immutable_legal_prefix_pass':True},
        'source_and_protocol_bindings':{rel(p):sha(p) for p in [CODE/'candidate2.py',OUT/'AMENDMENT_A2.md',OUT/'RUNTIME_DIAGNOSIS.md',OUT/'final-freeze.json',OUT/'poststop-decision.json']},'seconds':time.monotonic()-began,'protected':guard(),'budget':budget(),'platform_flags':'UNKNOWN; actual acceleration must be established by coordinator-only same-fixture official tests','new_strength_claim':False}
    save(OUT/'candidate2-package.json',package);print(json.dumps(package),flush=True)

if __name__=='__main__':main()
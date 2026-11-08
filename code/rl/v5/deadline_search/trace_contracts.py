"""Tiny pre-dataset actual-generator trace and exact transition contract."""
from student_common import *
from rl.data.replays import read
from rl.sim.native import Simulator
from rl.league.rollout import LIB as LEAGUE


def main():
    teacher_guard();STUDENT.mkdir(exist_ok=False)
    run(['clang++','-std=c++17','-O3','-shared','-fPIC','-pthread',rel(CODE/'trace.cpp'),'-o',rel(build_dir()/'student-trace.dylib')],'student-trace-build')
    trace=Trace();fixtures=[]
    for seed,opp,turn in [(62041,'v6',23),(62044,'lacoz',23),(62046,'lacoz',2)]:
        for p in (0,1):fixtures.append((seed,opp,turn,p))
    for item in json.loads((OUT/'changed-plan-contracts.json').read_text())['roots']:
        fixtures.append((item['seed'],'v6' if item['seed']==62041 else 'lacoz',item['turn'],item['player']))
    oracle=subprocess.Popen([str(java_home()/'bin/java'),'-Xmx1g','-cp',classpath(),'Oracle'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    records=[];total_groups=total_rows=0
    old_control=trace.native.lib.search_new(*[str(p).encode() for p in [ACTOR,CRITIC,*ENEMIES]],2,1,0)
    try:
        for index,(seed,opp,turn,p) in enumerate(fixtures):
            record=read(OLD/f'confirm3/search2-vs-{opp}-seed{seed}-seat0.json.gz');sim=Simulator(record['map']);inputs=[]
            prefix=[d['actions'] for d in record['decisions'][:turn]]
            try:
                for t in range(turn+1):
                    inputs.append(LEAGUE.league_observation(sim.ptr,p,int(t==0)))
                    if t<turn:sim.step(prefix[t])
                lines,logs=teacher_stream(inputs,f'contract-{index}')
                selected=logs[-1]['search']['selected'];assert not logs[-1]['search']['emergency']
                meta,x,offsets,labels=trace.capture(sim,p,selected,lines[-1])
                enemy=trace.native.lib.search_act(old_control,sim.ptr,1-p).decode()
                pair=[None,None];pair[p]=lines[-1];pair[1-p]=enemy
                oracle.stdin.write(json.dumps(dict(record['map'],actions=prefix+[pair]))+'\n');oracle.stdin.flush()
                expected=json.loads(oracle.stdout.readline())[-1];sim.step(pair);actual=sim.state()
                assert all(actual[k]==expected[k] for k in ('turn','score','units','edges','triangles','done')) and actual['errors']==[0,0]
                records.append({'seed':seed,'turn':turn,'player':p,'selected':selected,'meta':meta,
                    'one_step_java_exact':True,'next_state_sha256':hashlib.sha256(json.dumps(actual,sort_keys=True).encode()).hexdigest()})
                total_groups+=len(labels);total_rows+=len(x)
            finally:sim.close()
    finally:
        trace.native.lib.search_delete(old_control);trace.close();oracle.stdin.close();oracle.wait(timeout=30)
    save(STUDENT/'trace-contracts.json',{'as_of':now(),'passed':True,'roots':len(records),'groups':total_groups,'candidate_rows':total_rows,
        'records':records,'old_action_string_labels_used':False,'style_rewritten':False,'targets':'Legal one-hot mass1',
        'generator_trace_library_sha256':sha(build_dir()/'student-trace.dylib'),'sources':sources(),
        'protocol_sha256':sha(OUT/'STUDENT_PROTOCOL.md'),'teacher_freeze_sha256':sha(OUT/'freeze.json'),'budget':budget()})
    print(json.dumps({'passed':True,'roots':len(records),'groups':total_groups,'candidate_rows':total_rows}),flush=True)


if __name__=='__main__':main()
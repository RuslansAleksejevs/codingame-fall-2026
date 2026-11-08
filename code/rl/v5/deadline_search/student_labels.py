"""Exact actual-generator targets from a fixed complete-game collection."""
from student_common import *
from rl.data.replays import read
from rl.sim.native import Simulator
from rl.league.rollout import LIB as LEAGUE


def label(name):
    teacher_guard();directory=STUDENT/name
    verification=json.loads((STUDENT/(name+'-verification.json')).read_text())
    assert verification['passed'] and not verification['excluded']
    rows=[json.loads(s) for s in (directory/'matches.jsonl').read_text().splitlines()]
    max_roots=160 if name=='development' else 240
    trace=Trace();features=[];offsets=[0];targets=[];root_offsets=[0];roots=[];calls=0
    oracle=subprocess.Popen([str(java_home()/'bin/java'),'-Xmx1g','-cp',classpath(),'Oracle'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    prior_rows=sum(json.loads(p.read_text())['candidate_rows'] for p in STUDENT.glob('labels-*.json'))
    try:
        for row in rows:
            assert row['valid'] and not row['returncode'] and not row['own_action_errors'] and not row['opponent_action_errors']
            stem=f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}'
            path=directory/(stem+'.json.gz');record=read(path);p=row['seat'];inputs=[]
            sim=Simulator(record['map'])
            try:
                for turn,decision in enumerate(record['decisions']):
                    inputs.append(LEAGUE.league_observation(sim.ptr,p,int(turn==0)))
                    sim.step(decision['actions'])
            finally:sim.close()
            outputs,logs=teacher_stream(inputs,name+'-'+stem);calls+=len(inputs)
            sim=Simulator(record['map']);prefix=[]
            try:
                for turn,decision in enumerate(record['decisions']):
                    if turn in SELECTED_TURNS:
                        search=logs[turn]['search'];assert not search['emergency']
                        selected=search['selected'];meta,x,off,y=trace.capture(sim,p,selected,outputs[turn])
                        assert len(roots)<max_roots and prior_rows+offsets[-1]+len(x)<=3000000
                        pair=list(decision['actions']);pair[p]=outputs[turn]
                        oracle.stdin.write(json.dumps(dict(record['map'],actions=prefix+[pair]))+'\n');oracle.stdin.flush()
                        expected=json.loads(oracle.stdout.readline())[-1]
                        counter=Simulator(record['map'])
                        try:
                            for actions in prefix:counter.step(actions)
                            counter.step(pair);actual=counter.state()
                            assert actual['errors']==[0,0] and all(actual[k]==expected[k] for k in ('turn','score','units','edges','triangles','done'))
                        finally:counter.close()
                        features.append(x);offsets.extend((off[1:]+offsets[-1]).tolist());targets.extend(y.tolist());root_offsets.append(len(targets))
                        roots.append({'seed':row['seed'],'seat':p,'turn':turn,'record':rel(path),'record_sha256':sha(path),
                            'selected':selected,'changed':selected!=0,'command':outputs[turn],'trace':meta,
                            'groups':len(y),'candidate_rows':len(x),'counterfactual_java_exact':True,
                            'teacher_stream':rel(STUDENT/'teacher-streams'/(name+'-'+stem+'.json'))})
                    sim.step(decision['actions']);prefix.append(decision['actions'])
            finally:sim.close()
            print(json.dumps({'stage':'labels-'+name,'games':len({r['record'] for r in roots}),'roots':len(roots),'groups':len(targets),'rows':offsets[-1]}),flush=True)
    finally:trace.close();oracle.stdin.close();oracle.wait(timeout=30)
    assert roots and len(roots)<=max_roots
    destination=STUDENT/('labels-'+name+'.npz');assert not destination.exists()
    np.savez_compressed(destination,x=np.concatenate(features),offsets=np.asarray(offsets,dtype=np.int64),
        labels=np.asarray(targets,dtype=np.int64),root_offsets=np.asarray(root_offsets,dtype=np.int64),
        changed=np.asarray([r['changed'] for r in roots],dtype=np.bool_))
    save(STUDENT/('labels-'+name+'.json'),{'as_of':now(),'passed':True,'roots':len(roots),'groups':len(targets),
        'candidate_rows':offsets[-1],'changed_roots':sum(r['changed'] for r in roots),'teacher_inference_calls':calls,
        'counterfactual_java_checks':len(roots),'dataset_sha256':sha(destination),'records':roots,
        'feature_dtype':'float32','style':2,'feature_rewriting':False,'source_sha256':sha(Path(__file__)),
        'trace_source_sha256':sha(CODE/'trace.cpp'),'protocol_sha256':sha(OUT/'STUDENT_PROTOCOL.md'),'budget':budget()})


if __name__=='__main__':label(sys.argv[1])
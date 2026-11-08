"""Reconstruct every stored target without changing or expanding the dataset."""
from student_common import *
from rl.data.replays import read
from rl.sim.native import Simulator


def main():
    teacher_guard();freeze=json.loads((STUDENT/'data-training-freeze.json').read_text())
    for path,digest in freeze['identities'].items():assert sha(ROOT/path)==digest
    trace=Trace();results=[];total_calls=0
    try:
        for name in ('anchor','development','current'):
            meta=json.loads((STUDENT/('labels-'+name+'.json')).read_text());path=STUDENT/('labels-'+name+'.npz')
            assert meta['dataset_sha256']==sha(path);bank=dict(np.load(path));by_record={}
            for index,root in enumerate(meta['records']):by_record.setdefault(root['record'],[]).append((index,root))
            checked=0
            for record_path,roots in by_record.items():
                record=read(ROOT/record_path);assert all(sha(ROOT/record_path)==r['record_sha256'] for _,r in roots)
                p=roots[0][1]['seat'];stream=json.loads((ROOT/roots[0][1]['teacher_stream']).read_text())
                logs=[json.loads(s.split('=',1)[1]) for s in stream['stderr'].splitlines() if s.startswith('deadline=')]
                assert len(logs)==len(record['decisions'])==len(stream['outputs'])
                assert all(not d['search']['emergency'] for d in logs),'Emergency even on an unlabelled prefix is a blocker'
                total_calls+=len(logs);chosen={r['turn']:(i,r) for i,r in roots}
                assert sorted(chosen)==[t for t in SELECTED_TURNS if t<len(record['decisions'])],'Missing or extra target root'
                sim=Simulator(record['map'])
                try:
                    for turn,decision in enumerate(record['decisions']):
                        if turn in chosen:
                            i,r=chosen[turn];assert stream['outputs'][turn]==r['command'] and logs[turn]['search']['selected']==r['selected']
                            regenerated,x,offsets,labels=trace.capture(sim,p,r['selected'],r['command'])
                            a,b=bank['root_offsets'][i:i+2];first,last=bank['offsets'][a],bank['offsets'][b]
                            assert np.array_equal(x.view(np.uint32),bank['x'][first:last].view(np.uint32))
                            assert np.array_equal(offsets,bank['offsets'][a:b+1]-first) and np.array_equal(labels,bank['labels'][a:b])
                            assert regenerated['feature_sha256']==r['trace']['feature_sha256'];checked+=1
                        sim.step(decision['actions'])
                finally:sim.close()
            assert checked==meta['roots'];results.append({'bank':name,'roots':checked,'groups':meta['groups'],
                'candidate_rows':meta['candidate_rows'],'dataset_sha256':sha(path),'exact_reconstructed_float32_and_targets':True})
    finally:trace.close()
    save(STUDENT/'label-integrity-audit.json',{'as_of':now(),'passed':True,'banks':results,'teacher_calls_checked':total_calls,
        'new_targets_generated':0,'dataset_changes':0,'all_teacher_prefix_emergencies':0,'budget':budget(),
        'source_sha256':sha(Path(__file__))})
    print(json.dumps({'passed':True,'roots':sum(r['roots'] for r in results),'teacher_calls_checked':total_calls}),flush=True)


if __name__=='__main__':main()
"""Select solely by the fixed technical gate, before confirmation generation."""
from common import *
from analyze import timing
from panel import schedule
from verify import verify


def main():
    guard()
    run([sys.executable,'-B',rel(CODE/'test_analyze.py')],'gate-tests')
    # Retain the earlier verifier attempts, and bind final strict tail checks.
    for stage in ('regression','development'):
        verify(stage,stage+'-final-verification')
    rows=[]
    for stage in ('regression','development'):
        rows += [json.loads(s) for s in (OUT/stage/'matches.jsonl').read_text().splitlines()]
    assert len(rows)==54
    info=timing(rows)
    passed=(all(r['valid'] and r['returncode']==0 and not r['own_action_errors'] for r in rows)
        and all(t['emergency']==0 and t['outputs']==t['raw_timing_turns'] and t['totals']['through_flush_us']['1']<40000 for t in info.values())
        and json.loads((OUT/'diagnostic/summary.json').read_text())['passed']
        and json.loads((OUT/'contracts.json').read_text())['passed']
        and json.loads((OUT/'changed-plan-contracts.json').read_text())['passed']
        and json.loads((OUT/'development-novelty.json').read_text())['passed'])
    build=json.loads((OUT/'build-manifest.json').read_text())
    for path,digest in build['sources'].items():
        if path.endswith(('.cpp','.hpp','.java')):assert sha(ROOT/path)==digest,'Compiled source changed: '+path
    for path,digest in build['binaries'].items():assert sha(ROOT/path)==digest
    save(OUT/'technical-decision.json',{'as_of':now(),'passed':bool(passed),'timing':info,'games':54,
        'selection_rule':'D16 only; all predeclared correctness/timing checks, no winrate selection.',
        'verifications':{stage:sha(OUT/(stage+'-final-verification.json')) for stage in ('regression','development')},
        'retained_verifier_failure':'regression-verify.log','budget':budget()})
    assert passed,'Technical gate failed; no confirmation'
    deps={}
    for stage in ('regression','development'):
        deps.update(json.loads((OUT/stage/'manifest.json').read_text())['dependency_sha256'])
    public=ROOT/'code/opponents/public'
    for folder,filename in [('lacoz-7f190183','bot.py'),('khoufou-372c1cd6','Player.java'),('khoufou-070bc128','Player.java')]:
        path=public/folder/filename;deps[rel(path)]=sha(path)
    for p in build_dir().rglob('*.class'):deps[rel(p)]=sha(p)
    for path,digest in deps.items():assert sha(ROOT/path)==digest
    save(OUT/'freeze.json',{'as_of':now(),'classification':'PROJECT_REPORTED','candidate':'D16','designs_tested':1,
        'config':{'milliseconds_from_first_score_token':16,'max_forwards':20000,'proposals':4,'depth':2,
                  'temperatures':[.15,.35,.7],'margin':.02,'gamma':.995,'aggregation':'.5mean+.5minimum'},
        'sources':sources(),'weights':build['weights'],'binaries':build['binaries'],'dependencies':deps,
        'protected':guard(),'protocol_sha256':sha(OUT/'PROTOCOL.md'),'analyzer_sha256':sha(CODE/'analyze.py'),
        'gate_tests_sha256':sha(OUT/'gate-tests.log'),'technical_decision_sha256':sha(OUT/'technical-decision.json'),
        'schedule':schedule(list(range(70101,70141))), 'games':1120,'maps':40,'seats':[0,1],
        'confirmation_maps_generated':False,'global_final_opened':False,'budget':budget()})
    print(json.dumps({'technical_gate_passed':True,'freeze_sha256':sha(OUT/'freeze.json'),'games':1120}),flush=True)


if __name__=='__main__':main()
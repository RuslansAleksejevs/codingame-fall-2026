"""Additional post-stop evidence audit; frozen candidate/evaluator remain unchanged.

No new game, inference, map generation, retry, training or platform request.
"""
import contextlib
from collections import Counter
import numpy as np
from common import *
from analyze import read_rows, summarize
from panel import CANDIDATES, checked_freeze

def main():
    guard();frozen=checked_freeze();began=time.monotonic()
    v5=json.loads((V5/'freeze.json').read_text())
    refs={**v5['sources'],**v5['weights'],**v5['binaries'],**v5['dependencies']}
    reference_mismatches=[p for p,h in refs.items() if sha(ROOT/p)!=h]
    assert not reference_mismatches,reference_mismatches
    verifier=module('d16_poststop_verify',V5CODE/'verify.py')
    with (OUT/'poststop-replay.log').open('x') as log:
        with contextlib.redirect_stdout(log):verifier.verify('confirm2','confirm2-poststop-verification')
    rows,bindings,timing=read_rows(['confirm1','confirm2'])
    keys=[{k:r[k] for k in ('candidate','opponent','seed','seat')} for r in rows]
    assert keys==frozen['schedule'][:len(rows)] and len(rows)==359
    failures=[r for r in rows if r['own_failure']]
    assert len(failures)==1 and failures[0]['candidate']=='control' and failures[0]['seed']==72112 and failures[0]['opponent']=='lacoz' and failures[0]['seat']==0
    views=summarize(rows,list(range(72101,72141)))
    counts={c:{'games':sum(r['candidate']==c for r in rows),'raw_outcomes':dict(Counter(r['raw_outcome'] for r in rows if r['candidate']==c)),
        'technical_adjusted_outcomes':dict(Counter({0:'loss',.5:'draw',1:'win'}[r['points']] for r in rows if r['candidate']==c)),
        'own_failure_games':sum(r['candidate']==c and r['own_failure'] for r in rows),'opponent_failure_games':sum(r['candidate']==c and r['opponent_failure'] for r in rows),'emergency_games':sum(r['candidate']==c and r['emergency'] for r in rows)} for c in CANDIDATES}
    times={}
    for c,entries in timing.items():
        times[c]={'outputs_with_timing':len(entries),'baseline_complete_turns':sum(x['search'].get('baseline_complete',0) for x in entries),'emergency_turns':sum(x['search']['emergency'] for x in entries),'optional_stop_turns':sum(x['search']['stopped'] for x in entries),'changed_turns':sum(x['search']['selected']>0 for x in entries)}
        for field in ('parse_us','restore_us','optional_us','flush_us','through_flush_us'):
            values=[x[field] for x in entries if field in x]
            if values:times[c][field]={'p50':float(np.median(values)),'p95':float(np.quantile(values,.95)),'p99':float(np.quantile(values,.99)),'max':max(values)}
        baseline=[x['search']['baseline_us'] for x in entries];times[c]['baseline_us']={'p99':float(np.quantile(baseline,.99)),'max':max(baseline)}
    failure=json.loads((OUT/'confirm2/failure.json').read_text());r=failure['row'];stem='control-vs-lacoz-seed72112-seat0'
    raw=json.loads((OUT/'confirm2'/(stem+'-raw.json')).read_text())
    forensic={'as_of':now(),'game':failure['game'],'failed_program':'Unchanged greedy league3m through pinned v5 I/O wrapper, NOT repaired D16','actual_engine_timeout':True,'scores':[r['score'],r['opponent_score']],'own_action_errors':r['own_action_errors'],'last_recorded_turn':r['deadline_measurements'][-1],
        'accepted_outputs':[x for x in raw['outputs']['0'] if x],'all_own_stderr':[x for x in raw['errors']['0'] if x],'all_summaries':[x for x in raw['summaries'] if x],
        'accepted_output_count':r['own_output_count'],'timing_record_count':len(r['deadline_measurements']),'raw_sha256':sha(OUT/'confirm2'/(stem+'-raw.json')),
        'cause':'UNKNOWN. Last internal first-score-to-flush21.9147ms does not measure pre-first-score/scheduling/referee overhead. Do not infer parser/inference/OS blame. No rerun has been used to erase the actual timeout.'}
    save(OUT/'control-timeout-forensics.json',forensic)
    replay=[json.loads((OUT/p).read_text()) for p in ('confirm1-verification.json','confirm2-poststop-verification.json')]
    assert sum(x['clean_games'] for x in replay)==358 and sum(len(x['excluded']) for x in replay)==1
    report={'as_of':now(),'classification':'PROJECT_REPORTED','status':'STOPPED_INCOMPLETE_CONTROL_TIMEOUT','evidence_audit_passed':True,'full_final_passed':False,'planned_games':1200,'observed_games':359,'missing_games':841,
        'candidate_engine_failure_games':counts['candidate']['own_failure_games'],'candidate_emergency_turns':times['candidate']['emergency_turns'],'counts':counts,'timing':times,
        'replay':{'games':sum(x['clean_games'] for x in replay),'states':sum(x['states'] for x in replay),'transitions':sum(x['transitions'] for x in replay),'excluded':sum([x['excluded'] for x in replay],[])},
        'source_sha256':frozen['source_sha256'],'freeze_sha256':sha(OUT/'final-freeze.json'),'raw_bindings':bindings,'original_v5_reference_identity_count':len(refs),'original_v5_reference_mismatches':reference_mismatches,
        'map_exposure':{'generated':list(range(72101,72121)),'played':list(range(72101,72113)),'full_30game_maps':list(range(72101,72112)),'unopened':list(range(72121,72141))},
        'interpretation':'Descriptive partial paired estimates only, not a complete40-map final or passed historical/new gate. The stopped role is control, not D16. Early D16 technical readiness remains evidence; any authorized exploratory live decision must explicitly acknowledge this incomplete comparison and pass official tests.',
        'bootstrap':{'resamples':10000,'seed':20261109,'unit':'whole map/both seats'},'versions':{'python':sys.version,'numpy':np.__version__},'seconds':time.monotonic()-began,'budget':budget(),**views}
    save(OUT/'poststop-decision.json',report)
    print(json.dumps({'status':report['status'],'observed_games':359,'counts':counts,'replay':report['replay'],'all_gain':views['all_games']['external_gain'],'clean_gain':views['clean_paired']['external_gain'],'teacher_retention':views['clean_paired']['teacher_retention'],'direct_league3m':views['clean_paired']['direct_league3m'],'direct_b2m':views['clean_paired']['direct_b2m'],'candidate_timing':times['candidate'],'seconds':report['seconds']}),flush=True)

if __name__=='__main__':main()
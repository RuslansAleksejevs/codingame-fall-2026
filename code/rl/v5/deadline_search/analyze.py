"""Frozen whole-map all-games and clean-paired inference; no adaptive extension."""
from collections import Counter
import argparse
import numpy as np
from common import *
from panel import OPPONENTS, schedule

EXTERNAL=OPPONENTS[:3]
BOOTSTRAP_SEED=20261108
RESAMPLES=10000


def is_clean(r):
    return r['valid'] and not r['returncode'] and not r['own_action_errors'] and not r['opponent_action_errors']


def score(r):
    if not r['valid'] or r['returncode'] or r['own_action_errors']:return 0.0
    return {'win':1.,'draw':.5,'loss':0.}[r['outcome']]


def ci(values):
    if not values:return [None,None]
    a=np.asarray(values,dtype=float);rng=np.random.default_rng(BOOTSTRAP_SEED)
    draws=a[rng.integers(0,len(a),size=(RESAMPLES,len(a)))].mean(axis=1)
    return [float(v*100) for v in np.quantile(draws,[.025,.975])]


def estimate(values):
    return {'maps':len(values),'point_percent':float(np.mean(values)*100) if values else None,'map_95_percent':ci(values)}


def counts(rows):
    return {'games':len(rows),'win':sum(score(r)==1 for r in rows),'draw':sum(score(r)==.5 for r in rows),
        'loss':sum(score(r)==0 for r in rows),'own_technical_errors':sum(not r['valid'] or bool(r['returncode']) or bool(r['own_action_errors']) for r in rows),
        'opponent_technical_errors':sum(bool(r['opponent_action_errors']) for r in rows)}


def strategic_pass(data):
    gain=data['external_gain'];direct=data['direct_league3m']
    return (gain['point_percent'] is not None and gain['point_percent']>=5 and gain['map_95_percent'][0]>0
        and direct['point_percent'] is not None and direct['point_percent']>=55 and direct['map_95_percent'][0]>50
        and all(v['gain']['point_percent'] is not None and v['gain']['point_percent']>=-5 for v in data['per_opponent'].values()))


def evaluate(rows,verification_pass=True):
    expected=schedule(list(range(70101,70141)));key=lambda r:tuple(r[k] for k in ('candidate','opponent','seed','seat'))
    by={key(r):r for r in rows};assert len(by)==len(rows),'Duplicate evidence'
    assert set(by)<=set(map(key,expected)),'Unexpected evidence'
    complete=len(rows)==len(expected)
    seeds=list(range(70101,70141));hashes={}
    for r in rows:
        old=hashes.setdefault(r['seed'],r['map_content_sha256']);assert old==r['map_content_sha256'],'Paired map mismatch'
    assert len(set(hashes.values()))==len(hashes),'Duplicate map content'
    result={}
    for clean_only in (False,True):
        per={};deltas={}
        for opponent in OPPONENTS:
            retained=[];kept=[]
            for seed in seeds:
                keys=[(c,opponent,seed,p) for c in ('search','control') for p in (0,1)]
                if not all(k in by for k in keys):continue
                group=[by[k] for k in keys]
                if clean_only and not all(is_clean(r) for r in group):continue
                retained.append(seed);kept+=group
                deltas[opponent,seed]=sum(score(by['search',opponent,seed,p])-score(by['control',opponent,seed,p]) for p in (0,1))/2
            candidates={}
            for candidate in ('search','control'):
                rr=[r for r in kept if r['candidate']==candidate]
                vals=[sum(score(by[candidate,opponent,s,p]) for p in (0,1))/2 for s in retained]
                candidates[candidate]={'results':counts(rr),'score':estimate(vals),'seats':{
                    str(p):{'results':counts([r for r in rr if r['seat']==p]),
                            'score':estimate([score(by[candidate,opponent,s,p]) for s in retained])} for p in (0,1)}}
            per[opponent]={'complete_maps':len(retained),'retained_seeds':retained,
                'gain':estimate([deltas[opponent,s] for s in retained]),'candidates':candidates,
                'seat_gains':{str(p):estimate([score(by['search',opponent,s,p])-score(by['control',opponent,s,p]) for s in retained]) for p in (0,1)}}
        composite=[sum(deltas[o,s] for o in EXTERNAL)/3 for s in seeds if all((o,s) in deltas for o in EXTERNAL)]
        direct=[]
        for s in seeds:
            keys=[('search','league3m',s,p) for p in (0,1)]
            if all(k in by for k in keys) and (not clean_only or all(is_clean(by[k]) for k in keys)):
                direct.append(sum(score(by[k]) for k in keys)/2)
        data={'per_opponent':per,'external_gain':estimate(composite),'direct_league3m':estimate(direct)}
        data['strategic_thresholds_passed']=strategic_pass(data)
        result['clean_paired' if clean_only else 'all_games']=data
    errors=[r for r in rows if not r['valid'] or r['returncode'] or r['own_action_errors'] or r['opponent_action_errors']]
    own=sum(not r['valid'] or bool(r['returncode']) or bool(r['own_action_errors']) for r in rows)
    coverage=(result['clean_paired']['external_gain']['maps']>=36 and
        all(v['complete_maps']>=36 for v in result['clean_paired']['per_opponent'].values()))
    passed=complete and own==0 and verification_pass and coverage and all(result[k]['strategic_thresholds_passed'] for k in ('all_games','clean_paired'))
    return {'as_of':now(),'classification':'PROJECT_REPORTED','expected_games':1120,'completed_games':len(rows),
        'complete_fixed_series':complete,'own_control_error_games':own,'opponent_error_games':sum(bool(r['opponent_action_errors']) for r in rows),
        'coverage_passed':coverage,'exact_replay_passed':verification_pass,'teacher_gate_passed':bool(passed),
        'decision':'PASSED_TEACHER_NOT_DEPLOYABLE' if passed else 'REJECTED',
        'bootstrap':{'seed':BOOTSTRAP_SEED,'resamples':RESAMPLES,'unit':'Whole map, both seats together'},
        **result,'technical_records':errors,'labels_generated':0,'student_training':False,'platform_tests':0,
        'note':'All-games opponent technical wins are retained but are not strategic wins. Clean pairing removes whole affected opponent-map clusters. Related khoufou versions are not independent algorithm families.'}


def timing(rows):
    report={}
    for candidate in sorted({r['candidate'] for r in rows}):
        rr=[r for r in rows if r['candidate']==candidate];details=[t for r in rr for t in r['deadline_measurements']]
        fields={}
        for key in ('parse_us','restore_us','flush_us','through_flush_us'):
            values=[d[key] for d in details]
            fields[key]={str(q):float(np.quantile(values,q)) for q in (.5,.95,.99,1)} if values else {}
        nested={}
        for key in ('baseline_us','response_us','proposal_us','future_us','decoder_us','choices_us','feature_us','forward_us','clone_us','simulation_us','value_us','atomic_max_us'):
            values=[d['search'][key] for d in details]
            nested[key]={str(q):float(np.quantile(values,q)) for q in (.5,.95,.99,1)} if values else {}
        report[candidate]={'games':len(rr),'outputs':sum(r['own_output_count'] for r in rr),'raw_timing_turns':len(details),
            'changed':sum(d['search']['selected']>0 for d in details),'budget_stops':sum(d['search']['stopped'] for d in details),
            'emergency':sum(d['search']['emergency'] for d in details),'complete_candidates':dict(Counter(d['search']['complete'] for d in details)),
            'totals':fields,'nested_components_do_not_sum':nested,
            'post_flush_us':{str(q):float(np.quantile([v for r in rr for v in r['post_flush_us']],q)) for q in (.5,.95,.99,1)}}
    return report


def main():
    rows=[];verified=True;bindings={}
    for i in range(1,5):
        path=OUT/f'confirm{i}/matches.jsonl'
        if not path.exists():continue
        rr=[json.loads(line) for line in path.read_text().splitlines()];rows+=rr
        verification=OUT/f'confirm{i}-verification.json'
        if not verification.exists():verified=False
        else:
            report=json.loads(verification.read_text());verified&=report['passed'] and report['matches_sha256']==sha(path)
        bindings[rel(path)]=sha(path)
    result=evaluate(rows,verified)
    result.update(bindings=bindings,sources=sources(),budget=budget())
    save(OUT/'decision.json',result);save(OUT/'confirmation-timing.json',timing(rows))
    print(json.dumps({k:result[k] for k in ('decision','completed_games','own_control_error_games','opponent_error_games')},indent=2))
    print(json.dumps({k:{v:result[k][v] for v in ('external_gain','direct_league3m')} for k in ('all_games','clean_paired')},indent=2))


if __name__=='__main__':main()
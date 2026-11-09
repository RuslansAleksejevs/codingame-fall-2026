"""Prospective whole-map three-way inference, independent of coordinator code."""
from collections import Counter
import math
import numpy as np
from common import *
from panel import OPPONENTS,CANDIDATES,schedule
SEED=20261109

def own_error(r):return not r['valid'] or r['returncode']!=0 or bool(r['own_action_errors']) or r.get('emergency',False)
def clean_row(r):return not own_error(r) and not r['opponent_action_errors']
def points(r):return 0. if own_error(r) else {'win':1.,'draw':.5,'loss':0.}[r['outcome']]

def estimate(values):
    if not values:return {'maps':0,'point_percent':None,'map_95_percent':[None,None]}
    array=np.asarray(values,dtype=np.float64);rng=np.random.default_rng(SEED)
    bootstrap=array[rng.integers(0,len(array),size=(10000,len(array)))].mean(axis=1)
    return {'maps':len(values),'point_percent':float(array.mean()*100),'map_95_percent':[float(x*100) for x in np.quantile(bootstrap,[.025,.975])]}

def counts(rows):
    return {'games':len(rows),'win':sum(points(r)==1 for r in rows),'draw':sum(points(r)==.5 for r in rows),'loss':sum(points(r)==0 for r in rows),
        'own_technical':sum(bool(own_error(r)) for r in rows),'opponent_technical':sum(bool(r['opponent_action_errors']) for r in rows)}

def gates(view,stage):
    ge=lambda x,y:x is not None and x>=y-1e-12
    gt=lambda x,y:x is not None and x>y+1e-12
    gain=view['external_gain'];retained=view['external_candidate_minus_teacher'];direct=view['direct_league3m']
    per=[v['gain']['point_percent'] for v in view['per_opponent'].values()]
    if stage=='development':return {'external_positive':gt(gain['point_percent'],0),'league3m_majority':gt(direct['point_percent'],50),'retention_minus5':ge(retained['point_percent'],-5),'regression_minus10':all(ge(v,-10) for v in per)}
    b2m=view['direct_b2m']
    return {'external_3pp':ge(gain['point_percent'],3),'external_lower_positive':gt(gain['map_95_percent'][0],0),
        'league3m_55':ge(direct['point_percent'],55),'league3m_lower50':gt(direct['map_95_percent'][0],50),
        'b2m_55':ge(b2m['point_percent'],55),'b2m_lower50':gt(b2m['map_95_percent'][0],50),
        'retention_minus2':ge(retained['point_percent'],-2),'retention_lower_minus5':gt(retained['map_95_percent'][0],-5),
        'regression_minus5':all(ge(v,-5) for v in per)}

def evaluate(rows,seeds,stage,replay_pass,raw_pass,package_pass):
    key=lambda r:tuple(r[k] for k in ('candidate','opponent','seed','seat'))
    expected={key(r) for r in schedule(seeds)};by={key(r):r for r in rows}
    assert len(by)==len(rows) and set(by)<=expected,'Duplicate or undeclared evidence'
    hashes={}
    for row in rows:
        previous=hashes.setdefault(row['seed'],row['map_content_sha256']);assert previous==row['map_content_sha256']
    assert len(hashes)==len(set(hashes.values())),'Map-content collision'
    views={}
    for clean in (False,True):
        per={};retained={}
        for opponent in OPPONENTS:
            keep=[]
            for seed in seeds:
                cluster=[(c,opponent,seed,p) for c in CANDIDATES for p in (0,1)]
                if all(k in by for k in cluster) and (not clean or all(clean_row(by[k]) for k in cluster)):keep.append(seed)
            retained[opponent]=keep
            def value(candidate,seed):return sum(points(by[candidate,opponent,seed,p]) for p in (0,1))/2
            models={}
            for candidate in CANDIDATES:
                rr=[by[candidate,opponent,s,p] for s in keep for p in (0,1)]
                models[candidate]={'results':counts(rr),'score':estimate([value(candidate,s) for s in keep]),
                    'seats':{str(p):{'results':counts([by[candidate,opponent,s,p] for s in keep]),'score':estimate([points(by[candidate,opponent,s,p]) for s in keep])} for p in (0,1)}}
            per[opponent]={'complete_maps':len(keep),'retained_seeds':keep,'candidates':models,
                'gain':estimate([value('candidate',s)-value('control',s) for s in keep]),
                'candidate_minus_teacher':estimate([value('candidate',s)-value('teacher',s) for s in keep]),
                'teacher_minus_control':estimate([value('teacher',s)-value('control',s) for s in keep]),
                'seat_gains':{str(p):estimate([points(by['candidate',opponent,s,p])-points(by['control',opponent,s,p]) for s in keep]) for p in (0,1)}}
        common=[s for s in seeds if all(s in retained[o] for o in OPPONENTS[:3])]
        def composite(left,right):return estimate([sum(points(by[left,o,s,p])-points(by[right,o,s,p]) for o in OPPONENTS[:3] for p in (0,1))/6 for s in common])
        view={'per_opponent':per,'external_maps':common,'external_gain':composite('candidate','control'),
            'external_candidate_minus_teacher':composite('candidate','teacher'),'external_teacher_minus_control':composite('teacher','control'),
            'direct_league3m':per['league3m']['candidates']['candidate']['score'],'direct_b2m':per['b2m']['candidates']['candidate']['score']}
        view['gates']=gates(view,stage);view['strength_passed']=all(view['gates'].values());views['clean_paired' if clean else 'all_games']=view
    minimum=math.ceil(len(seeds)*(.9 if stage=='development' else .95));clean=views['clean_paired']
    technical=sum(bool(own_error(r)) for r in rows)
    checks={'complete_fixed_schedule':set(by)==expected,'zero_own_control_teacher_errors':technical==0,'replay_pass':bool(replay_pass),
        'raw_pass':bool(raw_pass),'package_pass':bool(package_pass),'clean_coverage':len(clean['external_maps'])>=minimum and all(v['complete_maps']>=minimum for v in clean['per_opponent'].values()),
        'strength_pass':views['all_games']['strength_passed'] and (stage=='development' or clean['strength_passed']),
        'timing_coverage':all(r.get('timing_coverage_pass',False) for r in rows),'internal_margin':all(r.get('internal_margin_pass',False) for r in rows)}
    return {'as_of':now(),'stage':stage,'classification':'PROJECT_REPORTED','gate_passed':all(checks.values()),'checks':checks,
        'expected_games':len(expected),'completed_games':len(rows),'minimum_clean_maps':minimum,'own_control_teacher_error_games':technical,
        'opponent_error_games':sum(bool(r['opponent_action_errors']) for r in rows),'missing_rows':[list(k) for k in sorted(expected-set(by))],
        'bootstrap':{'seed':SEED,'resamples':10000,'unit':'Whole map, both seats, six-row comparison clusters'},**views}

def timing(rows):
    report={}
    for c in CANDIDATES:
        rr=[r for r in rows if r['candidate']==c];details=[d for r in rr for d in r['deadline_measurements']]
        def quantiles(values):return {str(q):float(np.quantile(values,q)) for q in (.5,.95,.99,1)} if values else {}
        report[c]={'games':len(rr),'outputs':sum(r['own_output_count'] for r in rr),'timing_rows':len(details),
            'budget_stops':sum(d['search']['stopped'] for d in details),'emergencies':sum(d['search']['emergency'] for d in details),
            'changed_from_baseline':sum(d['search']['selected']>0 for d in details),'complete_candidates':dict(Counter(d['search']['complete'] for d in details)),
            'totals':{k:quantiles([d[k] for d in details]) for k in ('parse_us','restore_us','flush_us','through_flush_us')},
            'nested_components':{k:quantiles([d['search'][k] for d in details]) for k in ('baseline_us','response_us','proposal_us','future_us','decoder_us','choices_us','feature_us','forward_us','clone_us','simulation_us','value_us','atomic_max_us')},
            'post_flush_us':quantiles([v for r in rr for v in r['post_flush_us']])}
    return report

def main():
    stage=sys.argv[1];assert stage in ('development','final')
    names=['development'] if stage=='development' else [f'confirm{i}' for i in range(1,11)]
    rows=[];replay=True;bindings={}
    for name in names:
        path=OUT/name/'matches.jsonl'
        if not path.exists():replay=False;continue
        rows.extend(json.loads(line) for line in path.read_text().splitlines());bindings[rel(path)]=sha(path)
        check=OUT/(name+'-verification.json')
        if not check.exists():replay=False
        else:
            data=json.loads(check.read_text());replay&=data['passed'] and data['matches_sha256']==sha(path);bindings[rel(check)]=sha(check)
    raw=OUT/(stage+'-raw-audit.json');raw_pass=raw.exists() and json.loads(raw.read_text())['passed']
    package=json.loads((OUT/'package-attempt2.json').read_text());package_pass=package['passed'] and sha(ROOT/package['source'])==package['source_sha256']
    result=evaluate(rows,list(range(71001,71013)) if stage=='development' else list(range(40001,40101)),stage,replay,raw_pass,package_pass)
    result.update(bindings=bindings,budget=budget(),sources=sources());save(OUT/(stage+'-decision.json'),result)
    save(OUT/(stage+'-timing.json'),timing(rows))
    print(json.dumps({k:result[k] for k in ('stage','gate_passed','checks','completed_games')},indent=2))

if __name__=='__main__':main()
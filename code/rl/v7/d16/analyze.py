"""Frozen raw audit and whole-map paired descriptive/exploratory decision."""
from collections import Counter
import gzip
import numpy as np
from common import *
from panel import old, OPPONENTS, CANDIDATES, checked_freeze

paired=module('d16_paired_estimate',ROOT/'code/rl/v6/coordinator/paired.py')
estimate=paired.estimate

def read_rows(names):
    rows=[];binding={};timing={c:[] for c in CANDIDATES}
    for name in names:
        path=OUT/name/'matches.jsonl';binding[rel(path)]=sha(path)
        for line in path.read_text().splitlines():
            row=json.loads(line);stem=f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}'
            rawpath=path.parent/(stem+'-raw.json');raw=json.loads(rawpath.read_text())
            assert sha(rawpath)==row['raw_sha256']
            portable=json.loads(gzip.decompress((path.parent/(stem+'.json.gz')).read_bytes()));assert portable==clean(raw)
            actual=old.metrics(raw,row['seat'])
            for k,v in actual.items():assert row[k]==v,(stem,k)
            params=dict(s.split('=',1) for s in ''.join(raw['gameParameters']).splitlines() if '=' in s)
            board={k:[list(map(int,r.split(','))) for r in params[k].split('_') if r] for k in ('nodes','units','edges')}
            digest=hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest();assert digest==row['map_content_sha256']
            emergency=any(t['search']['emergency'] for t in actual['deadline_measurements']);assert emergency==row['emergency']
            own=not actual['valid'] or bool(row['returncode'] or actual['own_action_errors'] or emergency) or not all(row[k] for k in ('baseline_complete_pass','timing_coverage_pass','internal_margin_pass'))
            points=0 if own else {'win':1,'draw':.5,'loss':0}[actual['outcome']]
            rows.append({**{k:row[k] for k in ('candidate','opponent','seed','seat','map_content_sha256')},'points':points,'raw_outcome':actual['outcome'],'own_failure':own,'opponent_failure':bool(actual['opponent_action_errors']),'emergency':emergency,'raw_sha256':sha(rawpath)})
            timing[row['candidate']].extend(actual['deadline_measurements'])
    return rows,binding,timing

def strength_gates(view):
    return {
        'external_point_at_least_minus5':view['external_gain']['point_percent'] is not None and view['external_gain']['point_percent']>=-5-1e-10,
        'teacher_point_at_least_minus10':view['teacher_retention']['point_percent'] is not None and view['teacher_retention']['point_percent']>=-10-1e-10,
        'direct_league3m_at_least50':view['direct_league3m']['point_percent'] is not None and view['direct_league3m']['point_percent']>=50-1e-10,
        'direct_b2m_at_least40':view['direct_b2m']['point_percent'] is not None and view['direct_b2m']['point_percent']>=40-1e-10,
        'external_opponent_regression_at_least_minus15':all(view['per_opponent'][o]['gain']['point_percent'] is not None and view['per_opponent'][o]['gain']['point_percent']>=-15-1e-10 for o in OPPONENTS[:3]),
    }

def summarize(rows,seeds):
    by={};hashes={}
    for r in rows:
        k=tuple(r[x] for x in ('candidate','opponent','seed','seat'));assert k not in by;by[k]=r
        assert hashes.setdefault(r['seed'],r['map_content_sha256'])==r['map_content_sha256']
    assert len(set(hashes.values()))==len(hashes)
    views={}
    def point(c,o,s,p):return by[c,o,s,p]['points']
    def score(c,o,s):return sum(point(c,o,s,p) for p in (0,1))/2
    for clean_only in (False,True):
        per={};excluded={}
        for o in OPPONENTS:
            kept=[];excluded[o]={}
            for s in seeds:
                keys=[(c,o,s,p) for c in CANDIDATES for p in (0,1)]
                if any(k not in by for k in keys):excluded[o][s]='incomplete';continue
                fails=[list(k) for k in keys if by[k]['own_failure'] or by[k]['opponent_failure']]
                if clean_only and fails:excluded[o][s]=fails;continue
                kept.append(s)
            result={}
            for c in CANDIDATES:
                count=Counter({0:'loss',.5:'draw',1:'win'}[point(c,o,s,p)] for s in kept for p in (0,1))
                result[c]={'score':estimate([score(c,o,s) for s in kept]),'results':{k:count[k] for k in ('win','draw','loss')},'seats':{str(p):estimate([point(c,o,s,p) for s in kept]) for p in (0,1)}}
            per[o]={'seeds':kept,'candidates':result,'gain':estimate([score('candidate',o,s)-score('control',o,s) for s in kept]),'retention':estimate([score('candidate',o,s)-score('teacher',o,s) for s in kept])}
        ext=[s for s in seeds if all(s in per[o]['seeds'] for o in OPPONENTS[:3])]
        view={'per_opponent':per,'excluded_clusters':excluded,'external_seeds':ext,'external_gain':estimate([sum(score('candidate',o,s)-score('control',o,s) for o in OPPONENTS[:3])/3 for s in ext]),'teacher_retention':estimate([sum(score('candidate',o,s)-score('teacher',o,s) for o in OPPONENTS[:3])/3 for s in ext]),'direct_league3m':per['league3m']['candidates']['candidate']['score'],'direct_b2m':per['b2m']['candidates']['candidate']['score']}
        view['exploratory_sanity']=strength_gates(view)
        views['clean_paired' if clean_only else 'all_games']=view
    return views

def main():
    guard();frozen=checked_freeze();names=[f'confirm{i}' for i in range(1,5)]
    rows,bindings,timing=read_rows(names)
    assert [{k:r[k] for k in ('candidate','opponent','seed','seat')} for r in rows]==frozen['schedule']
    views=summarize(rows,list(range(72101,72141)))
    replay=[]
    for name in names:
        report=json.loads((OUT/(name+'-verification.json')).read_text());assert report['passed']
        assert report['matches_sha256']==sha(OUT/name/'matches.jsonl') and report['manifest_sha256']==sha(OUT/name/'manifest.json')
        replay.append(report)
    tech={c:{'games':sum(r['candidate']==c for r in rows),'own_failure_games':sum(r['candidate']==c and r['own_failure'] for r in rows),'opponent_failure_games':sum(r['candidate']==c and r['opponent_failure'] for r in rows),'emergency_games':sum(r['candidate']==c and r['emergency'] for r in rows),'raw_outcomes':dict(Counter(r['raw_outcome'] for r in rows if r['candidate']==c))} for c in CANDIDATES}
    times={}
    for c,entries in timing.items():
        times[c]={'outputs':len(entries)}
        for field in ('parse_us','restore_us','optional_us','flush_us','through_flush_us'):
            values=[r[field] for r in entries if field in r]
            if values:times[c][field]={'p50':float(np.median(values)),'p95':float(np.quantile(values,.95)),'p99':float(np.quantile(values,.99)),'max':max(values)}
        baseline=[r['search']['baseline_us'] for r in entries];times[c]['baseline_us']={'p99':float(np.quantile(baseline,.99)),'max':max(baseline)}
        times[c]['emergency_turns']=sum(r['search']['emergency'] for r in entries)
        times[c]['changed_turns']=sum(r['search']['selected']>0 for r in entries)
        times[c]['optional_stops']=sum(r['search']['stopped'] for r in entries)
    technical=not any(r['own_failure'] for r in rows)
    coverage=len(views['clean_paired']['external_seeds'])>=36 and all(len(p['seeds'])>=36 for p in views['clean_paired']['per_opponent'].values())
    sane=all(all(v['exploratory_sanity'].values()) for v in views.values())
    strong=all(v['external_gain']['map_95_percent'][0]>0 and v['direct_league3m']['map_95_percent'][0]>50 and v['direct_b2m']['map_95_percent'][0]>50 for v in views.values())
    report={'as_of':now(),'classification':'PROJECT_REPORTED','completed_games':len(rows),'maps':40,'raw_identity_pass':True,'technical_ready':technical,'clean_coverage_pass':coverage,'exploratory_sanity_pass':sane,'exploratory_live_recommended':technical and coverage and sane,'strong_local_evidence':strong,'interpretation':'Exploratory single ranking only; not the historical v6 gate; official tests and coordinator decision still required','bootstrap':{'resamples':10000,'seed':20261109,'unit':'whole map/both seats'},'technical':tech,'timing':times,'replay':{'games':sum(r['clean_games'] for r in replay),'states':sum(r['states'] for r in replay),'transitions':sum(r['transitions'] for r in replay),'excluded':sum([r['excluded'] for r in replay],[])},'raw_bindings':bindings,'freeze_sha256':sha(OUT/'final-freeze.json'),'source_sha256':frozen['source_sha256'],'budget':budget(),**views}
    save(OUT/'final-decision.json',report);print(json.dumps(report),flush=True)

if __name__=='__main__':main()
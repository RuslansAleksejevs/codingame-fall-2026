"""Independent student/unchanged-control/frozen-teacher map-cluster inference."""
from student_common import *
from analyze import ci, estimate, score, is_clean, counts, strategic_pass, EXTERNAL, RESAMPLES, BOOTSTRAP_SEED
from panel import OPPONENTS

CANDIDATES=('student','control','teacher')


def schedule():
    rows=[]
    for i,seed in enumerate(CONFIRM):
        k=i%len(OPPONENTS);opponents=OPPONENTS[k:]+OPPONENTS[:k]
        for j,opponent in enumerate(opponents):
            for seat in (i%2,1-i%2):
                k=(i+j+seat)%3;order=CANDIDATES[k:]+CANDIDATES[:k]
                if (i+j)%2:order=order[::-1]
                rows.extend({'candidate':c,'opponent':opponent,'seed':seed,'seat':seat} for c in order)
    return rows


def evaluate(rows,verification_pass=True,package_pass=True):
    key=lambda r:tuple(r[k] for k in ('candidate','opponent','seed','seat'))
    expected=schedule();by={key(r):r for r in rows};assert len(by)==len(rows) and set(by)<=set(map(key,expected))
    hashes={}
    for r in rows:assert hashes.setdefault(r['seed'],r['map_content_sha256'])==r['map_content_sha256']
    assert len(set(hashes.values()))==len(hashes),'Duplicate map content'
    result={}
    for clean_only in (False,True):
        per={};deltas={};retention={}
        for opponent in OPPONENTS:
            retained=[];kept=[]
            for seed in CONFIRM:
                keys=[(c,opponent,seed,p) for c in CANDIDATES for p in (0,1)]
                if not all(k in by for k in keys):continue
                group=[by[k] for k in keys]
                if clean_only and not all(is_clean(r) for r in group):continue
                retained.append(seed);kept.extend(group)
                deltas[opponent,seed]=sum(score(by['student',opponent,seed,p])-score(by['control',opponent,seed,p]) for p in (0,1))/2
                retention[opponent,seed]=sum(score(by['student',opponent,seed,p])-score(by['teacher',opponent,seed,p]) for p in (0,1))/2
            candidates={}
            for c in CANDIDATES:
                rr=[r for r in kept if r['candidate']==c]
                candidates[c]={'results':counts(rr),'score':estimate([sum(score(by[c,opponent,s,p]) for p in (0,1))/2 for s in retained]),
                    'seats':{str(p):{'results':counts([r for r in rr if r['seat']==p]),
                        'score':estimate([score(by[c,opponent,s,p]) for s in retained])} for p in (0,1)}}
            per[opponent]={'complete_maps':len(retained),'retained_seeds':retained,'candidates':candidates,
                'gain':estimate([deltas[opponent,s] for s in retained]),
                'student_minus_teacher':estimate([retention[opponent,s] for s in retained]),
                'seat_gains':{str(p):estimate([score(by['student',opponent,s,p])-score(by['control',opponent,s,p]) for s in retained]) for p in (0,1)}}
        complete_maps=[s for s in CONFIRM if all((o,s) in deltas for o in EXTERNAL)]
        composite=[sum(deltas[o,s] for o in EXTERNAL)/3 for s in complete_maps]
        teacher_composite=[sum(retention[o,s] for o in EXTERNAL)/3 for s in complete_maps]
        direct=[sum(score(by['student','league3m',s,p]) for p in (0,1))/2 for s in per['league3m']['retained_seeds']]
        data={'per_opponent':per,'external_gain':estimate(composite),'direct_league3m':estimate(direct),
            'external_student_minus_teacher':estimate(teacher_composite)}
        ret=data['external_student_minus_teacher'];data['retention_passed']=(ret['point_percent'] is not None and ret['point_percent']>=-2 and ret['map_95_percent'][0]>-5)
        data['strategic_thresholds_passed']=strategic_pass(data) and data['retention_passed']
        result['clean_paired' if clean_only else 'all_games']=data
    own=sum(not r['valid'] or bool(r['returncode']) or bool(r['own_action_errors']) for r in rows)
    coverage=result['clean_paired']['external_gain']['maps']>=36 and all(v['complete_maps']>=36 for v in result['clean_paired']['per_opponent'].values())
    passed=(len(rows)==1680 and own==0 and verification_pass and package_pass and coverage
        and all(result[k]['strategic_thresholds_passed'] for k in ('all_games','clean_paired')))
    return {'as_of':now(),'classification':'PROJECT_REPORTED','decision':'PASSED_LOCAL_STUDENT' if passed else 'REJECTED',
        'student_gate_passed':bool(passed),'expected_games':1680,'completed_games':len(rows),'complete_fixed_series':len(rows)==1680,
        'own_control_teacher_error_games':own,'opponent_error_games':sum(bool(r['opponent_action_errors']) for r in rows),
        'observed_all_rows':{c:{o:{'results':counts([r for r in rows if r['candidate']==c and r['opponent']==o]),
            'seats':{str(p):counts([r for r in rows if r['candidate']==c and r['opponent']==o and r['seat']==p]) for p in (0,1)}}
            for o in OPPONENTS} for c in CANDIDATES},
        'coverage_passed':coverage,'exact_replay_passed':verification_pass,'package_parity_passed':package_pass,
        'bootstrap':{'seed':BOOTSTRAP_SEED,'resamples':RESAMPLES,'unit':'Whole map, both seats and paired candidates together'},
        **result,'technical_records':[r for r in rows if not is_clean(r)],'platform_tests':0,'ranking_mutation':False,
        'note':'No pooling with original teacher evidence. Opponent technical wins are retained only in all-games and are not strategic wins.'}


def main():
    rows=[];verified=True;bindings={};states=transitions=0
    for n in range(1,5):
        p=STUDENT/f'confirm{n}/matches.jsonl'
        if not p.exists():continue
        rows.extend(json.loads(line) for line in p.read_text().splitlines());bindings[rel(p)]=sha(p)
        v=STUDENT/f'confirm{n}-verification.json'
        if not v.exists():verified=False;continue
        data=json.loads(v.read_text());verified&=data['passed'] and data['matches_sha256']==sha(p)
        states+=data['states'];transitions+=data['transitions']
    package=json.loads((STUDENT/'package-parity.json').read_text());result=evaluate(rows,verified,package['passed'])
    result.update(bindings=bindings,java_native_states=states,java_native_transitions=transitions,sources=sources(),budget=budget())
    save(STUDENT/'decision.json',result)
    print(json.dumps({k:result[k] for k in ('decision','completed_games','own_control_teacher_error_games','opponent_error_games')},indent=2),flush=True)
    print(json.dumps({k:{v:result[k][v] for v in ('external_gain','direct_league3m','external_student_minus_teacher')} for k in ('all_games','clean_paired')},indent=2),flush=True)


if __name__=='__main__':main()
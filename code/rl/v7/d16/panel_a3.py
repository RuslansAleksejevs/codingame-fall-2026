"""The single amended 96-game gross guard; reuse audited referee/replay machinery."""
from collections import Counter
from common import *
import panel as original
from maps import registry, classpath
from run_matches import java_home
from analyze import read_rows, estimate

NAME='a3-gross'
SEEDS=tuple(range(72005,72013))
OPPONENTS=('lacoz','khoufou2','khoufou')
ROLES=('candidate','control')
AMENDMENT=ROOT/'experiments/rl/2026-11-09-d16-live/AMENDMENT_A3.md'
CPP=OUT/'package-attempt3/bot.cpp'
EXPECTED_SHA='94f0d426de787f7ed29a0ce87fa03fd3e0bae2ebb27c7d76548f4624f67ab4f8'
_commands=original.commands
_identities=original.identities
_metrics=original.old.metrics

def commands():
    return dict(_commands(),candidate=[rel(OUT/'build/attempt3/candidate')])

def identities():
    package=json.loads((OUT/'candidate3-package.json').read_text())
    extra=[CPP,OUT/'candidate3-package.json',AMENDMENT,CODE/'act_a3.inc',CODE/'contracts_a3.cpp',CODE/'panel_a3.py']
    return {**_identities(),**package['binaries'],**package['implementation_bindings'],**{rel(p):sha(p) for p in extra}}

def schedule():
    rows=[]
    for i,seed in enumerate(SEEDS):
        opponents=OPPONENTS[i%3:]+OPPONENTS[:i%3]
        for j,opponent in enumerate(opponents):
            for seat in (i%2,1-i%2):
                roles=ROLES if (i+j+seat)%2==0 else ROLES[::-1]
                rows.extend({'candidate':c,'opponent':opponent,'seed':seed,'seat':seat} for c in roles)
    return rows

def check_timing(record):
    s=record['search']
    assert s['baseline_complete']==1 and s['emergency']==0
    assert s['shallow_complete']==len(s['shallow_values']) and s['complete']==len(s['values'])
    tier=2 if s['complete']>=2 else 1 if s['shallow_complete']>=2 else 0
    assert s['selected_tier']==tier and s['paired']==int(tier>0)
    count=s['complete'] if tier==2 else s['shallow_complete'] if tier==1 else 1
    assert 0<=s['selected']<count and record['process_cpu_us']>=0
    if tier:
        values=s['values'] if tier==2 else s['shallow_values'];chosen=0;best=values[0]
        # Printed values have10 significant digits; avoid creating a false failure
        # from rounded ties. Exact double prefix comparisons were tested in C++.
        if s['selected']:
            assert values[s['selected']]>values[0]+.02-1e-8
            assert values[s['selected']]>=max(values)-1e-8

def metrics(raw,seat):
    result=_metrics(raw,seat)
    for record in result['deadline_measurements']:
        if 'shallow_complete' in record['search']:check_timing(record)
    return result

def checked():
    original.checked_freeze()
    frozen=json.loads((OUT/'a3-freeze.json').read_text())
    for p,h in frozen['identities'].items():assert sha(ROOT/p)==h,('A3 frozen file changed',p)
    assert sha(CPP)==EXPECTED_SHA and frozen['schedule']==schedule()
    return frozen

def board_hash(props):
    board={k:[list(map(int,r.split(','))) for r in props[k].split('_') if r] for k in ('nodes','units','edges')}
    return board,hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def prepare_maps():
    checked();prior=registry(NAME+'-historical');known=set(prior['canonical']);legacy=set(prior['legacy'])
    bindings=dict(prior['sources']);live=ROOT/'experiments/rl/2026-11-09-d16-live'
    # Include even the preserved erroneous test08 map, not only the valid panel.
    for path in sorted(live.glob('test-*-result.json')):
        data=json.loads(path.read_text());log=data.get('log',{});text=log.get('game_options')
        if not text:continue
        props=dict(s.split('=',1) for s in text.splitlines() if '=' in s)
        if all(k in props for k in ('nodes','units','edges')):
            _,digest=board_hash(props);known.add(digest);bindings[rel(path)]=sha(path)
    save(OUT/(NAME+'-registry.json'),{'as_of':now(),'canonical':sorted(known),'legacy':sorted(legacy),'sources':bindings,'method':'All prior canonical registries/currentv7 claims plus every currently saved official test map, including erroneous08'})
    generator=subprocess.Popen([str(java_home()/'bin/java'),'-Xmx1g','-cp',classpath(),'MapGenerator'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    entries=[];hashes={};overlaps=[]
    try:
        for seed in SEEDS:
            generator.stdin.write(str(seed)+'\n');generator.stdin.flush();props=json.loads(generator.stdout.readline())
            board,digest=board_hash(props);old=hashlib.sha256(json.dumps(props,sort_keys=True).encode()).hexdigest()
            if digest in known or old in legacy or digest in hashes.values():overlaps.append(seed)
            entries.append({'seed':seed,'hash':digest,'legacy_hash':old,'map':board});hashes[str(seed)]=digest
    finally:generator.stdin.close();generator.wait(timeout=20)
    save(OUT/(NAME+'-maps.json'),{'as_of':now(),'maps':entries,'overlaps':overlaps});save(OUT/(NAME+'-map-hashes.json'),hashes)
    save(OUT/(NAME+'-novelty.json'),{'as_of':now(),'passed':not overlaps,'seeds':list(SEEDS),'overlaps':overlaps,'previous_canonical':len(known),'previous_legacy':len(legacy),'source_count':len(bindings),'registry_sha256':sha(OUT/(NAME+'-registry.json')),'freeze_sha256':sha(OUT/'a3-freeze.json')})
    assert not overlaps,'Novelty overlap: stop, do not replace maps'
    return hashes

def summarize(rows):
    by={tuple(r[k] for k in ('candidate','opponent','seed','seat')):r for r in rows};assert len(by)==len(rows)
    views={}
    for clean_only in (False,True):
        keep=[];excluded={}
        for seed in SEEDS:
            keys=[(c,o,seed,p) for c in ROLES for o in OPPONENTS for p in (0,1)]
            if any(k not in by for k in keys):excluded[str(seed)]='incomplete';continue
            errors=[list(k) for k in keys if by[k]['own_failure'] or by[k]['opponent_failure']]
            if clean_only and errors:excluded[str(seed)]=errors;continue
            keep.append(seed)
        def total(c,o,seed):return sum(by[c,o,seed,p]['points'] for p in (0,1))
        per={}
        for o in OPPONENTS:
            per[o]={'points':{c:sum(total(c,o,s) for s in keep) for c in ROLES},
                    'outcomes':{c:dict(Counter(by[c,o,s,p]['raw_outcome'] for s in keep for p in (0,1))) for c in ROLES},
                    'paired_gain':estimate([(total('candidate',o,s)-total('control',o,s))/2 for s in keep])}
        totals={c:sum(per[o]['points'][c] for o in OPPONENTS) for c in ROLES}
        guards={'external_candidate_at_least_control':bool(keep) and totals['candidate']>=totals['control'],
                'no_opponent_deficit_over_2':bool(keep) and all(per[o]['points']['candidate']>=per[o]['points']['control']-2 for o in OPPONENTS)}
        views['common_clean' if clean_only else 'all_games']={'seeds':keep,'excluded_maps':excluded,'points':totals,'per_opponent':per,'paired_external_gain':estimate([sum(total('candidate',o,s)-total('control',o,s) for o in OPPONENTS)/6 for s in keep]),'gross_guards':guards}
    return views

def analysis():
    frozen=checked();rows,bindings,timing=read_rows([NAME])
    assert [{k:r[k] for k in ('candidate','opponent','seed','seat')} for r in rows]==frozen['schedule']
    views=summarize(rows);replay=json.loads((OUT/(NAME+'-verification.json')).read_text())
    assert replay['passed'] and replay['matches_sha256']==sha(OUT/NAME/'matches.jsonl') and replay['manifest_sha256']==sha(OUT/NAME/'manifest.json')
    own=timing['candidate']
    for r in own:check_timing(r)
    technical=not any(r['own_failure'] for r in rows);coverage=len(views['common_clean']['seeds'])>=7
    gross=all(all(v['gross_guards'].values()) for v in views.values())
    report={'as_of':now(),'classification':'PROJECT_REPORTED','games':len(rows),'source_sha256':sha(CPP),'freeze_sha256':sha(OUT/'a3-freeze.json'),'amendment_sha256':sha(AMENDMENT),'raw_bindings':bindings,'technical_pass':technical,'clean_coverage_pass':coverage,'gross_guard_pass':gross,'local_guard_pass':technical and coverage and gross,'interpretation':'Small fixed gross-regression guard, NOT independent strength proof; official functional/technical checks and coordinator decision still required','own_failure_games':sum(r['own_failure'] for r in rows),'opponent_only_error_games':sum(r['opponent_failure'] for r in rows),'candidate_telemetry':{'outputs':len(own),'emergencies':sum(r['search']['emergency'] for r in own),'paired_turns':sum(r['search']['paired'] for r in own),'changed_turns':sum(r['search']['selected']>0 for r in own),'selected_tiers':dict(Counter(r['search']['selected_tier'] for r in own)),'changed_tiers':dict(Counter(r['search']['selected_tier'] for r in own if r['search']['selected']>0)),'through_flush_us_max':max(r['through_flush_us'] for r in own),'process_cpu_us_max':max(r['process_cpu_us'] for r in own),'baseline_us_max':max(r['search']['baseline_us'] for r in own)},'replay':replay,'bootstrap':{'seed':20261109,'resamples':10000,'unit':'whole map; both seats/all three opponents/roles kept together'},'budget':budget(),**views}
    save(OUT/'a3-gross-decision.json',report);print(json.dumps(report),flush=True)

def test_analyzer():
    rows=[dict(r,points=.5,own_failure=False,opponent_failure=False,raw_outcome='draw') for r in schedule()]
    assert all(all(v['gross_guards'].values()) for v in summarize(rows).values())
    negative=[dict(r,points=0 if r['candidate']=='candidate' else 1) for r in rows]
    assert not summarize(negative)['all_games']['gross_guards']['external_candidate_at_least_control']
    noisy=[dict(r,opponent_failure=(r['seed']==SEEDS[0] and r['opponent']=='lacoz' and r['seat']==0 and r['candidate']=='candidate')) for r in rows]
    result=summarize(noisy);assert len(result['all_games']['seeds'])==8 and len(result['common_clean']['seeds'])==7
    assert not summarize(rows[:-1])['all_games']['seeds']==list(SEEDS)
    save(OUT/'a3-analyzer-tests.json',{'as_of':now(),'passed':True,'tests':4})

def main():
    stage=sys.argv[1];guard()
    if stage=='freeze':
        assert sha(CPP)==EXPECTED_SHA and json.loads((OUT/'candidate3-package.json').read_text())['passed']
        original.checked_freeze();test_analyzer();assert not (OUT/(NAME+'-maps.json')).exists()
        record={'as_of':now(),'source_sha256':sha(CPP),'identities':identities(),'schedule':schedule(),'maps_generated':False,'amendment_sha256':sha(AMENDMENT),'config':{'deadline_ms':16,'forward_cap':20000,'bits':9,'shallow_then_deep':True,'minimum_common_clean_maps':7,'external_total_deficit_allowed':0,'per_opponent_deficit_allowed':2}}
        save(OUT/'a3-freeze.json',record);print(json.dumps({'source':EXPECTED_SHA,'freeze_sha256':sha(OUT/'a3-freeze.json'),'games':len(record['schedule'])}),flush=True)
    elif stage=='run':run([sys.executable,'-B',rel(CODE/'panel_a3.py'),'execute'],'a3-gross',540)
    elif stage=='execute':
        frozen=checked();hashes=prepare_maps()
        original.commands=commands;original.identities=identities;original.old.metrics=metrics
        original.panel(NAME,frozen['schedule'],hashes);analysis()
    elif stage=='analyze':analysis()
    else:raise ValueError(stage)

if __name__=='__main__':main()
"""Three-way fixed serial panels using the unchanged official referee."""
import argparse
import gzip
import subprocess
from common import *
from maps import classpath,prepare
from run_matches import java_home,COMMIT
from benchmark_public import ENV

frozen_panel=module('v5_panel_readonly',V5CODE/'panel.py')
OPPONENTS=('lacoz','khoufou2','khoufou','v6','bc','league3m','b2m')
CANDIDATES=('candidate','control','teacher')

def commands():
    old=V5/'build/attempt1';public=ROOT/'code/opponents/public';jdk=java_home()
    weights=[rel(p) for p in [ACTOR,CRITIC,*ENEMIES]]
    result={'candidate':[rel(build_dir()/'candidate')],
        'control':[rel(old/'bot'),*weights,'1','0'],'teacher':[rel(old/'bot'),*weights,'4','16'],
        'league3m':[rel(old/'league3m')],'b2m':[rel(old/'b2m')],'v6':[rel(old/'v6')],
        'bc':[rel(old/'bc'),'experiments/rl/2026-11-06-bc-v1/training/weights.txt','2'],
        'lacoz':['code/arena/.venv-lacoz/bin/python','-B','-u',rel(public/'lacoz-7f190183/bot.py')]}
    for label,folder in [('khoufou','khoufou-372c1cd6'),('khoufou2','khoufou-070bc128')]:
        source=public/folder/'Player.java';assert sha(source)==json.loads((source.parent/'PROVENANCE.json').read_text())['sha256']
        result[label]=[str(jdk/'bin/java'),'-cp',rel(old/label),'Player']
    return result

def schedule(seeds):
    result=[]
    for i,seed in enumerate(seeds):
        order=OPPONENTS[i%7:]+OPPONENTS[:i%7]
        for j,opponent in enumerate(order):
            for seat in (i%2,1-i%2):
                k=(i+j+seat)%3;labels=CANDIDATES[k:]+CANDIDATES[:k]
                if (i+j+seat)%2:labels=labels[::-1]
                result.extend({'candidate':c,'opponent':opponent,'seed':seed,'seat':seat} for c in labels)
    return result

def identities():
    package=json.loads((OUT/'package-attempt2.json').read_text())
    paths=[ROOT/package['source'],OUT/'PROTOCOL.md',OUT/'package-attempt2.json',V5/'freeze.json']
    paths+=list(build_dir().glob('*'))+list((V5/'build/attempt1').rglob('*'))
    paths+=[ROOT/p for p in package['dependencies']]
    paths+=list((ROOT/'code/rl/v6/coordinator').glob('*.py'))
    paths+=[V5CODE/p for p in ('panel.py','verify.py','maps.py')]
    return {**sources(),**{rel(p):sha(p) for p in paths if p.is_file()}}

def checked_freeze(path):
    data=json.loads(path.read_text())
    for p,h in data['identities'].items():assert sha(ROOT/p)==h,('Frozen identity changed',p)
    return data

def panel(name,entries,hashes,purpose):
    guard();out=OUT/name;out.mkdir(exist_ok=False);cmds=commands()
    save(out/'manifest.json',{'as_of':now(),'purpose':purpose,'schedule':entries,'commands':cmds,'identities':identities(),
        'referee_commit':COMMIT,'turn_ms':50,'first_turn_ms':1000,'parallel_games':1,'external_spend':0,
        'baseline':'Unchanged league3m actor through the pinned v5 D16 I/O wrapper, proposals1/budget0.',
        'timing_note':'First score token through stdout flush excludes startup/pre-token scheduling; diagnostics measured separately.'})
    save(out/'panel-spec.json',{'purpose':purpose,'schedule':entries,'expected_map_hashes':hashes})
    subprocess.run(['code/arena/.venv-lacoz/bin/python','-B','-c','import numpy,scipy.optimize'],env=ENV,check=True)
    start=time.monotonic();rows=[]
    for item in entries:
        guard();c,o,seed,seat=[item[k] for k in ('candidate','opponent','seed','seat')];stem=f'{c}-vs-{o}-seed{seed}-seat{seat}'
        raw_path=out/(stem+'-raw.json');agents=[cmds[o],cmds[o]];agents[seat]=cmds[c];labels=[o,o];labels[seat]=c
        spec={'seed':seed,'league':3,'agents':agents,'labels':labels,'result':rel(raw_path)}
        invocation=SCRATCH/(name+'-'+stem+'-spec.json');invocation.parent.mkdir(parents=True,exist_ok=True)
        with invocation.open('x') as f:json.dump(spec,f)
        save(out/(stem+'-spec.json'),spec)
        command=[str(java_home()/'bin/java'),'--add-opens','java.base/java.lang=ALL-UNNAMED','-cp',classpath(),'BenchmarkMatch',rel(invocation)]
        began=time.monotonic();result=subprocess.run(command,cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=90)
        with (out/(stem+'.log')).open('x') as f:f.write(clean(result.stdout+result.stderr))
        if not raw_path.exists():
            save(out/'failure.json',{'as_of':now(),'game':item,'returncode':result.returncode,'reason':'No raw result'});raise RuntimeError('No original-referee result')
        raw=json.loads(raw_path.read_text());params=dict(line.split('=',1) for line in ''.join(raw['gameParameters']).splitlines() if '=' in line)
        board={k:[list(map(int,r.split(','))) for r in params[k].split('_') if r] for k in ('nodes','units','edges')}
        digest=hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert str(seed) not in hashes or hashes[str(seed)]==digest,'Map differs from preflight'
        row={**item,'returncode':result.returncode,'wall_seconds':time.monotonic()-began,'map_content_sha256':digest,**frozen_panel.metrics(raw,seat)}
        detail=row['deadline_measurements'];row['emergency']=any(t['search']['emergency'] for t in detail)
        row['timing_coverage_pass']=len(detail)==row['own_output_count']==len(row['post_flush_us'])
        row['internal_margin_pass']=all(t['through_flush_us']<40000 for t in detail)
        with (out/(stem+'.json.gz')).open('xb') as f:f.write(gzip.compress(json.dumps(clean(raw)).encode(),mtime=0))
        rows.append(row)
        with (out/'matches.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush()
        technical=not row['valid'] or row['returncode']!=0 or bool(row['own_action_errors']) or row['emergency'] or not row['timing_coverage_pass'] or not row['internal_margin_pass']
        print(json.dumps({'stage':name,'completed':len(rows),'total':len(entries),'technical_failure':technical,'seconds':time.monotonic()-start}),flush=True)
        if technical:
            save(out/'failure.json',{'as_of':now(),'game':item,'reason':'Frozen technical gate failed; no rerun','row':row});raise RuntimeError('Technical gate failure')
    save(out/'runtime.json',{'as_of':now(),'games':len(rows),'seconds':time.monotonic()-start,'budget':budget()})
    verifier=module('v5_verify_readonly',V5CODE/'verify.py');verifier.verify(name)

def main():
    name=sys.argv[1]
    if name=='regression':
        assert json.loads((OUT/'contracts.json').read_text())['passed']
        entries=[{'candidate':'candidate','opponent':o,'seed':s,'seat':p} for s,o in [(62041,'v6'),(62044,'lacoz'),(62046,'lacoz')] for p in (0,1)]
        panel(name,entries,{},'disclosed_regression_only')
    elif name=='development':
        frozen=checked_freeze(OUT/'development-freeze.json');seeds=list(range(71001,71013))
        hashes=prepare(name,seeds);panel(name,frozen['schedule'],hashes,'fixed_development_admission')
    else:
        assert name in [f'confirm{i}' for i in range(1,11)]
        frozen=checked_freeze(OUT/'final-freeze.json');i=int(name[7:]);seeds=list(range(40001+10*(i-1),40001+10*i))
        hashes=prepare(name,seeds);panel(name,[r for r in frozen['schedule'] if r['seed'] in seeds],hashes,'independent_final')

if __name__=='__main__':main()
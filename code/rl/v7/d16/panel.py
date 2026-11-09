"""Fixed three-way panels, preserving full referee records and technical failures."""
import gzip
from common import *
from maps import classpath, prepare
from run_matches import java_home, COMMIT
from benchmark_public import ENV

old = module('d16_v5_panel', V5CODE/'panel.py')
OPPONENTS = ('lacoz','khoufou2','khoufou','league3m','b2m')
CANDIDATES = ('candidate','control','teacher')

def commands():
    base=V5/'build/attempt1';public=ROOT/'code/opponents/public';jdk=java_home()
    weights=[rel(p) for p in [ACTOR,CRITIC,*ENEMIES]]
    result={'candidate':[rel(build_dir()/'candidate')],
        'control':[rel(base/'bot'),*weights,'1','0'],'teacher':[rel(base/'bot'),*weights,'4','16'],
        'league3m':[rel(base/'league3m')],'b2m':[rel(base/'b2m')],'v6':[rel(base/'v6')],
        'lacoz':['code/arena/.venv-lacoz/bin/python','-B','-u',rel(public/'lacoz-7f190183/bot.py')]}
    for label,folder in [('khoufou','khoufou-372c1cd6'),('khoufou2','khoufou-070bc128')]:
        source=public/folder/'Player.java'; assert sha(source)==json.loads((source.parent/'PROVENANCE.json').read_text())['sha256']
        result[label]=[str(jdk/'bin/java'),'-cp',rel(base/label),'Player']
    return result

def schedule(seeds,opponents=OPPONENTS):
    result=[]
    for i,seed in enumerate(seeds):
        order=opponents[i%len(opponents):]+opponents[:i%len(opponents)]
        for j,opponent in enumerate(order):
            for seat in (i%2,1-i%2):
                k=(i+j+seat)%3;labels=CANDIDATES[k:]+CANDIDATES[:k]
                if (i+j+seat)%2:labels=labels[::-1]
                result.extend({'candidate':c,'opponent':opponent,'seed':seed,'seat':seat} for c in labels)
    return result

def identities():
    paths=[OUT/'package-attempt1/bot.cpp',OUT/'package.json',OUT/'PROTOCOL.md',V5/'freeze.json',V5CODE/'verify.py',V5CODE/'panel.py',ROOT/'code/rl/v6/coordinator/paired.py']
    paths+=list(build_dir().glob('*'))+list((V5/'build/attempt1').rglob('*'))+[ACTOR,CRITIC,*ENEMIES]
    paths+=[ROOT/p for p in json.loads((V6/'package-attempt2.json').read_text())['dependencies']]
    paths+=[ROOT/'code/build'/p for p in ('BenchmarkMatch.class','Oracle.class','MapGenerator.class','libtryangle.dylib','libtryangle_league.dylib')]
    return {**sources(),**{rel(p):sha(p) for p in paths if p.is_file()}}

def checked_freeze():
    frozen=json.loads((OUT/'final-freeze.json').read_text())
    for p,h in frozen['identities'].items():assert sha(ROOT/p)==h,('Frozen identity changed',p)
    return frozen

def panel(name,entries,hashes):
    guard();out=OUT/name;out.mkdir(exist_ok=False);cmds=commands()
    save(out/'manifest.json',{'as_of':now(),'schedule':entries,'commands':cmds,'identities':identities(),'referee_commit':COMMIT,'turn_ms':50,'first_turn_ms':1000,'parallel_games':1,'external_spend':0,'baseline':'Unchanged league3m actor through original verified v5 wrapper, proposals1/budget0. Packaged league3m is also a direct opponent.','timing_note':'Same first-score-token origin through stdout flush; mandatory greedy baseline, optional work16ms cumulative. Not full platform CPU.'})
    subprocess.run(['code/arena/.venv-lacoz/bin/python','-B','-c','import numpy,scipy.optimize'],env=ENV,check=True)
    began=time.monotonic()
    for index,item in enumerate(entries):
        guard(); c,o,seed,seat=[item[k] for k in ('candidate','opponent','seed','seat')];stem=f'{c}-vs-{o}-seed{seed}-seat{seat}'
        raw_path=out/(stem+'-raw.json');agents=[cmds[o],cmds[o]];agents[seat]=cmds[c];labels=[o,o];labels[seat]=c
        spec={'seed':seed,'league':3,'agents':agents,'labels':labels,'result':rel(raw_path)}
        invocation=SCRATCH/(name+'-'+stem+'-spec.json');invocation.parent.mkdir(parents=True,exist_ok=True)
        with invocation.open('x') as f:json.dump(spec,f)
        save(out/(stem+'-spec.json'),spec)
        command=[str(java_home()/'bin/java'),'--add-opens','java.base/java.lang=ALL-UNNAMED','-cp',classpath(),'BenchmarkMatch',rel(invocation)]
        start=time.monotonic();result=subprocess.run(command,cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=90)
        with (out/(stem+'.log')).open('x') as f:f.write(clean(result.stdout+result.stderr))
        if not raw_path.exists():
            save(out/'failure.json',{'as_of':now(),'game':item,'returncode':result.returncode,'reason':'No original-referee raw result'});raise RuntimeError('Missing raw result')
        raw=json.loads(raw_path.read_text());props=dict(s.split('=',1) for s in ''.join(raw['gameParameters']).splitlines() if '=' in s)
        board={k:[list(map(int,r.split(','))) for r in props[k].split('_') if r] for k in ('nodes','units','edges')}
        digest=hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert str(seed) not in hashes or hashes[str(seed)]==digest
        row={**item,'returncode':result.returncode,'wall_seconds':time.monotonic()-start,'map_content_sha256':digest,**old.metrics(raw,seat)}
        details=row['deadline_measurements'];row['emergency']=any(t['search']['emergency'] for t in details)
        row['baseline_complete_pass']=c!='candidate' or all(t['search'].get('baseline_complete')==1 for t in details)
        row['timing_coverage_pass']=len(details)==row['own_output_count']==len(row['post_flush_us'])
        row['internal_margin_pass']=all(t['through_flush_us']<40000 for t in details)
        row['raw_sha256']=sha(raw_path)
        with (out/(stem+'.json.gz')).open('xb') as f:f.write(gzip.compress(json.dumps(clean(raw)).encode(),mtime=0))
        with (out/'matches.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush()
        failure=not row['valid'] or bool(result.returncode or row['own_action_errors'] or row['emergency']) or not all(row[k] for k in ('baseline_complete_pass','timing_coverage_pass','internal_margin_pass'))
        print(json.dumps({'stage':name,'completed':index+1,'total':len(entries),'technical_failure':failure,'seconds':time.monotonic()-began}),flush=True)
        if failure:
            save(out/'failure.json',{'as_of':now(),'game':item,'reason':'Prospective technical gate failure; no replay/replacement','row':row});raise RuntimeError('Technical gate failed')
    save(out/'runtime.json',{'as_of':now(),'games':len(entries),'seconds':time.monotonic()-began,'budget':budget()})
    verifier=module('d16_v5_verify',V5CODE/'verify.py');verifier.verify(name)

def main():
    name=sys.argv[1]
    if name=='regression':
        assert json.loads((OUT/'contracts.json').read_text())['passed']
        entries=[{'candidate':'candidate','opponent':o,'seed':s,'seat':p} for s,o in [(62041,'v6'),(62044,'lacoz'),(62046,'lacoz')] for p in (0,1)]
        panel(name,entries,{})
    elif name=='development':
        seeds=list(range(72001,72005));panel(name,schedule(seeds,OPPONENTS[:3]),prepare(name,seeds))
    elif name=='freeze':
        assert json.loads((OUT/'regression-verification.json').read_text())['passed'] and json.loads((OUT/'development-verification.json').read_text())['passed']
        frozen={'as_of':now(),'identities':identities(),'schedule':schedule(list(range(72101,72141))),'source_sha256':sha(OUT/'package-attempt1/bot.cpp'),'config':{'bits':9,'mandatory_baseline':True,'optional_ms':16,'forward_cap':20000},'maps_generated':False}
        save(OUT/'final-freeze.json',frozen);print(json.dumps({'freeze_sha256':sha(OUT/'final-freeze.json'),'games':len(frozen['schedule'])}))
    else:
        assert name in ('confirm1','confirm2','confirm3','confirm4');frozen=checked_freeze();n=int(name[-1]);seeds=list(range(72101+(n-1)*10,72111+(n-1)*10))
        panel(name,[r for r in frozen['schedule'] if r['seed'] in seeds],prepare(name,seeds))

if __name__=='__main__':main()
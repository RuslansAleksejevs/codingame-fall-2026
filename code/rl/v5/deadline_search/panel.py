"""Serial original-referee games, with immutable schedule and full raw stderr."""
import argparse
import gzip
import os
import re
import subprocess
from common import *
from maps import classpath, prepare
from run_matches import java_home, COMMIT
from benchmark_public import ENV, NORMAL_ENDS

OPPONENTS=('lacoz','khoufou2','khoufou','v6','bc','league3m','b2m')


def commands():
    build=build_dir();public=ROOT/'code/opponents/public';jdk=java_home()
    result={
        'search':[rel(build/'bot'),*[rel(p) for p in [ACTOR,CRITIC,*ENEMIES]],'4','16'],
        'control':[rel(build/'bot'),*[rel(p) for p in [ACTOR,CRITIC,*ENEMIES]],'1','0'],
        'league3m':[rel(build/'league3m')], 'b2m':[rel(build/'b2m')], 'v6':[rel(build/'v6')],
        'bc':[rel(build/'bc'),'experiments/rl/2026-11-06-bc-v1/training/weights.txt','2'],
        'lacoz':['code/arena/.venv-lacoz/bin/python','-B','-u',rel(public/'lacoz-7f190183/bot.py')],
    }
    for label,folder in [('khoufou','khoufou-372c1cd6'),('khoufou2','khoufou-070bc128')]:
        source=public/folder/'Player.java';meta=json.loads((source.parent/'PROVENANCE.json').read_text())
        assert sha(source)==meta['sha256']
        target=build/label
        if not target.exists():
            target.mkdir();run([str(jdk/'bin/javac'),'-d',rel(target),rel(source)],label+'-build')
        result[label]=[str(jdk/'bin/java'),'-cp',rel(target),'Player']
    return result


def schedule(seeds,opponents=OPPONENTS):
    rows=[]
    for i,seed in enumerate(seeds):
        rotate=i%len(opponents);order=opponents[rotate:]+opponents[:rotate]
        for j,opponent in enumerate(order):
            for seat in (i%2,1-i%2):
                for candidate in (('search','control') if (i+j+seat)%2==0 else ('control','search')):
                    rows.append({'candidate':candidate,'opponent':opponent,'seed':seed,'seat':seat})
    return rows


def metrics(raw,seat):
    summaries=''.join(x or '' for x in raw.get('summaries',[]))
    messages=[re.findall(r'\$'+str(p)+r': ([^\n]+)',summaries) for p in (0,1)]
    errors=[[s for s in row if s not in NORMAL_ENDS] for row in messages]
    scores=raw.get('scores',{});own=scores.get(str(seat));other=scores.get(str(1-seat))
    referee=[s for s in raw.get('errors',{}).get('referee',[]) if s]
    valid=own is not None and other is not None and not raw.get('failCause') and not referee
    stderr=''.join(s or '' for s in raw.get('errors',{}).get(str(seat),[]))
    details=[]
    for line in stderr.splitlines():
        if line.startswith('deadline='):details.append(json.loads(line.split('=',1)[1]))
    return {'valid':bool(valid),'outcome':('win' if own>other else 'loss' if own<other else 'draw') if valid else 'invalid',
        'score':own,'opponent_score':other,'own_action_errors':errors[seat],'opponent_action_errors':errors[1-seat],
        'referee_errors':referee,'fail_cause':raw.get('failCause'),
        'own_plan_us':list(map(int,re.findall(r'plan_us=(\d+)',stderr))),
        'deadline_measurements':details,'post_flush_us':list(map(float,re.findall(r'post_flush_us=([0-9.]+)',stderr))),
        'own_output_count':sum(bool(s) for s in raw.get('outputs',{}).get(str(seat),[]))}


def panel(name,entries,hashes,purpose):
    guard();out=OUT/name;out.mkdir(exist_ok=False);cmds=commands()
    cp=classpath();jdk=java_home()
    dependency_paths=[ROOT/'code/build/BenchmarkMatch.class',ROOT/'code/build/Oracle.class',
        ROOT/'code/build/MapGenerator.class',ROOT/'code/build/libtryangle.dylib',ROOT/'code/build/libtryangle_league.dylib']
    save(out/'manifest.json',{'as_of':now(),'purpose':purpose,'schedule':entries,'commands':cmds,
        'sources':sources(),'weights':{rel(p):sha(p) for p in {ACTOR,CRITIC,*ENEMIES}},
        'dependency_sha256':{rel(p):sha(p) for p in dependency_paths},
        'referee_commit':COMMIT,'turn_ms':50,'first_turn_ms':1000,'parallel_games':1,'external_spend':0,
        'baseline':'Same executable and I/O; unchanged greedy league3m actor, no search/time cap.',
        'timing_note':'Raw stderr parsed by turn, not output frame: stdout is intentionally flushed first.'})
    save(out/'panel-spec.json',{'purpose':purpose,'schedule':entries,'expected_map_hashes':hashes})
    subprocess.run(['code/arena/.venv-lacoz/bin/python','-B','-c','import numpy,scipy.optimize'],env=ENV,check=True)
    start=time.monotonic();rows=[]
    for index,item in enumerate(entries):
        guard();c,o,seed,seat=[item[k] for k in ('candidate','opponent','seed','seat')]
        stem=f'{c}-vs-{o}-seed{seed}-seat{seat}'
        raw_path=out/(stem+'-raw.json');sp=out/(stem+'-spec.json')
        agents=[cmds[o],cmds[o]];agents[seat]=cmds[c];labels=[o,o];labels[seat]=c
        spec={'seed':seed,'league':3,'agents':agents,'labels':labels,'result':rel(raw_path)}
        # All process paths are repository-relative except the installed JDK;
        # portable copies normalize that environment dependency explicitly.
        invocation=SCRATCH/(name+'-'+stem+'-spec.json');invocation.parent.mkdir(parents=True,exist_ok=True)
        with invocation.open('x') as f:json.dump(spec,f)
        save(sp,clean(spec))
        command=[str(jdk/'bin/java'),'--add-opens','java.base/java.lang=ALL-UNNAMED','-cp',cp,'BenchmarkMatch',rel(invocation)]
        began=time.monotonic();result=subprocess.run(command,cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=90)
        with (out/(stem+'.log')).open('x') as f:f.write(clean(result.stdout+result.stderr))
        if not raw_path.exists():
            save(out/'failure.json',{'as_of':now(),'game':item,'returncode':result.returncode,'reason':'No result'})
            raise RuntimeError('Original referee produced no result: '+stem)
        raw=json.loads(raw_path.read_text());parameters=dict(line.split('=',1) for line in ''.join(raw['gameParameters']).splitlines() if '=' in line)
        board={k:[list(map(int,row.split(','))) for row in parameters[k].split('_') if row] for k in ('nodes','units','edges')}
        digest=hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert str(seed) not in hashes or hashes[str(seed)]==digest,'Map differs from preflight content'
        row={**item,'returncode':result.returncode,'wall_seconds':time.monotonic()-began,'map_content_sha256':digest,**metrics(raw,seat)}
        with (out/(stem+'.json.gz')).open('xb') as f:f.write(gzip.compress(json.dumps(clean(raw)).encode(),mtime=0))
        # Preserve exact raw original as well; do not unlink failed or baseline files.
        rows.append(row)
        with (out/'matches.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush()
        technical=not row['valid'] or row['returncode']!=0 or bool(row['own_action_errors'])
        print(json.dumps({'stage':name,'completed':len(rows),'total':len(entries),'own_technical_failure':technical,
            'opponent_errors':row['opponent_action_errors'],'seconds':time.monotonic()-start}),flush=True)
        if technical:
            save(out/'failure.json',{'as_of':now(),'game':item,'reason':'Frozen zero-own/control-error gate failed','row':row})
            raise RuntimeError('Own/control technical gate failed; stop without rerun')
    save(out/'runtime.json',{'as_of':now(),'games':len(rows),'seconds':time.monotonic()-start,'budget':budget()})
    return rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['regression','development','confirm1','confirm2','confirm3','confirm4']);args=ap.parse_args()
    if args.stage=='regression':
        entries=[{'candidate':'search','opponent':o,'seed':s,'seat':p} for s,o in [(62041,'v6'),(62044,'lacoz'),(62046,'lacoz')] for p in (0,1)]
        panel(args.stage,entries,{},'disclosed_regression')
    elif args.stage=='development':
        seeds=list(range(70001,70005));hashes=prepare(args.stage,seeds)
        panel(args.stage,schedule(seeds,OPPONENTS[:3]),hashes,'technical_development')
    else:
        frozen=json.loads((OUT/'freeze.json').read_text())
        for p,h in frozen['sources'].items():assert sha(ROOT/p)==h,'Frozen source changed: '+p
        for p,h in frozen['weights'].items():assert sha(ROOT/p)==h,'Frozen weights changed'
        for p,h in {**frozen['binaries'],**frozen['dependencies']}.items():assert sha(ROOT/p)==h,'Frozen dependency changed: '+p
        assert sha(OUT/'PROTOCOL.md')==frozen['protocol_sha256']
        n=int(args.stage[-1]);seeds=list(range(70101+(n-1)*10,70111+(n-1)*10))
        hashes=prepare(args.stage,seeds)
        entries=[r for r in frozen['schedule'] if r['seed'] in seeds]
        panel(args.stage,entries,hashes,'independent_confirmation')


if __name__=='__main__':main()
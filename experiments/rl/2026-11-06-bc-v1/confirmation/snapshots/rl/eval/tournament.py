#!/usr/bin/env python3
"""Frozen BC/v6 panel in the original timed referee; serial, paired, both seats."""
import argparse
from collections import Counter
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE,REPO,COMMIT,java_home
from benchmark_public import ENV,analyze,summarize

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def cleanpath(value):
    if isinstance(value,str):return value.replace(str(BASE),'${PROJECT_ROOT}').replace(str(Path.home()),'${HOME}')
    if isinstance(value,list):return [cleanpath(x) for x in value]
    if isinstance(value,dict):return {k:cleanpath(v) for k,v in value.items()}
    return value

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--weights',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--seeds',default='6001:6050');ap.add_argument('--smoke',action='store_true');args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);snap=out/'snapshots';snap.mkdir()
    # Executables are local caches; sources and weights are preserved and hashed.
    shutil.copytree(BASE/'code/rl',snap/'rl',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(BASE/'code/variants/v6-attack.cpp',snap/'v6.cpp');shutil.copy2(args.weights,snap/'weights.txt')
    (snap/'build').mkdir()
    for name,source,opt in [('bc',snap/'rl/export/bot.cpp','-O3'),('v6',snap/'v6.cpp','-O2')]:
        subprocess.run(['clang++','-std=c++17',opt,'-Wall','-Wextra','-Wpedantic',str(source),'-o',str(snap/'build'/name)],check=True)
    jdk=java_home();public=BASE/'code/opponents/public'
    for name,folder,source in [('lacoz','lacoz-7f190183','bot.py'),('khoufou','khoufou-372c1cd6','Player.java')]:
        root=public/folder;meta=json.loads((root/'PROVENANCE.json').read_text());assert sha(root/source)==meta['sha256']
        shutil.copytree(root,snap/name,ignore=shutil.ignore_patterns('__pycache__'))
    py=BASE/'code/arena/.venv-lacoz/bin/python'
    commands={'bc':[str(snap/'build/bc'),str(snap/'weights.txt'),'2'],'v6':[str(snap/'build/v6')],
              'lacoz':[str(py),'-u',str(snap/'lacoz/bot.py')],'khoufou':[str(jdk/'bin/java'),'-cp',str(snap/'khoufou/build'),'Player']}
    cp=str(BASE/'code/build')+':'+str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()
    lo,hi=map(int,args.seeds.split(':'));pairs=[('bc','lacoz'),('v6','lacoz'),('bc','khoufou'),('v6','khoufou'),('bc','v6')]
    dataset=json.loads((BASE/'experiments/rl/2026-11-06-bc-v1/dataset.json').read_text());seen=set(dataset['maps'])
    manifest={'as_of':datetime.now(timezone.utc).isoformat(),'provenance':'PROJECT_REPORTED','referee_commit':COMMIT,'league':3,'turn_ms':50,'first_turn_ms':1000,'parallel_games':1,'seeds':list(range(lo,hi+1)),'seats':[0,1],'pairs':pairs,'weights_sha256':sha(snap/'weights.txt'),
              'source_sha256':{str(p.relative_to(snap)):sha(p) for p in sorted(snap.rglob('*')) if p.is_file() and 'build' not in p.relative_to(snap).parts},
              'binary_sha256':{n:sha(snap/'build'/n) for n in ('bc','v6')},'compiler':subprocess.run(['clang++','--version'],capture_output=True,text=True).stdout,'commands':cleanpath(commands),'environment':{k:ENV[k] for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS')},'external_spend':0,'live_submission':False,'method':'Serial original-referee matches; interleaved candidate/control on identical seeds and both seats; no checkpoint changes during the panel. Opponent wall-time search can vary across reruns.'}
    save(out/'manifest.json',manifest);subprocess.run([str(py),'-c','import numpy,scipy.optimize'],env=ENV,check=True)
    rows=[];maphashes={};start=time.monotonic()
    for seed in range(lo,hi+1):
        for candidate,opponent in pairs:
            for seat in (0,1):
                stem=f'{candidate}-vs-{opponent}-seed{seed}-seat{seat}';path=out/(stem+'.json');sp=out/(stem+'-spec.json')
                agents=[commands[opponent],commands[opponent]];agents[seat]=commands[candidate];labels=[opponent,opponent];labels[seat]=candidate
                save(sp,{'seed':seed,'league':3,'agents':agents,'labels':labels,'result':str(path)})
                command=[str(jdk/'bin/java'),'--add-opens','java.base/java.lang=ALL-UNNAMED','-cp',cp,'BenchmarkMatch',str(sp)]
                began=time.monotonic()
                with (out/(stem+'.log')).open('w') as log:
                    proc=subprocess.run(command,cwd=REPO,env=ENV,stdout=log,stderr=subprocess.STDOUT,timeout=90)
                if not path.exists():raise RuntimeError(f'No result: {stem}')
                result=json.loads(path.read_text());metrics=analyze(result,seat)
                params={k:v for line in ''.join(result['gameParameters']).splitlines() if '=' in line for k,v in [line.split('=',1)]}
                data={k:[list(map(int,r.split(','))) for r in params[k].split('_') if r] for k in ('nodes','units','edges')}
                key=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                if key in seen and not args.smoke:raise RuntimeError(f'Confirmation map overlaps training/validation: {seed}')
                if seed in maphashes and maphashes[seed]!=key:raise RuntimeError('Paired map mismatch')
                maphashes[seed]=key
                row={'candidate':candidate,'opponent':opponent,'seed':seed,'seat':seat,'returncode':proc.returncode,'wall_seconds':time.monotonic()-began,'map_content_sha256':key,**metrics}
                rows.append(row)
                with (out/'matches.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
                with gzip.GzipFile(filename=str(out/(stem+'.json.gz')),mode='wb',mtime=0) as f:f.write(json.dumps(cleanpath(result)).encode())
                path.unlink()
                if len(rows)%10==0 or row['own_action_errors'] or row['opponent_action_errors'] or not row['valid']:
                    print(f'{len(rows)}/{(hi-lo+1)*10} {stem}: {row["outcome"]} {row["score"]}:{row["opponent_score"]}; own errors={row["own_action_errors"]}; opponent errors={row["opponent_action_errors"]}; {time.monotonic()-start:.1f}s',flush=True)
                if args.smoke and row['own_action_errors']:raise RuntimeError('Candidate smoke failure; records preserved')
        save(out/'summary.json',{c:summarize([r for r in rows if r['candidate']==c]) for c in ('bc','v6')})
    save(out/'map-hashes.json',maphashes);save(out/'runtime.json',{'wall_seconds':time.monotonic()-start,'games':len(rows),'external_spend':0})
    print(json.dumps({c:{o:dict(Counter(r['outcome'] for r in rows if r['candidate']==c and r['opponent']==o)) for o in ('v6','lacoz','khoufou')} for c in ('bc','v6')},indent=2),flush=True)
if __name__=='__main__':main()

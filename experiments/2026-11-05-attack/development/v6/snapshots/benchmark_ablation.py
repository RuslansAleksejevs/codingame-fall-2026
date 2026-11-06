#!/usr/bin/env python3
"""Interleave frozen variants on paired maps; preserve every outcome."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from benchmark_public import BASE, REPO, COMMIT, PUBLIC, ENV, analyze, summarize, save, sha, java_home


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--variants',nargs='+',required=True,help='label=source.cpp')
    parser.add_argument('--seeds',required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--map-context',choices=['fresh','reused'],default='fresh')
    args=parser.parse_args()
    root=args.out.resolve();root.mkdir(parents=True,exist_ok=False)
    lo,hi=map(int,args.seeds.split(':'));seeds=list(range(lo,hi+1))
    jdk=java_home();py=BASE/'code/arena/.venv-lacoz/bin/python'
    cp=str(BASE/'code/build')+os.pathsep+str(REPO/'target/classes')+os.pathsep+(REPO/'classpath.txt').read_text().strip()
    versions={}
    compiler=subprocess.run(['clang++','--version'],capture_output=True,text=True,check=True).stdout
    java=subprocess.run([str(jdk/'bin/java'),'-version'],capture_output=True,text=True,check=True).stderr
    packages=subprocess.run([str(py),'-m','pip','freeze'],capture_output=True,text=True,check=True).stdout
    python=subprocess.run([str(py),'--version'],capture_output=True,text=True,check=True).stdout
    for item in args.variants:
        label,source=item.split('=',1)
        if not label.replace('-','').isalnum():raise ValueError('Invalid variant label')
        out=root/label;snap=out/'snapshots';snap.mkdir(parents=True)
        shutil.copy2(Path(source).resolve(),snap/'candidate.cpp')
        compile_command=['clang++','-std=c++17','-O2','-Wall','-Wextra','-Wpedantic',str(snap/'candidate.cpp'),'-o',str(snap/'candidate')]
        with (out/'compile.log').open('w') as log:
            subprocess.run(compile_command,stdout=log,stderr=subprocess.STDOUT,check=True)
        for name,folder in [('khoufou','khoufou-372c1cd6'),('lacoz','lacoz-7f190183')]:
            shutil.copytree(PUBLIC/folder,snap/name)
        for file in [Path(__file__),BASE/'code/benchmark_public.py',BASE/'code/arena/BenchmarkMatch.java']:
            shutil.copy2(file,snap/file.name)
        commands={'khoufou':[str(jdk/'bin/java'),'-cp',str(snap/'khoufou/build'),'Player'],
                  'lacoz':[str(py),'-u',str(snap/'lacoz/bot.py')]}
        opponents={n:json.loads((snap/n/'PROVENANCE.json').read_text()) for n in commands}
        for name,meta in opponents.items():assert sha(snap/name/meta['original_file'])==meta['sha256']
        manifest={'as_of':datetime.now(timezone.utc).isoformat(),'provenance':'PROJECT_REPORTED',
                  'referee_commit':COMMIT,'league':3,'max_turn_ms':50,'first_turn_ms':1000,
                  'timing_limits_source':'unmodified core4.1.6 GameManager constructor, previously verified by javap',
                  'seeds':seeds,'seats':[0,1],'parallel_games':1,'candidate_label':label,
                  'candidate_source_sha256':sha(snap/'candidate.cpp'),'candidate_binary_sha256':sha(snap/'candidate'),
                  'compile_command':compile_command,'compiler':compiler,'java':java,'python':python,'python_packages':packages,
                  'opponents':opponents,'commands':commands,
                  'environment':{k:ENV[k] for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS')},
                  'warmup':'one NumPy/SciPy import before all matches',
                  'map_context':args.map_context,
                  'method':args.map_context+' seeds; interleaved variants on each map/seat/opponent; rotated variant order; every outcome retained, including timeouts',
                  'external_spend':0,'live_contest_submission':False}
        save(out/'manifest.json',manifest)
        versions[label]={'out':out,'snap':snap,'commands':commands,'rows':[]}
    subprocess.run([str(py),'-c','import numpy,scipy.optimize'],env=ENV,check=True)
    labels=list(versions)
    save(root/'schedule.json',{'as_of':datetime.now(timezone.utc).isoformat(),'variants':labels,'seeds':seeds,
                              'seats':[0,1],'opponents':['khoufou','lacoz'],
                              'order':'seed, seat, opponent; rotate variants by (seed_index+seat+opponent_index)%variant_count',
                              'planned_games':len(seeds)*4*len(labels),'map_context':args.map_context,
                              'purpose':'paired feature comparison; code frozen before this run; previous results on reused maps are already known'})
    completed=0
    for seed_index,seed in enumerate(seeds):
        for seat in (0,1):
            for oi,opponent in enumerate(['khoufou','lacoz']):
                start=(seed_index+seat+oi)%len(labels)
                for label in labels[start:]+labels[:start]:
                    entry=versions[label];out,snap=entry['out'],entry['snap']
                    stem=f'{opponent}-seed{seed}-seat{seat}';path=out/(stem+'.json')
                    agents=[entry['commands'][opponent],entry['commands'][opponent]]
                    agents[seat]=[str(snap/'candidate')]
                    players=[opponent,opponent];players[seat]=label
                    spec={'seed':seed,'league':3,'agents':agents,'labels':players,'result':str(path)}
                    sp=out/(stem+'-spec.json');save(sp,spec)
                    command=[str(jdk/'bin/java'),'--add-opens','java.base/java.lang=ALL-UNNAMED','-cp',cp,'BenchmarkMatch',str(sp)]
                    started=time.monotonic()
                    with (out/(stem+'.log')).open('w') as log:
                        proc=subprocess.run(command,cwd=REPO,env=ENV,stdout=log,stderr=subprocess.STDOUT,timeout=90)
                    if not path.exists():raise RuntimeError(f'{label}/{stem}: no referee result')
                    result=json.loads(path.read_text())
                    row={'opponent':opponent,'seed':seed,'seat':seat,'returncode':proc.returncode,
                         'wall_seconds':round(time.monotonic()-started,3),'command':command,**analyze(result,seat)}
                    with gzip.open(out/(stem+'.json.gz'),'wt') as f:json.dump(result,f)
                    path.unlink();entry['rows'].append(row)
                    with (out/'matches.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
                    completed+=1
                    if not row['valid'] or row['own_action_errors'] or row['opponent_action_errors']:
                        print('CHECK',label,stem,row['own_action_errors'],row['opponent_action_errors'],flush=True)
        if (seed_index+1)%5==0 or seed==hi:
            status={name:{o:dict(Counter(r['outcome'] for r in v['rows'] if r['opponent']==o and not r['own_action_errors'] and not r['opponent_action_errors'])) for o in ['khoufou','lacoz']} for name,v in versions.items()}
            print('GAMES',completed,'MAPS',seed_index+1,json.dumps(status),flush=True)
        for entry in versions.values():save(entry['out']/'summary.json',summarize(entry['rows']))
    save(root/'completion.json',{'completed_at':datetime.now(timezone.utc).isoformat(),'games':completed,'maps':len(seeds),'external_spend':0})


if __name__=='__main__':main()

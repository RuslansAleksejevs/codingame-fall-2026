#!/usr/bin/env python3
"""Named frozen-policy panel in the original timed referee; serial, paired, both seats."""
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
    ap=argparse.ArgumentParser();ap.add_argument('--spec',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);args=ap.parse_args()
    spec=json.loads(args.spec.read_text());pairs=spec['pairs'];seeds=spec['seeds'];purpose=spec['purpose'];assert purpose in ('development','confirmation','smoke')
    stop_at=datetime.fromisoformat(spec['stop_at'].replace('Z','+00:00')) if spec.get('stop_at') else None
    variants={name:spec.get('policy_variants',{}).get(name,'standard') for name in spec['policies']}
    assert set(spec.get('policy_variants',{}))<=set(spec['policies'])
    assert set(variants.values())<={'standard','roads','search','packaged'}
    search_configs=spec.get('search_configs',{})
    assert set(search_configs)=={name for name,variant in variants.items() if variant=='search'}
    packaged_configs=spec.get('packaged_configs',{})
    assert set(packaged_configs)=={name for name,variant in variants.items() if variant=='packaged'}
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);snap=out/'snapshots';snap.mkdir()
    # Executables are local caches; sources and weights are preserved and hashed.
    for relative in ('models/policy.hpp','sim/simulator.hpp','export/bot.cpp'):
        target=snap/'rl'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE/'code/rl'/relative,target)
    for relative in ('code/rl/eval/panel.py','code/benchmark_public.py','code/run_matches.py','code/arena/BenchmarkMatch.java'):
        target=snap/'harness'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE/relative,target)
    shutil.copy2(BASE/'code/variants/v6-attack.cpp',snap/'v6.cpp');(snap/'weights').mkdir()
    for name,path in spec['policies'].items():
        assert name.replace('_','').replace('-','').isalnum() and name not in ('v6','lacoz','khoufou','khoufou2')
        shutil.copy2(BASE/path,snap/'weights'/(name+'.txt'))
    (snap/'build').mkdir()
    builds=[('bc',snap/'rl/export/bot.cpp','-O3'),('v6',snap/'v6.cpp','-O2')]
    if packaged_configs:
        (snap/'packaged').mkdir()
        for name,configuration in packaged_configs.items():
            package_path=BASE/configuration['manifest'];package=json.loads(package_path.read_text())
            source=BASE/package['source_path']
            assert package['action_profile']=='full' and not package['external_files_required']
            assert package['source_utf16_units']<100000 and package['float32_parameters']==24833
            assert package['weights_sha256']==sha(snap/'weights'/(name+'.txt'))
            assert package['source_sha256']==sha(source)
            shutil.copy2(source,snap/'packaged'/(name+'.cpp'))
            shutil.copy2(package_path,snap/'packaged'/(name+'-manifest.json'))
            builds.append(('package-'+name,snap/'packaged'/(name+'.cpp'),'-O3'))
    if search_configs:
        for relative in ('search/search.hpp','search/bot.cpp','league/rollout_league.cpp','export/inference.hpp'):
            target=snap/'rl'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE/'code/rl'/relative,target)
        builds.append(('search',snap/'rl/search/bot.cpp','-O3'))
        for name,configuration in search_configs.items():
            assert len(configuration['responses'])==3
            assert configuration['depth'] in (1,2) and configuration['candidates'] in (1,4)
            assert 0<=configuration['budget_ms']<=30
            for suffix,path in [('critic',configuration['critic']),*[(f'response{i}',path) for i,path in enumerate(configuration['responses'])]]:
                shutil.copy2(BASE/path,snap/'weights'/f'{name}-{suffix}.txt')
    if 'roads' in variants.values():
        for name in ('policy.hpp','bot.cpp'):
            target=snap/'road-variant/roads'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE/'code/rl/roads'/name,target)
        target=snap/'road-variant/sim/simulator.hpp';target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE/'code/rl/sim/simulator.hpp',target)
        builds.append(('roads',snap/'road-variant/roads/bot.cpp','-O3'))
    for name,source,opt in builds:
        subprocess.run(['clang++','-std=c++17',opt,'-Wall','-Wextra','-Wpedantic',str(source),'-o',str(snap/'build'/name)],check=True)
    jdk=java_home();public=BASE/'code/opponents/public'
    public_sources=[('lacoz','lacoz-7f190183','bot.py'),('khoufou','khoufou-372c1cd6','Player.java')]
    if any('khoufou2' in pair for pair in pairs):public_sources.append(('khoufou2','khoufou-070bc128','Player.java'))
    for name,folder,source in public_sources:
        root=public/folder;meta=json.loads((root/'PROVENANCE.json').read_text());assert sha(root/source)==meta['sha256']
        shutil.copytree(root,snap/name,ignore=shutil.ignore_patterns('__pycache__'))
    py=BASE/'code/arena/.venv-lacoz/bin/python'
    commands={'v6':[str(snap/'build/v6')],
              'lacoz':[str(py),'-u',str(snap/'lacoz/bot.py')],'khoufou':[str(jdk/'bin/java'),'-cp',str(snap/'khoufou/build'),'Player']}
    if any('khoufou2' in pair for pair in pairs):commands['khoufou2']=[str(jdk/'bin/java'),'-cp',str(snap/'khoufou2/build'),'Player']
    for name in spec['policies']:
        variant=variants[name]
        if variant=='packaged':
            commands[name]=[str(snap/'build'/('package-'+name))]
        elif variant=='search':
            cfg=search_configs[name]
            commands[name]=[str(snap/'build/search'),str(snap/'weights'/(name+'.txt')),*[str(snap/'weights'/f'{name}-{suffix}.txt') for suffix in ('critic','response0','response1','response2')],str(cfg['depth']),str(cfg['candidates']),str(cfg['budget_ms'])]
        else:commands[name]=[str(snap/'build'/('roads' if variant=='roads' else 'bc')),str(snap/'weights'/(name+'.txt')),'3' if variant=='roads' else '2']
    assert all(c in commands and o in commands for c,o in pairs)
    for name,_,source in public_sources:
        if source.endswith('.java'):subprocess.run([str(jdk/'bin/javac'),'-d',str(snap/name/'build'),str(snap/name/source)],check=True)
    cp=str(BASE/'code/build')+':'+str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()
    candidates=sorted(set(c for c,o in pairs));total_games=len(seeds)*len(pairs)*2
    seen=set();seen_legacy=set()
    for path in spec.get('exclude_map_hash_files',[]):
        registry=json.loads((BASE/path).read_text());seen.update(registry['canonical']);seen_legacy.update(registry.get('legacy',[]))
    for path in spec.get('exclude_map_manifests',[]):
        data=json.loads((BASE/path).read_text())
        for part in ('training','selection'):
            seen.update(v['hash'] for v in data.get(part,[]))
    for path in ('experiments/rl/2026-11-06-bc-v1/confirmation/map-hashes.json','experiments/rl/2026-11-06-ppo-v1/confirmation/map-hashes.json'):
        seen.update(json.loads((BASE/path).read_text()).values())
    manifest={'as_of':datetime.now(timezone.utc).isoformat(),'provenance':'PROJECT_REPORTED','referee_commit':COMMIT,'league':3,'turn_ms':50,'first_turn_ms':1000,'parallel_games':1,'seeds':seeds,'purpose':purpose,'seats':[0,1],'pairs':pairs,'policy_weights_sha256':{name:sha(snap/'weights'/(name+'.txt')) for name in spec['policies']},
              'source_sha256':{str(p.relative_to(snap)):sha(p) for p in sorted(snap.rglob('*')) if p.is_file() and 'build' not in p.relative_to(snap).parts},
              'binary_sha256':{n:sha(snap/'build'/n) for n,_,_ in builds},'policy_variants':variants,'compiler':subprocess.run(['clang++','--version'],capture_output=True,text=True).stdout,'commands':cleanpath(commands),'environment':{k:ENV[k] for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS')},'external_spend':0,'live_submission':False,'method':'Serial original-referee matches; interleaved candidate/control on identical seeds and both seats; no checkpoint changes during the panel. Opponent wall-time search can vary across reruns.'}
    manifest['execution_order']='Cyclic pair rotation and alternating seat order by seed index' if spec.get('rotate_order',False) else 'Listed pair order; seat 0 then seat 1'
    manifest['benchmark_class_sha256']=sha(BASE/'code/build/BenchmarkMatch.class')
    manifest['java_version']=subprocess.run([str(jdk/'bin/java'),'-version'],capture_output=True,text=True).stderr
    save(out/'panel-spec.json',spec)
    save(out/'manifest.json',manifest);subprocess.run([str(py),'-c','import numpy,scipy.optimize'],env=ENV,check=True)
    rows=[];maphashes={};start=time.monotonic()
    for seed_index,seed in enumerate(seeds):
        offset=seed_index%len(pairs) if spec.get('rotate_order',False) else 0
        ordered_pairs=pairs[offset:]+pairs[:offset]
        ordered_seats=(seed_index%2,1-seed_index%2) if spec.get('rotate_order',False) else (0,1)
        for candidate,opponent in ordered_pairs:
            for seat in ordered_seats:
                if stop_at and datetime.now(timezone.utc)>=stop_at:raise RuntimeError('Panel cutoff reached; completed records preserved')
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
                legacy=hashlib.sha256(json.dumps({k:v for k,v in params.items() if k!='seed'},sort_keys=True).encode()).hexdigest()
                if (key in seen or legacy in seen_legacy) and (purpose=='confirmation' or spec.get('require_new_maps',False)):raise RuntimeError(f'Map overlaps training/validation: {seed}')
                if seed in maphashes and maphashes[seed]!=key:raise RuntimeError('Paired map mismatch')
                maphashes[seed]=key
                row={'candidate':candidate,'opponent':opponent,'seed':seed,'seat':seat,'returncode':proc.returncode,'wall_seconds':time.monotonic()-began,'map_content_sha256':key,**metrics}
                rows.append(row)
                with (out/'matches.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
                with gzip.GzipFile(filename=str(out/(stem+'.json.gz')),mode='wb',mtime=0) as f:f.write(json.dumps(cleanpath(result)).encode())
                path.unlink()
                if len(rows)%10==0 or row['own_action_errors'] or row['opponent_action_errors'] or not row['valid']:
                    print(f'{len(rows)}/{total_games} {stem}: {row["outcome"]} {row["score"]}:{row["opponent_score"]}; own errors={row["own_action_errors"]}; opponent errors={row["opponent_action_errors"]}; {time.monotonic()-start:.1f}s',flush=True)
                if purpose=='smoke' and row['own_action_errors']:raise RuntimeError('Candidate smoke failure; records preserved')
        save(out/'summary.json',{c:summarize([r for r in rows if r['candidate']==c]) for c in candidates})
    save(out/'map-hashes.json',maphashes);save(out/'runtime.json',{'wall_seconds':time.monotonic()-start,'games':len(rows),'external_spend':0})
    print(json.dumps({c:{o:dict(Counter(r['outcome'] for r in rows if r['candidate']==c and r['opponent']==o)) for o in sorted(set(o for a,o in pairs if a==c))} for c in candidates},indent=2),flush=True)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Use the unchanged Java generator, verify known maps, and freeze a larger train split."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE,REPO,COMMIT,java_home

def digest(data):return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seeds',required=True);ap.add_argument('--out',required=True,type=Path);args=ap.parse_args()
    assert not args.out.exists();jdk=java_home();cp=str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()
    subprocess.run([str(jdk/'bin/javac'),'-cp',cp,'-d',str(BASE/'code/build'),str(BASE/'code/rl/data/MapGenerator.java')],check=True)
    process=subprocess.Popen([str(jdk/'bin/java'),'-Xmx1g','-cp',str(BASE/'code/build')+':'+cp,'MapGenerator'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    def generate(seed):
        process.stdin.write(str(seed)+'\n');process.stdin.flush();line=process.stdout.readline()
        if not line:raise RuntimeError(f'Generator stopped at {seed}')
        props=json.loads(line);data={k:[list(map(int,row.split(','))) for row in props[k].split('_') if row] for k in ('nodes','units','edges')}
        return data,hashlib.sha256(json.dumps(props,sort_keys=True).encode()).hexdigest()
    start=time.monotonic();previous=json.loads((BASE/'experiments/rl/2026-11-06-ppo-v1/maps.json').read_text());checked=0
    try:
        for row in previous['training']+previous['selection']:
            data,_=generate(row['seed']);assert data==row['map'] and digest(data)==row['hash'],row['seed'];checked+=1
        old=json.loads((BASE/'experiments/2026-11-06-attack-holdout/historical-maps.json').read_text())['maps'];old={v['content_sha256'] for v in old.values()}
        old.update(json.loads((BASE/'experiments/2026-11-06-attack-holdout/selection.json').read_text())['map_novelty']['new_content_sha256_by_seed'].values())
        for run in ('bc-v1','ppo-v1'):old.update(json.loads((BASE/f'experiments/rl/2026-11-06-{run}/verification.json').read_text())['new_legacy_hashes_by_seed'].values())
        lo,hi=map(int,args.seeds.split(':'));training=[];seen=set()
        for seed in range(lo,hi+1):
            assert not 9001<=seed<=9100,'Reserved confirmation seed'
            data,legacy=generate(seed);key=digest(data);assert legacy not in old and key not in seen;seen.add(key)
            training.append({'hash':key,'legacy_hash':legacy,'seed':seed,'split':'train','map':data,'source':f'Original referee {COMMIT}, Java generator, seed {seed}'})
        result={'as_of':'2026-11-06','provenance':'PROJECT_REPORTED','training':training,'selection':previous['selection']}
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,separators=(',',':'))+'\n')
        report={'referee_commit':COMMIT,'known_original_maps_verified':checked,'new_training_maps':len(training),'selection_maps':len(previous['selection']),'previous_unique_maps_excluded':len(old),'map_overlap':[],'seeds':[lo,hi],'map_file_sha256':hashlib.sha256(args.out.read_bytes()).hexdigest(),'wall_seconds':time.monotonic()-start,'external_spend':0,'renderer':'Only the expected BoardView null-renderer exception is intercepted, after all map properties are written; original generator source and rules unchanged.'}
        args.out.with_suffix('.generation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    finally:process.stdin.close();process.wait(timeout=30)
if __name__=='__main__':main()

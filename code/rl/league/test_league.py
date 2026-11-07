#!/usr/bin/env python3
"""Check teacher observations, full Java transitions, legality and PPO likelihoods."""
import argparse
import gzip
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE,REPO,java_home
from rl.train.bc import Policy
from rl.train.ppo import pack,joint_stats
from rl.train.test_ppo import digest
from rl.sim.native import Simulator
from rl.league.rollout import Rollout,LIB,set_anchor
from rl.league.external import Teachers

def parsed(text,n,initial):
    rows=text.strip().splitlines();position=0;result={}
    def next_row():
        nonlocal position
        value=list(map(int,rows[position].split()));position+=1;return value
    if initial:
        assert next_row()==[n];result['coordinates']=[next_row() for _ in range(n)]
    result['scores']=next_row();result['units']=[next_row() for _ in range(n)]
    for name in ('edges','triangles','linkable'):
        count=next_row()[0];result[name]=sorted(next_row() for _ in range(count))
    assert position==len(rows);return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--maps',required=True,type=Path);parser.add_argument('--out',required=True,type=Path);args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(4);maps=json.loads(args.maps.read_text());training=[r['map'] for r in maps['training']]
    base=BASE/'experiments/rl/2026-11-06-ppo-v1/training';bc=BASE/'experiments/rl/2026-11-06-bc-v1/training/weights.txt'
    model=Policy();model.load_state_dict(torch.load(base/'checkpoint.pt',map_location='cpu',weights_only=False)['actor'])
    collector=Rollout(bc,training);collector.set_actor(model);set_anchor(collector,model)
    one=digest(collector.collect(16,1,20261109,audit=0));four=digest(collector.collect(16,4,20261109,audit=0));assert one==four
    start=time.monotonic()
    with Teachers(4,args.out/'teachers') as teachers:
        teachers.attach(collector);data=collector.collect(16,4,20261109,audit=16);records=collector.records();teacher_metrics=teachers.metrics();stats=data['stats']
        error=0.
        with torch.no_grad():
            for offset in range(0,len(data['old_logp']),128):
                ids=np.arange(offset,min(offset+128,len(data['old_logp'])));batch=pack(data,ids,'cpu');lp,_=joint_stats(model,batch,.7);error=max(error,float((lp-batch['old_logp']).abs().max()))
        assert error<.003 and not teacher_metrics['errors'];assert teacher_metrics['games']==2
    wall=time.monotonic()-start
    cp=str(BASE/'code/build')+':'+str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip();jdk=java_home()
    subprocess.run([str(jdk/'bin/javac'),'-cp',cp,'-d',str(BASE/'code/build'),str(BASE/'code/rl/league/InputOracle.java')],check=True)
    original=subprocess.Popen([str(jdk/'bin/java'),'-Xmx1g','-cp',cp,'Oracle'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    inputs=subprocess.Popen([str(jdk/'bin/java'),'-Xmx1g','-cp',cp,'InputOracle'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    transitions=observations=0
    try:
        for record in records:
            data=training[record['map_index']];job=json.dumps(dict(data,actions=record['actions']))+'\n'
            original.stdin.write(job);original.stdin.flush();expected=json.loads(original.stdout.readline())
            inputs.stdin.write(job);inputs.stdin.flush();expected_inputs=json.loads(inputs.stdout.readline())
            assert len(expected)==len(record['states'])
            simulator=Simulator(data)
            for turn,(state,java) in enumerate(zip(record['states'],expected)):
                assert all(state[k]==java[k] for k in ('turn','score','units','edges','triangles','done')),(record['kind'],turn,state,java)
                for player in (0,1):
                    native=LIB.league_observation(simulator.ptr,player,int(turn==0)).decode();reference=expected_inputs[turn][player]
                    assert parsed(native,len(data['nodes']),turn==0)==parsed(reference,len(data['nodes']),turn==0),(record['kind'],turn,player,native,reference)
                    observations+=1
                if turn<len(record['actions']):simulator.step(record['actions'][turn]);transitions+=1
            simulator.close()
    finally:
        for process in (original,inputs):process.stdin.close();process.wait(timeout=20)
    result={'passed':True,'worker_determinism_without_wall_timed_teacher':True,'teacher_is_original_unmodified_source':True,'games':len(records),'original_java_transitions':transitions,'original_java_observations':observations,'joint_logp_max_error':error,'collection':stats,'teacher':teacher_metrics,'collection_and_logp_check_wall_seconds':wall}
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    with gzip.GzipFile(filename=str(args.out/'sample-records.json.gz'),mode='wb',mtime=0) as f:f.write(json.dumps(records).encode())
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Numerical PPO contracts, worker determinism and original-referee rollout parity."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE,REPO,java_home
from rl.train.bc import Policy
from rl.train.ppo import gae,pack,joint_stats,surrogate
from rl.train.rollout import Rollout

def digest(data):
    h=hashlib.sha256()
    for k in ('x','value_x','old_logp','reward','group_offsets','choices','turn_offsets','episode_offsets','game_ids','players'):h.update(np.ascontiguousarray(data[k]).tobytes())
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--maps',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--device',default='cpu');ap.add_argument('--checkpoint',type=Path);args=ap.parse_args();torch.set_num_threads(4)
    maps=json.loads(args.maps.read_text());bc=BASE/'experiments/rl/2026-11-06-bc-v1/training';model=Policy().to(args.device);model.load_state_dict(torch.load(bc/'checkpoint.pt',map_location=args.device,weights_only=False)['model'])
    if args.checkpoint:model.load_state_dict(torch.load(args.checkpoint,map_location=args.device,weights_only=False)['actor'])
    r=Rollout(bc/'weights.txt',[v['map'] for v in maps['training']]);r.set_actor(model)
    d=r.collect(8,1,20261107,audit=8);one=digest(d);d=r.collect(8,4,20261107,audit=8);four=digest(d);assert one==four
    assert d['group_offsets'][-1]==len(d['x']) and d['turn_offsets'][-1]==len(d['choices'])
    lp_error=entropy_error=0.
    with torch.no_grad():
        for i in range(0,len(d['old_logp']),128):
            ids=np.arange(i,min(i+128,len(d['old_logp'])));b=pack(d,ids,args.device);lp,ent=joint_stats(model,b,.7)
            lp_error=max(lp_error,float((lp-b['old_logp']).abs().max().cpu()));counts=np.diff(d['turn_offsets'])[ids]
            entropy_error=max(entropy_error,float(np.max(np.abs(ent.cpu().numpy()-d['old_entropy'][ids]/counts))))
    assert lp_error<.003 and entropy_error<.001
    v=np.array([.2,-.4,.7,.9,-.3],dtype=np.float32);reward=np.array([0,0,1,0,-1],dtype=np.float32)
    adv,ret=gae(v,reward,np.array([0,3,5]),.9,1.)
    assert np.allclose(ret,[.81,.9,1,-.9,-1],atol=1e-6)
    z=torch.tensor(np.log([1.5,.5,1.05,.95]),dtype=torch.float32,requires_grad=True)
    loss=surrogate(z,torch.zeros(4),torch.tensor([1.,-1.,1.,-1.]),.1);loss.backward()
    assert torch.allclose(z.grad,torch.tensor([0.,0.,-1.05/4,.95/4]),atol=1e-6)
    # Each self-play game supplies opposite terminal outcomes, with no cross-episode GAE leakage.
    records=r.records();rewards=d['reward'];ends=d['episode_offsets'][1:]-1
    terminal={}
    for end in ends:terminal.setdefault(int(d['game_ids'][end]),[]).append(float(rewards[end]))
    for g,record in enumerate(records):
        if record['kind']==0:assert len(terminal[g])==2 and sum(terminal[g])==0
    cp=str(BASE/'code/build')+':'+str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()
    oracle=subprocess.Popen([str(java_home()/'bin/java'),'-Xmx1g','-cp',cp,'Oracle'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    transitions=0
    try:
        for record in records:
            job=dict(maps['training'][record['map_index']]['map'],actions=record['actions']);oracle.stdin.write(json.dumps(job)+'\n');oracle.stdin.flush();expected=json.loads(oracle.stdout.readline())
            assert len(expected)==len(record['states'])
            for a,b in zip(record['states'],expected):
                assert all(a[k]==b[k] for k in ('turn','score','units','edges','triangles','done')),(a,b)
            transitions+=len(expected)-1
    finally:oracle.stdin.close();oracle.wait(timeout=20)
    initial=r.evaluate([v['map'] for v in maps['selection'][:4]])
    if not args.checkpoint:assert initial['score_rate']==.5
    result={'device':args.device,'controlled_decisions':len(d['old_logp']),'groups':len(d['choices']),'joint_logp_max_error':lp_error,'mean_choice_entropy_max_error':entropy_error,'worker_1_vs_4_digest':one,'worker_determinism':True,'gae_episode_boundaries':True,'ppo_clipping_gradients':True,'self_play_zero_sum_terminal_rewards':True,'original_java_games':len(records),'original_java_transitions':transitions,'java_mismatches':0,'small_selection_score':initial['score_rate'],'checkpoint_sha256':hashlib.sha256(args.checkpoint.read_bytes()).hexdigest() if args.checkpoint else None,'passed':True}
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    with gzip.GzipFile(filename=str(args.out.with_suffix('.records.json.gz')),mode='wb',mtime=0) as f:f.write(json.dumps(records).encode())
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

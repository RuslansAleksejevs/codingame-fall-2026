#!/usr/bin/env python3
"""Resumable warm-start PPO blocks; external fixed-opponent panels select candidates."""
import argparse
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import platform
import resource
import sys
import time
import numpy as np
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE
from rl.train.bc import Policy,export
from rl.train.ppo import update,cpu_state,sha,save
from rl.train.rollout import Rollout,LIB


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',required=True,type=Path);ap.add_argument('--maps',required=True,type=Path)
    ap.add_argument('--init',required=True,type=Path);ap.add_argument('--initial-weights',required=True,type=Path)
    ap.add_argument('--steps',required=True,type=int);ap.add_argument('--minutes',default=120,type=float)
    ap.add_argument('--seed',default=20261108,type=int);ap.add_argument('--games',default=64,type=int)
    ap.add_argument('--workers',default=4,type=int);ap.add_argument('--resume',type=Path)
    ap.add_argument('--milestones',default='1000000,3000000,5000000')
    ap.add_argument('--pilot',action='store_true');args=ap.parse_args()
    assert args.steps>0 and args.games>0 and args.workers>0
    torch.set_num_threads(4);torch.manual_seed(args.seed);rng=np.random.default_rng(args.seed)
    out=args.out;out.mkdir(parents=True,exist_ok=bool(args.resume))
    maps=json.loads(args.maps.read_text());training=[v['map'] for v in maps['training']];selection=[v['map'] for v in maps['selection']]
    bc=BASE/'experiments/rl/2026-11-06-bc-v1/training/weights.txt'
    initial=torch.load(args.init,map_location='cpu',weights_only=False)
    actor=Policy();critic=Policy();actor.load_state_dict(initial['actor']);critic.load_state_dict(initial['critic'])
    ao=torch.optim.Adam(actor.parameters(),lr=3e-5);vo=torch.optim.Adam(critic.parameters(),lr=3e-4)
    ao.load_state_dict(initial['actor_optimizer']);vo.load_state_dict(initial['critic_optimizer'])
    config={k:initial['config'][k] for k in ('actor_lr','critic_lr','clip','gamma','gae_lambda','epochs','minibatch_turns','grad_clip','entropy_coef','target_kl','temperature','reward','ratio')}
    config.update({'device':'cpu','seed':args.seed,'maps_sha256':sha(args.maps),'initial_checkpoint_sha256':sha(args.init),'initial_weights_sha256':sha(args.initial_weights),'base_trained_steps':initial['steps'],'bc_weights_sha256':sha(bc),'training_maps':len(training),'selection_maps':len(selection),'games_per_rollout':args.games,'workers':args.workers,'pilot':args.pilot,'external_spend':0,'selection':'External original-arena development panel; native BC/PPO-v1 results are diagnostics only.'})
    collector=Rollout(bc,training);checks={'bc':Rollout(bc,selection),'ppo1':Rollout(args.initial_weights,selection)}
    pool=initial['pool'];pool_steps=initial['pool_steps'];base_steps=initial['steps'];next_pool=initial['next_pool']-base_steps
    steps=iteration=games=0;elapsed=0.;history=[];milestones=sorted(set(int(v) for v in args.milestones.split(',')));done_milestones=[]
    if args.resume:
        ck=torch.load(args.resume,map_location='cpu',weights_only=False)
        for key in config:assert config[key]==ck['config'][key],key
        actor.load_state_dict(ck['actor']);critic.load_state_dict(ck['critic']);ao.load_state_dict(ck['actor_optimizer']);vo.load_state_dict(ck['critic_optimizer'])
        rng.bit_generator.state=ck['numpy_rng'];torch.set_rng_state(ck['torch_rng']);pool=ck['pool'];pool_steps=ck['pool_steps']
        steps=ck['steps'];iteration=ck['iteration'];games=ck['games'];elapsed=ck['elapsed_seconds'];next_pool=ck['next_pool'];history=ck['history'];done_milestones=ck['done_milestones']
    LIB.ppo_clear_pool(collector.ptr);temporary=Policy()
    for state in pool:temporary.load_state_dict(state);collector.set_actor(temporary);collector.add_pool()
    save(out/'config.json',config)
    save(out/'hardware.json',{'as_of':datetime.now(timezone.utc).isoformat(),'platform':platform.platform(),'python':platform.python_version(),'torch':torch.__version__,'numpy':np.__version__,'torch_threads':torch.get_num_threads()})
    save(out/'source-sha256.json',{str(p.relative_to(BASE)):sha(p) for p in [Path(__file__).resolve(),BASE/'code/rl/train/ppo.py',BASE/'code/rl/train/rollout.cpp',BASE/'code/rl/train/rollout.py',BASE/'code/rl/models/policy.hpp',BASE/'code/rl/sim/simulator.hpp']})
    save(out/'block-request.json',{'target_additional_steps':args.steps,'total_training_wall_cap_seconds':args.minutes*60,'milestones':milestones,'resume':bool(args.resume)})
    start=time.monotonic();cache=BASE/'code/build/rl-cache'/out.name;cache.mkdir(parents=True,exist_ok=True)
    def checkpoint(path):
        temporary_path=path.with_suffix('.tmp')
        torch.save({'actor':cpu_state(actor),'critic':cpu_state(critic),'actor_optimizer':ao.state_dict(),'critic_optimizer':vo.state_dict(),'numpy_rng':rng.bit_generator.state,'torch_rng':torch.get_rng_state(),'config':config,'steps':steps,'iteration':iteration,'games':games,'next_pool':next_pool,'pool':pool,'pool_steps':pool_steps,'history':history,'elapsed_seconds':elapsed+time.monotonic()-start,'done_milestones':done_milestones},temporary_path)
        temporary_path.replace(path)
    def milestone():
        folder=out/f'step-{steps:08d}';folder.mkdir(exist_ok=True);export(actor,folder/'weights.txt')
        result={'additional_steps':steps,'base_steps':base_steps,'weights_sha256':sha(folder/'weights.txt'),'diagnostic_only':True}
        if not args.pilot:
            for name,evaluator in checks.items():evaluator.set_actor(actor);result[name]=evaluator.evaluate(selection)
        save(folder/'native-evaluation.json',result);checkpoint(folder/'checkpoint.pt')
        print(json.dumps({'checkpoint':folder.name,'additional_steps':steps,'native_scores':{k:result[k]['score_rate'] for k in checks if k in result}}),flush=True)
        return folder.name
    last_saved=None
    while steps<args.steps and elapsed+time.monotonic()-start<args.minutes*60:
        collector.set_actor(actor);data=collector.collect(args.games,args.workers,args.seed+iteration*1000003,config['temperature'],audit=2 if iteration==0 else 0)
        if iteration==0:
            with gzip.GzipFile(filename=str(out/'sample-rollouts.json.gz'),mode='wb',mtime=0) as f:f.write(json.dumps(collector.records()).encode())
        result=update(actor,critic,ao,vo,data,config,rng,'cpu');steps+=len(data['old_logp']);games+=data['stats']['games'];iteration+=1
        row={'iteration':iteration,'steps':steps,'games':games,'rollout':data['stats'],'update':result,'elapsed_seconds':elapsed+time.monotonic()-start};history.append(row)
        with (out/'history.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
        if iteration%10==0:print(json.dumps({'iteration':iteration,'steps':steps,'games':games,'elapsed_seconds':row['elapsed_seconds'],'kl':result['final_rollout_kl']}),flush=True)
        if steps>=next_pool:
            collector.set_actor(actor);collector.add_pool();pool.append(cpu_state(actor));pool_steps.append(base_steps+steps);pool=pool[-4:];pool_steps=pool_steps[-4:];next_pool+=100000
        reached=[v for v in milestones if steps>=v and v not in done_milestones]
        if reached:done_milestones.extend(reached);last_saved=milestone()
        if iteration%10==0 or reached:checkpoint(cache/'latest.pt')
    if last_saved!=f'step-{steps:08d}':last_saved=milestone()
    checkpoint(out/'final.pt');export(actor,out/'weights.txt')
    summary={'additional_steps':steps,'base_steps':base_steps,'games':games,'iterations':iteration,'elapsed_seconds':elapsed+time.monotonic()-start,'stop':'sample_target' if steps>=args.steps else 'wall_cap','last_checkpoint':last_saved,'weights_sha256':sha(out/'weights.txt'),'max_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'total_rollout_seconds':sum(r['rollout']['seconds'] for r in history),'total_update_seconds':sum(r['update']['seconds'] for r in history),'actor_early_stop_batches':sum(r['update']['actor_early_stopped'] for r in history),'external_spend':0}
    save(out/'summary.json',summary);print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()

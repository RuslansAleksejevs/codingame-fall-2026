#!/usr/bin/env python3
"""PPO-Clip on complete autoregressive turns, with a frozen self-play league."""
import argparse
import copy
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import platform
import resource
import shutil
import sys
import time
import numpy as np
import torch
from torch import nn
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE
from rl.train.bc import Policy,export
from rl.train.rollout import Rollout,LIB

def cpu_state(model):return {k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,data):path.write_text(json.dumps(data,indent=2)+'\n')

def pack(data,ids,device):
    """Gather every choice of each selected full turn; score flat candidate rows."""
    ids=np.asarray(ids,dtype=np.int64);turn_counts=np.diff(data['turn_offsets'])[ids]
    groups=np.concatenate([np.arange(data['turn_offsets'][i],data['turn_offsets'][i+1]) for i in ids])
    counts=np.diff(data['group_offsets'])[groups].astype(np.int64);starts=data['group_offsets'][groups].astype(np.int64)
    rows=np.repeat(np.arange(len(groups),dtype=np.int64),counts)
    cols=np.arange(int(counts.sum()),dtype=np.int64)-np.repeat(np.cumsum(counts)-counts,counts)
    indices=np.repeat(starts,counts)+cols
    tensor=lambda a,dtype=None:torch.as_tensor(a,dtype=dtype,device=device)
    return {'x':tensor(data['x'][indices]),'rows':tensor(rows),'cols':tensor(cols),'labels':tensor(data['choices'][groups],torch.long),
            'group_turn':tensor(np.repeat(np.arange(len(ids),dtype=np.int64),turn_counts)),'turn_counts':tensor(turn_counts,torch.float32),
            'groups':len(groups),'width':int(counts.max()),'turns':len(ids),'value_x':tensor(data['value_x'][ids]),'old_logp':tensor(data['old_logp'][ids])}

def joint_stats(actor,batch,temperature):
    logits=actor(batch['x'])/temperature
    padded=torch.full((batch['groups'],batch['width']),-1e9,dtype=logits.dtype,device=logits.device)
    padded=padded.index_put((batch['rows'],batch['cols']),logits)
    lp=nn.functional.log_softmax(padded,dim=-1)
    chosen=lp.gather(1,batch['labels'][:,None]).squeeze(1)
    logp=torch.zeros(batch['turns'],device=logits.device).index_add(0,batch['group_turn'],chosen)
    conditional_entropy=-(lp.exp()*lp).sum(-1)
    entropy=torch.zeros_like(logp).index_add(0,batch['group_turn'],conditional_entropy)/batch['turn_counts']
    return logp,entropy

def gae(values,rewards,offsets,gamma=.995,lam=.95):
    advantages=np.zeros_like(values,dtype=np.float32)
    for start,end in zip(offsets[:-1],offsets[1:]):
        last=0.;next_value=0.
        for i in range(int(end)-1,int(start)-1,-1):
            delta=float(rewards[i])+gamma*next_value-float(values[i]);last=delta+gamma*lam*last
            advantages[i]=last;next_value=float(values[i])
    return advantages,advantages+values

def surrogate(logp,old_logp,advantage,epsilon):
    ratio=(logp-old_logp).exp()
    return -torch.minimum(ratio*advantage,ratio.clamp(1-epsilon,1+epsilon)*advantage).mean()

def update(actor,critic,ao,vo,data,config,rng,device):
    n=len(data['old_logp']);size=config['minibatch_turns'];start=time.monotonic();values=np.zeros(n,dtype=np.float32)
    max_error=0.;old_ent=[]
    with torch.no_grad():
        for offset in range(0,n,size):
            ids=np.arange(offset,min(n,offset+size));b=pack(data,ids,device);lp,ent=joint_stats(actor,b,config['temperature'])
            max_error=max(max_error,float((lp-b['old_logp']).abs().max().cpu()));values[ids]=critic(b['value_x']).cpu().numpy();old_ent.extend(ent.cpu().tolist())
    if max_error>0.003:raise RuntimeError(f'Old joint log-probability mismatch: {max_error}')
    advantages,returns=gae(values,data['reward'],data['episode_offsets'],config['gamma'],config['gae_lambda'])
    normalized=(advantages-advantages.mean())/(advantages.std()+1e-8)
    actor_stopped=False;actor_steps=critic_steps=0;metrics=[];last_kl=0
    for epoch in range(config['epochs']):
        indices=rng.permutation(n)
        for offset in range(0,n,size):
            ids=indices[offset:offset+size];b=pack(data,ids,device);adv=torch.as_tensor(normalized[ids],device=device);target=torch.as_tensor(returns[ids],device=device)
            value=critic(b['value_x']);value_loss=.5*(value-target).square().mean();vo.zero_grad(set_to_none=True);value_loss.backward();nn.utils.clip_grad_norm_(critic.parameters(),config['grad_clip']);vo.step();critic_steps+=1
            if not actor_stopped:
                lp,entropy=joint_stats(actor,b,config['temperature']);diff=lp-b['old_logp'];ratio=diff.exp()
                kl=((ratio-1)-diff).mean();clipfrac=((ratio-1).abs()>config['clip']).float().mean()
                actor_loss=surrogate(lp,b['old_logp'],adv,config['clip'])-config['entropy_coef']*entropy.mean()
                if not torch.isfinite(actor_loss) or not torch.isfinite(value_loss):raise RuntimeError('Nonfinite loss')
                ao.zero_grad(set_to_none=True);actor_loss.backward();norm=nn.utils.clip_grad_norm_(actor.parameters(),config['grad_clip']);ao.step();actor_steps+=1
                metrics.append([float(actor_loss.detach().cpu()),float(kl.detach().cpu()),float(clipfrac.detach().cpu()),float(entropy.mean().detach().cpu()),float(norm.cpu())])
            if not torch.isfinite(value_loss):raise RuntimeError('Nonfinite critic loss')
        # Check the whole rollout, not a single noisy minibatch, before another actor epoch.
        if not actor_stopped:
            kl_sum=0.
            with torch.no_grad():
                for offset in range(0,n,size):
                    ids=np.arange(offset,min(n,offset+size));b=pack(data,ids,device);lp,_=joint_stats(actor,b,config['temperature']);diff=lp-b['old_logp'];kl_sum+=float(((diff.exp()-1)-diff).sum().cpu())
            last_kl=kl_sum/n
            if last_kl>config['target_kl']:actor_stopped=True
    with torch.no_grad():
        prediction=critic(torch.as_tensor(data['value_x'],device=device)).cpu().numpy()
    variance=float(np.var(returns));explained=1-float(np.var(returns-prediction))/variance if variance>1e-10 else None
    if not all(torch.isfinite(v).all() for v in list(actor.parameters())+list(critic.parameters())):raise RuntimeError('Nonfinite parameters')
    means=np.mean(metrics,axis=0).tolist() if metrics else [0]*5
    return {'seconds':time.monotonic()-start,'max_old_logp_error':max_error,'old_mean_choice_entropy':float(np.mean(old_ent)),
            'actor_steps':actor_steps,'critic_steps':critic_steps,'actor_early_stopped':actor_stopped,'final_rollout_kl':last_kl,
            'actor_loss':means[0],'minibatch_kl':means[1],'clip_fraction':means[2],'mean_choice_entropy':means[3],'actor_grad_norm_before_clip':means[4],
            'value_mse':float(np.mean((returns-prediction)**2)),'explained_variance':explained,'mean_advantage':float(advantages.mean()),'std_advantage':float(advantages.std())}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);ap.add_argument('--maps',required=True,type=Path);ap.add_argument('--steps',type=int,default=1000000);ap.add_argument('--minutes',type=float,default=60);ap.add_argument('--games',type=int,default=64);ap.add_argument('--workers',type=int,default=4);ap.add_argument('--device',choices=['cpu','mps'],default='mps');ap.add_argument('--pilot',action='store_true');ap.add_argument('--resume',type=Path);args=ap.parse_args()
    device=args.device;torch.set_num_threads(4)
    if device=='mps' and not torch.backends.mps.is_available():raise RuntimeError('MPS unavailable; use permitted local execution or --device cpu')
    out=args.out;out.mkdir(parents=True,exist_ok=bool(args.resume));seed=20261107;torch.manual_seed(seed);rng=np.random.default_rng(seed)
    maps=json.loads(args.maps.read_text());training=[v['map'] for v in maps['training']];selection=[v['map'] for v in maps['selection']]
    bc=BASE/'experiments/rl/2026-11-06-bc-v1/training';initial=torch.load(bc/'checkpoint.pt',map_location='cpu',weights_only=False)
    actor=Policy().to(device);actor.load_state_dict(initial['model']);critic=Policy().to(device)
    # Zero initial value outputs without changing the pretrained actor.
    nn.init.zeros_(critic.net[-1].weight);nn.init.zeros_(critic.net[-1].bias)
    ao=torch.optim.Adam(actor.parameters(),lr=3e-5);vo=torch.optim.Adam(critic.parameters(),lr=3e-4)
    config={'seed':seed,'device':device,'actor_lr':3e-5,'critic_lr':3e-4,'clip':.1,'gamma':.995,'gae_lambda':.95,'epochs':4,'minibatch_turns':128,'grad_clip':.5,'entropy_coef':.002,'target_kl':.03,'temperature':.7,'steps_target':args.steps,'wall_cap_seconds':args.minutes*60,'games_per_rollout':args.games,'workers':args.workers,'reward':'terminal win/loss/draw +1/-1/0; no shaping','ratio':'joint complete-turn likelihood','checkpoint_selection':'highest greedy score rate against BC on 42 selection maps, both seats; earlier trained checkpoint wins ties','bc_weights_sha256':sha(bc/'weights.txt'),'maps_sha256':sha(args.maps),'pilot':args.pilot,'external_spend':0}
    collector=Rollout(bc/'weights.txt',training);pool=[cpu_state(actor)];pool_steps=[0];steps=iteration=games=0;next_pool=100000;next_selection=0;selection_thresholds=[100000,250000,500000,750000,1000000];best=None;history=[];previous_seconds=0.
    if args.resume:
        ck=torch.load(args.resume,map_location=device,weights_only=False);actor.load_state_dict(ck['actor']);critic.load_state_dict(ck['critic']);ao.load_state_dict(ck['actor_optimizer']);vo.load_state_dict(ck['critic_optimizer']);rng.bit_generator.state=ck['numpy_rng'];torch.set_rng_state(ck['torch_rng'].cpu())
        if device=='mps' and ck.get('mps_rng') is not None:torch.mps.set_rng_state(ck['mps_rng'].cpu())
        for key in ('temperature','gamma','gae_lambda','actor_lr','critic_lr','maps_sha256','bc_weights_sha256'):assert config[key]==ck['config'][key]
        steps=ck['steps'];iteration=ck['iteration'];games=ck['games'];next_pool=ck['next_pool'];next_selection=ck['next_selection'];best=ck['best'];pool=ck['pool'];pool_steps=ck['pool_steps'];history=ck['history'];previous_seconds=ck['elapsed_seconds']
        LIB.ppo_clear_pool(collector.ptr);temporary=Policy()
        for state in pool:temporary.load_state_dict(state);collector.set_actor(temporary);collector.add_pool()
    save(out/'config.json',config);save(out/'hardware.json',{'as_of':datetime.now(timezone.utc).isoformat(),'platform':platform.platform(),'python':platform.python_version(),'torch':torch.__version__,'numpy':np.__version__,'mps_available':torch.backends.mps.is_available(),'torch_threads':torch.get_num_threads()})
    start=time.monotonic();cache=BASE/'code/build/rl-cache'/out.name;cache.mkdir(parents=True,exist_ok=True)
    def checkpoint(path):
        torch.save({'actor':cpu_state(actor),'critic':cpu_state(critic),'actor_optimizer':ao.state_dict(),'critic_optimizer':vo.state_dict(),'numpy_rng':rng.bit_generator.state,'torch_rng':torch.get_rng_state(),'mps_rng':torch.mps.get_rng_state() if device=='mps' else None,'config':config,'steps':steps,'iteration':iteration,'games':games,'next_pool':next_pool,'next_selection':next_selection,'best':best,'pool':pool,'pool_steps':pool_steps,'history':history,'elapsed_seconds':previous_seconds+time.monotonic()-start},path)
    def select(final=False):
        nonlocal best
        collector.set_actor(actor);began=time.monotonic();result=collector.evaluate(selection);result.update({'steps':steps,'seconds':time.monotonic()-began,'final':final})
        name=f'step-{steps:07d}';folder=out/name;folder.mkdir(exist_ok=True);export(actor,folder/'weights.txt');save(folder/'selection.json',result)
        if best is None or result['score_rate']>best['score_rate']:
            best={'steps':steps,'score_rate':result['score_rate'],'path':name};shutil.copy2(folder/'weights.txt',out/'weights.txt')
        checkpoint(folder/'checkpoint.pt');print(json.dumps({'selection':result,'best':best}),flush=True);return result
    while steps<args.steps and previous_seconds+time.monotonic()-start<args.minutes*60:
        collector.set_actor(actor);data=collector.collect(args.games,args.workers,seed+iteration*1000003,config['temperature'],audit=2 if iteration==0 else 0)
        if iteration==0:
            with gzip.GzipFile(filename=str(out/'sample-rollouts.json.gz'),mode='wb',mtime=0) as f:f.write(json.dumps(collector.records()).encode())
        result=update(actor,critic,ao,vo,data,config,rng,device);steps+=len(data['old_logp']);games+=data['stats']['games'];iteration+=1
        row={'iteration':iteration,'steps':steps,'games':games,'rollout':data['stats'],'update':result,'elapsed_seconds':previous_seconds+time.monotonic()-start};history.append(row)
        with (out/'history.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
        print(json.dumps(row),flush=True)
        if steps>=next_pool:
            collector.set_actor(actor);collector.add_pool();pool.append(cpu_state(actor));pool_steps.append(steps);pool=pool[-4:];pool_steps=pool_steps[-4:];next_pool+=100000
        if not args.pilot and next_selection<len(selection_thresholds) and steps>=selection_thresholds[next_selection]:
            next_selection+=1;select()
        checkpoint(cache/'latest.pt')
    selection_result=None
    if not args.pilot:
        existing=out/f'step-{steps:07d}'/'selection.json'
        if existing.exists():
            selection_result=json.loads(existing.read_text());selection_result['final']=True;save(existing,selection_result)
        else:selection_result=select(final=True)
    else:export(actor,out/'weights.txt')
    checkpoint(out/'final.pt')
    if best:shutil.copy2(out/best['path']/'checkpoint.pt',out/'checkpoint.pt')
    else:shutil.copy2(out/'final.pt',out/'checkpoint.pt')
    summary={'steps':steps,'games':games,'iterations':iteration,'elapsed_seconds':previous_seconds+time.monotonic()-start,'stop':'sample_target' if steps>=args.steps else 'wall_cap','best':best,'final_selection':selection_result,'actor_parameters':sum(p.numel() for p in actor.parameters()),'critic_parameters':sum(p.numel() for p in critic.parameters()),'max_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'total_rollout_seconds':sum(r['rollout']['seconds'] for r in history),'total_update_seconds':sum(r['update']['seconds'] for r in history),'actor_early_stop_batches':sum(r['update']['actor_early_stopped'] for r in history),'weights_sha256':sha(out/'weights.txt'),'external_spend':0}
    save(out/'summary.json',summary);print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Bounded, reproducible categorical behavior cloning on variable legal action sets."""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import platform
import resource
import sys
import time
import numpy as np
import torch
from torch import nn

class Policy(nn.Module):
    def __init__(self):
        super().__init__();self.net=nn.Sequential(nn.Linear(128,128),nn.ReLU(),nn.Linear(128,64),nn.ReLU(),nn.Linear(64,1))
    def forward(self,x):return self.net(x).squeeze(-1)

def sync(device):
    if device=='mps':torch.mps.synchronize()

def benchmark(device,steps=80):
    torch.manual_seed(20261106);m=Policy().to(device);opt=torch.optim.AdamW(m.parameters(),lr=.001)
    x=torch.randn(512,16,128,device=device);y=torch.randint(0,16,(512,),device=device)
    for _ in range(10):opt.zero_grad();nn.functional.cross_entropy(m(x),y).backward();opt.step()
    sync(device);start=time.perf_counter()
    for _ in range(steps):opt.zero_grad();nn.functional.cross_entropy(m(x),y).backward();opt.step()
    sync(device);seconds=time.perf_counter()-start
    return {'device':device,'steps':steps,'groups_per_step':512,'candidates_per_group':16,'seconds':seconds,'groups_per_second':steps*512/seconds}

def export(model,path):
    linear=[l for l in model.net if isinstance(l,nn.Linear)]
    dims=[linear[0].in_features]+[l.out_features for l in linear]
    with path.open('w') as f:
        f.write('TRYANGLE_MLP_V1 '+str(len(linear))+'\n'+' '.join(map(str,dims))+'\n')
        for layer in linear:
            for a in (layer.weight,layer.bias):f.write(' '.join(format(float(v),'.9g') for v in a.detach().cpu().flatten())+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--device',default='auto',choices=['auto','cpu','mps']);ap.add_argument('--epochs',type=int,default=10);ap.add_argument('--benchmark-only',action='store_true');args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);torch.set_num_threads(4)
    benches=[benchmark('cpu')]
    if torch.backends.mps.is_available():benches.append(benchmark('mps'))
    hardware={'python':platform.python_version(),'platform':platform.platform(),'torch':torch.__version__,'numpy':np.__version__,'torch_threads':torch.get_num_threads(),'mps_available':torch.backends.mps.is_available(),'benchmarks':benches}
    (args.out/'hardware.json').write_text(json.dumps(hardware,indent=2)+'\n');print(json.dumps(hardware),flush=True)
    if args.benchmark_only:return
    device=max(benches,key=lambda b:b['groups_per_second'])['device'] if args.device=='auto' else args.device
    if device=='mps' and not torch.backends.mps.is_available():raise RuntimeError('MPS unavailable')
    seed=20261106;torch.manual_seed(seed);rng=np.random.default_rng(seed)
    offsets=np.load(args.data/'offsets.npy');targets=np.load(args.data/'targets.npy');phases=np.load(args.data/'phases.npy');splits=np.load(args.data/'splits.npy');teachers=np.load(args.data/'teachers.npy')
    x=np.memmap(args.data/'features.f16',dtype='<f2',mode='r',shape=(int(offsets[-1]),128))
    lengths=np.diff(offsets);bucket=np.ceil(np.log2(np.maximum(2,lengths))).astype(int)
    model=Policy().to(device);opt=torch.optim.AdamW(model.parameters(),lr=0.001,weight_decay=0.0001)
    train_teachers=np.bincount(teachers[splits==0],minlength=2);tw=train_teachers.sum()/(2*train_teachers)
    cfg={'seed':seed,'device':device,'epochs_limit':args.epochs,'patience':3,'layers':[128,128,64,1],'parameters':sum(p.numel() for p in model.parameters()),'optimizer':'AdamW','learning_rate':.001,'weight_decay':.0001,'clip_grad_norm':1,'candidate_batch_budget':8192,'teacher_weights':tw.tolist(),'spend_loss_weight':2,'mixed_style_training_probability':.5,'validation_style':'equal mixture','checkpoint_selection':'lowest validation weighted cross-entropy; no tournament selection','dataset_sha256':hashlib.sha256((args.data/'dataset.json').read_bytes()).hexdigest(),'external_spend':0}
    (args.out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    all_start=time.monotonic();history=[];best=float('inf');best_epoch=0;updates=0
    def batches(split,shuffle):
        groups=[]
        for b in sorted(set(bucket)):
            ids=np.flatnonzero((splits==split)&(bucket==b))
            if shuffle:rng.shuffle(ids)
            size=max(32,min(1024,8192//(2**int(b))))
            groups.extend(ids[start:start+size] for start in range(0,len(ids),size))
        if shuffle:rng.shuffle(groups)
        return groups
    def epoch(split,training):
        nonlocal updates
        model.train(training);total=correct=0;loss_sum=weight_sum=0.;phase_stats=[[0,0],[0,0]];teacher_stats=[[0,0],[0,0]]
        start=time.monotonic()
        with torch.set_grad_enabled(training):
            for ids in batches(split,training):
                lens=lengths[ids];width=int(lens.max());positions=np.arange(width)[None,:];mask=positions<lens[:,None]
                ix=offsets[ids,None]+np.minimum(positions,lens[:,None]-1)
                xx=np.asarray(x[ix],dtype=np.float32)
                mixed=rng.random(len(ids))<.5 if training else np.ones(len(ids),dtype=bool)
                xx[mixed,:,13:15]=.5
                inp=torch.from_numpy(xx).to(device);yy=torch.as_tensor(targets[ids].astype(np.int64),device=device);mm=torch.as_tensor(mask,device=device)
                w=torch.as_tensor((tw[teachers[ids]]*(1+phases[ids])).astype(np.float32),device=device)
                logits=model(inp).masked_fill(~mm,-1e9);losses=nn.functional.cross_entropy(logits,yy,reduction='none');loss=(losses*w).sum()/w.sum()
                if training:opt.zero_grad(set_to_none=True);loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();updates+=1
                hit=(logits.argmax(-1)==yy).detach().cpu().numpy();loss_sum+=float((losses*w).sum().detach().cpu());weight_sum+=float(w.sum().cpu());total+=len(ids);correct+=int(hit.sum())
                for kind,stats in [(phases,phase_stats),(teachers,teacher_stats)]:
                    for j in (0,1):sel=kind[ids]==j;stats[j][0]+=int(hit[sel].sum());stats[j][1]+=int(sel.sum())
        return {'loss':loss_sum/weight_sum,'accuracy':correct/total,'groups':total,'seconds':time.monotonic()-start,'phase_correct_total':phase_stats,'teacher_correct_total':teacher_stats}
    for number in range(1,args.epochs+1):
        row={'epoch':number,'train':epoch(0,True),'validation':epoch(1,False),'updates':updates};history.append(row)
        print(json.dumps(row),flush=True)
        if row['validation']['loss']<best:
            best=row['validation']['loss'];best_epoch=number
            export(model,args.out/'weights.txt')
            torch.save({'model':model.state_dict(),'optimizer':opt.state_dict(),'epoch':number,'updates':updates,'torch_rng':torch.get_rng_state(),'numpy_rng':rng.bit_generator.state,'config':cfg},args.out/'checkpoint.pt')
        (args.out/'history.json').write_text(json.dumps(history,indent=2)+'\n')
        if number-best_epoch>=3:break
    summary={'best_epoch':best_epoch,'best_validation_loss':best,'epochs_completed':len(history),'optimizer_updates':updates,'wall_seconds':time.monotonic()-all_start,'max_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'parameters':cfg['parameters'],'device':device,'weights_sha256':hashlib.sha256((args.out/'weights.txt').read_bytes()).hexdigest(),'checkpoint_sha256':hashlib.sha256((args.out/'checkpoint.pt').read_bytes()).hexdigest(),'external_spend':0}
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()

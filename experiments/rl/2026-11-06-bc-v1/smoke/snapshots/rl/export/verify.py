#!/usr/bin/env python3
"""Check saved tensor/text weights and native/PyTorch logits on held-out features."""
import argparse
import ctypes
import json
from pathlib import Path
import sys
import time
import numpy as np
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from rl.sim.native import LIB
from rl.train.bc import Policy

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--training',required=True,type=Path);ap.add_argument('--data',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);args=ap.parse_args()
    torch.set_num_threads(4);model=Policy();ckpt=torch.load(args.training/'checkpoint.pt',map_location='cpu',weights_only=False);model.load_state_dict(ckpt['model']);model.eval()
    LIB.net_new.argtypes=[ctypes.c_char_p];LIB.net_new.restype=ctypes.c_void_p;LIB.net_evaluate.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_float)];LIB.net_evaluate.restype=ctypes.c_float;LIB.net_delete.argtypes=[ctypes.c_void_p]
    net=LIB.net_new(str((args.training/'weights.txt').resolve()).encode())
    if not net:raise RuntimeError('Native model load failed')
    offsets=np.load(args.data/'offsets.npy');splits=np.load(args.data/'splits.npy');x=np.memmap(args.data/'features.f16',dtype='<f2',mode='r',shape=(int(offsets[-1]),128))
    rng=np.random.default_rng(20261106);ids=rng.choice(np.flatnonzero(splits==1),1000,replace=False);native=[];python=[];agree=0;start=time.perf_counter()
    with torch.no_grad():
        for g in ids:
            xx=np.asarray(x[offsets[g]:offsets[g+1]],dtype=np.float32).copy();xx[:,13:15]=.5
            yy=model(torch.from_numpy(xx)).numpy();zz=np.asarray([LIB.net_evaluate(net,row.ctypes.data_as(ctypes.POINTER(ctypes.c_float))) for row in xx])
            native.extend(zz);python.extend(yy);agree+=int(yy.argmax()==zz.argmax())
    error=np.abs(np.asarray(native)-np.asarray(python));LIB.net_delete(net)
    report={'groups':len(ids),'candidate_logits':len(native),'argmax_agreement':agree/len(ids),'max_absolute_logit_error':float(error.max()),'mean_absolute_logit_error':float(error.mean()),'wall_seconds':time.perf_counter()-start,'passed':bool(agree==len(ids) and error.max()<.001),'checkpoint_epoch':ckpt['epoch']}
    args.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    if not report['passed']:raise SystemExit(1)
if __name__=='__main__':main()

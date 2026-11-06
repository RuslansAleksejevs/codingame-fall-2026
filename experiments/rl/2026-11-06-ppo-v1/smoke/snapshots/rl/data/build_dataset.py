#!/usr/bin/env python3
"""Rebuild BC arrays from pinned archived games; split entire maps before training."""
import argparse
from collections import Counter
import ctypes
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE
from rl.sim.native import Simulator,LIB
from rl.data.replays import read,sources

LIB.sim_labels.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_char_p]
LIB.sim_features.restype=ctypes.POINTER(ctypes.c_float)
for name in ('sim_groups','sim_targets','sim_phases'):
    getattr(LIB,name).restype=ctypes.POINTER(ctypes.c_int)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--report',type=Path,required=True);ap.add_argument('--limit',type=int);ap.add_argument('--exclude-audit',type=Path);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    paths=sources(BASE)
    exclusions=set()
    if args.exclude_audit:
        exclusions={(d['record'],d['turn']) for d in json.loads(args.exclude_audit.read_text())['differences']}
    if args.limit:paths=paths[::max(1,len(paths)//args.limit)][:args.limit]
    offsets=[0];targets=[];phases=[];splits=[];teachers=[];records=[];maps={};counts=Counter();reject=Counter();commands=Counter();began=time.monotonic()
    with (args.out/'features.f16').open('wb') as data:
        for i,path in enumerate(paths):
            rec=read(path);teacher=0 if 'lacoz-' in path.name else 1;pid=1-int(re.search(r'seat(\d)',path.name)[1])
            split=int(int(rec['map_hash'][:8],16)%5==0);maps[rec['map_hash']]={'split':'validation' if split else 'train','seed':rec['seed']}
            meta={'path':str(path.relative_to(BASE)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'map_hash':rec['map_hash'],'teacher':['lacoz','khoufou'][teacher],'accepted_turns':0,'rejections':{}}
            if rec['errors']:
                meta['excluded_game_errors']=rec['errors'];records.append(meta);counts['excluded_error_games']+=1;continue
            sim=Simulator(rec['map']);local_reject=Counter()
            for turn,d in enumerate(rec['decisions']):
                state=sim.state()
                if state['units']!=d['units']:raise RuntimeError(f'Viewer parity failed: {path.name}, turn {turn}')
                if state['done']:counts['excluded_post_terminal_turns']+=1;break
                counts['teacher_turns']+=1
                commands.update(cmd.strip().split()[0] for cmd in d['actions'][pid].split(';') if cmd.strip())
                if (str(path.relative_to(BASE)),turn) in exclusions:
                    local_reject['canonical_order_changes_transition']+=1;reject['canonical_order_changes_transition']+=1
                    sim.step(d['actions']);continue
                ng=LIB.sim_labels(sim.ptr,pid,teacher,d['actions'][pid].encode())
                if ng<0:
                    reason=LIB.sim_error().decode();local_reject[reason]+=1;reject[reason]+=1
                else:
                    bounds=np.ctypeslib.as_array(LIB.sim_groups(),shape=(ng+1,)).copy()
                    xx=np.ctypeslib.as_array(LIB.sim_features(),shape=(int(bounds[-1])*128,))
                    data.write(xx.astype('<f2').tobytes())
                    offsets.extend((bounds[1:]+offsets[-1]).tolist())
                    targets.extend(np.ctypeslib.as_array(LIB.sim_targets(),shape=(ng,)).tolist())
                    phases.extend(np.ctypeslib.as_array(LIB.sim_phases(),shape=(ng,)).tolist())
                    splits.extend([split]*ng);teachers.extend([teacher]*ng)
                    counts['accepted_turns']+=1;meta['accepted_turns']+=1
                    counts[['lacoz_turns','khoufou_turns'][teacher]]+=1
                sim.step(d['actions'])
            meta['rejections']=dict(local_reject);meta['unpaired_terminal_outputs']=rec['unpaired'];records.append(meta)
            if (i+1)%40==0:print(f'{i+1}/{len(paths)} games; {counts["accepted_turns"]} turns; {len(targets)} groups; {offsets[-1]} candidates; rejected {sum(reject.values())}; {time.monotonic()-began:.1f}s',flush=True)
    for name,values,dtype in [('offsets',offsets,np.int64),('targets',targets,np.int16),('phases',phases,np.uint8),('splits',splits,np.uint8),('teachers',teachers,np.uint8)]:np.save(args.out/(name+'.npy'),np.asarray(values,dtype=dtype))
    summary={'schema':'candidate-features-v1','features':128,'storage':'float16; computed in float32 by shared native encoder','groups':len(targets),'candidates':offsets[-1],'counts':dict(counts),'rejections':dict(reject),'teacher_command_counts':dict(commands),'full_plan_coverage':counts['accepted_turns']/max(1,counts['teacher_turns']),
             'map_counts':dict(Counter(v['split'] for v in maps.values())),'maps':maps,'split_groups':dict(Counter(map(str,splits))),'wall_seconds':time.monotonic()-began,'records':records,'external_spend':0,
             'exclude_audit_sha256':hashlib.sha256(args.exclude_audit.read_bytes()).hexdigest() if args.exclude_audit else None,
             'array_sha256':{p.name:hashlib.file_digest(p.open('rb'),'sha256').hexdigest() for p in args.out.iterdir() if p.is_file()}}
    (args.out/'dataset.json').write_text(json.dumps(summary,indent=2)+'\n');args.report.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('records','maps')},indent=2))
if __name__=='__main__':main()

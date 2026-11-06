#!/usr/bin/env python3
"""Freeze whole-map training/selection partitions inherited from the BC dataset."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE
from rl.data.replays import read

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    data=json.loads((BASE/'experiments/rl/2026-11-06-bc-v1/dataset.json').read_text());maps={}
    for row in data['records']:
        key=row['map_hash']
        if key in maps:continue
        rec=read(BASE/row['path']);assert rec['map_hash']==key
        maps[key]={'hash':key,'seed':rec['seed'],'split':data['maps'][key]['split'],'map':rec['map'],'source':row['path']}
    result={'as_of':'2026-11-06','provenance':'PROJECT_REPORTED','training':[v for k,v in sorted(maps.items()) if v['split']=='train'],'selection':[v for k,v in sorted(maps.items()) if v['split']=='validation']}
    assert len(result['training'])==158 and len(result['selection'])==42
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,indent=2)+'\n');print({'training':158,'selection':42,'sha256':hashlib.sha256(args.out.read_bytes()).hexdigest()})
if __name__=='__main__':main()

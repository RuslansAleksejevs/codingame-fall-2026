#!/usr/bin/env python3
"""Verify complete panel, source freeze, old-map exclusion and native replay outcomes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from run_matches import BASE
from analyze_holdout import map_content
from rl.data.replays import read
from rl.sim.native import Simulator

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    run=args.run;manifest=json.loads((run/'manifest.json').read_text());rows=[json.loads(v) for v in (run/'matches.jsonl').read_text().splitlines()]
    expected={(c,o,s,p) for c,o in manifest['pairs'] for s in manifest['seeds'] for p in manifest['seats']}
    assert len(rows)==len(expected)==500
    assert {(r['candidate'],r['opponent'],r['seed'],r['seat']) for r in rows}==expected
    for path,digest in manifest['source_sha256'].items():assert sha(run/'snapshots'/path)==digest,path
    assert sha(run/'snapshots/weights.txt')==manifest['weights_sha256']
    assert sha(run/'snapshots/v6.cpp')==sha(BASE/'code/bot.cpp')==sha(BASE/'code/variants/v6-attack.cpp')
    historical=json.loads((BASE/'experiments/2026-11-06-attack-holdout/historical-maps.json').read_text())['maps']
    previous=json.loads((BASE/'experiments/2026-11-06-attack-holdout/selection.json').read_text())['map_novelty']['new_content_sha256_by_seed']
    old={v['content_sha256'] for v in historical.values()}|set(previous.values());new={};turns=0;errors=[];start=time.monotonic()
    for r in rows:
        assert r['valid'] and r['returncode']==0
        path=run/f'{r["candidate"]}-vs-{r["opponent"]}-seed{r["seed"]}-seat{r["seat"]}.json.gz'
        seed,digest=map_content(path);assert digest not in old
        assert seed not in new or new[seed]==digest;new[seed]=digest
        rec=read(path);assert not rec['errors'];sim=Simulator(rec['map'])
        for turn,d in enumerate(rec['decisions']):
            state=sim.state()
            if state['units']!=d['units']:errors.append({'record':path.name,'turn':turn,'kind':'viewer_units'});break
            sim.step(d['actions']);turns+=1
        state=sim.state();scores=[rec['scores'][str(p)] for p in (0,1)]
        if not state['done'] or state['score']!=scores:errors.append({'record':path.name,'kind':'terminal','native':state['score'],'original':scores})
    report={'games':len(rows),'source_freeze_verified':True,'v6_source_sha256':sha(BASE/'code/bot.cpp'),'weights_sha256':manifest['weights_sha256'],'previous_unique_maps':len(old),'new_unique_maps':len(set(new.values())),'map_overlap':[],'map_content_definition':'SHA256 of sorted original game-parameter strings excluding seed, matching historical map registries.','new_legacy_hashes_by_seed':new,'native_joint_transitions':turns,'native_replay_mismatches':errors,'own_error_games':sum(bool(r['own_action_errors']) for r in rows),'opponent_error_games':sum(bool(r['opponent_action_errors']) for r in rows),'wall_seconds':time.monotonic()-start}
    args.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='new_legacy_hashes_by_seed'},indent=2))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()

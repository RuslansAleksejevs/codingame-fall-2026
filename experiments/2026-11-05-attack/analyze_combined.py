#!/usr/bin/env python3
"""Reproduce the pooled v3/v6 comparison from the two archived map sets."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'code'))
from analyze_incremental import paired,describe

folder=Path(__file__).resolve().parent
rows={label:[] for label in ['v3','v6']}
for stage in ['development','previous-validation']:
    old=ROOT/'experiments/2026-11-05-incremental'/('v3-dev' if stage=='development' else 'validation/v3')
    historical={(r['opponent'],r['seed'],r['seat']):r for r in map(json.loads,(old/'matches.jsonl').read_text().splitlines())}
    for label in rows:
        part=[json.loads(s) for s in (folder/stage/label/'matches.jsonl').read_text().splitlines()]
        assert len(part)==200
        assert all(r['map_sha256']==historical[r['opponent'],r['seed'],r['seat']]['map_sha256'] for r in part)
        rows[label]+=part
out={'provenance':'PROJECT_REPORTED','as_of':'2026-11-05',
     'map_context':'reused; both historical seed sets, no fresh holdout',
     'primary_games':800,'distinct_maps':100,'matches_historical_map_hashes':True,
     'runs':{label:describe(rr) for label,rr in rows.items()},
     'paired_without_errors':{o:paired(rows['v3'],rows['v6'],o,True) for o in ['khoufou','lacoz']},
     'match_process_seconds':sum(r['wall_seconds'] for rr in rows.values() for r in rr),'external_spend':0}
(folder/'combined-comparison.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out['paired_without_errors'],indent=2))

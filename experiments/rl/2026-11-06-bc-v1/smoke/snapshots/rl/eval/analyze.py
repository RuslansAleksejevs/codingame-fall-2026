#!/usr/bin/env python3
"""Map-clustered uncertainty and paired clean-game comparisons."""
import argparse
from collections import Counter
import json
from pathlib import Path
import random
import statistics

def clean(r):return r['valid'] and not r['own_action_errors'] and not r['opponent_action_errors']
def value(r):return {'win':1.,'draw':.5,'loss':0.}[r['outcome']]
def interval(values,seed=20261106):
    if not values:return None
    rng=random.Random(seed);b=sorted(statistics.mean(rng.choices(values,k=len(values))) for _ in range(10000))
    return [100*b[249],100*b[9749]]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    rows=[json.loads(line) for line in (args.run/'matches.jsonl').read_text().splitlines()];groups={};paired={}
    for candidate,opponent in sorted(set((r['candidate'],r['opponent']) for r in rows)):
        rr=[r for r in rows if r['candidate']==candidate and r['opponent']==opponent];cc=[r for r in rr if clean(r)];seeds=sorted(set(r['seed'] for r in cc))
        times=[us for r in rr for us in r['own_plan_us']];ordered=sorted(times)
        groups[f'{candidate}_vs_{opponent}']={'games':len(rr),'results':dict(Counter(r['outcome'] for r in rr)),'clean_games':len(cc),'clean_results':dict(Counter(r['outcome'] for r in cc)),
            'own_error_games':sum(bool(r['own_action_errors']) for r in rr),'opponent_error_games':sum(bool(r['opponent_action_errors']) for r in rr),'invalid_games':sum(not r['valid'] for r in rr),
            'score_rate':statistics.mean(map(value,cc)) if cc else None,'map_cluster_95_percent':interval([statistics.mean(value(r) for r in cc if r['seed']==s) for s in seeds]),
            'decisions':len(times),'plan_us_p50':ordered[len(ordered)//2] if ordered else None,'plan_us_p95':ordered[int(.95*(len(ordered)-1))] if ordered else None,'plan_us_max':max(times,default=None),
            'seat_results':{str(s):dict(Counter(r['outcome'] for r in cc if r['seat']==s)) for s in (0,1)},'mean_turns':statistics.mean(r['own_decisions'] for r in rr),'mean_captures':statistics.mean(r['own_events'].get('captured',0) for r in rr),'mean_spawns':statistics.mean(r['own_events'].get('spawned',0) for r in rr),
            'command_counts':dict(sum((Counter(r['own_commands']) for r in rr),Counter()))}
    for opponent in ('lacoz','khoufou'):
        a={(r['seed'],r['seat']):r for r in rows if r['candidate']=='bc' and r['opponent']==opponent};b={(r['seed'],r['seat']):r for r in rows if r['candidate']=='v6' and r['opponent']==opponent}
        keys=sorted(k for k in a.keys()&b.keys() if clean(a[k]) and clean(b[k]));maps={}
        for k in keys:
            assert a[k]['map_content_sha256']==b[k]['map_content_sha256'];maps.setdefault(k[0],[]).append(value(a[k])-value(b[k]))
        paired[opponent]={'clean_pairs':len(keys),'bc_results':dict(Counter(a[k]['outcome'] for k in keys)),'v6_results':dict(Counter(b[k]['outcome'] for k in keys)),
                         'score_rate_difference_pp':100*statistics.mean(value(a[k])-value(b[k]) for k in keys),'map_cluster_95_pp':interval([statistics.mean(v) for v in maps.values()]),
                         'improved':sum(value(a[k])>value(b[k]) for k in keys),'worsened':sum(value(a[k])<value(b[k]) for k in keys),'excluded_keys':[list(k) for k in sorted(a.keys()&b.keys()) if k not in keys]}
    report={'groups':groups,'paired_bc_minus_v6':paired,'bootstrap':{'replicates':10000,'seed':20261106,'unit':'whole map, both seats together','scope':'Game/map uncertainty for one training seed; does not measure training-seed variance.'}}
    args.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()

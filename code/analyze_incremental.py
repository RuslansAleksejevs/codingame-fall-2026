#!/usr/bin/env python3
"""Paired comparison of frozen variants, with uncertainty clustered by map."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import statistics


def value(row):
    return {'win': 1.0, 'draw': 0.5, 'loss': 0.0}[row['outcome']]


def quantile(a, p):
    a=sorted(a)
    return a[int((len(a)-1)*p)]


def clean(row):
    return not row['own_action_errors'] and not row['opponent_action_errors']


def paired(before, after, opponent, clean_only=False):
    a={(r['seed'],r['seat']):r for r in before if r['opponent']==opponent}
    b={(r['seed'],r['seat']):r for r in after if r['opponent']==opponent}
    assert a.keys()==b.keys(), 'Unpaired sample'
    diffs={};included=[]
    for key in a:
        assert a[key]['map_sha256']==b[key]['map_sha256'], 'Different maps'
        if clean_only and not (clean(a[key]) and clean(b[key])):
            continue
        included.append(key)
        diffs.setdefault(key[0],[]).append(value(b[key])-value(a[key]))
    if not diffs:return {'paired_games':0}
    d=[statistics.mean(x) for x in diffs.values()]
    rng=random.Random(1729)
    boot=[statistics.mean(rng.choices(d,k=len(d)))*100 for _ in range(10000)]
    return {
        'map_clusters':len(d), 'paired_games':sum(len(x) for x in diffs.values()),
        'score_change_percentage_points':statistics.mean(d)*100,
        'paired_map_bootstrap_95_percent_interval':[quantile(boot,.025),quantile(boot,.975)],
        'games_improved':sum(value(b[k])>value(a[k]) for k in included),
        'games_worsened':sum(value(b[k])<value(a[k]) for k in included),
        'method':'10,000 paired resamples of maps, keeping available paired seats together; draw=0.5; conditional on frozen opponents and observed runs',
        'clean_only':clean_only,
    }


def describe(rows):
    result={}
    for opponent in sorted({r['opponent'] for r in rows}):
        rr=[r for r in rows if r['opponent']==opponent]
        measured=[r for r in rr if clean(r)]
        if not measured:raise ValueError('No clean matches for secondary metrics')
        decisions=sum(r['own_decisions'] for r in measured)
        ours, theirs=Counter(),Counter()
        for r in measured:
            ours.update(r['own_events']);theirs.update(r['opponent_events'])
        t10=[p for r in measured for p in r['trajectory'] if p['turn']==10]
        timings=[t for r in rr for t in r['own_plan_us']]
        losses=[r['own_decisions'] for r in measured if r['outcome']=='loss']
        result[opponent]={
            'games':len(rr), 'results':dict(Counter(r['outcome'] for r in rr)),
            'clean_games':sum(clean(r) for r in rr),
            'clean_results':dict(Counter(r['outcome'] for r in rr if clean(r))),
            'wins_with_opponent_errors':sum(r['outcome']=='win' and bool(r['opponent_action_errors']) for r in rr),
            'own_error_games':sum(bool(r['own_action_errors']) for r in rr),
            'score_fraction':statistics.mean(value(r) for r in rr),
            'seats':{str(s):dict(Counter(r['outcome'] for r in rr if r['seat']==s)) for s in (0,1)},
            'errors':sum(bool(r['own_action_errors'] or r['opponent_action_errors']) for r in rr),
            'secondary_metric_games':len(measured),
            'total_decisions':decisions,
            'median_decisions':statistics.median(r['own_decisions'] for r in measured),
            'median_decisions_lost_games':statistics.median(losses) if losses else None,
            'own_mean_spawned':ours['spawned']/len(measured),
            'own_mean_captured':ours['captured']/len(measured),
            'opponent_mean_spawned':theirs['spawned']/len(measured),
            'opponent_mean_captured':theirs['captured']/len(measured),
            'own_spawned_per_100_decisions':ours['spawned']*100/decisions,
            'own_captured_per_100_decisions':ours['captured']*100/decisions,
            'own_surround_deaths_per_100_decisions':theirs['surrounded']*100/decisions,
            'own_attack_deaths_per_100_decisions':theirs['attacked']*100/decisions,
            'own_units_killed_by_surround':theirs['surrounded'],
            'own_units_killed_by_attack':theirs['attacked'],
            'army_at_10':{'games':len(t10),
                          'own':statistics.mean(p['own_units'] for p in t10) if t10 else None,
                          'opponent':statistics.mean(p['opponent_units'] for p in t10) if t10 else None},
            'own_plan_us':{'median':statistics.median(timings),'p95':quantile(timings,.95),'max':max(timings)},
        }
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--runs',nargs='+',required=True,help='label=directory, in stage order')
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--pairs',nargs='+',help='explicit before:after comparisons for branches')
    args=parser.parse_args()
    sets=[];out={'as_of':datetime.now(timezone.utc).isoformat(),
                'provenance':'PROJECT_REPORTED','runs':{},'increments':[],
                'interpretation':'Raw outcomes include timeouts. Strategy conclusions use clean game wins, with technical wins reported separately. Clean subsets may differ; paired clean comparisons use only shared clean matches. A zero bootstrap interval from all-zero observations is not proof of zero true effect.'}
    common_maps={}
    for item in args.runs:
        label,folder=item.split('=',1);folder=Path(folder)
        rows=[json.loads(line) for line in (folder/'matches.jsonl').read_text().splitlines()]
        manifest=json.loads((folder/'manifest.json').read_text())
        expected={(o,s,t) for o in manifest['opponents'] for s in manifest['seeds'] for t in manifest['seats']}
        actual={(r['opponent'],r['seed'],r['seat']) for r in rows}
        assert len(actual)==len(rows) and actual==expected, f'Incomplete or duplicate series: {label}'
        for r in rows:
            assert r['valid'] and r['returncode']==0, f'Invalid match in {label}'
            assert common_maps.setdefault(r['seed'],r['map_sha256'])==r['map_sha256']
            assert len(r['trajectory'])==r['own_decisions']==len(r['own_plan_us'])
        own_source=folder/'snapshots/candidate.cpp'
        if not own_source.exists():own_source=folder/'snapshots/baseline-v2.cpp'
        own_hash=hashlib.sha256(own_source.read_bytes()).hexdigest()
        assert own_hash==manifest.get('candidate_source_sha256',manifest.get('baseline_source_sha256'))
        for name,meta in manifest['opponents'].items():
            assert hashlib.sha256((folder/'snapshots'/name/meta['original_file']).read_bytes()).hexdigest()==meta['sha256']
        out['runs'][label]={'path':str(folder.resolve()),'source_sha256':own_hash,
                            'games':len(rows),'unique_maps':len(manifest['seeds']),
                            'validated_decision_states':sum(r['own_decisions'] for r in rows),
                            'all_matches_valid':True,'all_matches_error_free':all(clean(r) for r in rows),
                            'statistics':describe(rows)}
        if sets and not args.pairs:
            previous,old=sets[-1]
            out['increments'].append({'before':previous,'after':label,
                'opponents':{o:paired(old,rows,o) for o in manifest['opponents']},
                'paired_without_errors':{o:paired(old,rows,o,True) for o in manifest['opponents']}})
        sets.append((label,rows))
    if args.pairs:
        by_name=dict(sets)
        for item in args.pairs:
            before,after=item.split(':')
            old,rows=by_name[before],by_name[after]
            opponents=sorted({r['opponent'] for r in rows})
            out['increments'].append({'before':before,'after':after,
                'opponents':{o:paired(old,rows,o) for o in opponents},
                'paired_without_errors':{o:paired(old,rows,o,True) for o in opponents}})
    args.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    for label,entry in out['runs'].items():
        print(label,{o:{'clean':s['clean_results'],'technical_wins':s['wins_with_opponent_errors']} for o,s in entry['statistics'].items()})
    for delta in out['increments']:
        print(delta['before'],'->',delta['after'],'paired clean change',
              {o:s.get('score_change_percentage_points') for o,s in delta['paired_without_errors'].items()})


if __name__=='__main__':main()

#!/usr/bin/env python3
"""Check every v6 ATTACK against observed troop counts and preserved game records."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
from benchmark_public import analyze, ALPHABET

def audit_run(folder):
    manifest=json.loads((folder/'manifest.json').read_text())
    assert hashlib.sha256((folder/'snapshots/candidate.cpp').read_bytes()).hexdigest()==manifest['candidate_source_sha256']
    rows=[json.loads(line) for line in (folder/'matches.jsonl').read_text().splitlines()]
    expected={(o,s,t) for o in manifest['opponents'] for s in manifest['seeds'] for t in manifest['seats']}
    assert {(r['opponent'],r['seed'],r['seat']) for r in rows}==expected
    assert len(rows)==len(expected)
    counters={o:Counter() for o in manifest['opponents']}
    for row in rows:
        seat=row['seat'];c=counters[row['opponent']]
        path=folder/f"{row['opponent']}-seed{row['seed']}-seat{seat}.json.gz"
        result=json.loads(gzip.decompress(path.read_bytes()))
        reconstructed=analyze(result,seat)
        assert all(row[k]==v for k,v in reconstructed.items()),path
        assert row['valid'] and row['returncode']==0
        c['games']+=1;c['validated_decisions']+=row['own_decisions']
        c['own_error_games']+=bool(row['own_action_errors'])
        c['opponent_error_games']+=bool(row['opponent_action_errors'])
        c['reported_attack_kills']+=row['own_events'].get('attacked',0)
        units=[[0]*52 for _ in range(2)]
        commands_in_game=0
        for i,view in enumerate(result['views']):
            output=result['outputs'][str(seat)][i]
            if output:
                commands=[s.split() for s in output.strip().split(';') if s.strip()]
                attacks=[s for s in commands if s[0]=='ATTACK']
                assert len(attacks)<=1,(path,i,'multiple attacks')
                for command in attacks:
                    a,b,d,target=map(int,command[1:]);corners={a,b,d}
                    assert len(corners)==3 and sum(units[seat])>=6
                    assert all(units[seat][v]>=1 for v in corners)
                    assert units[1-seat][target]>=4,(path,i,'target below threshold')
                    moves=Counter()
                    for item in commands:
                        if item[0]=='MOVE':moves[int(item[1])]+=int(item[3])
                        if item[0]=='SPAWN':assert set(map(int,item[1:]))!=corners
                    assert all(moves[v]<=units[seat][v]-(v in corners) for v in range(52))
                    c['attack_commands']+=1;commands_in_game+=1
                    c['target_units_at_decision']+=units[1-seat][target]
            raw=view.split('\n',1)[1].strip() if '\n' in view else ''
            if not raw:continue
            frame=json.loads(raw);frame=frame.get('frame',frame)
            tasks=frame.get('tasks','')
            if tasks.startswith('A'):
                actions=tasks[1:].split(';')
                for action in actions[seat].split():
                    assert re.fullmatch('[a-zA-Z]{4}[0-9]*',action),action
                    c['executed_attacks']+=1
                    c['viewer_attack_kills']+=int(action[4:] or '1')
            for part in frame.get('nodes','').split():
                if len(part)>3 and part[2]=='=':
                    player,phase=int(part[0]),int(part[1])
                    for house,amount in re.findall(r'([a-zA-Z])(\d*)',part[3:]):
                        units[player][ALPHABET.index(house)]=int(amount) if amount else phase
        c['games_with_attack']+=commands_in_game>0
    return {o:dict(c) for o,c in counters.items()}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--runs',nargs='+',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    report={'provenance':'PROJECT_REPORTED','checks':'Complete schedule; frozen source SHA256; every record reanalyzed; attack count, threshold, unit budget and no triangle reuse checked at every decision.',
            'runs':{str(p):audit_run(p) for p in args.runs}}
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

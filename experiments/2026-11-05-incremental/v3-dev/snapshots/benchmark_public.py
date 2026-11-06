#!/usr/bin/env python3
"""Run frozen public bots against v2 or an explicitly supplied C++ source."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import time
from run_matches import BASE, REPO, COMMIT, java_home

PUBLIC = BASE/'code/opponents/public'
ENV = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1')
ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
NORMAL_ENDS = {'is dominated', 'no units or triangles left', "can't score any more points"}


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(result, seat):
    outputs = result.get('outputs', {})
    summaries = ''.join(s or '' for s in result.get('summaries', []))
    events = [Counter(), Counter()]
    for pid, action, amount in re.findall(r'\$(\d) (spawned|captured|surrounded|attacked|added|removed) (\d+)', summaries):
        events[int(pid)][action] += int(amount)
    messages = [re.findall(r'\$'+str(p)+r': ([^\n]+)', summaries) for p in (0,1)]
    errors = [[s for s in ss if s not in NORMAL_ENDS] for ss in messages]
    # Decode the original viewer protocol, including time=0 changes (departing troops).
    # Each decision's own unit count is cross-checked against our bot's stderr.
    units = [[0]*52 for _ in range(2)]
    trajectory = []
    command_counts = [Counter(), Counter()]
    time_us = []
    for i, view in enumerate(result.get('views', [])):
        own_out = outputs.get(str(seat), [])[i]
        if own_out:
            stderr = result['errors'][str(seat)][i] or ''
            m = re.search(r'turn=(\d+) units=(\d+) triangles=(\d+) plan_us=(\d+)', stderr)
            if m:
                turn, reported_units, triangles, micros = map(int, m.groups())
                if sum(units[seat]) != reported_units:
                    raise ValueError(f'Viewer decoding mismatch at T{turn}: {sum(units[seat])} != {reported_units}')
                trajectory.append({'turn':turn, 'own_units':reported_units, 'opponent_units':sum(units[1-seat]),
                                   'own_triangles':triangles, 'own_max_stack':max(units[seat]),
                                   'opponent_max_stack':max(units[1-seat])})
                time_us.append(micros)
        for p in (0,1):
            out = outputs.get(str(p), [])[i] or ''
            for cmd in out.strip().split(';'):
                if cmd.strip():
                    command_counts[p][cmd.strip().split()[0]] += 1
        raw = view.split('\n',1)[1].strip() if '\n' in view else ''
        if not raw:
            continue
        frame = json.loads(raw)
        frame = frame.get('frame', frame)
        for part in frame.get('nodes','').split():
            if len(part)>3 and part[2]=='=':
                p, phase = int(part[0]), int(part[1])
                for house, amount in re.findall(r'([a-zA-Z])(\d*)', part[3:]):
                    units[p][ALPHABET.index(house)] = int(amount) if amount else phase
    scores = result.get('scores', {})
    own, other = scores.get(str(seat)), scores.get(str(1-seat))
    referee_errors = [e for e in result.get('errors',{}).get('referee',[]) if e]
    valid = own is not None and other is not None and not result.get('failCause') and not referee_errors
    outcome = ('win' if own>other else 'loss' if own<other else 'draw') if valid else 'invalid'
    return {'valid':valid, 'outcome':outcome, 'score':own, 'opponent_score':other,
            'fail_cause':result.get('failCause'), 'referee_errors':referee_errors,
            'own_messages':messages[seat], 'opponent_messages':messages[1-seat],
            'own_action_errors':errors[seat], 'opponent_action_errors':errors[1-seat],
            'own_events':dict(events[seat]), 'opponent_events':dict(events[1-seat]),
            'own_commands':dict(command_counts[seat]), 'opponent_commands':dict(command_counts[1-seat]),
            'own_decisions':len(trajectory), 'trajectory':trajectory, 'own_plan_us':time_us,
            'map_sha256':hashlib.sha256(json.dumps(result.get('gameParameters'),sort_keys=True).encode()).hexdigest()}


def summarize(rows):
    summary = {}
    for opponent in sorted(set(r['opponent'] for r in rows)):
        rr = [r for r in rows if r['opponent']==opponent]
        clean = [r for r in rr if r['valid'] and not r['own_action_errors'] and not r['opponent_action_errors']]
        own_events, opp_events = Counter(), Counter()
        own_end, opp_end = Counter(), Counter()
        for r in rr:
            own_events.update(r['own_events']); opp_events.update(r['opponent_events'])
            own_end.update(r['own_messages']); opp_end.update(r['opponent_messages'])
        turns = [r['own_decisions'] for r in rr]
        checkpoints = {}
        for t in (5,10,15,20,30,40,50):
            pairs = [p for r in clean for p in r['trajectory'] if p['turn']==t]
            if pairs:
                checkpoints[str(t)] = {'games_still_playing':len(pairs),
                    'own_mean_army':statistics.mean(p['own_units'] for p in pairs),
                    'opponent_mean_army':statistics.mean(p['opponent_units'] for p in pairs)}
        summary[opponent] = {
            'games':len(rr), 'results':dict(Counter(r['outcome'] for r in rr)),
            'clean_games':len(clean), 'clean_results':dict(Counter(r['outcome'] for r in clean)),
            'seat0_results':dict(Counter(r['outcome'] for r in rr if r['seat']==0)),
            'seat1_results':dict(Counter(r['outcome'] for r in rr if r['seat']==1)),
            'median_decisions':statistics.median(turns), 'mean_decisions':statistics.mean(turns),
            'min_decisions':min(turns), 'max_decisions':max(turns),
            'own_event_totals':dict(own_events), 'opponent_event_totals':dict(opp_events),
            'own_event_mean':{k:v/len(rr) for k,v in own_events.items()},
            'opponent_event_mean':{k:v/len(rr) for k,v in opp_events.items()},
            'own_end_and_warning_counts':dict(own_end), 'opponent_end_and_warning_counts':dict(opp_end),
            'army_checkpoints':checkpoints,
            'own_error_games':sum(bool(r['own_action_errors']) for r in rr),
            'opponent_error_games':sum(bool(r['opponent_action_errors']) for r in rr),
        }
        by_seed = {}
        for r in rr:
            old = by_seed.setdefault(r['seed'],r['map_sha256'])
            if old != r['map_sha256']:
                raise ValueError(f'Map changed between seats on seed {r["seed"]}')
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', required=True, help='inclusive range')
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--opponents', nargs='+', choices=['khoufou','lacoz'], default=['khoufou','lacoz'])
    parser.add_argument('--source', type=Path, help='compile and freeze this candidate; default is frozen baseline-v2')
    parser.add_argument('--label', default='baseline-v2')
    args = parser.parse_args()
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    snap = out/'snapshots'; snap.mkdir()
    lo, hi = map(int,args.seeds.split(':'))
    jdk = java_home(); py = BASE/'code/arena/.venv-lacoz/bin/python'
    baseline = BASE/'experiments/2026-11-05-baseline-v2-validation'
    binary=snap/'candidate'
    source=snap/'candidate.cpp'
    compile_command=None
    if args.source:
        shutil.copy2(args.source.resolve(),source)
        compile_command=['clang++','-std=c++17','-O2','-Wall','-Wextra','-Wpedantic',str(source),'-o',str(binary)]
        with (out/'compile.log').open('w') as log:
            subprocess.run(compile_command,stdout=log,stderr=subprocess.STDOUT,check=True)
    else:
        shutil.copy2(baseline/'bot',binary)
        shutil.copy2(baseline/'bot.cpp',source)
    for name, folder in [('khoufou','khoufou-372c1cd6'),('lacoz','lacoz-7f190183')]:
        shutil.copytree(PUBLIC/folder,snap/name)
    shutil.copy2(Path(__file__),snap/Path(__file__).name)
    shutil.copy2(BASE/'code/arena/BenchmarkMatch.java',snap/'BenchmarkMatch.java')
    cp = str(BASE/'code/build')+os.pathsep+str(REPO/'target/classes')+os.pathsep+(REPO/'classpath.txt').read_text().strip()
    commands = {
        'khoufou':[str(jdk/'bin/java'),'-cp',str(snap/'khoufou/build'),'Player'],
        'lacoz':[str(py),'-u',str(snap/'lacoz/bot.py')],
    }
    manifest = {
        'as_of':datetime.now(timezone.utc).isoformat(), 'provenance':'PROJECT_REPORTED',
        'referee_commit':COMMIT, 'league':3, 'max_turn_ms':50, 'first_turn_ms':1000,
        'timing_limits_source':'javap inspection of unmodified core 4.1.6 GameManager constructor',
        'seeds':list(range(lo,hi+1)), 'seats':[0,1], 'parallel_games':1,
        'candidate_label':args.label, 'candidate_source_sha256':sha(source), 'candidate_binary_sha256':sha(binary),
        'compile_command':compile_command,
        'compiler':subprocess.run(['clang++','--version'],capture_output=True,text=True).stdout,
        'opponents':{n:json.loads((snap/n/'PROVENANCE.json').read_text()) for n in args.opponents},
        'commands':commands, 'environment':{k:ENV[k] for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS')},
        'java':subprocess.run([str(jdk/'bin/java'),'-version'],capture_output=True,text=True).stderr,
        'python_packages':subprocess.run([str(py),'-m','pip','freeze'],capture_output=True,text=True).stdout,
        'python':subprocess.run([str(py),'--version'],capture_output=True,text=True).stdout,
        'warmup':'NumPy/SciPy imported once before measured matches; first cold import in smoke test exceeded first-turn limit; no bot source changes',
        'external_spend':0, 'live_contest_submission':False,
        'method':'same 50ms referee limits, serial matches, unchanged opponent sources; runtime-dependent Python local search may differ across reruns',
    }
    save(out/'manifest.json',manifest)
    subprocess.run([str(py),'-c','import numpy,scipy.optimize'],env=ENV,check=True)
    rows=[]
    for opponent in args.opponents:
        for seed in range(lo,hi+1):
            for seat in (0,1):
                stem=f'{opponent}-seed{seed}-seat{seat}'
                path=out/(stem+'.json')
                agents=[commands[opponent],commands[opponent]]
                agents[seat]=[str(binary)]
                labels=[opponent,opponent];labels[seat]=args.label
                spec={'seed':seed,'league':3,'agents':agents,'labels':labels,'result':str(path)}
                sp=out/(stem+'-spec.json');save(sp,spec)
                command=[str(jdk/'bin/java'),'--add-opens','java.base/java.lang=ALL-UNNAMED','-cp',cp,'BenchmarkMatch',str(sp)]
                started=time.monotonic()
                with (out/(stem+'.log')).open('w') as log:
                    proc=subprocess.run(command,cwd=REPO,env=ENV,stdout=log,stderr=subprocess.STDOUT,timeout=90)
                if not path.exists():
                    raise RuntimeError(f'{stem}: engine produced no result, inspect log')
                result=json.loads(path.read_text())
                row={'opponent':opponent,'seed':seed,'seat':seat,'returncode':proc.returncode,
                     'wall_seconds':round(time.monotonic()-started,3),'command':command,**analyze(result,seat)}
                with gzip.open(out/(stem+'.json.gz'),'wt') as f:json.dump(result,f)
                path.unlink();rows.append(row)
                with (out/'matches.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
                if len(rows)%10==0 or not row['valid'] or row['own_action_errors'] or row['opponent_action_errors']:
                    rr=[r for r in rows if r['opponent']==opponent]
                    print(opponent,len(rr),dict(Counter(r['outcome'] for r in rr)),
                          'last',stem,row['own_action_errors'],row['opponent_action_errors'],flush=True)
        save(out/'summary.json',summarize(rows))
    print(json.dumps(summarize(rows),indent=2),flush=True)


if __name__=='__main__':
    main()

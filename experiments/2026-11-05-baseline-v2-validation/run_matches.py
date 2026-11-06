#!/usr/bin/env python3
"""Fixed-seed matches against the attributed Wood1 port, using the author's referee."""
import argparse
from concurrent.futures import ThreadPoolExecutor
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

BASE = Path(__file__).resolve().parent.parent
COMMIT = 'b6913124a10de328316ff42906448a18cb948431'
REPO = BASE / 'code/vendor' / ('TryAngle-Catch-' + COMMIT)


def java_home():
    if os.environ.get('JAVA_HOME'):
        return Path(os.environ['JAVA_HOME'])
    candidates = list(Path('/tmp/tryangle-tools').glob('jdk*/Contents/Home'))
    if not candidates:
        raise SystemExit('Set JAVA_HOME to a JDK 17 installation.')
    return candidates[0]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percentile(values, p):
    values = sorted(values)
    return values[min(len(values)-1, int((len(values)-1)*p))] if values else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', required=True, help='inclusive range, e.g. 1:4')
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--bot', type=Path, default=BASE/'code/build/bot')
    parser.add_argument('--opponent', type=Path, default=BASE/'code/build/wood1_port')
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--league', type=int, default=3)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    low, high = map(int, args.seeds.split(':'))
    jdk = java_home()
    cp = str(BASE/'code/build')+':'+str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()
    for name, src in [('bot', args.bot), ('opponent', args.opponent)]:
        shutil.copy2(src, out/name)
    for src in [BASE/'code/bot.cpp', BASE/'code/opponents/wood1_port.cpp', Path(__file__), BASE/'code/arena/LocalMatch.java']:
        shutil.copy2(src, out/src.name)
    manifest = {
        'as_of': datetime.now(timezone.utc).isoformat(),
        'provenance': 'PROJECT_REPORTED',
        'source': 'local run of author referee, no live contest submission',
        'referee_commit': COMMIT,
        'league': args.league, 'seeds': list(range(low, high+1)), 'seats': [0, 1], 'jobs': args.jobs,
        'bot_sha256': digest(out/'bot'), 'bot_cpp_sha256': digest(out/'bot.cpp'),
        'opponent_sha256': digest(out/'opponent'),
        'opponent_description': 'C++ adaptation of author config/level1/Boss.cs; mt19937 RNG differs from C# Random; not the live boss',
        'java': subprocess.run([str(jdk/'bin/java'), '-version'], capture_output=True, text=True).stderr,
        'compiler': subprocess.run(['clang++', '--version'], capture_output=True, text=True).stdout,
        'compile_command': 'clang++ -std=c++17 -O2 -Wall -Wextra -Wpedantic bot.cpp -o bot',
        'external_spend': 0,
    }
    (out/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')

    def match(item):
        seed, seat = item
        stem = f'seed{seed}-seat{seat}'
        result_path = out/(stem+'.json')
        agents = [out/'opponent', out/'opponent']
        agents[seat] = out/'bot'
        command = [str(jdk/'bin/java'), '--add-opens', 'java.base/java.lang=ALL-UNNAMED',
                   '-cp', cp, 'LocalMatch', str(seed), str(args.league), *map(str, agents), str(result_path)]
        start = time.monotonic()
        with (out/(stem+'.log')).open('w') as log:
            proc = subprocess.run(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT, timeout=90)
        row = {'seed': seed, 'seat': seat, 'wall_seconds': round(time.monotonic()-start, 3),
               'command': command, 'returncode': proc.returncode}
        if proc.returncode or not result_path.exists():
            raise RuntimeError(f'Engine failed: {stem}; inspect its log')
        result = json.loads(result_path.read_text())
        stderr = ''.join(x or '' for x in result['errors'].get(str(seat), []))
        stats = [tuple(map(int, m)) for m in re.findall(r'turn=(\d+) units=(\d+) triangles=(\d+) plan_us=(\d+)', stderr)]
        times = [s[3] for s in stats]
        summaries = ''.join(x or '' for x in result['summaries'])
        scores = result['scores']
        score, other = scores[str(seat)], scores[str(1-seat)]
        own_messages = re.findall(r'\$'+str(seat)+r': ([^\n]+)', summaries)
        terminal = {'is dominated', 'no units or triangles left', "can't score any more points"}
        row.update({
            'score': score, 'opponent_score': other,
            'outcome': 'win' if score>other else ('draw' if score==other else 'loss'),
            'failure': result.get('failCause'),
            'own_messages': own_messages,
            'own_action_errors': [m for m in own_messages if m not in terminal],
            'turns': len(stats), 'max_units': max((s[1] for s in stats), default=0),
            'max_triangles': max((s[2] for s in stats), default=0),
            'plan_us': times,
            'captures': sum(map(int,re.findall(r'\$'+str(seat)+r' captured (\d+) triangle',summaries))),
            'spawned': sum(map(int,re.findall(r'\$'+str(seat)+r' spawned (\d+) unit',summaries))),
        })
        with gzip.open(out/(stem+'.json.gz'), 'wt') as f:
            json.dump(result, f)
        result_path.unlink()
        print(f'{stem}: {row["outcome"]} {score}:{other}, {len(stats)} turns, errors={len(row["own_action_errors"])}', flush=True)
        return row

    items = [(seed, seat) for seed in range(low, high+1) for seat in (0,1)]
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        rows = list(pool.map(match, items))
    times = [v for row in rows for v in row['plan_us']]
    summary = {
        'games': len(rows),
        'wins': sum(r['outcome']=='win' for r in rows),
        'draws': sum(r['outcome']=='draw' for r in rows),
        'losses': sum(r['outcome']=='loss' for r in rows),
        'action_error_games': sum(bool(r['own_action_errors']) for r in rows),
        'engine_failures': sum(bool(r['failure']) for r in rows),
        'turns': len(times), 'p50_plan_us': percentile(times,.5),
        'p95_plan_us': percentile(times,.95), 'max_plan_us': max(times,default=None),
        'mean_captures': statistics.mean(r['captures'] for r in rows),
        'mean_spawned': statistics.mean(r['spawned'] for r in rows),
        'seat0_wins': sum(r['outcome']=='win' and r['seat']==0 for r in rows),
        'seat1_wins': sum(r['outcome']=='win' and r['seat']==1 for r in rows),
    }
    (out/'matches.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n')
    (out/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()

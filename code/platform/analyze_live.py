#!/usr/bin/env python3
"""Summarize saved platform logs without confusing warnings with game outcomes."""
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / 'experiments/rl/2026-11-06-live-ppo-v2'
NORMAL = {'is dominated', 'no units or triangles left', "can't score any more points"}

def read(path):
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes())

def analyze(path):
    data = read(path)
    log = data.get('log', data)
    mine = [a['index'] for a in log['agents'] if a.get('me')]
    warnings, errors, times, commands = [], [], [], Counter()
    for frame in log.get('frames', []):
        for seat, message in re.findall(r'\$(\d+): ([^\n]+)', frame.get('summary', '')):
            if int(seat) in mine and message not in NORMAL:
                target = errors if re.search(r'timeout|invalid|error|crash', message, re.I) else warnings
                target.append({'frame': frame['frame'], 'seat': int(seat), 'message': message})
        if any(f'${s}' in frame.get('referee', '') for s in mine) and re.search(r'not provided.*time|timeout', frame.get('referee', ''), re.I):
            errors.append({'frame': frame['frame'], 'referee': frame['referee']})
        if frame.get('agent') in mine:
            if frame.get('error') or frame.get('timeout'):
                errors.append({'frame': frame['frame'], 'error': frame.get('error'), 'timeout': frame.get('timeout')})
            times.extend(map(int, re.findall(r'plan_us=(\d+)', frame.get('stderr', ''))))
            for command in frame.get('stdout', '').split(';'):
                if command.strip(): commands[command.strip().split()[0]] += 1
    for tip in log.get('tooltips', []):
        if any(f'${s}' in tip['text'] for s in mine) and re.search(r'timeout|invalid|error|crash', tip['text'], re.I):
            errors.append(tip)
    return {'file': str(path.relative_to(BASE)), 'game_id': log['game_id'], 'agents': log['agents'],
            'scores': log.get('scores'), 'ranking': log.get('ranking'), 'own_seats': mine,
            'warnings': warnings, 'errors': errors, 'commands': dict(commands),
            'fail_cause': log.get('fail_cause'),
            'measured_plan_us_max': max(times, default=None)}

tests = [analyze(p) for p in sorted(OUT.glob('test-*.json'))]
battles = [analyze(p) for p in sorted((OUT / 'games').glob('*.json*'))]
sources = [read(p) for p in sorted(OUT.glob('submission-source*.json.gz'))]
accepted = [{'submission_id': s['submission_id'], 'sha256': hashlib.sha256(s['code'].encode()).hexdigest()} for s in sources]
selected = json.loads((BASE / 'code/rl/configs/selected-policy.json').read_text())
candidate = selected.get('platform', {}).get('source', 'submissions/ppo-v2-league3m-silver.cpp')
source_sha = hashlib.sha256((BASE / candidate).read_bytes()).hexdigest()
assert any(s['sha256'] == source_sha for s in accepted)
by_agent = {}
for game in battles:
    for agent in game['agents']:
        if not agent.get('me'): continue
        stats = by_agent.setdefault(str(agent['agent_id']), {'games': 0, 'games_with_errors': 0, 'games_with_warnings': 0})
        stats['games'] += 1
        stats['games_with_errors'] += bool(game['errors'])
        stats['games_with_warnings'] += bool(game['warnings'])
summary = {'as_of': datetime.now(timezone.utc).isoformat(), 'provenance': 'SOURCE_VERIFIED',
           'source': 'CodinGame public API; saved complete responses in this directory',
           'accepted_source_sha256': source_sha, 'accepted_source_matches_package': True,
           'verified_submissions': accepted,
           'ranked_logs_by_agent': by_agent,
           'tests': tests, 'inspected_battles': battles,
           'test_own_warnings': sum(len(t['warnings']) for t in tests),
           'test_own_errors': sum(len(t['errors']) for t in tests),
           'battle_own_warnings': sum(len(t['warnings']) for t in battles),
           'battle_own_errors': sum(len(t['errors']) for t in battles),
           'battle_games_with_own_errors': sum(bool(t['errors']) for t in battles),
           'battle_games_with_own_warnings': sum(bool(t['warnings']) for t in battles)}
(OUT / 'platform-verification.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ('tests','inspected_battles')}, indent=2))

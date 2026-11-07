#!/usr/bin/env python3
"""Create a frozen ranking result from completed progress and saved battle pages."""
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / 'experiments/rl/2026-11-06-live-ppo-v2'
progress = json.loads((OUT / 'progress-final.json').read_text())
leaderboard = json.loads((OUT / 'leaderboard-final.json').read_text())
verification = json.loads((OUT / 'platform-verification.json').read_text())
assert progress['submission_id'] == 41657621
assert progress['percentage'] == 100 and not progress['in_progress']
assert leaderboard['me']['percentage'] == 100
battles = {}
for path in sorted(OUT.glob('battles-final*.json')):
    page = json.loads(path.read_text())
    assert page['submission_id'] == progress['submission_id']
    for game in page['battles']:
        battles[game['game_id']] = game
finished = [g for g in battles.values() if g['done']]
counts = {'wins': 0, 'draws': 0, 'losses': 0}
inspected = {g['game_id']: g for g in verification['inspected_battles']}
errors, warnings = [], []
for game in finished:
    positions = [p['position'] for p in game['players']]
    mine = game['my_position']
    outcome = 'losses' if mine > min(positions) else 'draws' if positions.count(mine) > 1 else 'wins'
    counts[outcome] += 1
    log = inspected[game['game_id']]
    assert any(a.get('me') and a['agent_id'] == leaderboard['me']['agent_id'] for a in log['agents'])
    if log['errors']: errors.append(game['game_id'])
    if log['warnings']: warnings.append(game['game_id'])
result = {
    'as_of': datetime.fromtimestamp((OUT / 'leaderboard-final.json').stat().st_mtime, timezone.utc).isoformat(),
    'provenance': 'SOURCE_VERIFIED',
    'source': 'CodinGame public API: progress-final.json, leaderboard-final.json, battles-final*.json and complete logs',
    'contest': 'fall-challenge-2026', 'submission_id': progress['submission_id'],
    'agent_id': leaderboard['me']['agent_id'], 'nickname': leaderboard['me']['nickname'],
    'ranking_complete': True, 'percentage': progress['percentage'],
    'rank': leaderboard['me']['rank'], 'total': leaderboard['total'],
    'league': progress['league'], 'league_rank': progress.get('league_rank'),
    'league_total': progress.get('league_total'), 'score': leaderboard['me']['score'],
    'progress_rank': progress['rank'], 'league_history': progress['league_history'],
    'next_league_opens_at': progress.get('next_league_opens_at'),
    'accepted_source_sha256': verification['accepted_source_sha256'],
    'finished_battles_in_snapshot': len(finished), **counts,
    'own_error_games': errors, 'own_warning_games': warnings,
    'completed_game_ids': sorted(g['game_id'] for g in finished),
    'pending_game_ids': sorted(g['game_id'] for g in battles.values() if not g['done']),
    'scope': 'Ongoing-contest snapshot after ranking completed. Arena games continue; battle results are not a fixed independent tournament.',
    'external_compute_spend_usd': 0,
}
(OUT / 'result.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if not k.endswith('_ids')}, indent=2))

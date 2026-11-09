#!/usr/bin/env python3
"""Preserve only task-relevant public rank fields and bind the known agent ID."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
raw = HERE / 'public-leaderboard-0458.json'
data = json.loads(raw.read_text())
audit = json.loads((HERE / 'audit-saved004.json').read_text())
own_ids = {a['agent_id'] for g in audit['games'] for a in g['agents'] if a.get('me')}
assert own_ids == {6866403} and len(data['users']) == 1
row = data['users'][0]
assert row['agentId'] in own_ids and row['percentage'] == 100 and row['inProgress'] is False
result = {
    'summarized_at': datetime.now(timezone.utc).isoformat(),
    'retrieval_window_utc': '2026-11-09T04:58Z',
    'classification': 'SOURCE_VERIFIED',
    'source_page': 'https://www.codingame.com/contests/fall-challenge-2026/leaderboard/global',
    'read_only_rpc': 'POST https://www.codingame.com/services/Leaderboards/getFilteredChallengeLeaderboard',
    'authentication': 'none; public website row, no private API access',
    'raw_response_sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
    'raw_response_retention': 'Original remains local; unrelated profile fields excluded from publication',
    'submission_id_from_prior_acceptance': audit['submission_id'],
    'source_sha256_from_prior_accepted_readback': audit['source_sha256'],
    'agent_id': row['agentId'], 'agent_matches_all_26_saved_logs': True,
    'rank': row['rank'], 'total': data['count'], 'score': row['score'],
    'percentage': row['percentage'], 'in_progress': row['inProgress'],
    'league': 'Gold', 'league_division_index': row['league']['divisionIndex'],
    'website_local_rank': row['localRank'], 'website_division_agents_count': row['league']['divisionAgentsCount'],
    'server_row_update_at': datetime.fromtimestamp(row['updateTime']/1000, timezone.utc).isoformat(),
    'server_agent_created_at': datetime.fromtimestamp(row['creationTime']/1000, timezone.utc).isoformat(),
    'approximate_top_fraction_percent': 100*row['rank']/data['count'],
    'players_below_percent': 100*(data['count']-row['rank'])/data['count'],
    'ranking_completion_verified_publicly': True,
    'full_final_battle_audit': False,
    'fresh_authenticated_source_history_progress': False,
    'limitations': ['Not the final contest standings', 'Moving unpaired rank comparison',
                   'Public row completion does not verify all battle logs or rule out technical failures',
                   'Website localRank/divisionAgentsCount are retained as named; not silently mapped to API league_rank/league_total'],
}
with (HERE / 'public-ranking.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps(result, indent=2))
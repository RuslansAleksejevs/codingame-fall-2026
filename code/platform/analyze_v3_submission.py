#!/usr/bin/env python3
"""Audit saved B2M ranking snapshots and battle logs without network access."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from analyze_v3_tests import analyze, sha

BASE = Path(__file__).resolve().parents[2]
DIRECTORY = BASE / 'experiments/rl/2026-11-07-ppo-v3/live-submission'


def read(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    request = read(DIRECTORY / 'submission-request.json')
    accepted = read(DIRECTORY / 'accepted-source.json')
    response = read(DIRECTORY / 'submission-response.json')
    expected_id = response['submission_id']
    assert accepted['submission_id'] == expected_id
    expected_sha = request['source_sha256']
    published_sha = hashlib.sha256(accepted['code'].encode()).hexdigest()
    assert published_sha == expected_sha == sha(BASE / request['code_file'])
    progress_paths = sorted(DIRECTORY.glob('progress-[0-9][0-9][0-9].json'))
    assert progress_paths
    progress = read(progress_paths[-1])
    assert progress['submission_id'] == expected_id
    completed, latest_pending = {}, set()
    battle_sources = []
    for path in sorted(DIRECTORY.glob('battles-[0-9][0-9][0-9]*.json')):
        data = read(path)
        assert data['submission_id'] == expected_id
        battle_sources.append({'file': str(path.relative_to(BASE)), 'sha256': sha(path)})
        for battle in data['battles']:
            game_id = battle['game_id']
            if battle.get('done'):
                completed[game_id] = battle
                latest_pending.discard(game_id)
            elif game_id not in completed:
                latest_pending.add(game_id)
    games, missing = [], []
    snapshot_counts = Counter()
    for game_id, battle in sorted(completed.items()):
        own = [p for p in battle['players'] if p.get('me')]
        enemies = [p for p in battle['players'] if not p.get('me')]
        assert len(own) == 1 and enemies
        place, other = own[0]['position'], min(p['position'] for p in enemies)
        outcome = 'win' if place < other else 'draw' if place == other else 'loss'
        snapshot_counts[outcome] += 1
        path = DIRECTORY / 'games' / f'{game_id}.json'
        if not path.exists():
            missing.append(game_id)
            continue
        game = analyze(path)
        assert game['status'] == 'done' and game['game_id'] == game_id
        assert [a['agent_id'] for a in game['agents'] if a.get('me')] == [own[0]['agent_id']]
        assert game['outcome'] == outcome
        games.append(game)
    own_errors = sum(g['own_errors'] for g in games)
    own_warnings = sum(g['own_warnings'] for g in games)
    own_turns = sum(s['turns'] for g in games for s in g['seats'].values() if s['own'])
    times = [s['planning_us_max'] for g in games for s in g['seats'].values()
             if s['own'] and s['planning_us_max'] is not None]
    clean = [g for g in games if not (g['own_errors'] or g['opponent_errors'] or
                                    g['global_errors'] or g['fail_cause'])]
    result = {
        'as_of': datetime.now(timezone.utc).isoformat(),
        'provenance': 'PROJECT_REPORTED',
        'source': 'Saved complete official CodinGame API responses',
        'submission_id': expected_id, 'accepted_source_sha256': published_sha,
        'accepted_source_matches_candidate': True,
        'progress_source': str(progress_paths[-1].relative_to(BASE)),
        'progress_sha256': sha(progress_paths[-1]),
        'ranking_complete': progress.get('percentage') == 100 and not progress.get('in_progress', True),
        'progress': {k: progress.get(k) for k in ('rank', 'total', 'league', 'league_rank',
                    'league_total', 'score', 'percentage', 'in_progress', 'eligible_for_promotion')},
        'baseline_progress': read(DIRECTORY / 'progress-before.json'),
        'battle_snapshot_sources': battle_sources,
        'completed_battles_in_saved_snapshots': len(completed),
        'pending_battles_in_saved_snapshots': sorted(latest_pending),
        'snapshot_outcomes': dict(snapshot_counts),
        'audited_battles': len(games), 'missing_game_logs': missing,
        'own_errors': own_errors, 'own_warnings': own_warnings,
        'own_games_with_errors': sum(bool(g['own_errors']) for g in games),
        'opponent_games_with_errors': sum(bool(g['opponent_errors']) for g in games),
        'global_failure_games': sum(bool(g['global_errors'] or g['fail_cause']) for g in games),
        'clean_battle_outcomes': dict(Counter(g['outcome'] for g in clean)),
        'own_turn_outputs': own_turns, 'planning_us_max': max(times, default=None),
        'caveats': ['Live rank changes are not a controlled comparison with the old bot.',
                    'plan_us is bot instrumentation, not total platform CPU time.',
                    'Conclusions cover the recorded snapshot; the contest continues.'],
        'games': games,
    }
    result['audit_sources'] = {
        str(path.relative_to(BASE)): sha(path)
        for path in (Path(__file__).resolve(), Path(__file__).with_name('analyze_v3_tests.py').resolve())
    }
    fallback = BASE / 'submissions/ppo-v2-league3m.cpp'
    fallback_sha = sha(fallback)
    assert fallback_sha == '199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1'
    result['preserved_fallback_sha256'] = fallback_sha
    final_submissions = DIRECTORY / 'submissions-final.json'
    if final_submissions.exists():
        before = read(DIRECTORY / 'submissions-before.json')['submissions']
        after = read(final_submissions)['submissions']
        old_ids = {s['submission_id'] for s in before}
        new_ids = {s['submission_id'] for s in after}
        current = [s['submission_id'] for s in after if s.get('current')]
        assert new_ids - old_ids == {expected_id} and old_ids <= new_ids
        assert current == [expected_id]
        result['submission_transition'] = {
            'exactly_one_new_submission': True, 'previous_history_preserved': True,
            'current_submission': expected_id,
            'submitted_at': next(s['submitted_at'] for s in after if s['submission_id'] == expected_id),
            'source': str(final_submissions.relative_to(BASE)), 'sha256': sha(final_submissions),
        }
    if args.require_complete:
        assert result['ranking_complete'] and not missing
        assert not latest_pending and final_submissions.exists()
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('games', 'battle_snapshot_sources', 'baseline_progress')}, indent=2))


if __name__ == '__main__':
    main()
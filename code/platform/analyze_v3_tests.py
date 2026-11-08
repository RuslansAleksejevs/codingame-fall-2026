#!/usr/bin/env python3
"""Audit the bounded B2M platform tests; never contact the API or modify code."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[2]
DIRECTORY = BASE / 'experiments/rl/2026-11-07-ppo-v3/platform'
NORMAL_END = {'is dominated', 'no units or triangles left', "can't score any more points"}
TECHNICAL = re.compile(r'timeout|invalid|error|crash|not provided.*time|out of time', re.I)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def options_sha(text):
    """The API reorders property lines; preserve all values and reject duplicates."""
    properties = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        key, value = line.split('=', 1)
        assert key not in properties, f'Duplicate game option {key}'
        properties[key] = value
    assert {'seed', 'nodes', 'edges', 'units'} <= properties.keys()
    return hashlib.sha256(json.dumps(properties, sort_keys=True).encode()).hexdigest()


def analyze(path):
    data = json.loads(path.read_text())
    # Official battle logs use the same schema without the test-game envelope.
    if all(key in data for key in ('game_id', 'agents', 'frames')):
        data = {'status': 'done', 'test_game_id': data['game_id'], 'log': data}
    result = {'file': str(path.relative_to(BASE)), 'file_sha256': sha(path),
              'game_id': data.get('test_game_id'), 'status': data.get('status')}
    if data.get('status') != 'done' or 'log' not in data:
        result['failure'] = data.get('failure', data.get('hint', 'No completed log'))
        return result
    log = data['log']
    mine = {a['index'] for a in log['agents'] if a.get('me')}
    seats = {a['index']: {'own': a['index'] in mine, 'turns': 0, 'times': [],
                         'commands': Counter(), 'warnings': [], 'errors': []}
             for a in log['agents']}
    global_errors = []
    for frame in log.get('frames', []):
        seat = frame.get('agent')
        if seat in seats:
            stats = seats[seat]
            if 'stdout' in frame:
                stats['turns'] += 1
                for command in frame['stdout'].split(';'):
                    if command.strip():
                        stats['commands'][command.strip().split()[0]] += 1
            stats['times'].extend(map(int, re.findall(r'plan_us=(\d+)', frame.get('stderr', ''))))
        if frame.get('error') or frame.get('timeout'):
            error = {'frame': frame['frame'], 'error': frame.get('error'),
                     'timeout': frame.get('timeout')}
            (seats[seat]['errors'] if seat in seats else global_errors).append(error)
        for mentioned, text in re.findall(r'\$(\d+): ([^\n]+)', frame.get('summary', '')):
            mentioned = int(mentioned)
            if mentioned in seats and text not in NORMAL_END:
                kind = 'errors' if TECHNICAL.search(text) else 'warnings'
                seats[mentioned][kind].append({'frame': frame['frame'], 'message': text})
        for key in ('summary', 'referee'):
            text = frame.get(key, '')
            if TECHNICAL.search(text) and not re.search(r'\$\d+: ', text):
                targets = set(map(int, re.findall(r'\$(\d+)', text))) & seats.keys()
                error = {'frame': frame['frame'], key: text}
                for target in targets:
                    seats[target]['errors'].append(error)
                if not targets:
                    global_errors.append(error)
    for tip in log.get('tooltips', []):
        if TECHNICAL.search(tip.get('text', '')):
            targets = set(map(int, re.findall(r'\$(\d+)', tip['text']))) & seats.keys()
            for target in targets:
                seats[target]['errors'].append(tip)
            if not targets:
                global_errors.append(tip)
    for stats in seats.values():
        times = stats.pop('times')
        stats['planning_samples'] = len(times)
        stats['planning_us_max'] = max(times, default=None)
        stats['commands'] = dict(stats['commands'])
    outcome = 'selfplay'
    if len(mine) == 1:
        own = next(iter(mine))
        ranks = log['ranking']
        other = [r for i, r in enumerate(ranks) if i != own]
        outcome = 'win' if ranks[own] < min(other) else 'draw' if ranks[own] == min(other) else 'loss'
    result.update(agents=log['agents'], own_seats=sorted(mine), seats=seats,
                  scores=log.get('scores'), ranking=log.get('ranking'), outcome=outcome,
                  global_errors=global_errors, fail_cause=log.get('fail_cause'),
                  game_options_raw_sha256=hashlib.sha256(log['game_options'].encode()).hexdigest(),
                  game_options_sha256=options_sha(log['game_options']),
                  own_errors=sum(len(s['errors']) for s in seats.values() if s['own']),
                  own_warnings=sum(len(s['warnings']) for s in seats.values() if s['own']),
                  opponent_errors=sum(len(s['errors']) for s in seats.values() if not s['own']))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    files = {}
    for path in sorted(DIRECTORY.glob('test-*-start.json')):
        files[path.name.removesuffix('-start.json')] = path
    for path in sorted(DIRECTORY.glob('test-*-result.json')):
        files[path.name.removesuffix('-result.json')] = path
    tests = {name: analyze(path) for name, path in files.items()}
    assert len(tests) <= 10
    pairs = []
    manifest = json.loads((DIRECTORY / 'paired-replays.json').read_text())
    for pair in manifest['pairs']:
        candidate, baseline = (tests.get(pair[key]) for key in ('candidate_test', 'baseline_test'))
        if not candidate or not baseline or candidate['status'] != 'done' or baseline['status'] != 'done':
            continue
        source = json.loads((DIRECTORY / f'replay-source-{pair["replay_game_id"]}.json').read_text())
        original_map = options_sha(source['game_options'])
        actual_opponents = lambda t: [a['agent_id'] for a in t['agents'] if not a.get('me')]
        valid = (candidate['game_options_sha256'] == baseline['game_options_sha256'] == original_map
                 and candidate['own_seats'] == baseline['own_seats'] == [pair['own_seat']]
                 and actual_opponents(candidate) == actual_opponents(baseline) == [pair['opponent_agent_id']])
        pairs.append(dict(pair=pair['pair'], opponent=pair['opponent_name'], own_seat=pair['own_seat'],
                          candidate=candidate['outcome'], baseline=baseline['outcome'],
                          map_seat_opponent_match=valid,
                          clean=all(not (t['own_errors'] or t['own_warnings'] or t['opponent_errors']
                                        or t['global_errors'] or t['fail_cause']) for t in (candidate, baseline))))
    result = {'as_of': datetime.now(timezone.utc).isoformat(), 'provenance': 'PROJECT_REPORTED',
              'source': 'Saved official CodinGame API logs', 'tests': tests, 'paired_results': pairs,
              'completed_games': sum(t['status'] == 'done' for t in tests.values()),
              'own_errors': sum(t.get('own_errors', 0) for t in tests.values()),
              'own_warnings': sum(t.get('own_warnings', 0) for t in tests.values()),
              'planning_time_caveat': 'plan_us is bot instrumentation, not total platform CPU time.',
              'strength_caveat': 'Four adaptive archived replays and two smokes are not independent strength confirmation.',
              'competitive_submission': False}
    requests = json.loads((DIRECTORY / 'test-requests.json').read_text())
    expected_sources = {
        requests['candidate_source']: requests['candidate_source_sha256'],
        requests['baseline_source']: requests['baseline_source_sha256'],
        'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/checkpoint.pt':
            '9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663',
        'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt':
            'dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb',
    }
    result['source_integrity'] = {path: {'sha256': sha(BASE / path), 'expected': expected,
                                       'matches': sha(BASE / path) == expected}
                                  for path, expected in expected_sources.items()}
    if (DIRECTORY / 'submitted-fallback-source.json').exists():
        published = json.loads((DIRECTORY / 'submitted-fallback-source.json').read_text())
        progress = json.loads((DIRECTORY / 'progress-end.json').read_text())
        before = json.loads((DIRECTORY / 'submissions-start.json').read_text())['submissions']
        after = json.loads((DIRECTORY / 'submissions-end.json').read_text())['submissions']
        identity = lambda rows: [(r['submission_id'], r['language'], r.get('current', False)) for r in rows]
        published_sha = hashlib.sha256(published['code'].encode()).hexdigest()
        result['published_fallback'] = {
            'submission_id': published['submission_id'], 'current': published.get('current'),
            'source_sha256': published_sha,
            'matches_preserved_source': published_sha == requests['baseline_source_sha256'],
            'submission_ids_languages_current_flags_unchanged': identity(before) == identity(after),
            'timestamp_caveat': 'API submitted_at values drifted by7ms between GETs. Source hash, IDs and current flags are compared explicitly, not full response bytes.',
            'live_snapshot': {k: progress[k] for k in ('submission_id', 'rank', 'total', 'league', 'league_rank', 'league_total', 'score', 'in_progress')},
        }
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    compact = {k: v for k, v in result.items() if k != 'tests'}
    compact['test_results'] = {k: {field: v.get(field) for field in ('status', 'outcome', 'own_errors', 'own_warnings', 'opponent_errors', 'failure')}
                             for k, v in tests.items()}
    print(json.dumps(compact, indent=2))


if __name__ == '__main__':
    main()
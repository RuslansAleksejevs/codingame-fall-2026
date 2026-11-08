#!/usr/bin/env python3
"""Final per-arm provenance, actual training dose and saved-rollout Java audit."""
import argparse
from collections import Counter
import json
from common import ROOT, OUT, BASE, Oracle, now, save, sha
from prepare import same
from train import MAPS


def audit(arm):
    out = OUT / f'pilot-{arm}'
    target = out / 'technical-audit.json'
    assert not target.exists()
    summary = json.loads((out / 'summary.json').read_text())
    config = json.loads((out / 'config.json').read_text())
    sources = json.loads((out / 'source-sha256.json').read_text())
    assert all(sha(ROOT / path) == expected for path, expected in sources.items())
    assert summary['weights_sha256'] == sha(out / 'weights.txt')
    assert summary['checkpoint_sha256'] == sha(out / 'checkpoint.pt')
    export = json.loads((out / 'export-verification.json').read_text())
    assert export['passed'] and summary['stop'] == 'sample_target'
    assert not summary['teacher']['errors']
    history = [json.loads(line) for line in (out / 'history.jsonl').read_text().splitlines()]
    assert len(history) == summary['iterations']
    assert sum(row['rollout']['controlled_decisions'] for row in history) == summary['steps']
    assert sum(row['rollout']['games'] for row in history) == summary['games']
    assert 100000 <= summary['steps'] < 100200
    names = {-1: 'current', 0: 'league3m', 1: 'older_ppo', -2: 'lacoz'}
    opponents, seats = Counter(), Counter()
    for row in history:
        for opponent, seat, start, outcome, turns in row['rollout']['outcomes']:
            opponents[names[opponent]] += 1
            seats[seat] += 1
            assert outcome in (-1, 0, 1) and 0 < turns <= 200
            assert not (opponent == -2 and start >= 0)
    bank = json.loads((OUT / 'bank.json').read_text())['records']
    maps = [r['map'] for r in json.loads(MAPS.read_text())['training']]
    records = json.loads((out / 'sample-rollouts.json').read_text())
    states = 0
    with Oracle() as oracle:
        for record in records:
            assert not any(any(state['errors']) for state in record['states'])
            if record['start_index'] >= 0:
                source = bank[record['start_index']]
                job = {'snapshot': source['snapshot'], 'actions': record['actions']}
                sequence = oracle.run(dict(source['map'], actions=source['prefix'] + record['actions']))[source['snapshot']['turn']:]
                same(record['states'], sequence, {'mode': 'actual_training_sequential_java', 'arm': arm}, java=True)
                states += len(sequence)
            else:
                job = dict(maps[record['map_index']], actions=record['actions'])
            actual = oracle.run(job)
            same(record['states'], actual, {'mode': 'actual_training_direct_java', 'arm': arm}, java=True)
            states += len(actual)
    result = {'as_of': now(), 'passed': True, 'arm': arm, 'source_hashes_unchanged': True,
              'source_manifest_sha256': sha(out / 'source-sha256.json'), 'config_sha256': sha(out / 'config.json'),
              'base_checkpoint_sha256': sha(BASE / 'checkpoint.pt'), 'bank_sha256': config['bank_sha256'],
              'trained_decisions': summary['steps'], 'trained_complete_episodes': summary['games'],
              'collected_complete_episodes': sum(row['rollout'].get('collected_games', row['rollout']['games']) for row in history),
              'unused_complete_episode_decisions': sum(row['rollout'].get('unused_complete_episode_decisions', 0) for row in history),
              'partial_episodes_used': 0, 'decision_overshoot': summary['decision_overshoot'],
              'opponent_episodes': dict(opponents), 'opponent_shares': {k: v / summary['games'] for k, v in opponents.items()},
              'learner_seat_episodes': dict(seats), 'restored_episode_share': summary['restored_episode_share'],
              'restored_decision_share': summary['restored_decision_share'], 'restored_categories': summary['category_episodes'],
              'teacher_errors': summary['teacher']['errors'], 'actual_training_sample_games': len(records),
              'java_full_states': states, 'java_mismatches': 0, 'export_verification': export,
              'max_old_logp_error': max(row['update']['max_old_logp_error'] for row in history),
              'weights_sha256': summary['weights_sha256'], 'external_spend': 0}
    save(target, result)
    return result


def audit_pair():
    folders = [OUT / 'pilot-control', OUT / 'pilot-curriculum']
    configs = [json.loads((folder / 'config.json').read_text()) for folder in folders]
    assert [c['fraction'] for c in configs] == [0., .15]
    assert {k: v for k, v in configs[0].items() if k != 'fraction'} == {k: v for k, v in configs[1].items() if k != 'fraction'}
    sources = [json.loads((folder / 'source-sha256.json').read_text()) for folder in folders]
    assert sources[0] == sources[1]
    summaries = [json.loads((folder / 'summary.json').read_text()) for folder in folders]
    assert all(s['target_steps'] == 100000 for s in summaries)
    assert summaries[0]['restored_games'] == 0 and .10 <= summaries[1]['restored_episode_share'] <= .20
    histories = [[json.loads(line) for line in (folder / 'history.jsonl').read_text().splitlines()] for folder in folders]
    matched = 0
    for control, treatment in zip(*histories):
        assert control['iteration'] == treatment['iteration']
        assert [row[:3] for row in control['schedule']] == [row[:3] for row in treatment['schedule']]
        matched += 1
    result = {'as_of': now(), 'passed': True, 'same_config_except_fraction': True, 'same_training_sources': True,
              'same_seed': configs[0]['seed'], 'nominal_decision_budget': 100000,
              'actual_decisions': [s['steps'] for s in summaries], 'actual_episodes': [s['games'] for s in summaries],
              'actual_training_seconds': [s['elapsed_seconds'] for s in summaries],
              'matched_map_opponent_seat_rollout_prefix_updates': matched,
              'rollout_updates': [len(h) for h in histories],
              'note': 'Same scheduled prefix and nominal decisions/cap, not identical episode counts or elapsed time. Different episode lengths and final whole-episode overshoot are reported.',
              'bank_sha256': configs[0]['bank_sha256'], 'source_manifest_sha256': sha(folders[0] / 'source-sha256.json')}
    save(OUT / 'matched-pair-audit.json', result)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('arm', choices=['control', 'curriculum'])
    print(json.dumps(audit(ap.parse_args().arm)), flush=True)
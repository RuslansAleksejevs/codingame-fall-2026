#!/usr/bin/env python3
"""Training-bank recovery is diagnostic only; never a promotion score."""
import json
import time
from common import ROOT, OUT, BASE, Oracle, now, save, sha
from native import Network
from prepare import continue_live, same, OLDER

target = OUT / 'recovery-diagnostic.json'
assert not target.exists()
bank = json.loads((OUT / 'bank.json').read_text())['records']
paths = {'curriculum': OUT / 'pilot-curriculum/weights.txt', 'control': OUT / 'pilot-control/weights.txt',
         'base': BASE / 'weights.txt', 'older': OLDER}
plan_path = OUT / 'recovery-plan.json'
plan = json.loads(plan_path.read_text())
assert plan['games'] == len(bank) * 2 * 3 == 288
assert all(sha(ROOT / path) == expected for path, expected in plan['sha256'].items())
assert not json.loads((OUT / 'screen-strict-decision.json').read_text())['strict_gate']
assert json.loads((OUT / 'final-data-audit.json').read_text())['passed']
nets = {name: Network(path) for name, path in paths.items()}
started = time.monotonic()
rows = []
oracle = Oracle()
java_states = 0
try:
    for record in bank:
        for opponent in ('base', 'older'):
            for candidate in ('curriculum', 'control', 'base'):
                played = continue_live(record['snapshot'], record['seat'], nets[candidate], nets[opponent])
                assert not any(any(s['errors']) for s in played['states'])
                expected = oracle.run({'snapshot': record['snapshot'], 'actions': played['actions']})
                same(played['states'], expected, {'mode': 'learned_recovery_java', 'game': record['game_id'], 'candidate': candidate}, java=True)
                java_states += len(expected)
                rows.append({'game_id': record['game_id'], 'snapshot_hash': record['snapshot_hash'], 'category': record['category'],
                             'turn': record['snapshot']['turn'], 'candidate': candidate, 'opponent': opponent,
                             'seat': record['seat'], 'outcome': played['outcome'], 'scores': played['states'][-1]['score'],
                             'continuation_turns': len(played['actions']), 'actions': played['actions'], 'final_snapshot': played['states'][-1]})
finally:
    oracle.close()
    for net in nets.values():
        net.close()
save(target, {'as_of': now(), 'bank_sha256': sha(OUT / 'bank.json'), 'weights_sha256': {k: sha(v) for k, v in paths.items()},
     'plan_sha256': sha(plan_path),
     'rows': rows, 'summary': {name: {'games': sum(r['candidate'] == name for r in rows),
         'wins': sum(r['candidate'] == name and r['outcome'] == 1 for r in rows),
         'draws': sum(r['candidate'] == name and r['outcome'] == 0 for r in rows)} for name in ('curriculum', 'control', 'base')},
     'scope': 'Training-bank recovery, selected for recoverability against these anchors. Not independent strength evidence.',
     'java_full_states': java_states, 'java_mismatches': 0,
     'wall_seconds': time.monotonic() - started, 'external_spend': 0})
print(json.dumps(json.loads(target.read_text())['summary']), flush=True)
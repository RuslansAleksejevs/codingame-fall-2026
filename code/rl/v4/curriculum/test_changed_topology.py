#!/usr/bin/env python3
"""Extra correctness-only restore coverage on archived post-road states."""
import json
import time
from common import OUT, BASE, Oracle, now, save
from native import Simulator, Network
from prepare import same, continue_live, OLDER

target = OUT / 'changed-topology-restoration.json'
assert not target.exists()
records = json.loads((OUT / 'archive-boundaries.json').read_text())
started = time.monotonic()
cases = []
learner, opponent = Network(BASE / 'weights.txt'), Network(OLDER)
with Oracle() as oracle:
    for record in records:
        sim = Simulator(record['map'])
        for turn, actions in enumerate(record['actions']):
            state = sim.state()
            if state['edges'] != record['map']['edges'] and not state['done'] and not any(state['errors']):
                restored = Simulator(snapshot=state)
                same(restored.state(), state, {'mode': 'changed_topology_native', 'game': record['game_id'], 'turn': turn})
                played = continue_live(state, record['seat'], learner, opponent)
                direct = oracle.run({'snapshot': state, 'actions': played['actions']})
                sequential = oracle.run(dict(record['map'], actions=record['actions'][:turn] + played['actions']))[turn:]
                same(played['states'], direct, {'mode': 'changed_topology_direct_java', 'game': record['game_id']}, java=True)
                same(played['states'], sequential, {'mode': 'changed_topology_sequential_java', 'game': record['game_id']}, java=True)
                assert not any(any(s['errors']) for s in played['states'])
                cases.append({'game_id': record['game_id'], 'turn': turn, 'initial_edges': record['map']['edges'],
                              'snapshot': state, 'continuation': played, 'java_full_states': len(direct) + len(sequential)})
                restored.close()
                break
            sim.step(actions)
        sim.close()
        if len(cases) == 3:
            break
learner.close()
opponent.close()
assert len(cases) == 3, 'Insufficient actual changed-topology restoration coverage'
save(target, {'as_of': now(), 'passed': True, 'cases': cases, 'restored_states': len(cases),
     'java_full_states': sum(c['java_full_states'] for c in cases), 'mismatches': 0,
     'purpose': 'Correctness-only late archival development states; NOT added to the early training bank.',
     'seconds': time.monotonic() - started, 'external_spend': 0})
print(json.dumps({'passed': True, 'restored_states': len(cases), 'java_full_states': sum(c['java_full_states'] for c in cases),
                  'turns': [c['turn'] for c in cases]}), flush=True)
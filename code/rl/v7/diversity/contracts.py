"""Reuse the exact v5 trace on a small disclosed finite set; no new maps."""
from support import *
from student_common import Trace
from rl.data.replays import read
from rl.sim.native import Simulator
from rl.league.rollout import LIB as LEAGUE


def main():
    identities = teacher_guard()
    trace = Trace()
    fixtures = [(62041, 'v6', 23, p) for p in (0, 1)] + [(62044, 'lacoz', 23, p) for p in (0, 1)]
    fixtures += [(r['seed'], 'v6' if r['seed'] == 62041 else 'lacoz', r['turn'], r['player'])
        for r in json.loads((V5/'changed-plan-contracts.json').read_text())['roots']]
    oracle = subprocess.Popen([str(java_home()/'bin/java'), '-Xmx1g', '-cp', classpath(), 'Oracle'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    reports = []
    try:
        for i, (seed, opponent, turn, player) in enumerate(fixtures):
            path = ROOT/f'experiments/rl/2026-11-08-rl4/search-teacher/confirm3/search2-vs-{opponent}-seed{seed}-seat0.json.gz'
            record = read(path)
            sim = Simulator(record['map'])
            prefix = [d['actions'] for d in record['decisions'][:turn]]
            inputs = []
            try:
                for t in range(turn+1):
                    inputs.append(LEAGUE.league_observation(sim.ptr, player, int(t == 0)))
                    if t < turn: sim.step(prefix[t])
                outputs, logs = teacher_stream(inputs, f'contract-{i}')
                meta, features, offsets, labels = trace.capture(sim, player, logs[-1]['search']['selected'], outputs[-1])
                enemy, _ = trace.native.act(sim, 1-player, count=1)
                actions = [enemy, enemy]; actions[player] = outputs[-1]
                oracle.stdin.write(json.dumps(dict(record['map'], actions=prefix+[actions]))+'\n'); oracle.stdin.flush()
                expected = json.loads(oracle.stdout.readline())[-1]
                sim.step(actions); actual = sim.state()
                assert actual['errors'] == [0, 0]
                assert all(actual[k] == expected[k] for k in ('turn', 'score', 'units', 'edges', 'triangles', 'done'))
                reports.append({'seed': seed, 'player': player, 'turn': turn, 'meta': meta,
                    'record_sha256': sha(path), 'one_step_java_exact': True})
            finally: sim.close()
    finally:
        trace.close(); oracle.stdin.close(); oracle.wait(timeout=30)
    save(OUT/'contracts.json', {'as_of': now(), 'passed': True, 'teacher_adapter_changed': False,
        'roots': len(reports), 'groups': sum(r['meta']['groups'] for r in reports),
        'changed': sum(r['meta']['selected'] != 0 for r in reports), 'records': reports,
        'teacher_identities': identities, 'source_sha256': sha(Path(__file__)), 'protocol_sha256': sha(OUT/'PROTOCOL.md')})
    print(json.dumps({'contracts': 'PASS', 'roots': len(reports)}))


if __name__ == '__main__': main()
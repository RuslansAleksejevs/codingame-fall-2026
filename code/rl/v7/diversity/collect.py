"""Finite full-game anchor collection and exact teacher-prefix target banks."""
from support import *
import numpy as np
from student_common import Trace
from rl.data.replays import read
from rl.sim.native import Simulator
from rl.league.rollout import LIB as LEAGUE


def turns(total):
    assert total > 0
    return sorted({i*(total-1)//15 for i in range(16)})


def exclude_maps(rows):
    """A1: symmetric whole-map exclusion, determined only by technical status."""
    assert all(r['valid'] and not r['returncode'] and not r['own_action_errors'] for r in rows)
    excluded = sorted({r['seed'] for r in rows if r['opponent_action_errors']})
    retained = [r for r in rows if r['seed'] not in excluded]
    assert all(not r['opponent_action_errors'] for r in retained)
    for seed in {r['seed'] for r in retained}:
        assert sorted(r['seat'] for r in retained if r['seed'] == seed) == [0, 1]
    return retained, excluded


def collect(name, seeds):
    teacher_guard(); check_freeze()
    assert json.loads((OUT/'contracts.json').read_text())['passed']
    hashes = prepare(name, seeds)
    first = 73201 if name == 'labeldev' else 73001
    schedule = [{'candidate': 'base', 'opponent': COLLECTION_OPPONENTS[(s-first)%4], 'seed': s, 'seat': p}
        for s in seeds for p in ((s-first)%2, 1-(s-first)%2)]
    panel(name, schedule, hashes)
    verified = verify(name)
    assert verified['passed']
    label(name)


def label(name):
    check_freeze(); teacher_guard()
    rows = [json.loads(s) for s in (OUT/name/'matches.jsonl').read_text().splitlines()]
    verified = json.loads((OUT/(name+'-verification.json')).read_text())
    assert verified['passed'] and verified['matches_sha256'] == sha(OUT/name/'matches.jsonl')
    retained, excluded = exclude_maps(rows)
    save(OUT/(name+'-a1-exclusions.json'), {'as_of': now(), 'rule': 'A1 whole-map/both-seat opponent-only technical exclusion',
        'excluded_maps': excluded, 'retained_maps': sorted({r['seed'] for r in retained}),
        'original_games': len(rows), 'retained_games': len(retained), 'replayed_games': 0,
        'excluded_records': [{k: r[k] for k in ('seed', 'seat', 'opponent', 'own_action_errors', 'opponent_action_errors')}
            for r in rows if r['seed'] in excluded], 'amendment_sha256': sha(OUT/'AMENDMENT_A1.md')})
    rows = retained
    trace = Trace(); features = []; offsets = [0]; labels = []; root_offsets = [0]; roots = []
    calls = 0
    oracle = subprocess.Popen([str(java_home()/'bin/java'), '-Xmx1g', '-cp', classpath(), 'Oracle'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    try:
        for row in rows:
            assert row['valid'] and not row['returncode'] and not row['own_action_errors'] and not row['opponent_action_errors']
            stem = f'base-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}'
            path = OUT/name/(stem+'.json.gz'); record = read(path); player = row['seat']
            total = len(record['decisions']); broad = set(turns(total))
            narrow = set(range(0, min(28, total), 3)) if row['seed'] in TRAIN[:12] else set()
            sim = Simulator(record['map']); inputs = []
            try:
                for t, decision in enumerate(record['decisions']):
                    inputs.append(LEAGUE.league_observation(sim.ptr, player, int(t == 0)))
                    sim.step(decision['actions'])
            finally: sim.close()
            outputs, logs = teacher_stream(inputs, name+'-'+stem); calls += len(logs)
            sim = Simulator(record['map']); prefix = []
            try:
                for t, decision in enumerate(record['decisions']):
                    if t in broad | narrow:
                        state = sim.state()
                        meta, x, off, y = trace.capture(sim, player, logs[t]['search']['selected'], outputs[t])
                        assert offsets[-1]+len(x) <= 4000000
                        actions = list(decision['actions']); actions[player] = outputs[t]
                        oracle.stdin.write(json.dumps(dict(record['map'], actions=prefix+[actions]))+'\n'); oracle.stdin.flush()
                        expected = json.loads(oracle.stdout.readline())[-1]
                        counter = Simulator(record['map'])
                        try:
                            for pair in prefix: counter.step(pair)
                            counter.step(actions); actual = counter.state()
                            assert actual['errors'] == [0, 0]
                            assert all(actual[k] == expected[k] for k in ('turn', 'score', 'units', 'edges', 'triangles', 'done'))
                        finally: counter.close()
                        features.append(x); offsets.extend((off[1:]+offsets[-1]).tolist()); labels.extend(y.tolist())
                        root_offsets.append(len(labels))
                        state_id = hashlib.sha256(json.dumps({'map': row['map_content_sha256'], 'state': state, 'player': player},
                            sort_keys=True, separators=(',', ':')).encode()).hexdigest()
                        roots.append({'seed': row['seed'], 'seat': player, 'opponent': row['opponent'], 'turn': t,
                            'total_joint_turns': total, 'phase': min(2, 3*t//max(1, total)), 'state_sha256': state_id,
                            'broad': t in broad, 'narrow': t in narrow, 'changed': meta['selected'] != 0,
                            'record': rel(path), 'record_sha256': sha(path), 'command': outputs[t], 'trace': meta,
                            'teacher_stream': rel(OUT/'teacher-streams'/(name+'-'+stem+'.json')),
                            'counterfactual_java_exact': True})
                    sim.step(decision['actions']); prefix.append(decision['actions'])
            finally: sim.close()
            print(json.dumps({'label_block': name, 'roots': len(roots), 'groups': len(labels), 'teacher_calls': calls}), flush=True)
    finally:
        trace.close(); oracle.stdin.close(); oracle.wait(timeout=30)
    destination = OUT/('labels-'+name+'.npz'); assert not destination.exists()
    np.savez_compressed(destination, x=np.concatenate(features), offsets=np.asarray(offsets, dtype=np.int64),
        labels=np.asarray(labels, dtype=np.int64), root_offsets=np.asarray(root_offsets, dtype=np.int64))
    save(destination.with_suffix('.json'), {'as_of': now(), 'passed': True, 'roots': roots,
        'teacher_calls': calls, 'groups': len(labels), 'candidate_rows': offsets[-1], 'dataset_sha256': sha(destination),
        'feature_dtype': 'float32', 'style': 2, 'teacher_adapter_changed': False, 'feature_rewriting': False})


def assemble():
    check_freeze()
    blocks = []
    for name in ('train1', 'train2', 'labeldev'):
        path = OUT/('labels-'+name+'.npz'); metadata = json.loads(path.with_suffix('.json').read_text())
        assert metadata['passed'] and sha(path) == metadata['dataset_sha256']
        blocks.append((name, dict(np.load(path)), metadata))
    reports = {}
    for bank in ('narrow', 'broad', 'development'):
        features = []; offsets = [0]; labels = []; root_offsets = [0]; roots = []
        for name, data, metadata in blocks:
            if (bank == 'development') != (name == 'labeldev'): continue
            for index, root in enumerate(metadata['roots']):
                if bank != 'development' and not root[bank]: continue
                a, b = data['root_offsets'][index:index+2]
                low, high = data['offsets'][a], data['offsets'][b]
                features.append(data['x'][low:high])
                offsets.extend((data['offsets'][a+1:b+1]-low+offsets[-1]).tolist())
                labels.extend(data['labels'][a:b].tolist()); root_offsets.append(len(labels)); roots.append(root)
        destination = OUT/('bank-'+bank+'.npz'); assert not destination.exists()
        np.savez_compressed(destination, x=np.concatenate(features), offsets=np.asarray(offsets, dtype=np.int64),
            labels=np.asarray(labels, dtype=np.int64), root_offsets=np.asarray(root_offsets, dtype=np.int64),
            changed=np.asarray([r['changed'] for r in roots], dtype=np.bool_))
        report = {'as_of': now(), 'roots': len(roots), 'unique_states': len({r['state_sha256'] for r in roots}),
            'maps': sorted({r['seed'] for r in roots}), 'groups': len(labels), 'candidate_rows': offsets[-1],
            'changed_roots': sum(r['changed'] for r in roots), 'phase_counts': [sum(r['phase'] == i for r in roots) for i in range(3)],
            'seat_counts': [sum(r['seat'] == i for r in roots) for i in (0, 1)],
            'opponent_counts': {o: sum(r['opponent'] == o for r in roots) for o in COLLECTION_OPPONENTS},
            'absolute_turn_counts': {str(t): sum(r['turn'] == t for r in roots) for t in sorted({r['turn'] for r in roots})},
            'dataset_sha256': sha(destination), 'records': roots}
        save(destination.with_suffix('.json'), report); reports[bank] = {k: v for k, v in report.items() if k != 'records'}
    assert reports['broad']['unique_states'] > 826 and len(reports['broad']['maps']) >= 58
    assert len(reports['narrow']['maps']) >= 11 and len(reports['development']['maps']) >= 15
    assert all(all(count > 0 for count in report['opponent_counts'].values()) for report in reports.values())
    save(OUT/'data-summary.json', {'as_of': now(), 'passed': True, 'banks': reports,
        'teacher_calls': sum(m['teacher_calls'] for _, _, m in blocks), 'combined_count_map_phase_treatment': True,
        'amendment_sha256': sha(OUT/'AMENDMENT_A1.md'), 'amended_clean_collection_population': True})


if __name__ == '__main__':
    stage = sys.argv[1]
    if stage == 'assemble': assemble()
    elif stage == 'resume-train1': label('train1')
    elif stage == 'train1': collect(stage, TRAIN[:32])
    elif stage == 'train2': collect(stage, TRAIN[32:])
    elif stage == 'labeldev': collect(stage, LABELDEV)
    else: raise ValueError(stage)
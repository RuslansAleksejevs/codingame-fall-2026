#!/usr/bin/env python3
"""Validate road observations against actual transitions and preserved warm-start logits."""
import argparse
import ctypes as C
import gzip
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from run_matches import BASE, REPO, java_home
from rl.sim.native import Simulator
from rl.train.bc import Policy
from rl.train.ppo import pack, joint_stats
from rl.train.test_ppo import digest
from rl.roads.initialize import convert_checkpoint
from rl.roads.rollout import Rollout, LIB, set_anchor
from rl.league.external import Teachers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--maps', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(4)
    maps = [r['map'] for r in json.loads(args.maps.read_text())['training']]
    original = torch.load(BASE / 'experiments/rl/2026-11-06-ppo-v1/training/checkpoint.pt', map_location='cpu', weights_only=False)
    converted = convert_checkpoint(original)
    old_actor, actor, old_critic, critic = [Policy() for _ in range(4)]
    for model, state in ((old_actor, original['actor']), (actor, converted['actor']),
                         (old_critic, original['critic']), (critic, converted['critic'])):
        model.load_state_dict(state)
    collector = Rollout(BASE / 'experiments/rl/2026-11-06-bc-v1/training/weights.txt', maps)
    collector.set_actor(actor)
    set_anchor(collector, old_actor)
    LIB.roads_clear_pool(collector.ptr)
    temporary = Policy()
    for state in converted['pool']:
        temporary.load_state_dict(state)
        collector.set_actor(temporary)
        collector.add_pool()
    collector.set_actor(actor)
    one = digest(collector.collect(16, 1, 20261110))
    four = digest(collector.collect(16, 4, 20261110))
    assert one == four
    with Teachers(4, args.out / 'teachers') as teachers:
        LIB.roads_set_external(collector.ptr, teachers.callback)
        data = collector.collect(16, 4, 20261110, audit=16)
        records = collector.records()
        teacher_metrics = teachers.metrics()
        logp_error = 0.
        with torch.no_grad():
            for offset in range(0, len(data['old_logp']), 128):
                ids = np.arange(offset, min(offset + 128, len(data['old_logp'])))
                batch = pack(data, ids, 'cpu')
                lp, _ = joint_stats(actor, batch, .7)
                logp_error = max(logp_error, float((lp - batch['old_logp']).abs().max()))
            x = torch.tensor(data['x'][:20000].copy())
            old_x = x.clone()
            old_x[:, 13:16] = torch.tensor([.5, .5, 1.])
            actor_error = float((actor(x) - old_actor(old_x)).abs().max())
            vx = torch.tensor(data['value_x'].copy())
            old_vx = vx.clone()
            old_vx[:, 13:16] = torch.tensor([.5, .5, 1.])
            critic_error = float((critic(vx) - old_critic(old_vx)).abs().max())
        assert logp_error < .003 and actor_error < .001 and critic_error < .001
        assert not teacher_metrics['errors']
    LIB.roads_feature_probe.argtypes = [C.c_void_p, C.c_int]
    LIB.roads_feature_probe.restype = C.c_char_p
    cp = str(BASE / 'code/build') + ':' + str(REPO / 'target/classes') + ':' + (REPO / 'classpath.txt').read_text().strip()
    oracle = subprocess.Popen([str(java_home() / 'bin/java'), '-Xmx1g', '-cp', cp, 'Oracle'],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    transitions = road_cases = 0
    geometry_examples = []
    try:
        for record in records:
            board = maps[record['map_index']]
            oracle.stdin.write(json.dumps(dict(board, actions=record['actions'])) + '\n')
            oracle.stdin.flush()
            expected = json.loads(oracle.stdout.readline())
            for state, reference in zip(record['states'], expected):
                assert all(state[k] == reference[k] for k in ('turn', 'score', 'units', 'edges', 'triangles', 'done'))
            transitions += len(record['actions'])
            simulator = Simulator(board)
            for turn, actions in enumerate(record['actions']):
                if road_cases < 40:
                    for player in (0, 1):
                        candidates = json.loads(LIB.roads_feature_probe(simulator.ptr, player))
                        road = [c for c in candidates if c['kind'] in (5, 6)]
                        # Include positive and zero triangle effects, ADD and REMOVE.
                        selected = {}
                        for c in road:
                            selected.setdefault((c['kind'], c['new'][13]), c)
                        for candidate in selected.values():
                            if road_cases >= 40:
                                break
                            pair = ['WAIT', 'WAIT']
                            pair[player] = candidate['action']
                            trace = record['actions'][:turn] + [pair]
                            oracle.stdin.write(json.dumps(dict(board, actions=trace)) + '\n')
                            oracle.stdin.flush()
                            states = json.loads(oracle.stdout.readline())
                            actual = len(states[-1]['triangles']) - len(states[-2]['triangles'])
                            predicted = 2 * candidate['new'][13]
                            assert abs(actual - predicted) < 1e-6, (candidate, actual)
                            geometry_examples.append({'kind': candidate['kind'], 'action': candidate['action'],
                                                      'triangle_delta': actual, 'features': candidate['new'][13:16]})
                            road_cases += 1
                simulator.step(actions)
            simulator.close()
    finally:
        oracle.stdin.close()
        oracle.wait(timeout=20)
    assert road_cases >= 10
    report = {'passed': True, 'games': len(records), 'original_java_transitions': transitions,
              'road_effect_cases_against_original_java': road_cases,
              'geometry_examples': geometry_examples, 'worker_determinism_without_teacher': True,
              'joint_logp_max_error': logp_error, 'warm_start_actor_max_error': actor_error,
              'warm_start_critic_max_error': critic_error, 'teacher': teacher_metrics}
    (args.out / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    with gzip.GzipFile(filename=str(args.out / 'sample-records.json.gz'), mode='wb', mtime=0) as file:
        file.write(json.dumps(records).encode())
    print(json.dumps({k: v for k, v in report.items() if k != 'geometry_examples'}, indent=2))


if __name__ == '__main__':
    main()

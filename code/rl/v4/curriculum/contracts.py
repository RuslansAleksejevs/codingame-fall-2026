#!/usr/bin/env python3
"""Must pass before heavy training: live restore semantics, reward, PPO, resume."""
import copy
import hashlib
import json
import subprocess
import sys
import numpy as np
import torch
from common import ROOT, OUT, BASE, Oracle, now, save, sha
from native import Rollout, LIB, EXTERNAL
from prepare import same
from train import scheduled, MAPS, OLDER
from rl.train.bc import Policy, export
from rl.train.ppo import pack, joint_stats
from rl.league.external import Teachers
from rl.train.test_resume import equal


def data_digest(data):
    return {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in data.items() if isinstance(v, np.ndarray)}


def main():
    out = OUT / 'contracts'
    out.mkdir(exist_ok=False)
    torch.set_num_threads(4)
    ck = torch.load(BASE / 'checkpoint.pt', weights_only=False, map_location='cpu')
    actor = Policy()
    actor.load_state_dict(ck['actor'])
    export(actor, out / 'base-export.txt')
    assert sha(out / 'base-export.txt') == sha(BASE / 'weights.txt')
    bank = json.loads((OUT / 'bank.json').read_text())['records']
    maps = [r['map'] for r in json.loads(MAPS.read_text())['training']]
    for iteration in range(20):
        ordinary = scheduled(202611081, iteration, len(maps), bank, 0.)
        treatment = scheduled(202611081, iteration, len(maps), bank, .15)
        assert np.array_equal(ordinary[:, :3], treatment[:, :3])
        assert np.all(treatment[treatment[:, 1] == -2, 3] == -1)
    collector = Rollout(BASE / 'weights.txt', maps, [r['snapshot'] for r in bank], [BASE / 'weights.txt', OLDER])
    collector.set_actor(actor)
    schedule = []
    for category in ('loss', 'win', 'fresh'):
        for seat in (0, 1):
            index = next(i for i, row in enumerate(bank) if row['category'] == category and row['seat'] == seat)
            schedule.append([0, 0, seat, index])
    schedule += [[1, -1, 0, -1], [2, 1, 1, -1]]
    first = data_digest(collector.collect(schedule, 1, 202611082))
    second = data_digest(collector.collect(schedule, 4, 202611082))
    assert first == second
    # Stateful external opponents must start from the real initial position.
    schedule += [[3, -2, 0, -1], [4, -2, 1, -1]]
    with Teachers(4, out / 'teachers') as teachers:
        callback = EXTERNAL(teachers.dispatch)
        LIB.league_set_external(collector.ptr, callback)
        data = collector.collect(schedule, 4, 202611082, audit=len(schedule))
        records, teacher = collector.records(), teachers.metrics()
        assert teacher['games'] == 2 and not teacher['errors']
    ends = data['episode_offsets'][1:] - 1
    mask = np.ones(len(data['reward']), dtype=bool)
    mask[ends] = False
    assert np.all(data['reward'][mask] == 0) and len(ends) == len(schedule)
    for end in ends:
        scores = records[int(data['game_ids'][end])]['scores']
        seat = int(data['players'][end])
        assert data['reward'][end] == np.sign(scores[seat] - scores[1 - seat])
    error = 0.
    with torch.no_grad():
        for start in range(0, len(data['old_logp']), 128):
            batch = pack(data, np.arange(start, min(start + 128, len(data['old_logp']))), 'cpu')
            lp, _ = joint_stats(actor, batch, .7)
            error = max(error, float((lp - batch['old_logp']).abs().max()))
    assert error < .003
    checks = 0
    with Oracle() as oracle:
        for record in records:
            if record['start_index'] >= 0:
                source = bank[record['start_index']]
                job = {'snapshot': source['snapshot'], 'actions': record['actions']}
                sequential = oracle.run(dict(source['map'], actions=source['prefix'] + record['actions']))[source['snapshot']['turn']:]
                same(record['states'], sequential, {'mode': 'stochastic_sequential_java'}, java=True)
                checks += len(sequential)
            else:
                job = dict(maps[record['map_index']], actions=record['actions'])
            expected = oracle.run(job)
            same(record['states'], expected, {'mode': 'stochastic_java'}, java=True)
            assert not any(any(s['errors']) for s in record['states'])
            checks += len(expected)
    save(out / 'rollouts.json', records)
    collector.close()
    commands = []
    base = [sys.executable, '-B', 'code/rl/v4/curriculum/train.py', '--fraction', '.15', '--minutes', '3',
            '--seed', '202611083', '--games', '8', '--no-external']
    for name, steps, resume in [('full', 4000, False), ('split', 4000, False), ('split', 4000, True)]:
        command = base + ['--out', str((out / name).relative_to(ROOT)), '--steps', str(steps)] + (['--resume'] if resume else [])
        if name == 'split' and not resume:
            command += ['--max-updates', '1']
        commands.append(command[2:])
        subprocess.run(command, cwd=ROOT, check=True)
    a, b = [torch.load(out / name / 'checkpoint.pt', weights_only=False, map_location='cpu') for name in ('full', 'split')]
    fields = ('actor', 'critic', 'actor_optimizer', 'critic_optimizer', 'numpy_rng', 'torch_rng', 'steps', 'iteration', 'games', 'restored_games', 'restored_decisions', 'category_episodes')
    exact = {key: bool(equal(a[key], b[key])) for key in fields}
    exact['export'] = sha(out / 'full/weights.txt') == sha(out / 'split/weights.txt')
    assert all(exact.values()), exact
    save(out / 'summary.json', {'as_of': now(), 'passed': True, 'base_export_exact': True,
         'worker_determinism': True, 'matched_map_opponent_seat_schedule': True, 'terminal_only_rewards': True,
         'stateful_external_full_start_only': True,
         'joint_logp_max_error': error, 'java_full_states': checks, 'java_mismatches': 0, 'live_games': len(records),
         'external_teacher': teacher, 'exact_resume': exact, 'commands': commands, 'external_spend': 0})
    print(json.dumps(json.loads((out / 'summary.json').read_text())), flush=True)


if __name__ == '__main__':
    main()
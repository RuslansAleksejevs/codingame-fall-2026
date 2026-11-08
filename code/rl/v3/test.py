#!/usr/bin/env python3
"""PPO-v3 contracts: schedule, reward, Java parity, likelihood and exact resume."""
import argparse
import gzip
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from run_matches import BASE, REPO, java_home
from rl.train.bc import Policy, export
from rl.train.ppo import pack, joint_stats, sha, save
from rl.train.test_ppo import digest
from rl.train.test_resume import equal
from rl.league.external import Teachers
from rl.v3.rollout import Rollout, LIB, EXTERNAL
from rl.v3.sampling import NAMES, probabilities


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(4)
    experiment = BASE / 'experiments/rl/2026-11-07-ppo-v3'
    maps_path = BASE / 'experiments/rl/2026-11-06-ppo-v2/maps-2000.json'
    base = BASE / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173'
    initial = torch.load(base / 'checkpoint.pt', weights_only=False, map_location='cpu')
    actor = Policy()
    actor.load_state_dict(initial['actor'])
    export(actor, args.out / 'base-reexport.txt')
    assert sha(args.out / 'base-reexport.txt') == sha(base / 'weights.txt')
    maps = [r['map'] for r in json.loads(maps_path.read_text())['training']]
    pool = [initial['actor']]
    for p in json.loads((experiment / 'training-opponents.json').read_text()).values():
        pool.append(torch.load(BASE / p, weights_only=False, map_location='cpu')['actor'])
    pool += [initial['actor'], initial['actor']]
    collector = Rollout(base / 'weights.txt', maps)
    collector.set_pool(pool)
    collector.set_actor(actor)
    planned = np.array([(0 if label == 0 else 3 if label == 6 else 2, max(0, label - 1), seat)
                        for label in range(7) for seat in (0, 1)], dtype=np.int32)
    first = digest(collector.collect(planned[:12], 1, 202611072, audit=0))
    second = digest(collector.collect(planned[:12], 4, 202611072, audit=0))
    assert first == second
    with Teachers(4, args.out / 'teachers') as teachers:
        callback = EXTERNAL(teachers.dispatch)
        LIB.league_set_external(collector.ptr, callback)
        data = collector.collect(planned, 4, 202611072, audit=14)
        records, teacher = collector.records(), teachers.metrics()
        assert teacher['games'] == 2 and not teacher['errors']
    assert [(v[0], v[1], v[2]) for v in data['stats']['outcomes']] == [tuple(v) for v in planned]
    ends = data['episode_offsets'][1:] - 1
    mask = np.ones(len(data['reward']), dtype=bool)
    mask[ends] = False
    assert np.all(data['reward'][mask] == 0)
    for end in ends:
        game = int(data['game_ids'][end])
        player = int(data['players'][end])
        scores = records[game]['scores']
        assert data['reward'][end] == np.sign(scores[player] - scores[1 - player])
    error = 0.
    with torch.no_grad():
        for start in range(0, len(data['old_logp']), 128):
            ids = np.arange(start, min(start + 128, len(data['old_logp'])))
            batch = pack(data, ids, 'cpu')
            logp, _ = joint_stats(actor, batch, .7)
            error = max(error, float((logp - batch['old_logp']).abs().max()))
    assert error < .003
    cp = str(BASE / 'code/build') + ':' + str(REPO / 'target/classes') + ':' + (REPO / 'classpath.txt').read_text().strip()
    oracle = subprocess.Popen([str(java_home() / 'bin/java'), '-Xmx1g', '-cp', cp, 'Oracle'],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    transitions = 0
    try:
        for record in records:
            oracle.stdin.write(json.dumps(dict(maps[record['map_index']], actions=record['actions'])) + '\n')
            oracle.stdin.flush()
            expected = json.loads(oracle.stdout.readline())
            assert len(expected) == len(record['states'])
            for actual, reference in zip(record['states'], expected):
                assert all(actual[k] == reference[k] for k in ('turn', 'score', 'units', 'edges', 'triangles', 'done'))
            transitions += len(expected) - 1
    finally:
        oracle.stdin.close()
        oracle.wait(timeout=20)
    with gzip.GzipFile(filename=str(args.out / 'records.json.gz'), mode='wb', mtime=0) as f:
        f.write(json.dumps(records).encode())
    rng = np.random.default_rng(51)
    for _ in range(100):
        for external in (True, False):
            p = probabilities(rng.random(7), external)
            active = p[1:] if external else p[1:-1]
            assert p[0] == .35 and abs(p.sum() - 1) < 1e-9
            assert np.all(active >= .06 - 1e-9) and np.all(active <= .25 + 1e-9)
    result = {'passed': True, 'java_games': 14, 'java_transitions': transitions, 'java_mismatches': 0,
              'joint_logp_max_error': error, 'terminal_only_rewards': True, 'explicit_schedule': True,
              'worker_determinism_without_external': True, 'priority_floor_cap': True,
              'base_export_identical': True, 'teacher': teacher}
    save(args.out / 'contracts.json', result)
    print(json.dumps(result), flush=True)
    collector.close()
    command = [sys.executable, str(BASE / 'code/rl/v3/train.py'), '--maps', str(maps_path),
               '--init', str(base / 'checkpoint.pt'), '--initial-weights', str(base / 'weights.txt'),
               '--opponents', str(experiment / 'training-opponents.json'), '--minutes', '5',
               '--seed', '202611073', '--games', '16', '--no-external', '--checkpoint-every', '2000']
    full, split = args.out / 'full', args.out / 'split'
    commands = [command + ['--out', str(full), '--steps', '8000'],
                command + ['--out', str(split), '--steps', '1'],
                command + ['--out', str(split), '--steps', '8000', '--resume', str(split / 'final.pt')]]
    for i, cmd in enumerate(commands):
        with (args.out / f'resume-{i}.log').open('w') as f:
            subprocess.run(cmd, cwd=BASE, stdout=f, stderr=subprocess.STDOUT, check=True)
    a, b = [torch.load(folder / 'final.pt', weights_only=False, map_location='cpu') for folder in (full, split)]
    fields = ('actor', 'critic', 'actor_optimizer', 'critic_optimizer', 'numpy_rng', 'torch_rng',
              'pool', 'pool_steps', 'next_pool', 'next_checkpoint', 'recent_slot', 'opponent_scores',
              'steps', 'iteration', 'games')
    checks = {key: bool(equal(a[key], b[key])) for key in fields}
    checks['export_identical'] = sha(full / 'weights.txt') == sha(split / 'weights.txt')
    result['resume'] = checks
    result['passed'] = all(checks.values())
    save(args.out / 'summary.json', result)
    print(json.dumps(result, indent=2), flush=True)
    assert result['passed']


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""Bounded PPO-v3 continuation: terminal reward, diverse prioritized opponents."""
import argparse
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import platform
import resource
import shutil
import sys
import time
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from run_matches import BASE
from rl.train.bc import Policy, export
from rl.train.ppo import update, cpu_state, sha, save
from rl.league.external import Teachers
from rl.v3.rollout import Rollout, LIB, EXTERNAL
from rl.v3.sampling import NAMES, schedule, update_scores


def main():
    ap = argparse.ArgumentParser()
    for flag in ('out', 'maps', 'init', 'initial-weights', 'opponents'):
        ap.add_argument('--' + flag, required=True, type=Path)
    ap.add_argument('--steps', required=True, type=int)
    ap.add_argument('--minutes', default=120, type=float)
    ap.add_argument('--seed', required=True, type=int)
    ap.add_argument('--games', default=64, type=int)
    ap.add_argument('--workers', default=4, type=int)
    ap.add_argument('--checkpoint-every', default=250000, type=int)
    ap.add_argument('--resume', type=Path)
    ap.add_argument('--no-external', action='store_true')
    ap.add_argument('--until', default='2026-11-09T02:00:00Z')
    args = ap.parse_args()
    assert min(args.steps, args.games, args.workers, args.checkpoint_every) > 0
    cutoff = datetime.fromisoformat(args.until.replace('Z', '+00:00'))
    assert datetime.now(timezone.utc) < cutoff, 'Research cutoff reached'
    torch.set_num_threads(4)
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    out = args.out
    out.mkdir(parents=True, exist_ok=bool(args.resume))
    maps = json.loads(args.maps.read_text())
    training = [r['map'] for r in maps['training']]
    initial = torch.load(args.init, map_location='cpu', weights_only=False)
    actor, critic = Policy(), Policy()
    actor.load_state_dict(initial['actor'])
    critic.load_state_dict(initial['critic'])
    ao = torch.optim.Adam(actor.parameters(), lr=3e-5)
    vo = torch.optim.Adam(critic.parameters(), lr=3e-4)
    ao.load_state_dict(initial['actor_optimizer'])
    vo.load_state_dict(initial['critic_optimizer'])
    paths = json.loads(args.opponents.read_text())
    assert list(paths) == ['long3m', 'league_extended']
    pool = [cpu_state(actor)] + [torch.load(BASE / paths[n], map_location='cpu', weights_only=False)['actor'] for n in paths]
    pool.extend([cpu_state(actor), cpu_state(actor)])
    pool_steps = [initial['steps'], None, None, initial['steps'], initial['steps']]
    config = {k: initial['config'][k] for k in ('actor_lr', 'critic_lr', 'clip', 'gamma', 'gae_lambda', 'epochs', 'minibatch_turns', 'grad_clip', 'entropy_coef', 'target_kl', 'temperature', 'reward', 'ratio')}
    config.update({'recipe': 'ppo-v3-priority-v1', 'seed': args.seed, 'device': 'cpu', 'torch_threads': 4,
                   'maps_sha256': sha(args.maps), 'initial_checkpoint_sha256': sha(args.init),
                   'initial_weights_sha256': sha(args.initial_weights), 'base_trained_steps': initial['steps'],
                   'opponent_manifest_sha256': sha(args.opponents), 'historical_checkpoint_sha256': {n: sha(BASE / p) for n, p in paths.items()},
                   'names': list(NAMES), 'external_enabled': not args.no_external, 'current_share': .35,
                   'opponent_min_share': .06, 'opponent_max_share': .25, 'difficulty': '(0.2 + 1 - score_ema)^1.5',
                   'ema_decay_per_game': .99, 'greedy_frozen_opponents': True, 'recent_slots': 2,
                   'refresh_decisions': 250000, 'checkpoint_every': args.checkpoint_every,
                   'training_maps': len(training), 'games_per_rollout': args.games, 'workers': args.workers,
                   'evaluation_only': ['khoufou2', 'khoufou', 'v6', 'bc'], 'until': args.until,
                   'selection': 'Separate serial original-referee panel; no in-training selection', 'external_spend': 0})
    assert config['reward'] == 'terminal win/loss/draw +1/-1/0; no shaping'
    steps = iteration = games = 0
    elapsed = 0.
    scores = np.full(len(NAMES), .5)
    next_pool, next_checkpoint, recent_slot = 250000, args.checkpoint_every, 3
    history = []
    previous_teacher = {'games': 0, 'calls': 0, 'summed_call_seconds': 0., 'errors': []}
    source_paths = [Path(__file__).resolve(), BASE / 'code/rl/train/ppo.py', BASE / 'code/rl/train/bc.py',
                    BASE / 'code/rl/league/rollout_league.cpp', BASE / 'code/rl/league/external.py',
                    BASE / 'code/rl/league/teacher_worker.py', BASE / 'code/rl/models/policy.hpp',
                    BASE / 'code/rl/sim/simulator.hpp', BASE / 'code/rl/v3/rollout.py',
                    BASE / 'code/rl/v3/sampling.py', BASE / 'code/rl/v3/build.py',
                    BASE / 'code/opponents/public/lacoz-7f190183/bot.py']
    sources = {str(p.relative_to(BASE)): sha(p) for p in source_paths}
    if args.resume:
        ck = torch.load(args.resume, map_location='cpu', weights_only=False)
        assert config == ck['config'], 'Configuration changed across resume'
        assert sources == json.loads((out / 'source-sha256.json').read_text()), 'Training sources changed across resume'
        actor.load_state_dict(ck['actor'])
        critic.load_state_dict(ck['critic'])
        ao.load_state_dict(ck['actor_optimizer'])
        vo.load_state_dict(ck['critic_optimizer'])
        rng.bit_generator.state = ck['numpy_rng']
        torch.set_rng_state(ck['torch_rng'])
        pool, pool_steps = ck['pool'], ck['pool_steps']
        steps, iteration, games, elapsed = (ck[k] for k in ('steps', 'iteration', 'games', 'elapsed_seconds'))
        next_pool, next_checkpoint, recent_slot = (ck[k] for k in ('next_pool', 'next_checkpoint', 'recent_slot'))
        scores = np.array(ck['opponent_scores'])
        history, previous_teacher = ck['history'], ck['teacher_totals']
        # Preserve crash-tail records separately before returning to the saved boundary.
        existing = [json.loads(line) for line in (out / 'history.jsonl').read_text().splitlines()]
        excess = [r for r in existing if r['iteration'] > iteration]
        if excess:
            save(out / f'recovered-unsaved-{time.time_ns()}.json', excess)
        (out / 'history.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in history))
    else:
        save(out / 'source-sha256.json', sources)
        save(out / 'config.json', config)
        for p in source_paths:
            target = out / 'sources' / p.relative_to(BASE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
    request = {'as_of': datetime.now(timezone.utc).isoformat(), 'target_steps': args.steps,
               'cumulative_wall_cap_seconds': args.minutes * 60, 'resume': bool(args.resume), 'from_steps': steps}
    with (out / 'block-requests.jsonl').open('a') as f:
        f.write(json.dumps(request) + '\n')
    save(out / f'hardware-{steps:08d}.json', {'as_of': request['as_of'], 'python': platform.python_version(),
         'platform': platform.platform(), 'torch': torch.__version__, 'numpy': np.__version__,
         'torch_threads': 4, 'rollout_binary_sha256': sha(BASE / 'code/build/libtryangle_v3.dylib')})
    collector = Rollout(args.initial_weights, training)
    collector.set_pool(pool)
    teachers = Teachers(args.workers, out / 'teachers' / f'block-{steps:08d}') if not args.no_external else None
    if teachers:
        callback = EXTERNAL(teachers.dispatch)
        LIB.league_set_external(collector.ptr, callback)
    start = time.monotonic()
    last_saved = None

    def teacher_totals():
        current = teachers.metrics() if teachers else {'games': 0, 'calls': 0, 'summed_call_seconds': 0., 'errors': []}
        return {**current, **{k: previous_teacher[k] + current[k] for k in previous_teacher if k in current and k != 'teacher_source_sha256'}}

    def checkpoint(path):
        temporary = path.with_suffix('.tmp')
        torch.save({'actor': cpu_state(actor), 'critic': cpu_state(critic), 'actor_optimizer': ao.state_dict(),
                    'critic_optimizer': vo.state_dict(), 'numpy_rng': rng.bit_generator.state, 'torch_rng': torch.get_rng_state(),
                    'config': config, 'steps': steps, 'iteration': iteration, 'games': games, 'pool': pool,
                    'pool_steps': pool_steps, 'next_pool': next_pool, 'next_checkpoint': next_checkpoint,
                    'recent_slot': recent_slot, 'opponent_scores': scores.tolist(), 'history': history,
                    'elapsed_seconds': elapsed + time.monotonic() - start, 'teacher_totals': teacher_totals()}, temporary)
        temporary.replace(path)

    def milestone():
        folder = out / f'step-{steps:08d}'
        folder.mkdir(exist_ok=False)
        export(actor, folder / 'weights.txt')
        checkpoint(folder / 'checkpoint.pt')
        save(folder / 'manifest.json', {'additional_steps': steps, 'base_steps': initial['steps'],
             'weights_sha256': sha(folder / 'weights.txt'), 'checkpoint_sha256': sha(folder / 'checkpoint.pt'),
             'selection_performed': False, 'as_of': datetime.now(timezone.utc).isoformat()})
        print(json.dumps({'checkpoint': str(folder.relative_to(BASE)), 'steps': steps}), flush=True)
        return folder.name

    try:
        while steps < args.steps and elapsed + time.monotonic() - start < args.minutes * 60 and datetime.now(timezone.utc) < cutoff:
            labels, planned, weights = schedule(rng, args.games, scores, not args.no_external)
            collector.set_actor(actor)
            data = collector.collect(planned, args.workers, args.seed + iteration * 1000003,
                                     config['temperature'], audit=16 if iteration == 0 else 0)
            if iteration == 0:
                with gzip.GzipFile(filename=str(out / 'sample-rollouts.json.gz'), mode='wb', mtime=0) as f:
                    f.write(json.dumps(collector.records()).encode())
            result = update(actor, critic, ao, vo, data, config, rng, 'cpu')
            update_scores(scores, labels, data['stats']['outcomes'])
            steps += len(data['old_logp'])
            iteration += 1
            games += data['stats']['games']
            row = {'iteration': iteration, 'steps': steps, 'games': games, 'rollout': data['stats'], 'update': result,
                   'opponent_names': list(NAMES), 'sampled_labels': labels.tolist(), 'sampling_probabilities': weights.tolist(),
                   'opponent_scores': scores.tolist(), 'elapsed_seconds': elapsed + time.monotonic() - start}
            history.append(row)
            with (out / 'history.jsonl').open('a') as f:
                f.write(json.dumps(row) + '\n')
            if steps >= next_pool:
                pool[recent_slot] = cpu_state(actor)
                pool_steps[recent_slot] = initial['steps'] + steps
                scores[recent_slot + 1] = .5
                recent_slot = 4 if recent_slot == 3 else 3
                next_pool += 250000
                collector.set_pool(pool)
            if steps >= next_checkpoint:
                while next_checkpoint <= steps:
                    next_checkpoint += args.checkpoint_every
                last_saved = milestone()
            if iteration % 10 == 0:
                checkpoint(out / 'recovery.pt')
                print(json.dumps({'iteration': iteration, 'steps': steps, 'games': games, 'elapsed_seconds': row['elapsed_seconds'],
                                  'kl': result['final_rollout_kl'], 'opponent_scores': dict(zip(NAMES, scores.tolist()))}), flush=True)
        if last_saved != f'step-{steps:08d}':
            last_saved = milestone()
        checkpoint(out / 'final.pt')
        export(actor, out / 'weights.txt')
        summary = {'additional_steps': steps, 'base_steps': initial['steps'], 'games': games, 'iterations': iteration,
                   'elapsed_seconds': elapsed + time.monotonic() - start, 'last_checkpoint': last_saved,
                   'stop': 'sample_target' if steps >= args.steps else 'deadline' if datetime.now(timezone.utc) >= cutoff else 'wall_cap',
                   'weights_sha256': sha(out / 'weights.txt'), 'max_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   'teacher': teacher_totals(), 'external_spend': 0}
        save(out / f'summary-block-{steps:08d}.json', summary)
        save(out / 'summary.json', summary)
        print(json.dumps(summary, indent=2), flush=True)
    finally:
        if teachers:
            teachers.close()
        collector.close()


if __name__ == '__main__':
    main()
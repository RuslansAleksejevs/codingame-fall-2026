#!/usr/bin/env python3
"""Controlled 85/15 vs ordinary continuation using the unchanged PPO update."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import resource
import signal
import time
import numpy as np
import torch
from common import ROOT, HERE, OUT, BASE, BUILD, now, save, sha
from native import Rollout, LIB, EXTERNAL
from rl.train.bc import Policy, export
from rl.train.ppo import update, cpu_state
from rl.league.external import Teachers

MAPS = ROOT / 'experiments/rl/2026-11-06-ppo-v2/maps-2000.json'
OLDER = ROOT / 'experiments/rl/2026-11-06-ppo-v1/training/weights.txt'
FIELDS = ('actor_lr', 'critic_lr', 'clip', 'gamma', 'gae_lambda', 'epochs', 'minibatch_turns',
          'grad_clip', 'entropy_coef', 'target_kl', 'temperature', 'reward', 'ratio')


def completed_prefix(data, remaining):
    """Stop the last training batch at a real episode boundary, never fake terminal."""
    if len(data['old_logp']) < remaining:
        return data
    episodes = int(np.searchsorted(data['episode_offsets'][1:], remaining, side='left')) + 1
    turns = int(data['episode_offsets'][episodes])
    groups = int(data['turn_offsets'][turns])
    candidates = int(data['group_offsets'][groups])
    result = dict(data)
    for key in ('value_x', 'old_logp', 'old_entropy', 'reward', 'game_ids', 'players'):
        result[key] = data[key][:turns]
    result.update(x=data['x'][:candidates], group_offsets=data['group_offsets'][:groups + 1],
                  choices=data['choices'][:groups], turn_offsets=data['turn_offsets'][:turns + 1],
                  episode_offsets=data['episode_offsets'][:episodes + 1])
    outcomes = data['stats']['outcomes'][:episodes]
    result['stats'] = dict(data['stats'], collected_decisions=len(data['old_logp']), collected_games=data['stats']['games'],
                           games=episodes, controlled_decisions=turns, groups=groups, candidates=candidates,
                           outcomes=outcomes, restored_games=sum(row[2] >= 0 for row in outcomes),
                           unused_complete_episode_decisions=len(data['old_logp']) - turns)
    return result


def scheduled(seed, iteration, maps, bank, fraction, games=64, external=True):
    # Separate streams: treatment does not change ordinary maps/opponents/seats.
    rng = np.random.default_rng(np.random.SeedSequence([seed, iteration, 1]))
    starts_rng = np.random.default_rng(np.random.SeedSequence([seed, iteration, 2]))
    labels = np.array([-1] * (games // 2) + [0] * (games // 4) + [1] * (games // 8) +
                      [(-2 if external else 1)] * (games - games // 2 - games // 4 - games // 8))
    rng.shuffle(labels)
    result = np.column_stack([rng.integers(maps, size=games), labels, rng.integers(2, size=games), np.full(games, -1)])
    for i in range(games):
        probability = fraction / .875 if external else fraction
        if starts_rng.random() < probability and result[i, 1] != -2:
            category = ('loss', 'win', 'fresh')[int(starts_rng.integers(3))]
            candidates = [j for j, row in enumerate(bank) if row['category'] == category and row['seat'] == result[i, 2]]
            assert candidates, (category, int(result[i, 2]))
            result[i, 3] = candidates[int(starts_rng.integers(len(candidates)))]
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--fraction', required=True, type=float, choices=[0., .15])
    ap.add_argument('--steps', default=100000, type=int)
    ap.add_argument('--minutes', default=12., type=float)
    ap.add_argument('--seed', default=202611081, type=int)
    ap.add_argument('--games', default=64, type=int)
    ap.add_argument('--workers', default=4, type=int)
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--no-external', action='store_true')
    ap.add_argument('--max-updates', type=int)
    args = ap.parse_args()
    assert 0 < args.minutes <= 23 and args.steps > 0 and args.games >= 8 and 1 <= args.workers <= 4
    cutoff = datetime(2026, 11, 9, 2, tzinfo=timezone.utc)
    assert datetime.now(timezone.utc) < cutoff
    out = args.out.resolve()
    assert out.is_relative_to(OUT)
    out.mkdir(parents=True, exist_ok=args.resume)
    verification = json.loads((OUT / 'bank-verification.json').read_text())
    assert verification['passed'] and verification['bank_sha256'] == sha(OUT / 'bank.json')
    assert json.loads((OUT / 'restoration.json').read_text())['passed']
    if args.steps > 4000:
        assert json.loads((OUT / 'contracts/summary.json').read_text())['passed']
    bank = json.loads((OUT / 'bank.json').read_text())['records']
    maps = [r['map'] for r in json.loads(MAPS.read_text())['training']]
    assert sha(BASE / 'checkpoint.pt') == '9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663'
    assert sha(BASE / 'weights.txt') == 'dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb'
    torch.set_num_threads(4)
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    ck = torch.load(BASE / 'checkpoint.pt', weights_only=False, map_location='cpu')
    config = {key: ck['config'][key] for key in FIELDS}
    config.update({'recipe': 'rl4-early-state-controlled-v1', 'seed': args.seed, 'fraction': args.fraction,
                   'workers': args.workers, 'games_per_rollout': args.games, 'external': not args.no_external,
                   'bank_sha256': sha(OUT / 'bank.json'), 'maps_sha256': sha(MAPS), 'base_sha256': sha(BASE / 'checkpoint.pt'),
                   'opponents_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (BASE / 'weights.txt', OLDER)},
                   'learner_seats': 'one scheduled learner seat per episode, including current self-play',
                   'opponent_schedule': '50% current,25% frozen league3m,12.5% older PPO,12.5% Lacoz',
                   'restored_opponents': 'Stateless neural policies only; stateful Lacoz always starts from the real initial state',
                   'torch_threads': 4, 'device': 'cpu', 'external_spend': 0})
    assert config['reward'] == 'terminal win/loss/draw +1/-1/0; no shaping'
    sources = {str(p.relative_to(ROOT)): sha(p) for p in [HERE / 'train.py', HERE / 'native.py', HERE / 'native.cpp', HERE / 'state.py', HERE / 'state.hpp',
               ROOT / 'code/rl/train/ppo.py', ROOT / 'code/rl/train/bc.py', ROOT / 'code/rl/sim/simulator.hpp', ROOT / 'code/rl/models/policy.hpp',
               ROOT / 'code/rl/league/rollout_league.cpp', ROOT / 'code/rl/league/external.py', ROOT / 'code/rl/league/teacher_worker.py',
               ROOT / 'code/opponents/public/lacoz-7f190183/bot.py']}
    initial = ck
    if args.resume:
        ck = torch.load(out / 'checkpoint.pt', weights_only=False, map_location='cpu')
        assert ck['config'] == config and ck['sources'] == sources
        rng.bit_generator.state = ck['numpy_rng']
    actor, critic = Policy(), Policy()
    actor.load_state_dict(ck['actor'])
    critic.load_state_dict(ck['critic'])
    ao = torch.optim.Adam(actor.parameters(), lr=config['actor_lr'])
    vo = torch.optim.Adam(critic.parameters(), lr=config['critic_lr'])
    ao.load_state_dict(ck['actor_optimizer'])
    vo.load_state_dict(ck['critic_optimizer'])
    if args.resume:
        torch.set_rng_state(ck['torch_rng'])
    steps = ck['steps'] if args.resume else 0
    iteration = ck['iteration'] if args.resume else 0
    games = ck['games'] if args.resume else 0
    restored_games = ck['restored_games'] if args.resume else 0
    restored_decisions = ck['restored_decisions'] if args.resume else 0
    category_episodes = ck['category_episodes'] if args.resume else {'loss': 0, 'win': 0, 'fresh': 0}
    elapsed = ck['elapsed_seconds'] if args.resume else 0.
    save(out / 'config.json', config)
    save(out / 'source-sha256.json', sources)
    save(out / f'run-{iteration:06d}.json', {'as_of': now(), 'target_steps': args.steps, 'block_minutes': args.minutes,
         'starting_steps': steps, 'python': platform.python_version(), 'torch': torch.__version__, 'numpy': np.__version__,
         'binary_sha256': sha(BUILD / 'libcurriculum.dylib'), 'pid': os.getpid(), 'external_spend': 0})
    collector = Rollout(BASE / 'weights.txt', maps, [r['snapshot'] for r in bank], [BASE / 'weights.txt', OLDER])
    teachers = Teachers(args.workers, out / f'teachers-{iteration:06d}') if not args.no_external else None
    if teachers:
        callback = EXTERNAL(teachers.dispatch)
        LIB.league_set_external(collector.ptr, callback)
    start = time.monotonic()
    starting_iteration = iteration
    stopping = False

    def request_stop(*unused):
        nonlocal stopping
        stopping = True
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    def checkpoint():
        temporary = out / 'checkpoint.tmp'
        torch.save({'actor': cpu_state(actor), 'critic': cpu_state(critic), 'actor_optimizer': ao.state_dict(),
                    'critic_optimizer': vo.state_dict(), 'numpy_rng': rng.bit_generator.state, 'torch_rng': torch.get_rng_state(),
                    'config': config, 'sources': sources, 'steps': steps, 'iteration': iteration, 'games': games,
                    'restored_games': restored_games, 'elapsed_seconds': elapsed + time.monotonic() - start,
                    'restored_decisions': restored_decisions, 'category_episodes': category_episodes,
                    'base_steps': initial['steps']}, temporary)
        temporary.replace(out / 'checkpoint.pt')

    try:
        while steps < args.steps and time.monotonic() - start < args.minutes * 60 and not stopping and datetime.now(timezone.utc) < cutoff and (args.max_updates is None or iteration - starting_iteration < args.max_updates):
            planned = scheduled(args.seed, iteration, len(maps), bank, args.fraction, args.games, not args.no_external)
            collector.set_actor(actor)
            data = collector.collect(planned, args.workers, args.seed + iteration * 1000003, config['temperature'], audit=8 if iteration == 0 else 0)
            if iteration == 0:
                save(out / 'sample-rollouts.json', collector.records())
            data = completed_prefix(data, args.steps - steps)
            result = update(actor, critic, ao, vo, data, config, rng, 'cpu')
            steps += len(data['old_logp'])
            games += data['stats']['games']
            restored_games += data['stats']['restored_games']
            restored_decisions += sum(row[4] for row in data['stats']['outcomes'] if row[2] >= 0)
            for row in planned[:data['stats']['games']]:
                if row[3] >= 0:
                    category_episodes[bank[int(row[3])]['category']] += 1
            iteration += 1
            row = {'iteration': iteration, 'steps': steps, 'games': games, 'restored_games': restored_games,
                   'elapsed_seconds': elapsed + time.monotonic() - start, 'rollout': data['stats'], 'update': result,
                   'schedule': planned.tolist()}
            with (out / 'history.jsonl').open('a') as log:
                log.write(json.dumps(row) + '\n')
            checkpoint()
            if iteration % 5 == 0:
                print(json.dumps({k: row[k] for k in ('iteration', 'steps', 'games', 'restored_games', 'elapsed_seconds')}), flush=True)
        export(actor, out / 'weights.txt')
        checkpoint()
        summary = {'as_of': now(), 'steps': steps, 'target_steps': args.steps, 'decision_overshoot': max(0, steps - args.steps),
                   'games': games, 'restored_games': restored_games, 'restored_episode_share': restored_games / games if games else 0,
                   'restored_decisions': restored_decisions, 'restored_decision_share': restored_decisions / steps if steps else 0,
                   'category_episodes': category_episodes,
                   'iterations': iteration, 'elapsed_seconds': elapsed + time.monotonic() - start,
                   'stop': 'sample_target' if steps >= args.steps else 'time_or_stop', 'weights_sha256': sha(out / 'weights.txt'),
                   'checkpoint_sha256': sha(out / 'checkpoint.pt'), 'max_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   'teacher': teachers.metrics() if teachers else None, 'external_spend': 0}
        save(out / 'summary.json', summary)
        print(json.dumps(summary), flush=True)
    finally:
        if teachers:
            teachers.close()
        collector.close()


if __name__ == '__main__':
    main()
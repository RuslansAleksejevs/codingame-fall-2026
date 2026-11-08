#!/usr/bin/env python3
"""Search contracts and small counterfactual ranking checks on exposed maps."""
import argparse
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import statistics
import subprocess
import sys
import ctypes as C

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from run_matches import BASE, REPO, java_home
from rl.sim.native import Simulator, LIB as SIM
from rl.search.native import Search
from rl.data.replays import read
from rl.train.ppo import save, sha

SIM.sim_clone.argtypes = [C.c_void_p]
SIM.sim_clone.restype = C.c_void_p
SIM.net_new.argtypes = [C.c_char_p]
SIM.net_new.restype = C.c_void_p
SIM.net_act.argtypes = [C.c_void_p, C.c_void_p, C.c_int, C.c_int]
SIM.net_act.restype = C.c_char_p
SIM.net_delete.argtypes = [C.c_void_p]


def clone(sim):
    result = object.__new__(Simulator)
    result.ptr = SIM.sim_clone(sim.ptr)
    return result


def rollout(root, player, first, actor, enemy):
    sim = clone(root)
    commands = []
    try:
        while not sim.state()['done']:
            own = first if not commands else actor.act(sim, player)[0]
            other = enemy.act(sim, 1 - player)[0]
            pair = [own, other] if player == 0 else [other, own]
            sim.step(pair)
            commands.append(pair)
            assert not any(sim.state()['errors'])
        score = sim.state()['score']
        outcome = (score[player] > score[1 - player]) - (score[player] < score[1 - player])
        return {'value': .995 ** (len(commands) - 1) * outcome, 'scores': score, 'actions': commands}
    finally:
        sim.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    root = BASE / 'experiments/rl/2026-11-07-ppo-v3'
    actor = BASE / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt'
    critic = root / 'search/frozen-critic/critic.txt'
    enemies = [actor, BASE / 'experiments/rl/2026-11-06-ppo-v2/control-long/step-03002813/weights.txt',
               BASE / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-04836947/weights.txt']
    search = Search(actor, critic, enemies, depth=2, candidates=4, budget_ms=0)
    budgeted = Search(actor, critic, enemies, depth=2, candidates=4, budget_ms=30)
    greedy = Search(actor, critic, enemies, candidates=1, budget_ms=0)
    enemy_policies = [Search(p, critic, enemies, candidates=1, budget_ms=0) for p in enemies]
    scalar = SIM.net_new(str(actor).encode())
    assert scalar
    cp = str(BASE / 'code/build') + ':' + str(REPO / 'target/classes') + ':' + (REPO / 'classpath.txt').read_text().strip()
    oracle = subprocess.Popen([str(java_home() / 'bin/java'), '-Xmx1g', '-cp', cp, 'Oracle'],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    cases = []
    counterfactuals = []
    states_compared = 0
    records = [root / 'baseline-dev' / f'league3m-vs-lacoz-seed30001-seat{seat}.json.gz' for seat in (0, 1)]
    try:
        for path in records:
            record = read(path)
            sim = Simulator(record['map'])
            prefix = []
            try:
                for turn, decision in enumerate(record['decisions']):
                    if turn in (0, 5, 10):
                        for player in (0, 1):
                            before = sim.state()
                            action, info = search.act(sim, player)
                            again, _ = search.act(sim, player)
                            assert action == again and sim.state() == before
                            assert abs(search.value(sim, 0) + search.value(sim, 1)) < 1e-12
                            control, control_info = greedy.act(sim, player)
                            assert control == SIM.net_act(scalar, sim.ptr, player, 2).decode()
                            assert control_info['transitions'] == 0
                            bounded_action, bounded_info = budgeted.act(sim, player)
                            alternate = clone(sim)
                            pair = decision['actions'].copy()
                            pair[player] = action
                            alternate.step(pair)
                            assert not any(alternate.state()['errors']) and sim.state() == before
                            oracle.stdin.write(json.dumps(dict(record['map'], actions=prefix + [pair])) + '\n')
                            oracle.stdin.flush()
                            reference = json.loads(oracle.stdout.readline())[-1]
                            actual = alternate.state()
                            assert all(actual[k] == reference[k] for k in ('turn', 'score', 'units', 'edges', 'triangles', 'done'))
                            states_compared += 1
                            alternate.close()
                            bounded_sim = clone(sim)
                            pair[player] = bounded_action
                            bounded_sim.step(pair)
                            assert not any(bounded_sim.state()['errors'])
                            bounded_sim.close()
                            diagnostic = {'record': str(path.relative_to(BASE)), 'turn': turn, 'player': player,
                                          'search': info, 'budgeted': bounded_info, 'changed': action != control}
                            if action != control:
                                outcomes = {}
                                for name, first in [('greedy', control), ('search', action)]:
                                    outcomes[name] = [rollout(sim, player, first, greedy, enemy) for enemy in enemy_policies]
                                values = {name: [r['value'] for r in results] for name, results in outcomes.items()}
                                aggregate = {name: .5 * statistics.mean(v) + .5 * min(v) for name, v in values.items()}
                                diagnostic['counterfactual_complete_game_delta'] = aggregate['search'] - aggregate['greedy']
                                counterfactuals.append({'case': len(cases), 'root': before, 'outcomes': outcomes})
                            cases.append(diagnostic)
                    sim.step(decision['actions'])
                    prefix.append(decision['actions'])
                    if turn >= 10:
                        break
            finally:
                sim.close()
    finally:
        oracle.stdin.close()
        oracle.wait(timeout=20)
        SIM.net_delete(scalar)
        for policy in [search, budgeted, greedy, *enemy_policies]:
            policy.close()
    changed = [c for c in cases if c['changed']]
    result = {'as_of': datetime.now(timezone.utc).isoformat(), 'passed': True, 'cases': len(cases),
              'java_counterfactual_states': states_compared, 'root_immutable': True,
              'greedy_matches_scalar': True, 'unbounded_search_deterministic': True,
              'value_antisymmetric': True, 'changed_plans': len(changed),
              'counterfactual_improved': sum(c['counterfactual_complete_game_delta'] > .001 for c in changed),
              'counterfactual_worsened': sum(c['counterfactual_complete_game_delta'] < -.001 for c in changed),
              'under_training_load': True,
              'timing_caveat': 'Diagnostic timings under active PPO load; not uncontended runtime evidence.',
              'ranking_caveat': 'Same exposed roots; full greedy continuations against the three response models. Not independent external-opponent evidence.',
              'source_sha256': {str(p.relative_to(BASE)): sha(p) for p in (BASE / 'code/rl/search').glob('*') if p.is_file()},
              'weights_sha256': {str(p.relative_to(BASE)): sha(p) for p in [actor, critic, *enemies]},
              'details': cases}
    save(args.out / 'summary.json', result)
    with gzip.GzipFile(filename=str(args.out / 'counterfactuals.json.gz'), mode='wb', mtime=0) as f:
        f.write(json.dumps(counterfactuals).encode())
    print(json.dumps({k: v for k, v in result.items() if k not in ('details', 'source_sha256', 'weights_sha256')}, indent=2))


if __name__ == '__main__':
    main()
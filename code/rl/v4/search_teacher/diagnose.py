"""Fresh-map, exact-simulator ranking checks. No student targets are generated."""
import argparse
import ctypes as C
import gzip
import json
import statistics
import subprocess
import time
from pathlib import Path
from common import ACTOR, CRITIC, ENEMIES, OUT, ROOT, checked_seeds, check_preserved, now, relative, save, sha
from run_matches import REPO, java_home
from rl.sim.native import Simulator


def combined(values):
    return .5*statistics.mean(values)+.5*min(values)


def select(values):
    best = 0
    for i, value in enumerate(values[1:], 1):
        if value > values[0]+.02 and value > values[best]: best = i
    return best


class Native:
    def __init__(self):
        self.lib = C.CDLL(str(OUT / 'build/diagnostic.dylib'))
        self.lib.search_new.argtypes = [C.c_char_p]*5+[C.c_int, C.c_int, C.c_double]
        self.lib.search_new.restype = C.c_void_p
        for name in ('search_act', 'teacher_inspect'):
            getattr(self.lib, name).argtypes = [C.c_void_p, C.c_void_p, C.c_int]
            getattr(self.lib, name).restype = C.c_char_p
        self.lib.search_info.argtypes = [C.c_void_p]; self.lib.search_info.restype = C.c_char_p
        self.lib.search_error.restype = C.c_char_p
        self.lib.search_delete.argtypes = [C.c_void_p]
        self.policies = []

    def policy(self, path=ACTOR, count=1):
        ptr = self.lib.search_new(*[str(p).encode() for p in [path, CRITIC, *ENEMIES]], 2, count, 0)
        if not ptr: raise RuntimeError(self.lib.search_error().decode())
        self.policies.append(ptr)
        return ptr

    def act(self, policy, sim, player):
        result = self.lib.search_act(policy, sim.ptr, player)
        if result is None: raise RuntimeError(self.lib.search_error().decode())
        return result.decode()

    def inspect(self, policy, sim, player):
        result = self.lib.teacher_inspect(policy, sim.ptr, player)
        if result is None: raise RuntimeError(self.lib.search_error().decode())
        return json.loads(result)

    def close(self):
        for ptr in self.policies: self.lib.search_delete(ptr)
        self.policies.clear()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--registry', type=Path, required=True)
    ap.add_argument('--maps',type=Path,required=True)
    args = ap.parse_args(); check_preserved()
    out = OUT / 'diagnostic'; out.mkdir(exist_ok=False)
    registry = json.loads(args.registry.read_text())
    known = set(registry['canonical']); legacy = set(registry.get('legacy', []))
    cp = str(ROOT/'code/build')+':'+str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()
    command = [str(java_home()/'bin/java'), '-Xmx1g', '-cp', cp]
    oracle = subprocess.Popen([*command, 'Oracle'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    native = Native(); teacher = native.policy(count=4); actor = native.policy()
    enemies = [native.policy(p) for p in ENEMIES]
    cases, maps = [], {}; comparisons = 0; continuations = 0
    started = time.monotonic()
    try:
        entries=json.loads(args.maps.read_text())['maps']
        assert [row['seed'] for row in entries]==checked_seeds(list(range(62001,62007)))
        for index, entry in enumerate(entries):
            check_preserved()
            seed,board=entry['seed'],entry['map']
            import hashlib
            digest = hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            old_digest = entry['legacy_hash']
            assert digest==entry['hash']
            assert digest not in known and old_digest not in legacy and digest not in maps.values(), 'Content overlap'
            maps[seed] = digest
            for player in (0, 1):
                sim = Simulator(board); prefix = []
                try:
                    for turn in range(11):
                        if sim.state()['done']: break
                        if turn in (0,5,10):
                            before = sim.state()
                            result = native.inspect(teacher, sim, player)
                            assert sim.state() == before == result['root']
                            assert native.act(actor, sim, player) == result['plans'][0]['command']
                            predicted = [combined([m['short_values'][1] for m in p['models']]) for p in result['plans']]
                            actual = native.act(teacher, sim, player)
                            info = json.loads(native.lib.search_info(teacher))
                            assert actual == result['plans'][select(predicted)]['command']
                            assert all(abs(a-b)<1e-7 for a,b in zip(predicted,info['values']))
                            assert len(predicted)==len(info['values'])
                            if turn==0:
                                repeated = native.inspect(teacher, sim, player)
                                assert repeated == result, 'Nondeterministic diagnostic'
                            for plan in result['plans']:
                                for model, continuation in enumerate(plan['models']):
                                    actions = continuation['actions']
                                    assert actions[0][1-player] == result['root_responses'][model]
                                    oracle.stdin.write(json.dumps(dict(board,actions=prefix+actions))+'\n'); oracle.stdin.flush()
                                    references = json.loads(oracle.stdout.readline())
                                    for snapshot in continuation['snapshots']:
                                        expected = references[len(prefix)+snapshot['depth']]
                                        observed = snapshot['state']
                                        assert all(observed[k]==expected[k] for k in ('turn','score','units','edges','triangles','done'))
                                        assert not any(observed['errors'])
                                        comparisons += 1
                                    assert references[-1]['done']
                                    continuations += 1
                            result.update(seed=seed, turn=turn, map_content_sha256=digest,
                                          trajectory_enemy=index%3, board=board, prefix=prefix.copy())
                            cases.append(result)
                            print(json.dumps({'case':len(cases),'seed':seed,'player':player,'turn':turn,
                                              'plans':len(predicted),'java_snapshots':comparisons}), flush=True)
                        own = native.act(actor, sim, player)
                        other = native.act(enemies[index%3], sim, 1-player)
                        pair = [own,other] if player==0 else [other,own]
                        sim.step(pair); prefix.append(pair)
                        assert not any(sim.state()['errors'])
                finally:
                    sim.close()
    finally:
        native.close()
        for process in (oracle,):
            process.stdin.close(); process.wait(timeout=20)
        with gzip.GzipFile(filename=str(out/'cases.json.gz'), mode='wb',mtime=0) as stream:
            stream.write(json.dumps(cases).encode())
        save(out/'map-hashes.json', maps)
    metrics = {}
    for h, depth in enumerate((1,2,4,8)):
        concordant = comparable = improvements = worsenings = changed = 0; regret = []; deltas = []
        per_model = [{'concordant':0,'comparable':0} for _ in range(3)]
        for case in cases:
            plans = case['plans']
            prediction = [combined([m['short_values'][h] for m in p['models']]) for p in plans]
            terminal = [combined([m['discounted_terminal'] for m in p['models']]) for p in plans]
            choice = select(prediction)
            regret.append(max(terminal)-terminal[choice]); deltas.append(terminal[choice]-terminal[0])
            changed += choice != 0; improvements += deltas[-1]>1e-8; worsenings += deltas[-1]<-1e-8
            for i in range(len(plans)):
                for j in range(i):
                    a,b = prediction[i]-prediction[j],terminal[i]-terminal[j]
                    if abs(b)>1e-8:
                        comparable += 1; concordant += a*b>0
                    for m in range(3):
                        a=plans[i]['models'][m]['short_values'][h]-plans[j]['models'][m]['short_values'][h]
                        b=plans[i]['models'][m]['discounted_terminal']-plans[j]['models'][m]['discounted_terminal']
                        if abs(b)>1e-8:
                            per_model[m]['comparable']+=1;per_model[m]['concordant']+=a*b>0
        metrics[str(depth)] = {'pairwise_concordant':concordant,'pairwise_non_tied':comparable,
            'concordance':concordant/comparable if comparable else None,
            'mean_selection_regret':statistics.mean(regret),'mean_delta_vs_greedy':statistics.mean(deltas),
            'changed':changed,'improved':improvements,'worsened':worsenings,'per_model':per_model}
    save(out/'summary.json', {'as_of':now(),'passed':True,'cases':len(cases), 'maps':len(maps),
        'complete_counterfactual_continuations':continuations,'java_snapshots_compared':comparisons,
        'root_immutable':True,'baseline_included':True,'depth2_matches_frozen_teacher':True,
        'deterministic_repeat':True,'parse_errors':0,'metrics':metrics,'wall_seconds':time.monotonic()-started,
        'registry':relative(args.registry),'registry_sha256':sha(args.registry),
        'cases_sha256':sha(out/'cases.json.gz'),'weights':{relative(p):sha(p) for p in [ACTOR,CRITIC,*ENEMIES]},
        'external_spend':0,'scope':'Offline diagnostics versus three teacher response models; not independent strength or timed-program evidence.'})
    print(json.dumps(metrics,indent=2),flush=True)


if __name__ == '__main__':
    main()
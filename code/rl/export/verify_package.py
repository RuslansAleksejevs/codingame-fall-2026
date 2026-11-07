#!/usr/bin/env python3
"""Check original C++ weight parsing and full replay plans against the package."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BASE / 'code'))
from rl.data.replays import read
from rl.sim.native import Simulator
from rl.league.rollout import LIB

build = BASE / 'code/build'
build.mkdir(exist_ok=True)
selection = json.loads((BASE / 'code/rl/configs/selected-policy.json').read_text())
weights = BASE / selection['weights']
def run(args, **kwargs):
    return subprocess.run(list(map(str, args)), check=True, capture_output=True, **kwargs)

run(['clang++', '-std=c++17', '-O3', BASE / 'code/rl/export/bot.cpp', '-o', build / 'ppo2-reference'])
run(['clang++', '-std=c++17', '-O3', '-Wall', '-Wextra', '-Wpedantic', BASE / 'submissions/ppo-v2-league3m.cpp', '-o', build / 'ppo2-submission'])
run(['clang++', '-std=c++17', '-O3', '-DTRYANGLE_PACK_CHECK', BASE / 'submissions/ppo-v2-league3m.cpp', '-o', build / 'ppo2-unpack-check'])
run(['clang++', '-std=c++17', '-O3', BASE / 'submissions/ppo-v2-league3m-silver.cpp', '-o', build / 'ppo2-submission-silver'])
silver_header = (BASE / 'code/rl/models/policy.hpp').read_text().replace('#include "../sim/simulator.hpp"', '#include "../rl/sim/simulator.hpp"')
assert silver_header.count('float v=evaluate(dec.features(cs[j]));') == 1
silver_header = silver_header.replace('float v=evaluate(dec.features(cs[j]));', 'if(cs[j].kind>4)continue;float v=evaluate(dec.features(cs[j]));')
(build / 'package-reference-silver.hpp').write_text(silver_header)
(build / 'package-reference-silver.cpp').write_text((BASE / 'code/rl/export/bot.cpp').read_text().replace('#include "../models/policy.hpp"', '#include "package-reference-silver.hpp"'))
run(['clang++', '-std=c++17', '-O3', build / 'package-reference-silver.cpp', '-o', build / 'ppo2-reference-silver'])
dump = build / 'ppo2-dump-original.cpp'
dump.write_text('''#include "../rl/models/policy.hpp"
#include <iostream>
int main(int argc, char** argv) {
    rl::Network net; net.load(argv[1]);
    for (size_t i = 0; i < net.weights.size(); ++i) {
        for (auto* v : {&net.weights[i], &net.bias[i]})
            std::cout.write(reinterpret_cast<const char*>(v->data()), v->size()*sizeof(float));
    }
}
''')
run(['clang++', '-std=c++17', '-O3', dump, '-o', build / 'ppo2-dump-original'])
original = run([build / 'ppo2-dump-original', weights]).stdout
embedded = run([build / 'ppo2-unpack-check']).stdout
assert original == embedded == (build / 'ppo2-expected-float32.bin').read_bytes()
math_check = build / 'ppo2-check-math.cpp'
math_check.write_text('''#include "../rl/export/inference.hpp"
#include <cstring>
#include <iostream>
#include <random>
int main(int argc, char** argv) {
    rl::Network net; net.load(argv[1]); rl::FastNetwork fast(net);
    std::mt19937 rng(20261107);
    int mismatches=0;float largest=0,relative=0;
    for(int i=0;i<10000;++i) {
        std::array<float,rl::FEATURES> x;
        for(float& v:x) v=(int(rng()%10001)-5000)/1000.f;
        float a=net.evaluate(x), b=fast.evaluate(x);
        mismatches+=std::memcmp(&a,&b,sizeof(float))!=0;
        largest=std::max(largest,std::abs(a-b));
        relative=std::max(relative,std::abs(a-b)/std::max(1.f,std::abs(a)));
    }
    std::cout << mismatches << " " << largest << " " << relative;
}
''')
run(['clang++', '-std=c++17', '-O3', math_check, '-o', build / 'ppo2-check-math'])
math_values = run([build / 'ppo2-check-math', weights]).stdout.decode().split()
assert float(math_values[2]) < 5e-5
run(['clang++', '-std=c++17', '-O3', '-ffp-contract=off', math_check, '-o', build / 'ppo2-check-math'])
fixed_values = run([build / 'ppo2-check-math', weights]).stdout.decode().split()
assert int(fixed_values[0]) == 0

archive = BASE / 'experiments/rl/2026-11-06-ppo-v2/confirmation/records.tar.gz'
results, timings = [], []
with tarfile.open(archive) as bundle:
    members = [m for m in bundle.getmembers() if m.name.startswith('ppo2-') and m.name.endswith('.json.gz')]
    # Spread across the archive rather than selecting the shortest games.
    chosen = [members[i * (len(members)-1)//99] for i in range(100)]
    for member in chosen:
        replay_path = build / 'package-replay.json.gz'
        replay_path.write_bytes(bundle.extractfile(member).read())
        replay = read(replay_path)
        assert not replay['errors']
        simulator = Simulator(replay['map'])
        inputs = [[], []]
        for turn, decision in enumerate(replay['decisions']):
            for seat in (0, 1):
                inputs[seat].append(LIB.league_observation(simulator.ptr, seat, int(turn == 0)))
            simulator.step(decision['actions'])
        simulator.close()
        for seat in (0, 1):
            stdin = b''.join(inputs[seat])
            reference = run([build / 'ppo2-reference', weights, '2'], input=stdin)
            packaged = run([build / 'ppo2-submission'], input=stdin)
            assert reference.stdout == packaged.stdout, (member.name, seat)
            reference_silver = run([build / 'ppo2-reference-silver', weights, '2'], input=stdin)
            packaged_silver = run([build / 'ppo2-submission-silver'], input=stdin)
            assert reference_silver.stdout == packaged_silver.stdout, (member.name, seat, 'silver')
            assert b'ADD_PATH' not in packaged_silver.stdout and b'REMOVE_PATH' not in packaged_silver.stdout
            plans = packaged.stdout.splitlines()
            assert len(plans) == len(replay['decisions'])
            timings.extend(map(int, re.findall(rb'plan_us=(\d+)', packaged.stderr)))
            results.append({'replay': member.name, 'seat': seat, 'plans': len(plans),
                            'input_sha256': hashlib.sha256(stdin).hexdigest(),
                            'silver_output_sha256': hashlib.sha256(packaged_silver.stdout).hexdigest(),
                            'output_sha256': hashlib.sha256(packaged.stdout).hexdigest()})
timings.sort()
report = {'as_of': datetime.now(timezone.utc).isoformat(), 'provenance': 'PROJECT_REPORTED',
          'source_sha256': hashlib.sha256((BASE / 'submissions/ppo-v2-league3m.cpp').read_bytes()).hexdigest(),
          'original_cpp_weights_equal_embedded': True, 'float32_parameters': len(original)//4,
          'float32_sha256': hashlib.sha256(original).hexdigest(),
          'random_forward_values': 10000, 'fixed_contraction_bit_mismatches': int(fixed_values[0]),
          'default_contraction': {'bit_mismatches': int(math_values[0]), 'max_absolute_error': float(math_values[1]), 'max_normalized_error': float(math_values[2])},
          'replays': len(chosen), 'seats': len(results),
          'identical_plans': sum(r['plans'] for r in results), 'mismatches': 0,
          'silver_identical_plans': sum(r['plans'] for r in results), 'silver_road_commands': 0,
          'silver_source_sha256': hashlib.sha256((BASE / 'submissions/ppo-v2-league3m-silver.cpp').read_bytes()).hexdigest(),
          'local_plan_us': {'median': timings[len(timings)//2], 'p99': timings[int(.99*(len(timings)-1))], 'max': timings[-1]},
          'compiler': run(['clang++', '--version']).stdout.decode().splitlines()[0], 'results': results}
out = BASE / 'experiments/rl/2026-11-06-live-ppo-v2/package-verification.json'
out.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k != 'results'}, indent=2))

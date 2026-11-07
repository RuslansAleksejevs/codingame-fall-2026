#!/usr/bin/env python3
"""Compare the standalone stdin/stdout road bot with native policy actions."""
import argparse
import ctypes as C
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from rl.sim.native import Simulator
from rl.roads.rollout import LIB


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--maps', type=Path, required=True)
    parser.add_argument('--records', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    maps = [row['map'] for row in json.loads(args.maps.read_text())['training']]
    records = json.loads(gzip.decompress(args.records.read_bytes()))
    LIB.roads_net_new.argtypes = [C.c_char_p]
    LIB.roads_net_new.restype = C.c_void_p
    LIB.roads_net_delete.argtypes = [C.c_void_p]
    LIB.roads_net_act.argtypes = [C.c_void_p, C.c_void_p, C.c_int, C.c_int]
    LIB.roads_net_act.restype = C.c_char_p
    net = LIB.roads_net_new(str(args.weights.resolve()).encode())
    assert net
    streams = []
    try:
        for record in records[:4]:
            for player in (0, 1):
                simulator = Simulator(maps[record['map_index']])
                inputs, expected = [], []
                for turn, actions in enumerate(record['actions']):
                    inputs.append(LIB.roads_observation(simulator.ptr, player, int(turn == 0)).decode())
                    expected.append(LIB.roads_net_act(net, simulator.ptr, player, 3).decode())
                    simulator.step(actions)
                simulator.close()
                text = ''.join(inputs)
                result = subprocess.run([str(args.binary.resolve()), str(args.weights.resolve()), '3'],
                                        input=text, text=True, capture_output=True, timeout=60, check=True)
                assert result.stdout.splitlines() == expected
                streams.append({'map_index': record['map_index'], 'player': player, 'turns': len(expected),
                                'input_sha256': hashlib.sha256(text.encode()).hexdigest(),
                                'output_sha256': hashlib.sha256(result.stdout.encode()).hexdigest()})
    finally:
        LIB.roads_net_delete(net)
    report = {'passed': True, 'streams': streams, 'identical_full_turn_plans': sum(r['turns'] for r in streams),
              'weights_sha256': hashlib.sha256(args.weights.read_bytes()).hexdigest(),
              'binary_sha256': hashlib.sha256(args.binary.read_bytes()).hexdigest(),
              'note': 'Untimed protocol/action parity; not a competitive strength/timing evaluation.'}
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'streams'}, indent=2))


if __name__ == '__main__':
    main()

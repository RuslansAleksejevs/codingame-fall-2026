#!/usr/bin/env python3
"""Check unchanged frozen-anchor actions and exported road-model logits."""
import argparse
import ctypes as C
import gzip
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from run_matches import BASE
from rl.sim.native import Simulator, LIB as ORIGINAL
from rl.train.bc import Policy
from rl.roads.rollout import LIB


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--training', type=Path, required=True)
    parser.add_argument('--maps', type=Path, required=True)
    parser.add_argument('--records', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(4)
    checkpoint = torch.load(args.training / 'checkpoint.pt', map_location='cpu', weights_only=False)
    model = Policy()
    model.load_state_dict(checkpoint['actor'])
    maps = [row['map'] for row in json.loads(args.maps.read_text())['training']]
    records = json.loads(gzip.decompress(args.records.read_bytes()))
    for lib, prefix in ((ORIGINAL, 'net'), (LIB, 'roads_net')):
        getattr(lib, prefix + '_new').argtypes = [C.c_char_p]
        getattr(lib, prefix + '_new').restype = C.c_void_p
        getattr(lib, prefix + '_act').argtypes = [C.c_void_p, C.c_void_p, C.c_int, C.c_int]
        getattr(lib, prefix + '_act').restype = C.c_char_p
        getattr(lib, prefix + '_delete').argtypes = [C.c_void_p]
    ORIGINAL.net_evaluate.argtypes = [C.c_void_p, C.POINTER(C.c_float)]
    ORIGINAL.net_evaluate.restype = C.c_float
    LIB.roads_feature_probe.argtypes = [C.c_void_p, C.c_int]
    LIB.roads_feature_probe.restype = C.c_char_p
    weights = args.training / 'weights.txt'
    native = ORIGINAL.net_new(str(weights.resolve()).encode())
    anchor = BASE / 'experiments/rl/2026-11-06-ppo-v1/training/weights.txt'
    original_anchor = ORIGINAL.net_new(str(anchor).encode())
    roads_anchor = LIB.roads_net_new(str(anchor).encode())
    assert native and original_anchor and roads_anchor
    cases = logits = 0
    error = 0.
    try:
        with torch.no_grad():
            for record in records:
                simulator = Simulator(maps[record['map_index']])
                for turn, actions in enumerate(record['actions']):
                    if turn % 5 == 0:
                        for player in (0, 1):
                            a = ORIGINAL.net_act(original_anchor, simulator.ptr, player, 2)
                            b = LIB.roads_net_act(roads_anchor, simulator.ptr, player, 2)
                            assert a == b, (record['map_index'], turn, player)
                            cases += 1
                            rows = json.loads(LIB.roads_feature_probe(simulator.ptr, player))[:80]
                            if rows:
                                x = np.asarray([row['new'] for row in rows], dtype=np.float32)
                                expected = model(torch.from_numpy(x)).numpy()
                                actual = np.asarray([ORIGINAL.net_evaluate(native, row.ctypes.data_as(C.POINTER(C.c_float))) for row in x])
                                error = max(error, float(np.max(np.abs(actual - expected))))
                                logits += len(rows)
                    simulator.step(actions)
                simulator.close()
    finally:
        ORIGINAL.net_delete(native)
        ORIGINAL.net_delete(original_anchor)
        LIB.roads_net_delete(roads_anchor)
    assert error < .001
    report = {'passed': True, 'original_anchor_actions_identical': cases,
              'exported_candidate_logits': logits, 'max_absolute_logit_error': error,
              'weights_sha256': hashlib.sha256(weights.read_bytes()).hexdigest(),
              'policy_header_sha256': hashlib.sha256((BASE / 'code/rl/roads/policy.hpp').read_bytes()).hexdigest(),
              'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

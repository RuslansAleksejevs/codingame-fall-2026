#!/usr/bin/env python3
"""Verify an explicitly packaged full-profile candidate, without touching fallback.

Compare every embedded float32 bit and all emitted commands on recorded states.
This is untimed verification; it never plays new maps or calls the platform.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'code'))
from rl.data.replays import read
from rl.sim.native import Simulator
from rl.league.rollout import LIB
from rl.eval.analyze import clean


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--panel', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--records', type=int, default=20)
    args = ap.parse_args()
    assert 1 <= args.records <= 200
    manifest = json.loads(args.manifest.read_text())
    assert manifest['action_profile'] == 'full' and not manifest['external_files_required']
    weights, source, raw = [ROOT / manifest[k] for k in ('weights_path', 'source_path', 'raw_path')]
    assert sha(weights) == manifest['weights_sha256']
    assert sha(source) == manifest['source_sha256']
    assert sha(raw) == manifest['float32_sha256']
    assert manifest['float32_parameters'] == 24833 and manifest['source_utf16_units'] < 100000
    out = args.out.resolve()
    assert out.is_relative_to(ROOT / 'experiments')
    out.mkdir(parents=True, exist_ok=False)
    commands = []

    def run(command, **kwargs):
        command = [str(x) for x in command]
        commands.append([s.replace(str(ROOT), '${PROJECT_ROOT}') for s in command])
        result = subprocess.run(command, capture_output=True, check=True, timeout=90, **kwargs)
        return result

    common = ['clang++', '-std=c++17', '-O3', '-Wall', '-Wextra', '-Wpedantic']
    run([*common, ROOT / 'code/rl/export/bot.cpp', '-o', out / 'reference'])
    run([*common, source, '-o', out / 'packaged'])
    run([*common, '-DTRYANGLE_PACK_CHECK', source, '-o', out / 'unpack'])
    unpacked = run([out / 'unpack']).stdout
    assert unpacked == raw.read_bytes()
    rows = [json.loads(line) for line in (args.panel / 'matches.jsonl').read_text().splitlines()]
    record_name = lambda r: f'{r["candidate"]}-vs-{r["opponent"]}-seed{r["seed"]}-seat{r["seat"]}.json.gz'
    excluded = [record_name(r) for r in rows if not clean(r) or r['returncode']]
    records = sorted(args.panel / record_name(r) for r in rows if clean(r) and not r['returncode'])
    assert len(records) >= args.records
    chosen = [records[i*(len(records)-1)//max(1, args.records-1)] for i in range(args.records)]
    streams = []
    mismatches = []
    try:
        for path in chosen:
            replay = read(path)
            assert not replay['errors'], 'Do not use a technical-failure replay as contract evidence'
            simulator = Simulator(replay['map'])
            inputs = [[], []]
            try:
                for turn, decision in enumerate(replay['decisions']):
                    for player in (0, 1):
                        inputs[player].append(LIB.league_observation(simulator.ptr, player, int(turn == 0)))
                    simulator.step(decision['actions'])
            finally:
                simulator.close()
            for player in (0, 1):
                stdin = b''.join(inputs[player])
                reference = run([out / 'reference', weights, '2'], input=stdin)
                packaged = run([out / 'packaged'], input=stdin)
                expected = reference.stdout.splitlines()
                actual = packaged.stdout.splitlines()
                assert len(expected) == len(replay['decisions'])
                different = [i for i, (a, b) in enumerate(zip(expected, actual)) if a != b]
                count = len(different)+abs(len(expected)-len(actual))
                item = {'record': str(path.resolve().relative_to(ROOT)), 'player': player,
                        'plans': len(expected), 'mismatches': count,
                        'input_sha256': hashlib.sha256(stdin).hexdigest(),
                        'output_sha256': hashlib.sha256(packaged.stdout).hexdigest()}
                streams.append(item)
                if count:
                    mismatches.append(dict(item, first_differences=[{'turn': i, 'expected': expected[i].decode(),
                                          'actual': actual[i].decode()} for i in different[:3]]))
    finally:
        report = {'as_of': datetime.now(timezone.utc).isoformat(), 'provenance': 'PROJECT_REPORTED',
                  'passed': not mismatches and len(streams) == 2*args.records,
                  'exact_float32_bits': True, 'float32_parameters': len(unpacked)//4,
                  'source_sha256': sha(source), 'weights_sha256': sha(weights), 'manifest_sha256': sha(args.manifest),
                  'source_utf16_units': manifest['source_utf16_units'], 'records': len(chosen),
                  'plans_checked': sum(s['plans'] for s in streams), 'streams': streams, 'mismatches': mismatches,
                  'technical_replays_not_used_for_contracts': excluded,
                  'binary_sha256': {n: sha(out / n) for n in ('reference', 'packaged', 'unpack')},
                  'commands': commands, 'scope': 'Untimed native/packaged command and weight parity only, not strength or platform timing.',
                  'live_submission': False, 'external_spend': 0}
        (out / 'summary.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('streams', 'mismatches', 'commands')}, indent=2))
    assert report['passed'], 'Package parity failed; preserved mismatches'


if __name__ == '__main__':
    main()
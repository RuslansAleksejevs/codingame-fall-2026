#!/usr/bin/env python3
"""Retain the original result; enforce the declared >=90% coverage exactly."""
import json
import math
from common import ROOT, OUT, BASE, BUILD, now, save, sha

panel = OUT / 'screen'
target = OUT / 'screen-strict-decision.json'
assert not target.exists()
analysis = json.loads((panel / 'analysis.json').read_text())
spec = json.loads((panel / 'panel-spec.json').read_text())
manifest = json.loads((panel / 'manifest.json').read_text())
freeze = json.loads((OUT / 'screen-analysis-freeze.json').read_text())
assert all(sha(ROOT / path) == expected for path, expected in freeze['source_sha256'].items())
expected_games = len(spec['pairs']) * len(spec['seeds']) * 2
assert len((panel / 'matches.jsonl').read_text().splitlines()) == expected_games == 264
minimum = math.ceil(.9 * len(spec['seeds']) * 2)
paired = analysis['paired_curriculum_minus']['control']
counts = {opponent: paired[opponent]['clean_pairs'] for opponent in ('lacoz', 'khoufou', 'b2m')}
strict_coverage = all(n >= minimum for n in counts.values())
original = analysis['continuation_gate_passed']
strict = bool(original and strict_coverage)
control = json.loads((OUT / 'pilot-control/run-000000.json').read_text())
treatment = json.loads((OUT / 'pilot-curriculum/run-000000.json').read_text())
assert sha(BUILD / 'libcurriculum.dylib') == control['binary_sha256'] == treatment['binary_sha256']
preserved = {
    str((BASE / 'checkpoint.pt').relative_to(ROOT)): '9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663',
    str((BASE / 'weights.txt').relative_to(ROOT)): 'dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb',
    'submissions/ppo-v2-league3m.cpp': '199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1',
}
assert all(sha(ROOT / path) == expected for path, expected in preserved.items())
result = {'as_of': now(), 'original_gate': original, 'strict_gate': strict,
          'minimum_clean_pairs_per_opponent': minimum, 'actual_clean_pairs': counts,
          'original_and_strict_agree': original == strict, 'scope': 'Frozen development expansion only, not promotion',
          'source_hashes_unchanged': True, 'shared_rollout_binary_sha256': control['binary_sha256'],
          'panel_binary_sha256': manifest['binary_sha256'], 'policy_weights_sha256': manifest['policy_weights_sha256'],
          'analysis_sha256': sha(panel / 'analysis.json'), 'panel_manifest_sha256': sha(panel / 'manifest.json'),
          'panel_matches_sha256': sha(panel / 'matches.jsonl'), 'analysis_freeze_sha256': sha(OUT / 'screen-analysis-freeze.json'),
          'frozen_baseline_preservation': preserved, 'external_spend': 0,
          'freeze_timing_limitation': freeze['status']}
save(target, result)
print(json.dumps(result), flush=True)
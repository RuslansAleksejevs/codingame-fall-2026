"""Compiler-environment recovery only; all learned weights stay unchanged.

Run via one explicitly reviewed full-access shared lease if sandbox compilation
cannot use the host SDK temporary cache. No alternate compiler/cache workaround.
"""
from support import *
from train import package
from stage import freeze_candidates

before = {rel(OUT/'models'/a/'weights.txt'): sha(OUT/'models'/a/'weights.txt') for a in ARMS[:-1]}
directory = OUT/'models/narrow1'
failed = directory/'verify'
assert failed.is_dir() and not any(failed.iterdir()), 'Preserve any unexpected verifier output'
assert not (directory/'verify-attempt1-failed').exists()
failed.rename(directory/'verify-attempt1-failed')
run([PYTHON, '-B', 'code/rl/v3/verify_package.py', '--manifest', rel(directory/'package/package.json'),
    '--panel', rel(V5/'confirm1'), '--out', rel(directory/'verify'), '--records', '20'], 'narrow1-verify-attempt2')
for arm in ('broad1', 'narrow2', 'broad2'):
    package(arm)
for path, digest in before.items(): assert sha(ROOT/path) == digest, path
freeze_candidates()
run([PYTHON, '-B', rel(CODE/'coverage_audit.py')], 'coverage-content-audit')
save(OUT/'export-recovery.json', {'as_of': now(), 'passed': True, 'weights_before_after_exact': before,
    'retrained_models': 0, 'failed_verifier_directory_preserved': rel(directory/'verify-attempt1-failed'),
    'initial_failure': 'First clang reference compile returned1; original nested verifier did not expose compiler stderr.',
    'recovery': 'Same source/compiler/verifier, reviewed host access for SDK temporary-cache availability.',
    'scope': 'Technical export only; no strength games or candidate/seed/hyperparameter changes.'})
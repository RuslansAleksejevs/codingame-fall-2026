#!/usr/bin/env python3
"""Final local evidence inventory and checks; no training, games or Git actions."""
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
from common import ROOT, OUT, now, save, sha


def load(path):
    return json.loads(path.read_text())


def main():
    target = OUT / 'completion.json'
    assert not target.exists()
    audit = load(OUT / 'final-data-audit.json')
    plan = load(OUT / 'recovery-plan.json')
    recovery = load(OUT / 'recovery-diagnostic.json')
    assert audit['passed'] and not audit['continuation_gate_passed']
    assert all(sha(OUT / name) == expected for name, expected in audit['evidence_sha256'].items())
    assert all(sha(ROOT / name) == expected for name, expected in plan['sha256'].items())
    assert recovery['plan_sha256'] == sha(OUT / 'recovery-plan.json')
    assert recovery['java_mismatches'] == 0 and len(recovery['rows']) == 288
    bank = load(OUT / 'bank.json')['records']
    expected = {(r['snapshot_hash'], candidate, opponent) for r in bank
                for candidate in ('curriculum', 'control', 'base') for opponent in ('base', 'older')}
    actual = {(r['snapshot_hash'], r['candidate'], r['opponent']) for r in recovery['rows']}
    assert actual == expected and len(actual) == 288
    diagnostic = {}
    for candidate in ('curriculum', 'control', 'base'):
        rows = [r for r in recovery['rows'] if r['candidate'] == candidate]
        counts = Counter(r['outcome'] for r in rows)
        assert len(rows) == recovery['summary'][candidate]['games'] == 96
        assert counts[1] == recovery['summary'][candidate]['wins']
        assert counts[0] == recovery['summary'][candidate]['draws']
        diagnostic[candidate] = {'games': 96, 'wins': counts[1], 'losses': counts[-1], 'draws': counts[0],
                                 'win_rate': counts[1] / 96,
                                 'categories': {category: dict(Counter(r['outcome'] for r in rows if r['category'] == category))
                                                for category in ('loss', 'win', 'fresh')}}
    assert load(OUT / 'preflight-archive.json')['roundtrip_verified']
    assert load(OUT / 'pilot-evidence-archive.json')['roundtrip_verified']
    campaign = OUT.parent
    own_claim = load(OUT / 'map-contribution.json')
    assert own_claim == load(OUT / 'map-registry-claim.json')
    assert len(own_claim['canonical']) == len(own_claim['legacy']) == 12
    registry = campaign / 'map-registry-base.json'
    assert sha(registry) == '6185ddba8c2eac022e1f2201ae4b669e7c1e7dc962f1bc6636c805609b6c3702'
    exclusion_paths = [registry]
    for lane in ('exploiters', 'search-teacher'):
        for name in ('map-contribution.json', 'map-registry-claim.json'):
            path = campaign / lane / name
            if path.exists():
                exclusion_paths.append(path)
    exclusion_hashes = {}
    for path in exclusion_paths:
        data = load(path)
        for encoding in ('canonical', 'legacy'):
            assert not (set(own_claim[encoding]) & set(data.get(encoding, [])))
        exclusion_hashes[str(path.relative_to(ROOT))] = sha(path)
    tests = []
    commands = [([sys.executable, '-B', 'code/rl/v4/curriculum/test_state.py'], ROOT),
                ([sys.executable, '-B', 'code/rl/v4/curriculum/test_sampling.py'], ROOT),
                ([sys.executable, 'contest.py', 'check'], ROOT.parents[1])]
    for command, cwd in commands:
        run = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, timeout=30)
        output = run.stdout.replace(str(ROOT), '${PROJECT_ROOT}').replace(str(Path.home()), '${HOME}')
        tests.append({'command': ['${PYTHON}', *command[1:]], 'cwd': 'repository' if cwd == ROOT else 'contest-project',
                      'returncode': run.returncode, 'output': output})
        assert run.returncode == 0, tests[-1]
    events = [json.loads(line) for line in (ROOT / '.context/rl4-compute/events.jsonl').read_text().splitlines()]
    own_events = [e for e in events if e['owner'] == 'curriculum']
    assert own_events[-1]['event'] == 'finished' and own_events[-1]['exit_code'] == 0
    heavy_seconds = sum(e['seconds'] for e in own_events if e['event'] == 'finished')
    roots = [ROOT / 'code/rl/v4/curriculum', OUT]
    ignored_raw = {'archive-boundaries.json', 'bank-screen-records.json', 'contracts/rollouts.json'}
    inventory = {}
    for root in roots:
        for path in sorted(root.rglob('*')):
            if not path.is_file() or path == target:
                continue
            rel = path.relative_to(root)
            if 'build' in rel.parts or '__pycache__' in rel.parts:
                continue
            if str(rel) in ignored_raw or path.name.endswith(('.json.gz', '.jsonl', '.log', '-spec.json')):
                continue
            if path.suffix in ('.md', '.json', '.py', '.cpp', '.hpp', '.java', '.txt'):
                text = path.read_text()
                assert ('/' + 'Users' + '/') not in text and ('@' + 'gmail' + '.com') not in text, str(rel)
            inventory[str(path.relative_to(ROOT))] = {'bytes': path.stat().st_size, 'sha256': sha(path)}
    doc = ROOT / 'docs/rl/v4/CURRICULUM.md'
    inventory[str(doc.relative_to(ROOT))] = {'bytes': doc.stat().st_size, 'sha256': sha(doc)}
    result = {'as_of': now(), 'status': 'CLOSED_REJECTED', 'classification': 'PROJECT_REPORTED',
              'continuation_gate_passed': False, 'no_further_training_or_dev_games': True,
              'screen_result_source': 'final-data-audit.json',
              'recovery_diagnostic': diagnostic, 'recovery_java_states': recovery['java_full_states'],
              'recovery_java_mismatches': recovery['java_mismatches'],
              'recovery_wall_seconds': recovery['wall_seconds'],
              'heavy_lease_seconds': heavy_seconds, 'compute_events': own_events,
              'checks': tests, 'inventory': inventory,
              'final_content_audit': {'unique_maps': 12, 'overlap': 0, 'exclusion_files_sha256': exclusion_hashes,
                                      'scope': 'Hash-only reread of latest neighboring claims and frozen prior registry; no held-out map content opened'},
              'inventory_scope': 'Owned source/docs and portable evidence; every raw replay/history/log/spec is in verified archives, with private prefixes normalized only in archived copies and dual hash ledger. Build caches and redundant raw extracts remain local.',
              'test_invocation_erratum': 'A manual system-python invocation of test_sampling.py lacked NumPy; using the prescribed RL virtual environment passed both tests without any code change. This was an environment invocation issue, not a failed algorithm audit.',
              'external_spend': 0,
              'integration': 'Preserve rejected candidate and restoration evidence only. Do not promote either pilot or change the active submission. Coordinator serializes organizational state and handles any Git action.'}
    save(target, result)
    print(json.dumps({k: result[k] for k in ('as_of', 'status', 'recovery_diagnostic', 'recovery_java_states',
                                           'recovery_wall_seconds', 'heavy_lease_seconds')}) , flush=True)
    print(json.dumps({'completion_sha256': sha(target), 'inventory_files': len(inventory),
                      'check_returncodes': [check['returncode'] for check in tests]}), flush=True)


if __name__ == '__main__':
    main()
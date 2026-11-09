#!/usr/bin/env python3
"""Read-only science/portable-archive audit and explicit Git selection; no API/jobs/Git writes."""
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'experiments/rl/2026-11-09-repository-refresh'
sys.path.insert(0, str(ROOT / 'code'))
from split_evidence import verify as verify_parts

ARCHIVES = [
    ('v6', 'experiments/rl/2026-11-08-rl6/compact-d16/evidence.tar.gz',
     'experiments/rl/2026-11-08-rl6/compact-d16/inventory.json',
     '9a01ea0cefad6f688fb4fee72d5183541aa9be85252e2a96b49641e9c76116ff',
     'experiments/rl/2026-11-08-rl6/archive-parts/manifest.json'),
    ('d16', 'experiments/rl/2026-11-09-rl7/d16/publication-2026-11-09/evidence.tar.gz',
     'experiments/rl/2026-11-09-rl7/d16/publication-2026-11-09/inventory.json',
     'eb20a8efe42d4fc1da3de580bd1309ccc90de7eb5ab37ade886d4d896618e5a6', None),
    ('diversity', 'experiments/rl/2026-11-09-rl7/diversity/publication-2026-11-09/attempt2/evidence.tar.gz',
     'experiments/rl/2026-11-09-rl7/diversity/publication-2026-11-09/attempt2/inventory.json',
     '1eb876975fa85572585c7585e46a636c01ea80e43af5a19aa1f74e51a2127691',
     'experiments/rl/2026-11-09-rl7/diversity/publication-2026-11-09/attempt2/archive-parts/manifest.json'),
]
RULES = {
    'codingame_token': rb'(?<!\w)cgp_[A-Za-z0-9._-]{16,}',
    'github_token': rb'(?<!\w)(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})',
    'api_token': rb'(?<!\w)sk-(?:proj-|ant-|svcacct-)?[A-Za-z0-9_-]{20,}',
    'private_key': rb'-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----',
    'bearer_credential': rb'(?i)\bbearer\s+[A-Za-z0-9._~-]{24,}',
    'credential_value': rb'(?i)"(?:access_token|refresh_token|client_secret|api_key|password|authorization|cookie)"\s*:\s*"(?!\$\{|REDACTED|UNKNOWN|NONE|NULL)[^"\r\n]{16,}"',
    'host_path': rb'/(?:Users|home)/[^/\\\s"\x27<>]+',
    'windows_host_path': rb'(?i)[a-z]:[\\/]+Users[\\/]+[^\\/\s"\x27<>]+',
}
RULES = {k: re.compile(v) for k, v in RULES.items()}
MAGIC = (b'\xcf\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\x7fELF', b'\xca\xfe\xba\xbe', b'MZ')
REVIEWED_FALSE_POSITIVES = {
    ('experiments/rl/2026-11-08-leaderboard-recheck/submission-request.json', 'credential_value'):
        ('dc48c9a3b02316828544438babc4c87ceb50b77c09cbef55d872252e822fd981', 'authorization is a plain-language task-consent note, not an HTTP credential'),
    ('experiments/rl/2026-11-08-leaderboard-recheck/test-request.json', 'credential_value'):
        ('bd771ae73e4d7b2c44ee75753c33b1527a362698c91cd2c3045d7970c58b9389', 'authorization is a plain-language technical-test scope note, not a credential'),
    ('experiments/rl/2026-11-08-leaderboard-recheck/verify_documentation.py', 'host_path'):
        ('88138c0d6bcbd1540c47f47cd3e5e19b5358653e62a3fccf88360bb091634bb0', 'generic path-detection regex contains no user path'),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def safe(name):
    p = PurePosixPath(name)
    return bool(name) and not p.is_absolute() and '..' not in p.parts and '\\' not in name


def scan(name, data, depth=0):
    """Never deserialize checkpoints. Inspect compressed container bytes recursively."""
    assert depth <= 5, 'Unexpected nested container depth'
    failures = [[name, k] for k, regex in RULES.items() if regex.search(data)]
    if data.startswith(MAGIC):
        failures.append([name, 'compiled_executable_magic'])
    if name.endswith('.gz') and data[:2] == b'\x1f\x8b':
        decoded = gzip.decompress(data)
        failures += scan(name[:-3], decoded, depth + 1)
    elif data[:4] == b'PK\x03\x04':
        with zipfile.ZipFile(io.BytesIO(data)) as container:
            for member in container.infolist():
                assert safe(member.filename), 'Unsafe nested zip member'
                if not member.is_dir():
                    failures += scan(name + '::' + member.filename, container.read(member), depth + 1)
    elif name.endswith('.tar'):
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:') as container:
            for member in container:
                assert member.isfile() and safe(member.name), 'Unsafe nested tar member'
                failures += scan(name + '::' + member.name, container.extractfile(member).read(), depth + 1)
    return failures


def inventory_rows(path):
    document = json.loads(path.read_text())
    rows = document['files']
    if isinstance(rows, list):
        rows = {r['path']: r for r in rows}
    return {name: {'original': r.get('original_sha256', r.get('source_sha256')),
                   'export': r.get('export_sha256', r.get('archive_sha256'))}
            for name, r in rows.items()}


def save(path, result):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')


def archives(output):
    results, problems = [], []
    for label, filename, inventory, expected_archive, parts in ARCHIVES:
        assert file_sha(ROOT / filename) == expected_archive, label
        rows = inventory_rows(ROOT / inventory)
        expected = {p: r['export'] for p, r in rows.items()}
        expected[inventory] = file_sha(ROOT / inventory)
        seen = set()
        with tarfile.open(ROOT / filename, 'r|gz') as archive:
            for member in archive:
                assert member.isfile() and safe(member.name) and member.name not in seen
                assert member.name in expected, (label, member.name)
                data = archive.extractfile(member).read()
                assert len(data) == member.size and sha(data) == expected[member.name]
                problems.extend(scan(member.name, data))
                seen.add(member.name)
        assert seen == set(expected)
        changed = [p for p, r in rows.items() if not (ROOT / p).is_file() or file_sha(ROOT / p) != r['original']]
        if label != 'v6':
            assert not changed, (label, 'Frozen original changed', changed)
        if parts:
            assert verify_parts(ROOT / parts)['original_sha256'] == expected_archive
        results.append({'label': label, 'archive': filename, 'sha256': expected_archive,
                        'bytes': (ROOT / filename).stat().st_size, 'members': len(seen),
                        'parts_manifest': parts, 'current_original_hash_matches': len(rows) - len(changed),
                        'later_original_updates': changed})
    result = {'as_of': datetime.now(timezone.utc).isoformat(), 'passed': not problems,
              'archives': results, 'privacy_findings_paths_and_rules_only': problems,
              'method': 'Independent full tar member bytes/SHA/safe paths, source rehash, recursive gzip/zip/tar token/path/magic scan; no checkpoint unpickling, no experiments.',
              'limit': 'Pattern screening cannot prove absence of every possible secret.'}
    save(output, result)
    print(json.dumps(result, indent=2))
    assert result['passed']


SCOPES = ('code/rl/v6', 'code/rl/v7', 'docs/rl/v6', 'docs/rl/v7',
          'experiments/rl/2026-11-08-rl6', 'experiments/rl/2026-11-09-rl7',
          'experiments/rl/2026-11-08-leaderboard-recheck', 'experiments/rl/2026-11-09-d16-live',
          'experiments/rl/2026-11-09-repository-refresh')
EDITED = ('.gitignore', 'README.md', 'docs/STATUS.md', 'docs/ARCHIVE.md', 'docs/rl/README.md',
          'docs/rl/v7/PLAN.md', 'docs/EXPERIMENT_TIMELINE.md')


def selection(output):
    archive_coverage = set()
    for _, _, inventory, _, _ in ARCHIVES:
        archive_coverage.update(inventory_rows(ROOT / inventory))
    files = {ROOT / p for p in EDITED}
    for scope in SCOPES:
        files.update(p for p in (ROOT / scope).rglob('*') if p.is_file() or p.is_symlink())
    selected, excluded, issues, reviewed = {}, [], [], []
    for path in sorted(files):
        name = path.relative_to(ROOT).as_posix()
        reason = None
        if path.is_symlink():
            reason = 'symlink'
        elif path.parent == OUT and path.suffix == '.paths':
            reason = 'local_generated_git_pathspec'
        elif any(p in path.parts for p in ('__pycache__', 'build', 'contract-build', '.context', '.venv')):
            reason = 'build_cache_or_scratch'
        elif path.name == '.DS_Store' or path.name.startswith('.env'):
            reason = 'host_environment'
        elif path.suffix in ('.dylib', '.so', '.o', '.a', '.pyc', '.class'):
            reason = 'compiled_artifact'
        elif any(p.startswith('verify') for p in path.parts) and path.name in ('packaged', 'reference', 'unpack'):
            reason = 'compiled_artifact'
        elif name in {ARCHIVES[0][1], ARCHIVES[2][1]}:
            reason = 'exact_archive_stored_as_verified_parts'
        elif name in archive_coverage and (name.endswith(('-raw.json', '-spec.json', '.json.gz', '.jsonl', '.log', '.npz', '.npy', '.bin')) or path.name == 'matches.json'):
            reason = 'scientific_record_preserved_in_verified_archive'
        if reason:
            excluded.append({'path': name, 'reason': reason, 'archive_covered': name in archive_coverage})
            continue
        data = path.read_bytes()
        if data.startswith(MAGIC):
            excluded.append({'path': name, 'reason': 'compiled_executable_magic', 'archive_covered': False})
            continue
        assert len(data) < 100 * 1024 * 1024, (name, 'GitHub size limit')
        # Archive bytes and parts were independently recursively checked above.
        if not (name.endswith('.tar.gz') or '.tar.gz.part-' in name):
            for finding in scan(name, data):
                exception = REVIEWED_FALSE_POSITIVES.get(tuple(finding))
                if exception and sha(data) == exception[0]:
                    reviewed.append({'path': name, 'rule': finding[1], 'exact_file_sha256': exception[0], 'reason': exception[1]})
                else:
                    issues.append(finding)
        if path.suffix == '.py':
            ast.parse(data.decode('utf8'), filename=name)
        selected[name] = sha(data)
    result = {'as_of': datetime.now(timezone.utc).isoformat(), 'passed': not issues,
              'selected': selected, 'selected_count': len(selected),
              'selected_bytes': sum((ROOT / p).stat().st_size for p in selected),
              'excluded': excluded, 'exclusion_counts': dict(Counter(r['reason'] for r in excluded)),
              'privacy_findings_paths_and_rules_only': issues,
              'reviewed_exact_file_false_positives': reviewed,
              'method': 'Explicit scoped selection, SHA256/AST/privacy checks; no Git mutation and no original deletion.'}
    save(output, result)
    print(json.dumps({k: v for k, v in result.items() if k not in ('selected', 'excluded')}, indent=2))
    assert result['passed']
    # Generated NUL-delimited exact pathspec, reviewed separately before Git mutation.
    with output.with_suffix('.paths').open('xb') as stream:
        stream.write(b'\0'.join(p.encode() for p in selected) + b'\0')


def tests(output):
    suites = ['code/test_split_evidence.py', 'code/rl/v6/coordinator/test_paired.py',
              'code/rl/v7/d16/test_analyze.py', 'code/rl/v7/diversity/test_analyze.py',
              'code/rl/v7/test_publication_snapshot.py']
    python = ROOT / 'code/arena/.venv-rl/bin/python'
    results = []
    for suite in suites:
        result = subprocess.run([str(python), '-B', suite], cwd=ROOT, text=True,
                                capture_output=True, timeout=90)
        text = (result.stdout + result.stderr).replace(str(ROOT), '${PROJECT_ROOT}').replace(str(Path.home()), '${USER_HOME}')
        assert not scan(suite + '::test-output', text.encode())
        results.append({'command': ['code/arena/.venv-rl/bin/python', '-B', suite],
                        'source_sha256': file_sha(ROOT / suite), 'returncode': result.returncode,
                        'output': text})
    report = {'as_of': datetime.now(timezone.utc).isoformat(),
              'passed': all(r['returncode'] == 0 for r in results), 'tests': results,
              'scope': 'Synthetic analyzer/security/archive tests only, no scientific games/training/platform requests.'}
    save(output, report)
    print(json.dumps(report, indent=2))
    assert report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('archives', 'selection', 'tests'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert args.out.resolve().is_relative_to(OUT) and not args.out.exists()
    {'archives': archives, 'selection': selection, 'tests': tests}[args.action](args.out)
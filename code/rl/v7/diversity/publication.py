#!/usr/bin/env python3
"""Publication-only export. Never modify original pilot evidence or run games."""
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tarfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[4]
CODE = ROOT / 'code/rl/v7/diversity'
OUT = ROOT / 'experiments/rl/2026-11-09-rl7/diversity'
PUB_ROOT = OUT / 'publication-2026-11-09'
PUB = PUB_ROOT / 'attempt2'
DOC = ROOT / 'docs/rl/v7/DIVERSITY.md'
sys.path.insert(0, str(ROOT / 'code'))
from archive_run import normalized
from split_evidence import PART_BYTES, create as split_create, verify as split_verify

TOKEN_RULES = {
    'codingame_token': re.compile(rb'cgp_[A-Za-z0-9_-]{16,}'),
    'github_token': re.compile(rb'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}'),
    'api_secret': re.compile(rb'sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}'),
    'private_key': re.compile(b'-----' + b'BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY' + b'-----'),
}
PERSONAL_PREFIXES = (b'/' + b'Users' + b'/', b'/' + b'home' + b'/')
TEXT_SUFFIXES = {'.py', '.hpp', '.h', '.cpp', '.md', '.txt', '.json', '.jsonl', '.log'}
BINARY_SUFFIXES = {'.npz', '.npy', '.pt', '.bin'}
STAGES = ('train1', 'train2', 'labeldev', 'gamedev1', 'gamedev2', 'gamedev3', 'gamedev4')
ARMS = ('narrow1', 'broad1', 'narrow2', 'broad2')


def rel(path):
    return path.relative_to(ROOT).as_posix()


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def file_digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    assert path.parent == PUB
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=True, indent=2)
        stream.write('\n')


def safe_name(name):
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and '..' not in path.parts and '\\' not in name


def selection():
    paths = {p for p in OUT.rglob('*') if not p.is_relative_to(PUB_ROOT) and (p.is_file() or p.is_symlink())}
    paths.update(p for p in CODE.rglob('*') if p.is_file() or p.is_symlink())
    paths.add(DOC)
    # Append-only retry: retain first preflight failure and its exact helper.
    paths.update(p for p in PUB_ROOT.iterdir() if p.is_file())
    selected, excluded = [], []
    for path in sorted(paths):
        name = rel(path)
        assert safe_name(name)
        parts = path.relative_to(OUT).parts if path.is_relative_to(OUT) else path.relative_to(ROOT).parts
        lower = tuple(p.lower() for p in parts)
        reason = None
        if path.is_symlink():
            reason = 'symlink excluded; no link targets followed'
        elif any(p in lower for p in ('build', '__pycache__', '.cache', 'scratch', '.context')):
            reason = 'compiled build/cache/scratch; scientific per-game specs remain in stage folders'
        elif any(p.startswith('.venv') or p in ('venv', 'node_modules') for p in lower):
            reason = 'environment/dependency installation excluded'
        elif path.suffix.lower() in ('.dylib', '.so', '.o', '.a', '.pyc', '.class'):
            reason = 'compiled binary excluded'
        elif any(p.startswith('verify') for p in lower) and path.name in ('packaged', 'reference', 'unpack'):
            reason = 'compiled package-verification executable excluded; summary retained'
        elif any(re.search(r'(?:^|[-_.])(permission|credential|oauth|secret|chat)(?:[-_.]|$)', p) for p in lower):
            reason = 'permission/credential/private-chat transport file excluded'
        if reason:
            excluded.append({'path': name, 'reason': reason,
                'original_sha256': None if path.is_symlink() else file_digest(path),
                'source_bytes': None if path.is_symlink() else path.stat().st_size})
        else:
            assert path.is_file() and stat.S_ISREG(path.stat().st_mode), name
            selected.append(path)
    return selected, excluded


def scan_bytes(value, location):
    hits = [name for name, rule in TOKEN_RULES.items() if rule.search(value)]
    if any(prefix in value for prefix in PERSONAL_PREFIXES):
        hits.append('personal_user_path')
    if str(ROOT).encode() in value or str(Path.home()).encode() in value:
        hits.append('unresolved_host_path')
    if hits:
        # Never include matched values in a report or exception.
        raise ValueError('Export scan failed: ' + location + ' categories=' + ','.join(hits))


def scan_container(value, name, depth=0):
    assert depth <= 4, name
    scan_bytes(value, name)
    if value[:2] == b'\x1f\x8b':
        scan_container(gzip.decompress(value), name + '::gzip', depth+1)
    elif zipfile.is_zipfile(io.BytesIO(value)):
        with zipfile.ZipFile(io.BytesIO(value)) as archive:
            seen = set()
            for member in archive.infolist():
                assert safe_name(member.filename) and member.filename not in seen and not member.is_dir(), name
                assert not stat.S_ISLNK(member.external_attr >> 16), name
                seen.add(member.filename)
                scan_bytes(member.filename.encode(), name + '::zip-name')
                scan_container(archive.read(member), name + '::' + member.filename, depth+1)
    elif name.endswith('.tar'):
        with tarfile.open(fileobj=io.BytesIO(value), mode='r:') as archive:
            seen = set()
            for member in archive:
                assert member.isfile() and safe_name(member.name) and member.name not in seen, name
                seen.add(member.name)
                scan_bytes(member.name.encode(), name + '::tar-name')
                scan_container(archive.extractfile(member).read(), name + '::' + member.name, depth+1)


def portable(path):
    original = path.read_bytes()
    change = None
    if path.suffix == '.gz':
        content = gzip.decompress(original)
        cleaned = normalized(content)
        exported = original if cleaned == content else gzip.compress(cleaned, mtime=0)
        if exported != original:
            change = 'ROOT/home path normalization in decompressed UTF8 only; gzip rebuilt with mtime=0'
    elif path.suffix in TEXT_SUFFIXES or path.name == '.gitignore':
        exported = normalized(original)
        if exported != original:
            change = 'ROOT/home path normalization in UTF8 only'
    else:
        assert path.suffix in BINARY_SUFFIXES or path.name in ('pre-a1-sources.tar', 'attempt1-source.tar'), rel(path)
        exported = original
    scan_container(exported, rel(path))
    return original, exported, change


def frozen_guard():
    closeout = json.loads((OUT/'closeout-audit.json').read_text())
    expected = dict(closeout['protected'])
    for name, record in closeout['freezes'].items():
        assert file_digest(OUT/name) == record['sha256'], name
        expected.update(json.loads((OUT/name).read_text())['identities'])
    for path, sha in expected.items():
        assert file_digest(ROOT/path) == sha, path
    return {'identities': len(expected), 'passed': True,
        'closeout_sha256': file_digest(OUT/'closeout-audit.json')}


def main():
    started = time.monotonic()
    assert not PUB.exists(), 'Publication destination already exists; never overwrite'
    lease = json.loads((ROOT/'.context/rl4-compute/slot.lock').read_text())
    assert lease['event'] == 'started' and lease['owner'] == 'diversity'
    assert lease['command'][-1].endswith('code/rl/v7/diversity/publication.py')
    frozen_before = frozen_guard()
    paths, exclusions = selection()
    PUB.mkdir(exist_ok=False)
    save(PUB/'START.json', {'as_of': now(), 'classification': 'PROJECT_REPORTED',
        'purpose': 'New authorized publication-only export; no game/training/API/Git actions',
        'lease_id': lease['lease_id'], 'source_sha256': file_digest(Path(__file__)),
        'frozen_before': frozen_before})
    entries, normalizations = {}, []
    for path in paths:
        original, exported, change = portable(path)
        entries[rel(path)] = {'original_sha256': digest(original), 'export_sha256': digest(exported),
            'original_bytes': len(original), 'export_bytes': len(exported), 'normalization': change}
        if change:
            normalizations.append(rel(path))
    counts = {
        'raw_game_records': sum(p.name.endswith('-raw.json') and p.parent.name in STAGES for p in paths),
        'portable_game_records': sum(p.name.endswith('.json.gz') and p.parent.name in STAGES for p in paths),
        'teacher_streams': sum(p.parent.name == 'teacher-streams' and p.suffix == '.json' for p in paths),
        'collection_teacher_streams': sum(p.parent.name == 'teacher-streams' and p.suffix == '.json' and not p.name.startswith('contract-') for p in paths),
        'old_contract_teacher_streams': sum(p.parent.name == 'teacher-streams' and p.name.startswith('contract-') and p.suffix == '.json' for p in paths),
        'label_npz': sum(p.parent == OUT and p.name.startswith('labels-') and p.suffix == '.npz' for p in paths),
        'bank_npz': sum(p.parent == OUT and p.name.startswith('bank-') and p.suffix == '.npz' for p in paths),
        'student_checkpoints': sum(p.name == 'checkpoint.pt' and p.parent.name in ARMS for p in paths),
        'student_weights': sum(p.name == 'weights.txt' and p.parent.name in ARMS for p in paths),
        'student_exposures': sum(p.name == 'exposures.npy' and p.parent.name in ARMS for p in paths),
        'student_sources': sum(p.name == 'bot.cpp' and p.parent.parent.name in ARMS for p in paths),
    }
    assert counts == {'raw_game_records': 960, 'portable_game_records': 960, 'teacher_streams': 165,
        'collection_teacher_streams': 158, 'old_contract_teacher_streams': 7,
        'label_npz': 3, 'bank_npz': 3, 'student_checkpoints': 4, 'student_weights': 4,
        'student_exposures': 4, 'student_sources': 4}, counts
    for required in ('pre-a1-sources.tar', 'AMENDMENT_A1.md', 'BUILD_RECOVERY.md',
                     'execution/collection1-end.json', 'execution/optimize1-end.json', 'narrow1-verify.log'):
        assert rel(OUT/required) in entries, required
    inventory = {'as_of': now(), 'classification': 'PROJECT_REPORTED', 'files': entries,
        'payload_files': len(entries), 'counts': counts, 'exclusions': exclusions,
        'publication_retry_note': 'Attempt1 stopped before inventory/archive because 158 collection streams plus 7 old contract streams were counted together. Both categories and all first-attempt files are now retained; no scientific data or prior files changed.',
        'excluded_by_reason': dict(Counter(e['reason'] for e in exclusions)),
        'normalizations': normalizations, 'normalization_policy': 'Only ROOT/home path strings in exported UTF8/gzip JSON copies; original scientific values and originals retained.',
        'secret_scan': {'passed': True, 'rules': list(TOKEN_RULES) + ['personal_user_path', 'unresolved_host_path'],
            'compressed_containers_scanned_recursively': True, 'matched_values_logged': False},
        'restore_note': 'Archive names are repository-relative. Restore ONLY into a new directory/clone without overwriting local evidence. Frozen manifests refer to original bytes; this ledger maps normalized export bytes.',
        'excluded_code_or_measurements': False,
        'inventory_self_exclusion': 'Inventory is an extra archive member; its SHA and the archive SHA are in PUBLICATION.json.'}
    save(PUB/'inventory.json', inventory)
    archive_path = PUB/'evidence.tar.gz'
    expected = {name: record['export_sha256'] for name, record in entries.items()}
    expected[rel(PUB/'inventory.json')] = file_digest(PUB/'inventory.json')
    scan_container((PUB/'inventory.json').read_bytes(), rel(PUB/'inventory.json'))
    with archive_path.open('xb') as output:
        with gzip.GzipFile(fileobj=output, mode='wb', filename='', mtime=0, compresslevel=3) as compressed:
            with tarfile.open(fileobj=compressed, mode='w|', format=tarfile.PAX_FORMAT) as archive:
                for path in [*paths, PUB/'inventory.json']:
                    if path == PUB/'inventory.json':
                        value = path.read_bytes()
                    else:
                        original, value, _ = portable(path)
                        assert digest(original) == entries[rel(path)]['original_sha256'], rel(path)
                    assert digest(value) == expected[rel(path)], rel(path)
                    info = tarfile.TarInfo(rel(path))
                    info.size, info.mode, info.mtime = len(value), 0o644, 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ''
                    archive.addfile(info, io.BytesIO(value))
    seen = set()
    with tarfile.open(archive_path, 'r|gz') as archive:
        for member in archive:
            assert member.isfile() and safe_name(member.name) and member.name in expected and member.name not in seen
            value = archive.extractfile(member).read()
            assert digest(value) == expected[member.name], member.name
            scan_container(value, member.name)
            seen.add(member.name)
    assert seen == set(expected)
    for path in paths:
        assert file_digest(path) == entries[rel(path)]['original_sha256'], rel(path)
    for record in exclusions:
        if record['original_sha256'] is not None:
            assert file_digest(ROOT/record['path']) == record['original_sha256'], record['path']
    current_paths, current_exclusions = selection()
    assert current_paths == paths and current_exclusions == exclusions
    assert frozen_guard() == frozen_before
    parts = None
    if archive_path.stat().st_size > PART_BYTES:
        split_create(archive_path, PUB/'archive-parts')
        parts = split_verify(PUB/'archive-parts/manifest.json')
        assert parts['original_sha256'] == file_digest(archive_path)
    result = {'as_of': now(), 'classification': 'PROJECT_REPORTED', 'passed': True,
        'archive_path': rel(archive_path), 'archive_sha256': file_digest(archive_path),
        'archive_bytes': archive_path.stat().st_size, 'archive_members': len(seen),
        'inventory_path': rel(PUB/'inventory.json'), 'inventory_sha256': file_digest(PUB/'inventory.json'),
        'payload_files': len(entries), 'counts': counts, 'normalizations': len(normalizations),
        'exclusions': len(exclusions), 'full_stream_sha_verified': True, 'safe_regular_files_only': True,
        'secret_scan_passed': True, 'originals_rehashed_unchanged': True, 'frozen_after': frozen_before,
        'parts_manifest': rel(PUB/'archive-parts/manifest.json') if parts else None,
        'parts': len(parts['parts']) if parts else 0, 'seconds': time.monotonic()-started,
        'source_sha256': file_digest(Path(__file__)), 'lease_id': lease['lease_id'],
        'new_experiments': 0, 'git_or_platform_actions': 0}
    save(PUB/'PUBLICATION.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        if PUB.is_dir() and not (PUB/'FAILED.json').exists():
            save(PUB/'FAILED.json', {'as_of': now(), 'passed': False,
                'error': normalized(str(error).encode()).decode(), 'partial_outputs_preserved': True})
        raise
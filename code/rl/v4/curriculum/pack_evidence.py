#!/usr/bin/env python3
"""Archive every ignored raw result; normalize private prefixes in copies only."""
import gzip
import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import time
from common import ROOT, OUT, now, save, sha

archive = OUT / 'pilot-evidence.tar.gz'
assert not archive.exists()
names = [str(path.relative_to(OUT)) for path in sorted(OUT.rglob('*'))
         if path.is_file() and 'build' not in path.relative_to(OUT).parts
         and '__pycache__' not in path.relative_to(OUT).parts
         and path.name.endswith(('.json.gz', '.jsonl', '.log', '-spec.json'))]
assert sum(name.endswith('.json.gz') for name in names) == 264
hashes = {name: sha(OUT / name) for name in names}
prefixes = [(str(ROOT), '${PROJECT_ROOT}'), (str(Path.home()), '${HOME}')]
temporary = tempfile.gettempdir()
if temporary.startswith(('/var/folders/', '/private/var/folders/')):
    prefixes.append((temporary, '${TMPDIR}'))
ledger = {}
started = time.monotonic()
with archive.open('xb') as raw:
    with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0, compresslevel=6) as compressed:
        with tarfile.open(mode='w|', fileobj=compressed) as output:
            for name in names:
                path = OUT / name
                info = output.gettarinfo(str(path), arcname=name)
                info.uid = info.gid = 0
                info.uname = info.gname = ''
                info.mtime = 0
                original = path.read_bytes()
                unpacked = gzip.decompress(original) if name.endswith('.json.gz') else original
                text = unpacked.decode('utf-8')
                normalized = text
                for prefix, placeholder in prefixes:
                    normalized = normalized.replace(prefix, placeholder)
                assert ('/' + 'Users' + '/') not in normalized, name
                changed = normalized != text
                data = original
                if changed:
                    data = normalized.encode('utf-8')
                    if name.endswith('.json.gz'):
                        data = gzip.compress(data, mtime=0)
                info.size = len(data)
                ledger[name] = {'original_sha256': hashes[name],
                                'archived_sha256': hashlib.sha256(data).hexdigest(),
                                'original_bytes': len(original), 'archived_bytes': len(data),
                                'private_prefixes_normalized_in_copy': changed}
                output.addfile(info, io.BytesIO(data))
verified = {}
with tarfile.open(archive, 'r:gz') as source:
    for member in source:
        digest = hashlib.sha256()
        with source.extractfile(member) as data:
            while chunk := data.read(1024 * 1024):
                digest.update(chunk)
        verified[member.name] = digest.hexdigest()
assert verified == {name: row['archived_sha256'] for name, row in ledger.items()}
assert all(sha(OUT / name) == expected for name, expected in hashes.items())
result = {'as_of': now(), 'archive': archive.name, 'archive_sha256': sha(archive),
          'members': ledger, 'roundtrip_verified': True, 'raw_files_preserved': True,
          'member_count': len(ledger),
          'normalized_copies': sum(row['private_prefixes_normalized_in_copy'] for row in ledger.values()),
          'compressed_bytes': archive.stat().st_size,
          'raw_bytes': sum((OUT / name).stat().st_size for name in names),
          'seconds': time.monotonic() - started,
          'scope': 'All ignored raw .json.gz/.jsonl/.log/-spec.json under this lane, including contracts. Build/cache excluded. Three huge raw preflight JSON files remain in their separately verified preflight archive.',
          'normalization': 'Only archived copies replace current repository root, home and private macOS temporary prefix with PROJECT_ROOT/HOME/TMPDIR placeholders. Original files are byte-for-byte unchanged; original and stored SHA256 are retained for every member.',
          'external_spend': 0}
save(OUT / 'pilot-evidence-archive.json', result)
print({k: v for k, v in result.items() if k != 'members'}, flush=True)
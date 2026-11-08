#!/usr/bin/env python3
"""Lossless small archive of large raw preflight evidence; no source is deleted."""
import gzip
import hashlib
import json
import tarfile
import time
from common import OUT, now, save, sha

archive = OUT / 'preflight-evidence.tar.gz'
assert not archive.exists()
names = ['archive-boundaries.json', 'bank-screen-records.json', 'contracts/rollouts.json']
hashes = {name: sha(OUT / name) for name in names}
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
                with path.open('rb') as source:
                    output.addfile(info, source)
verified = {}
with tarfile.open(archive, 'r:gz') as source:
    for member in source:
        digest = hashlib.sha256()
        with source.extractfile(member) as data:
            while chunk := data.read(1024 * 1024):
                digest.update(chunk)
        verified[member.name] = digest.hexdigest()
assert verified == hashes
report = {'as_of': now(), 'archive': archive.name, 'archive_sha256': sha(archive), 'members_sha256': hashes,
          'roundtrip_verified': True, 'raw_files_preserved': True, 'compressed_bytes': archive.stat().st_size,
          'raw_bytes': sum((OUT / name).stat().st_size for name in names), 'seconds': time.monotonic() - started}
save(OUT / 'preflight-archive.json', report)
print(json.dumps(report), flush=True)
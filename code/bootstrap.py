#!/usr/bin/env python3
"""Restore the pinned referee source bundled with this repository."""
from pathlib import Path
import tarfile,hashlib,json
BASE=Path(__file__).resolve().parent.parent
archive=BASE/'sources/referee-source.tar.gz'
checks=json.loads((BASE/'CHECKSUMS.json').read_text())
assert hashlib.sha256(archive.read_bytes()).hexdigest()==checks[str(archive.relative_to(BASE))]
target=BASE/'code/vendor';target.mkdir(exist_ok=True)
with tarfile.open(archive) as tar:
    for member in tar.getmembers():
        out=target/member.name
        if out.exists() and member.isfile():
            assert out.read_bytes()==tar.extractfile(member).read(), f'Different existing source: {out}'
    tar.extractall(target,filter='data')
print('Pinned referee source restored.')

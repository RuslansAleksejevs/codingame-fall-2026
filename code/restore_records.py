#!/usr/bin/env python3
"""Restore raw records without replacing changed files."""
from pathlib import Path
import hashlib,json,tarfile
BASE=Path(__file__).resolve().parent.parent
checks=json.loads((BASE/'CHECKSUMS.json').read_text());count=0
for archive in sorted((BASE/'experiments').rglob('records.tar.gz')):
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==checks[str(archive.relative_to(BASE))]
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            assert Path(member.name).name==member.name and member.isfile()
            out=archive.parent/member.name;data=tar.extractfile(member).read()
            if out.exists():assert out.read_bytes()==data,f'Different existing record: {out}'
            else:out.write_bytes(data)
            count+=1
print(f'Restored {count} record files.')

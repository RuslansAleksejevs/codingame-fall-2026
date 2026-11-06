#!/usr/bin/env python3
"""Package a completed run, normalizing personal paths without changing measurements."""
import argparse
import gzip
import io
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]

def normalized(raw):
    text=raw.decode('utf-8')
    # Replace the most specific path first, including JSON-escaped Unicode forms.
    for old,new in [(str(ROOT),'${PROJECT_ROOT}'),(str(Path.home()),'${HOME}')]:
        text=text.replace(old,new).replace(json.dumps(old)[1:-1],new)
    return text.encode('utf-8')

def package(folder):
    assert folder.is_relative_to(ROOT/'experiments'), 'Expected an experiment directory'
    groups={}
    for path in sorted(folder.rglob('*')):
        if not path.is_file() or any(x in path.parts for x in ['build','__pycache__']):continue
        if path.name.endswith('.tar.gz'):continue
        raw=(path.suffix in ['.gz','.log','.jsonl'] or path.name.endswith('-spec.json')
             or path.name=='matches.json')
        if raw:
            data=path.read_bytes()
            if path.suffix=='.gz':
                original=gzip.decompress(data);cleaned=normalized(original)
                if cleaned!=original:data=gzip.compress(cleaned,mtime=0)
            else:data=normalized(data)
            groups.setdefault(path.parent,[]).append((path.name,data))
            # Keep loose copies identical to the archive so restoration is idempotent.
            if data!=path.read_bytes():path.write_bytes(data)
        elif path.suffix in ['.json','.md']:
            data=normalized(path.read_bytes())
            if data!=path.read_bytes():path.write_bytes(data)
    for directory,items in groups.items():
        path=directory/'records.tar.gz'
        with path.open('wb') as out, gzip.GzipFile(fileobj=out,mode='wb',filename='',mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode='w') as archive:
                for name,data in items:
                    info=tarfile.TarInfo(name);info.size=len(data);info.mtime=0;info.mode=0o644
                    archive.addfile(info,io.BytesIO(data))
        print(path.relative_to(ROOT),len(items),'records')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('folder',type=Path,help='Completed experiment directory')
    args=parser.parse_args()
    package(args.folder.resolve())

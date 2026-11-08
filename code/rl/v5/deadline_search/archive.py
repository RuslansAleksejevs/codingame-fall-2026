"""Lossless portable archive with roundtrip SHA verification; originals stay intact."""
import gzip
import io
import re
import tarfile
import zipfile
from common import *


def candidates():
    paths=[]
    for root in (CODE,OUT):
        for p in sorted(root.rglob('*')):
            if not p.is_file() or 'build' in p.relative_to(root).parts or '__pycache__' in p.parts:continue
            if p.name in ('evidence.tar.gz','evidence-manifest.json','COMPLETION.json','inventory.json','STATUS.json','HISTORY.md'):continue
            if p.suffix in ('.dylib','.so','.pyc','.class'):continue
            paths.append(p)
    paths.append(ROOT/'docs/rl/v5/DEADLINE_SEARCH.md')
    return sorted(set(paths))


def scan(path,data):
    if str(Path.home()).encode() in data or str(ROOT).encode() in data:raise RuntimeError('Personal host path in '+rel(path))
    if data[:4] in (b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\x7fELF',b'\xca\xfe\xba\xbe'):
        raise RuntimeError('Executable binary in evidence: '+rel(path))
    if re.search(rb'(?i)(?:bearer\s+[a-z0-9._~-]{24,}|sk-[a-z0-9_-]{32,})',data):
        raise RuntimeError('Potential credential in evidence: '+rel(path))


def main():
    guard();target=OUT/'evidence.tar.gz';assert not target.exists();start=time.monotonic();entries=[]
    with target.open('xb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as packed:
            with tarfile.open(fileobj=packed,mode='w|',format=tarfile.PAX_FORMAT) as archive:
                for path in candidates():
                    data=path.read_bytes();scan(path,data)
                    if path.suffix=='.gz':scan(path,gzip.decompress(data))
                    if path.suffix in ('.pt','.npz'):
                        with zipfile.ZipFile(path) as scientific:
                            for member in scientific.namelist():scan(path,scientific.read(member))
                    name=rel(path);info=tarfile.TarInfo(name);info.size=len(data);info.mtime=0;info.mode=0o644
                    info.uid=info.gid=0;info.uname=info.gname=''
                    archive.addfile(info,io.BytesIO(data))
                    entries.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    expected={r['path']:r['sha256'] for r in entries}
    with tarfile.open(target,'r:gz') as archive:
        found={m.name:hashlib.sha256(archive.extractfile(m).read()).hexdigest() for m in archive}
    assert found==expected
    for p,h in expected.items():assert sha(ROOT/p)==h,'Original modified while archiving'
    save(OUT/'evidence-manifest.json',{'as_of':now(),'archive':rel(target),'archive_sha256':sha(target),
        'members':len(entries),'compressed_bytes':target.stat().st_size,'roundtrip_verified':True,
        'originals_unchanged':True,'normalizations':0,'entries':entries,'seconds':time.monotonic()-start,
        'excluded':'Compiled build/cache, scratch, mutable STATUS/HISTORY, recursive archive/inventory/completion.',
        'security_scan':'Current personal home/project prefixes, executable magic, common credential forms; gzip and scientific PT/NPZ contents also scanned. Scientific float/checkpoint data retained, compiled executables excluded.',
        'protected':guard(),'budget':budget()})
    print(json.dumps({'archive_sha256':sha(target),'members':len(entries),'seconds':time.monotonic()-start}),flush=True)


if __name__=='__main__':main()
"""Portable evidence snapshot; preserve originals and exclude compiled artifacts."""
import gzip
import io
import tarfile
from common import *

MUTABLE={'STATUS.json','HISTORY.md','COMPLETION.json','closing-checks.json','resource-ledger-final.json',
         'inventory.json','archive.json','archive-run.log','archive-run-command.json','evidence.tar.gz'}

def portable(path):
    raw=path.read_bytes();value=raw;normalization=None
    if path.suffix=='.gz':
        decoded=gzip.decompress(raw)
        try:text=decoded.decode('utf-8')
        except UnicodeDecodeError:return raw,None
        normalized=clean(text)
        if normalized!=text:value=gzip.compress(normalized.encode(),mtime=0);normalization='Host path normalization in decompressed UTF8; original retained locally'
    elif path.suffix not in ('.bin',):
        text=raw.decode('utf-8');normalized=clean(text)
        if normalized!=text:value=normalized.encode();normalization='Host path normalization in UTF8; original retained locally'
    return value,normalization

def main():
    guard();started=time.monotonic()
    paths=list(CODE.glob('*.py'))+list(CODE.glob('*.hpp'))+list((ROOT/'docs/rl/v6').glob('*.md'))
    # Independent audit modules are read-only snapshots, not candidate code changes.
    paths+=list((ROOT/'code/rl/v6/coordinator').glob('*.py'))
    for path in OUT.rglob('*'):
        if not path.is_file():continue
        relative=path.relative_to(OUT)
        if 'build' in relative.parts or '__pycache__' in relative.parts:continue
        if len(relative.parts)==1 and path.name in MUTABLE:continue
        if path.suffix in ('.dylib','.so','.o','.pyc'):continue
        paths.append(path)
    paths=sorted(set(paths));entries={};normalized=[]
    for path in paths:
        value,change=portable(path)
        # No personal host path is included in the portable snapshot.
        inspected=gzip.decompress(value) if path.suffix=='.gz' else value
        assert str(ROOT).encode() not in inspected and str(Path.home()).encode() not in inspected,rel(path)
        entries[rel(path)]={'source_sha256':sha(path),'archive_sha256':hashlib.sha256(value).hexdigest(),
            'source_bytes':path.stat().st_size,'archive_bytes':len(value),'normalization':change}
        if change:normalized.append(rel(path))
    inventory={'as_of':now(),'classification':'PROJECT_REPORTED','files':entries,'payload_files':len(entries),
        'scope':'Read-only source/evidence snapshot. Compiled builds/environments, scratch and mutable closure records excluded.',
        'mutable_closure_records_outside_archive':sorted(MUTABLE),'normalized_host_path_files':normalized,
        'originals_preserved':True,'inventory_self_exclusion':'This manifest is added to the archive as an extra member; its own digest is bound in archive.json and COMPLETION.json.'}
    save(OUT/'inventory.json',inventory)
    target=OUT/'evidence.tar.gz'
    with target.open('xb') as output:
        with gzip.GzipFile(fileobj=output,mode='wb',compresslevel=3,mtime=0) as compressed:
            with tarfile.open(fileobj=compressed,mode='w|') as archive:
                for path in [*paths,OUT/'inventory.json']:
                    value,_=portable(path)
                    if path!=OUT/'inventory.json':
                        expected=entries[rel(path)];assert sha(path)==expected['source_sha256']
                        assert hashlib.sha256(value).hexdigest()==expected['archive_sha256']
                    info=tarfile.TarInfo(rel(path));info.size=len(value);info.mtime=0;info.mode=0o644;info.uid=info.gid=0
                    archive.addfile(info,io.BytesIO(value))
    expected={name:row['archive_sha256'] for name,row in entries.items()};expected[rel(OUT/'inventory.json')]=sha(OUT/'inventory.json')
    seen=set()
    with tarfile.open(target,'r:gz') as archive:
        for member in archive:
            assert member.isfile() and member.name in expected and member.name not in seen
            value=archive.extractfile(member).read();assert hashlib.sha256(value).hexdigest()==expected[member.name]
            seen.add(member.name)
    assert seen==set(expected)
    save(OUT/'archive.json',{'as_of':now(),'passed':True,'archive':rel(target),'sha256':sha(target),'bytes':target.stat().st_size,
        'members':len(seen),'inventory_sha256':sha(OUT/'inventory.json'),'payload_files':len(entries),
        'normalized_host_path_files':normalized,'exact_originals_retained_locally':True,'compiled_artifacts_included':False,
        'seconds':time.monotonic()-started,'protected':guard(),'budget':budget()})
    print(json.dumps({'archive_passed':True,'members':len(seen),'bytes':target.stat().st_size,'sha256':sha(target),'seconds':time.monotonic()-started}),flush=True)

if __name__=='__main__':main()
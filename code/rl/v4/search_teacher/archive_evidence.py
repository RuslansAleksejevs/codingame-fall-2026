"""Preserve complete branch records without binaries, private paths or caches."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
from common import CODE, OUT, ROOT, now, relative, save, sha


def normalized(value):
    if isinstance(value, str):
        return value.replace(str(ROOT), '${PROJECT_ROOT}').replace(str(Path.home()), '${HOME}')
    if isinstance(value, list):
        return [normalized(item) for item in value]
    if isinstance(value, dict):
        return {key: normalized(item) for key, item in value.items()}
    return value


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--name',default='evidence');args=ap.parse_args()
    assert args.name.replace('-','').isalnum()
    target=OUT/(args.name+'.tar.gz');assert not target.exists()
    assert (OUT/'teacher-decision.json').exists() or (OUT/'screen-decision.json').exists(), 'Complete a strength stage first'
    files=[]
    for root in (CODE,OUT):
        for path in sorted(root.rglob('*')):
            if not path.is_file():continue
            if any(part in ('build','__pycache__') for part in path.relative_to(root).parts):continue
            if path.suffix in ('.pyc','.class','.dylib','.so','.o') or path.name.endswith('.tar.gz'):continue
            files.append(path)
    files.append(ROOT/'docs/rl/v4/SEARCH_TEACHER.md')
    entries=[]
    # New archive only; the original per-game evidence is kept, not deleted.
    with target.open('xb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as compressed:
            with tarfile.open(fileobj=compressed,mode='w') as archive:
                for path in files:
                    original=path.read_bytes()
                    content=original
                    invocation='-seed' in path.name and path.name.endswith('-spec.json')
                    if invocation:
                        content=(json.dumps(normalized(json.loads(original)),indent=2)+'\n').encode()
                    inspect=gzip.decompress(content) if path.name.endswith('.json.gz') else content
                    private_path_prefix=b'/' + b'Users' + b'/'
                    assert private_path_prefix not in inspect, 'Personal absolute path in '+relative(path)
                    name=relative(path)
                    info=tarfile.TarInfo(name);info.size=len(content);info.mode=0o644;info.mtime=0
                    archive.addfile(info,io.BytesIO(content))
                    entries.append({'path':name,'size':len(content),'sha256':hashlib.sha256(content).hexdigest(),
                                    'original_sha256':hashlib.sha256(original).hexdigest(),
                                    'normalized_invocation_copy':invocation and content!=original})
    with tarfile.open(target,'r:gz') as archive:
        members=archive.getmembers();assert len(members)==len(entries)
        for member,entry in zip(members,entries):
            assert member.name==entry['path'] and member.isfile()
            assert hashlib.sha256(archive.extractfile(member).read()).hexdigest()==entry['sha256']
    save(OUT/(args.name+'-manifest.json'),{'as_of':now(),'archive':relative(target),
        'sha256':sha(target),'files':len(entries),'entries':entries,'roundtrip_verified':True,
        'omitted':'Build/cache binaries and other tar.gz archives only; all per-game invocation specs retained as normalized copies.',
        'normalization':'Absolute project/home prefixes replaced by placeholders only inside archived invocation copies; original files untouched. Each entry binds original_sha256 to archived sha256.',
        'normalized_invocations':sum(entry['normalized_invocation_copy'] for entry in entries),
        'original_records_deleted':False,'external_spend':0})
    print(json.dumps({'archive':relative(target),'sha256':sha(target),'files':len(entries),'verified':True}))


if __name__=='__main__':main()
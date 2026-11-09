"""Publication-only, non-overwriting D16 snapshot; no experiment or API execution."""
from collections import Counter
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
import tarfile
import time
import zlib

from common import ROOT, CODE, OUT, guard, budget, now, rel, sha, save

PUB=OUT/'publication-2026-11-09'
DOC=ROOT/'docs/rl/v7/D16.md'
ARCHIVE=PUB/'evidence.tar.gz'
GAME_DIRS=('regression','development','confirm1','confirm2','a3-gross')
COMPILED_SUFFIXES={'.dylib','.so','.a','.o','.class','.exe','.bin','.pt','.pkl','.pickle','.pyc','.pyo'}
EXCLUDED_COMPONENTS={'build','__pycache__','.context','scratch','.git','.venv','venv','env','cache','node_modules'}
SENSITIVE_NAMES=re.compile(r'(?i)(?:^|[-_.])(?:credential|oauth|keychain|privatechat|transcript|permission-execution|approval-execution)(?:[-_.]|$)')
SCANS=[
    ('codingame_token',re.compile(rb'(?<![A-Za-z0-9])cgp_[A-Za-z0-9._-]{12,}')),
    ('github_token',re.compile(rb'(?<![A-Za-z0-9])(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})')),
    ('openai_token',re.compile(rb'(?<![A-Za-z0-9])sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}')),
    ('private_key',re.compile(rb'-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----')),
    ('bearer_credential',re.compile(rb'(?i)\bbearer\s+[A-Za-z0-9._~-]{24,}')),
    ('credential_payload',re.compile(rb'(?i)"(?:access_token|refresh_token|client_secret|api_key|password|authorization|cookie)"\s*:\s*"(?!\$\{|REDACTED|UNKNOWN|NONE|NULL)[^"\r\n]{16,}"')),
    ('residual_user_path',re.compile(rb'/(?:Users|home)/[^/\\\s"\x27<>]+')),
    ('residual_windows_user_path',re.compile(rb'(?i)[a-z]:[\\/]+Users[\\/]+[^\\/\s"\x27<>]+')),
]
BINARY_MAGICS=(b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\x7fELF',b'\xca\xfe\xba\xbe',b'MZ')

def digest(data):return hashlib.sha256(data).hexdigest()

def collect():
    paths=[]
    for scope in (CODE,OUT):
        for directory,dirs,names in os.walk(scope,followlinks=False):
            directory=Path(directory)
            dirs[:]=[n for n in dirs if not (directory/n).is_symlink() and (directory/n)!=PUB]
            paths.extend(directory/n for n in names)
    paths.extend([DOC,PUB/'README.md'])
    return sorted(set(paths))

def excluded_reason(path):
    parts=path.relative_to(ROOT).parts
    if path.is_symlink():return 'symlink_not_exported'
    if not path.is_file():return 'not_regular_file'
    if any(p in EXCLUDED_COMPONENTS for p in parts):return 'compiled_build_environment_cache_or_scratch'
    if path.suffix.lower() in COMPILED_SUFFIXES:return 'binary_or_compiled_artifact'
    if path.name=='.DS_Store' or path.name=='.env' or path.name.startswith('.env.'):return 'host_metadata_or_environment_file'
    if SENSITIVE_NAMES.search(path.name):return 'credential_private_chat_or_permission_execution_path'
    return None

def normalize(text):
    changes={}
    for label,old,new in [('project_path',str(ROOT),'${PROJECT_ROOT}'),('home_path',str(Path.home()),'${USER_HOME}')]:
        seen=set()
        for encoding,value in [('literal',old),('json_escaped',json.dumps(old)[1:-1])]:
            if value in seen:continue
            seen.add(value);count=text.count(value)
            if count:text=text.replace(value,new);changes[label+'_'+encoding]=count
    return text,changes

def reasons(data):
    found=[name for name,pattern in SCANS if pattern.search(data)]
    if data.startswith(BINARY_MAGICS):found.append('executable_binary_magic')
    return found

def portable(path,original):
    compressed=path.name.endswith('.gz')
    decoded=gzip.decompress(original) if compressed else original
    try:text=decoded.decode('utf-8')
    except UnicodeDecodeError:return None,{},['unscannable_non_utf8_payload'],None
    normalized,changes=normalize(text);inspected=normalized.encode('utf-8')
    problems=reasons(inspected)
    if problems:return None,changes,problems,None
    exported=original if not changes else gzip.compress(inspected,compresslevel=9,mtime=0) if compressed else inspected
    return exported,changes,[],{'original_decoded_sha256':digest(decoded),'export_decoded_sha256':digest(inspected)} if compressed else None

def safe_name(name):
    p=PurePosixPath(name)
    return bool(name) and not p.is_absolute() and '..' not in p.parts and '.' not in p.parts and '\\' not in name and str(p)==name

def main():
    began=time.monotonic();protected=guard()
    assert PUB.is_dir() and {p.name for p in PUB.iterdir()}=={'README.md'},'New publication directory must contain only its initial README'
    assert not ARCHIVE.exists()
    # Read-only validation of historical frozen dependencies; this runs no phase.
    from panel_a3 import checked
    frozen=checked()
    paths=collect();original_hashes={};entries=[];excluded=[];normalizations=Counter()
    source_counts={'raw_games':0,'portable_games':0,'contract_gzip_records':0}
    for path in paths:
        name=rel(path);assert safe_name(name)
        reason=excluded_reason(path)
        if path.is_symlink() or not path.is_file():
            excluded.append({'path':name,'reason':reason,'original_sha256':None});continue
        original=path.read_bytes();original_hashes[name]=digest(original)
        if path.parent.name in GAME_DIRS:
            source_counts['raw_games']+=path.name.endswith('-raw.json')
            source_counts['portable_games']+=path.name.endswith('.json.gz')
        elif path.name.endswith('.json.gz') and 'contracts' in path.parent.name:source_counts['contract_gzip_records']+=1
        if reason:
            excluded.append({'path':name,'reason':reason,'original_sha256':digest(original),'original_bytes':len(original)});continue
        try:exported,changes,problems,decoded=portable(path,original)
        except (gzip.BadGzipFile,EOFError):exported=None;changes={};problems=['invalid_gzip_payload'];decoded=None
        if problems:
            excluded.append({'path':name,'reason':'sensitive_or_unscannable_export','scan_reasons':problems,'original_sha256':digest(original),'original_bytes':len(original)});continue
        normalizations.update(changes)
        row={'path':name,'original_sha256':digest(original),'export_sha256':digest(exported),'original_bytes':len(original),'export_bytes':len(exported),'normalizations':changes}
        if decoded:row.update(decoded)
        entries.append(row)
    assert source_counts['raw_games']==source_counts['portable_games']==533,source_counts
    included_paths={r['path'] for r in entries}
    included_counts={k:sum(1 for r in entries if (ROOT/r['path']).parent.name in GAME_DIRS and r['path'].endswith(suffix)) for k,suffix in [('raw_games','-raw.json'),('portable_games','.json.gz')]}
    inventory={'as_of':now(),'classification':'PROJECT_REPORTED','scope':'Owned D16 scientific evidence, raw/portable games, contracts, failures, readable packages, code/docs; publication-only export, not new research.',
        'method':'Normalize current project/home prefixes in export copies only, including JSON-escaped forms and decompressed gzip UTF8. Preserve source bytes. Do not alter measurements or embedded historical hashes.',
        'source_scope':[rel(CODE),rel(OUT),rel(DOC)],'payload_files':len(entries),'included_source_counts':included_counts,'discovered_source_counts':source_counts,
        'normalized_files':sum(bool(r['normalizations']) for r in entries),'normalization_occurrences':dict(normalizations),'exclusions':excluded,'exclusion_counts':dict(Counter(r['reason'] for r in excluded)),
        'security_scan':'CodinGame/GitHub/OpenAI token forms, bearer/credential payloads, private-key blocks, residual POSIX/Windows user paths and executable magic. Compressed UTF8 inspected after decompression. Matched values are never recorded or printed.',
        'files':entries,'metadata_members_outside_original_inventory':[rel(PUB/'inventory.json')],
        'limitations':'Regex screening is not proof of absence of all possible secrets. Frozen verifier hashes refer to original files; use each original/export SHA mapping. This is a dated in-progress-ranking snapshot, not a final leaderboard claim.',
        'originals_retained':True,'candidate_source_sha256':sha(OUT/'package-attempt3/bot.cpp'),'a3_freeze_sha256':sha(OUT/'a3-freeze.json'),'a3_frozen_identity_count':len(frozen['identities']),
        'commands':{'create':'python3 -B code/rl/v7/compute_slot.py --owner d16 --minutes 5 -- code/arena/.venv-rl/bin/python -B code/rl/v7/d16/publication.py','large_archive_split':'code/split_evidence.py create <archive> <publication/archive-parts>'},
        'versions':{'python':sys.version,'platform':platform.system(),'machine':platform.machine(),'zlib':zlib.ZLIB_VERSION,'zlib_runtime':zlib.ZLIB_RUNTIME_VERSION},'budget_before_compression':budget()}
    save(PUB/'inventory.json',inventory)
    expected={r['path']:r['export_sha256'] for r in entries};expected[rel(PUB/'inventory.json')]=sha(PUB/'inventory.json')
    with ARCHIVE.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0,compresslevel=3) as packed:
        with tarfile.open(fileobj=packed,mode='w|',format=tarfile.PAX_FORMAT) as archive:
            for row in entries:
                path=ROOT/row['path'];original=path.read_bytes();assert digest(original)==row['original_sha256'],('Original changed',row['path'])
                data,_,problems,_=portable(path,original);assert not problems and digest(data)==row['export_sha256'],('Export mismatch',row['path'])
                info=tarfile.TarInfo(row['path']);info.size=len(data);info.mtime=0;info.mode=0o644;info.uid=info.gid=0;info.uname=info.gname=''
                archive.addfile(info,io.BytesIO(data))
            data=(PUB/'inventory.json').read_bytes();assert not reasons(data)
            info=tarfile.TarInfo(rel(PUB/'inventory.json'));info.size=len(data);info.mtime=0;info.mode=0o644;info.uid=info.gid=0;info.uname=info.gname=''
            archive.addfile(info,io.BytesIO(data))
    seen=set()
    with tarfile.open(ARCHIVE,'r|gz') as archive:
        for member in archive:
            assert member.isfile() and safe_name(member.name) and member.name in expected and member.name not in seen,('Unsafe member',member.name)
            stream=archive.extractfile(member);hashed=hashlib.sha256();size=0
            for block in iter(lambda:stream.read(1024*1024),b''):hashed.update(block);size+=len(block)
            assert size==member.size and hashed.hexdigest()==expected[member.name],('Member SHA mismatch',member.name)
            seen.add(member.name)
    assert seen==set(expected)
    assert set(collect())==set(paths),'Original file set changed during snapshot'
    for name,h in original_hashes.items():assert sha(ROOT/name)==h,('Original changed after archive',name)
    checked();assert guard()==protected
    split=None
    if ARCHIVE.stat().st_size>48*1024*1024:
        command=[sys.executable,'-B','code/split_evidence.py','create',rel(ARCHIVE),rel(PUB/'archive-parts')]
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=60)
        save(PUB/'split-command.json',{'as_of':now(),'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        assert result.returncode==0,'Archive split failed; preserve original and logs'
        split={'manifest':rel(PUB/'archive-parts/manifest.json'),'manifest_sha256':sha(PUB/'archive-parts/manifest.json')}
    receipt={'as_of':now(),'passed':True,'archive':rel(ARCHIVE),'archive_sha256':sha(ARCHIVE),'archive_bytes':ARCHIVE.stat().st_size,
        'inventory':rel(PUB/'inventory.json'),'inventory_sha256':sha(PUB/'inventory.json'),'payload_files':len(entries),'members_verified_full_stream':len(seen),
        'included_source_counts':included_counts,'discovered_source_counts':source_counts,'normalized_files':inventory['normalized_files'],'normalization_occurrences':dict(normalizations),
        'exclusion_counts':inventory['exclusion_counts'],'sensitive_exclusions':[{'path':r['path'],'reasons':r.get('scan_reasons',[r['reason']])} for r in excluded if r['reason'] not in ('compiled_build_environment_cache_or_scratch','binary_or_compiled_artifact','host_metadata_or_environment_file')],
        'originals_rehashed_unchanged':len(original_hashes),'source_file_set_unchanged':True,'file_only_safe_members':True,'scientific_compiler_run_logs_retained':True,
        'compiled_builds_env_cache_private_chats_permission_execution_logs_included':False,'split':split,'seconds':time.monotonic()-began,'budget_before_this_lease_finish':budget(),
        'ranking_status':'In progress at source snapshot; no new official API call by this helper','new_games':0,'new_inference_training':0,'git_mutations':0,'external_spend':0}
    save(PUB/'archive.json',receipt);print(json.dumps(receipt),flush=True)

if __name__=='__main__':main()
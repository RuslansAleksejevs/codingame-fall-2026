"""Hash-audited allocations; read only previously exposed datasets/claims."""
import gzip
import re
import subprocess
from common import *
from rl.v3.map_registry import build as prior_registry
from run_matches import REPO, java_home


def classpath():
    return str(ROOT/'code/build')+':'+str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()


def registry(name):
    result=prior_registry();canonical=set(result['canonical']);legacy=set(result['legacy']);bindings=result['sources']
    # Explicitly add every later platform log and every branch claim; avoid relying
    # on the historical collector's file-name coverage for these later datasets.
    candidates=[]
    for folder in ('experiments/rl/2026-11-07-ppo-v3/platform',
                   'experiments/rl/2026-11-07-ppo-v3/live-submission',
                   'experiments/rl/2026-11-08-rl4'):
        for path in (ROOT/folder).rglob('*.json*'):
            if 'snapshots' in path.parts or 'build' in path.parts:continue
            if path.name in ('map-contribution.json','map-registry-claim.json') or (
                '2026-11-07-ppo-v3' in path.parts and (path.suffix=='.gz' or 'log' in path.name)):
                candidates.append(path)
    for path in sorted(candidates):
        raw=path.read_bytes()
        try:value=json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
        except (ValueError,OSError):continue
        canonical.update(value.get('canonical',[]));legacy.update(value.get('legacy',[]))
        def visit(item):
            if isinstance(item,list):
                for v in item:visit(v)
            elif isinstance(item,dict):
                for key in ('gameParameters','game_options'):
                    if key in item:
                        text=item[key];text=''.join(text) if isinstance(text,list) else text
                        if isinstance(text,str):
                            props=dict(line.split('=',1) for line in text.splitlines() if '=' in line)
                            if all(k in props for k in ('nodes','units','edges')):
                                props={k:props[k] for k in ('nodes','units','edges')}
                                board={k:[list(map(int,row.split(','))) for row in props[k].split('_') if row] for k in props}
                                canonical.add(hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest())
                                legacy.add(hashlib.sha256(json.dumps(props,sort_keys=True).encode()).hexdigest())
                for v in item.values():visit(v)
        visit(value);bindings[rel(path)]=sha(path)
    for path in OUT.glob('*-map-hashes.json'):
        canonical.update(json.loads(path.read_text()).values());bindings[rel(path)]=sha(path)
    result.update(canonical=sorted(canonical),legacy=sorted(legacy),sources=bindings,as_of=now())
    save(OUT/(name+'-registry.json'),result);return result


def prepare(name,seeds):
    assert set(seeds)<=set(range(70001,70021))|set(range(70101,70141))
    exclusions=registry(name);known=set(exclusions['canonical']);old=set(exclusions['legacy'])
    generator=subprocess.Popen([str(java_home()/'bin/java'),'-Xmx1g','-cp',classpath(),'MapGenerator'],
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    entries=[];hashes={};overlaps=[]
    try:
        for seed in seeds:
            generator.stdin.write(str(seed)+'\n');generator.stdin.flush();props=json.loads(generator.stdout.readline())
            board={k:[list(map(int,row.split(','))) for row in props[k].split('_') if row] for k in ('nodes','units','edges')}
            digest=hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            legacy=hashlib.sha256(json.dumps(props,sort_keys=True).encode()).hexdigest()
            if digest in known or legacy in old or digest in hashes.values():overlaps.append(seed)
            hashes[str(seed)]=digest;entries.append({'seed':seed,'hash':digest,'legacy_hash':legacy,'map':board})
    finally:generator.stdin.close();generator.wait(timeout=20)
    save(OUT/(name+'-maps.json'),{'as_of':now(),'maps':entries,'overlaps':overlaps})
    save(OUT/(name+'-map-hashes.json'),hashes)
    save(OUT/(name+'-novelty.json'),{'as_of':now(),'passed':not overlaps,'seeds':seeds,'overlaps':overlaps,
         'previous_canonical':len(known),'previous_legacy':len(old),'source_count':len(exclusions['sources']),
         'registry_sha256':sha(OUT/(name+'-registry.json')),'map_sha256':sha(OUT/(name+'-maps.json'))})
    assert not overlaps,'Map content overlap: stop, no replacement'
    return hashes
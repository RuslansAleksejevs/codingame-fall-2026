"""Canonical/legacy novelty, explicitly including every exposed v5 partition."""
import gzip
import subprocess
from common import *
from run_matches import REPO,java_home

def classpath():return str(ROOT/'code/build')+':'+str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()

def registry(name):
    old=module('v5_maps_readonly',V5CODE/'maps.py').registry(name+'-prior')
    canonical=set(old['canonical']);legacy=set(old['legacy']);bindings=dict(old['sources'])
    def visit(value):
        if isinstance(value,list):
            for v in value:visit(v)
        elif isinstance(value,dict):
            if all(k in value for k in ('nodes','units','edges')):
                data={k:value[k] for k in ('nodes','units','edges')}
                if all(isinstance(v,str) for v in data.values()):
                    legacy.add(hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest())
                    data={k:[list(map(int,row.split(','))) for row in v.split('_') if row] for k,v in data.items()}
                if all(isinstance(v,list) for v in data.values()):canonical.add(hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest())
            for k,v in value.items():
                if k in ('canonical','legacy') and isinstance(v,list):(canonical if k=='canonical' else legacy).update(v)
                if k in ('map_hash','map_content_sha256','hash') and isinstance(v,str) and len(v)==64:canonical.add(v)
                if k=='legacy_hash' and isinstance(v,str):legacy.add(v)
                visit(v)
    candidates=set(V5.rglob('*-maps.json'))|set(V5.rglob('*-map-hashes.json'))|set(OUT.glob('*-map-hashes.json'))
    for pattern in ('*map-contribution*.json','*map-registry-claim*.json','*map-reservations*.json'):
        candidates.update((ROOT/'experiments').rglob(pattern))
    for path in sorted(candidates):
        value=json.loads(path.read_text());visit(value)
        if path.name.endswith('-map-hashes.json'):canonical.update(value.values())
        bindings[rel(path)]=sha(path)
    assert all(len(h)==64 for h in canonical|legacy)
    result={'as_of':now(),'canonical':sorted(canonical),'legacy':sorted(legacy),'sources':bindings,'method':'Original registry plus all v5 main/student maps and hashes, all branch claims/reservations, prior v6 blocks; no seed-only novelty inference'}
    save(OUT/(name+'-registry.json'),result);return result

def prepare(name,seeds):
    allowed=set(range(71001,71013)) if name=='development' else set(range(40001,40101))
    assert set(seeds)<=allowed and len(set(seeds))==len(seeds)
    if name!='development':
        approval=json.loads((OUT/'parent-final-approval.json').read_text())
        assert approval['approved'] and approval['freeze_sha256']==sha(OUT/'final-freeze.json')
    exclusions=registry(name);known=set(exclusions['canonical']);old=set(exclusions['legacy'])
    generator=subprocess.Popen([str(java_home()/'bin/java'),'-Xmx1g','-cp',classpath(),'MapGenerator'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    entries=[];hashes={};overlaps=[]
    try:
        for seed in seeds:
            generator.stdin.write(str(seed)+'\n');generator.stdin.flush();props=json.loads(generator.stdout.readline())
            board={k:[list(map(int,row.split(','))) for row in props[k].split('_') if row] for k in ('nodes','units','edges')}
            digest=hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            previous=hashlib.sha256(json.dumps(props,sort_keys=True).encode()).hexdigest()
            if digest in known or previous in old or digest in hashes.values():overlaps.append(seed)
            hashes[str(seed)]=digest;entries.append({'seed':seed,'hash':digest,'legacy_hash':previous,'map':board})
    finally:generator.stdin.close();generator.wait(timeout=20)
    save(OUT/(name+'-maps.json'),{'as_of':now(),'maps':entries,'overlaps':overlaps})
    save(OUT/(name+'-map-hashes.json'),hashes)
    save(OUT/(name+'-novelty.json'),{'as_of':now(),'passed':not overlaps,'seeds':seeds,'overlaps':overlaps,'previous_canonical':len(known),'previous_legacy':len(old),'source_count':len(exclusions['sources']),'registry_sha256':sha(OUT/(name+'-registry.json')),'map_sha256':sha(OUT/(name+'-maps.json'))})
    assert not overlaps,'Map overlap: stop without replacement'
    return hashes
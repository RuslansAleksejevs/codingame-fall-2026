"""Content novelty using the historical registry plus every later exposed claim."""
import gzip
from common import *
from run_matches import REPO, java_home

def classpath(): return str(ROOT/'code/build')+':'+str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()

def registry(name):
    source=V6/'confirm2-registry.json'; prior=json.loads(source.read_text())
    canonical=set(prior['canonical']); legacy=set(prior['legacy']); bindings={rel(source):sha(source)}
    def visit(value):
        if isinstance(value,list):
            for x in value:visit(x)
        elif isinstance(value,dict):
            if all(k in value for k in ('nodes','units','edges')):
                board={k:value[k] for k in ('nodes','units','edges')}
                if all(isinstance(v,str) for v in board.values()):
                    legacy.add(hashlib.sha256(json.dumps(board,sort_keys=True).encode()).hexdigest())
                    board={k:[list(map(int,r.split(','))) for r in v.split('_') if r] for k,v in board.items()}
                if all(isinstance(v,list) for v in board.values()):canonical.add(hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest())
            for k,v in value.items():
                if k in ('gameParameters','game_options'):
                    text=''.join(v) if isinstance(v,list) else v
                    if isinstance(text,str):visit(dict(x.split('=',1) for x in text.splitlines() if '=' in x))
                if k in ('canonical','legacy') and isinstance(v,list):(canonical if k=='canonical' else legacy).update(v)
                if k in ('map_hash','map_content_sha256','hash') and isinstance(v,str) and len(v)==64:canonical.add(v)
                if k=='legacy_hash' and isinstance(v,str):legacy.add(v)
                visit(v)
    candidates=set()
    for folder in [V5,V6,ROOT/'experiments/rl/2026-11-09-rl7']:
        for pattern in ('*-maps.json','*-map-hashes.json','*map-contribution*.json','*map-registry-claim*.json','*map-reservations*.json'):
            candidates.update(folder.rglob(pattern))
    live=ROOT/'experiments/rl/2026-11-08-leaderboard-recheck'
    candidates.update(live.rglob('*log*.json'));candidates.update(live.rglob('*.json.gz'));candidates.update((live/'games').glob('*.json'));candidates.update(live.glob('test-*.json'))
    for path in sorted(candidates):
        data=path.read_bytes();value=json.loads(gzip.decompress(data) if path.suffix=='.gz' else data);visit(value)
        if path.name.endswith('-map-hashes.json'):canonical.update(value.values())
        bindings[rel(path)]=sha(path)
    result={'as_of':now(),'canonical':sorted(canonical),'legacy':sorted(legacy),'sources':bindings,'method':'Pinned full v6 prior registry plus all v5/v6/v7 map claims and later exposed platform logs; canonical content, not seed IDs'}
    save(OUT/(name+'-registry.json'),result);return result

def prepare(name,seeds):
    allowed=set(range(72001,72005)) if name=='development' else set(range(72101,72141))
    assert set(seeds)<=allowed and len(set(seeds))==len(seeds)
    if name!='development':assert (OUT/'final-freeze.json').exists()
    prior=registry(name);known=set(prior['canonical']);old=set(prior['legacy'])
    generator=subprocess.Popen([str(java_home()/'bin/java'),'-Xmx1g','-cp',classpath(),'MapGenerator'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    entries=[];hashes={};overlaps=[]
    try:
        for seed in seeds:
            generator.stdin.write(str(seed)+'\n');generator.stdin.flush();props=json.loads(generator.stdout.readline())
            board={k:[list(map(int,r.split(','))) for r in props[k].split('_') if r] for k in ('nodes','units','edges')}
            digest=hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            previous=hashlib.sha256(json.dumps(props,sort_keys=True).encode()).hexdigest()
            if digest in known or previous in old or digest in hashes.values():overlaps.append(seed)
            hashes[str(seed)]=digest;entries.append({'seed':seed,'hash':digest,'legacy_hash':previous,'map':board})
    finally:generator.stdin.close();generator.wait(timeout=20)
    save(OUT/(name+'-maps.json'),{'as_of':now(),'maps':entries,'overlaps':overlaps});save(OUT/(name+'-map-hashes.json'),hashes)
    save(OUT/(name+'-novelty.json'),{'as_of':now(),'passed':not overlaps,'seeds':seeds,'overlaps':overlaps,'previous_canonical':len(known),'previous_legacy':len(old),'source_count':len(prior['sources']),'registry_sha256':sha(OUT/(name+'-registry.json'))})
    assert not overlaps,'Map overlap: stop without replacement'
    return hashes
"""Hash-only inter-lane map exclusion and reproducible stage snapshots."""
import hashlib
import json
import subprocess
from common import OUT, ROOT, checked_seeds, now, relative, save, sha

BASE = ROOT / 'experiments/rl/2026-11-08-rl4/map-registry-base.json'


def registry(path, include_own=True):
    sources = [BASE]
    for lane in ('exploiters', 'curriculum', 'search-teacher'):
        if lane=='search-teacher' and not include_own: continue
        for name in ('map-contribution.json', 'map-registry-claim.json'):
            contribution = BASE.parent / lane / name
            if contribution.exists(): sources.append(contribution)
    canonical, legacy = set(), set()
    for source in sources:
        data = json.loads(source.read_text())
        canonical.update(data['canonical']); legacy.update(data.get('legacy', []))
    result = {'as_of':now(),'canonical':sorted(canonical),'legacy':sorted(legacy),
              'sources':{relative(p):sha(p) for p in sources},
              'method':'Frozen prior exposure plus exact hash-only lane contributions, no foreign map payloads.'}
    save(path, result)
    return result


def contribute(stage_hash_file, legacy_hashes=(), seed_mapping=None):
    path = OUT / 'map-contribution.json'
    previous = json.loads(path.read_text()) if path.exists() else {'canonical':[], 'legacy':[], 'sources':{}}
    hashes = json.loads(stage_hash_file.read_text())
    data = {'as_of':now(),'lane':'search-teacher','purpose':'Development exposure; never global final.',
            'canonical':sorted(set(previous['canonical']) | set(hashes.values())),
            'legacy':sorted(set(previous['legacy']) | set(legacy_hashes)),
            'sources':dict(previous['sources'], **{relative(stage_hash_file):sha(stage_hash_file)}),
            'seed_mapping':dict(previous.get('seed_mapping',{}), **(seed_mapping or {}))}
    # Mutable, branch-owned hash-only registry; immutable stage sources retain history.
    path.write_text(json.dumps(data, indent=2)+'\n')
    (OUT/'map-registry-claim.json').write_text(json.dumps(data,indent=2)+'\n')
    return data


def prepare(name, seeds, exclusions, reuse=False):
    """Generate and claim exact contents before the first match/rollout."""
    from run_matches import REPO, java_home
    checked_seeds(seeds)
    cp=str(ROOT/'code/build')+':'+str(REPO/'target/classes')+':'+(REPO/'classpath.txt').read_text().strip()
    generator=subprocess.Popen([str(java_home()/'bin/java'),'-Xmx1g','-cp',cp,'MapGenerator'],
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    known=set(exclusions['canonical']); old=set(exclusions['legacy']); entries=[]; hashes={}; legacy=[]
    own=json.loads((OUT/'map-registry-claim.json').read_text()) if (OUT/'map-registry-claim.json').exists() else {}
    try:
        for seed in seeds:
            generator.stdin.write(str(seed)+'\n');generator.stdin.flush()
            props=json.loads(generator.stdout.readline())
            board={k:[list(map(int,r.split(','))) for r in props[k].split('_') if r] for k in ('nodes','units','edges')}
            digest=hashlib.sha256(json.dumps(board,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            previous=hashlib.sha256(json.dumps(props,sort_keys=True).encode()).hexdigest()
            assert digest not in known and previous not in old and digest not in hashes.values(), 'Content overlap'
            if reuse: assert own['seed_mapping'][str(seed)]==digest, 'Only previously claimed diagnostic smoke reuse is allowed'
            hashes[str(seed)]=digest;legacy.append(previous)
            entries.append({'seed':seed,'hash':digest,'legacy_hash':previous,'map':board})
    finally:
        generator.stdin.close();generator.wait(timeout=20)
    save(OUT/(name+'-maps.json'), {'as_of':now(),'purpose':name,'maps':entries})
    path=OUT/(name+'-map-hashes.json');save(path,hashes)
    contribute(path,legacy,hashes)
    return OUT/(name+'-maps.json')
"""Read frozen arena records without relying on simultaneous output frame indices."""
import gzip
import hashlib
import json
import re
from pathlib import Path

ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
NORMAL = {'is dominated', 'no units or triangles left', "can't score any more points"}

def read(path):
    result=json.loads(gzip.decompress(path.read_bytes()))
    params={}
    for line in ''.join(result['gameParameters']).splitlines():
        if '=' in line:
            k,v=line.split('=',1);params[k]=v
    data={k:[list(map(int,row.split(','))) for row in params[k].split('_') if row] for k in ('nodes','units','edges')}
    key=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    units=[[0,0] for _ in data['nodes']]
    decisions=[[],[]]
    for i,view in enumerate(result['views']):
        for p in (0,1):
            output=result['outputs'][str(p)][i]
            if output:
                decisions[p].append({'action':output.strip(),'units':[u.copy() for u in units], 'frame':i})
        raw=view.split('\n',1)[1].strip() if '\n' in view else ''
        if raw:
            frame=json.loads(raw);frame=frame.get('frame',frame)
            for part in frame.get('nodes','').split():
                if len(part)>3 and part[2]=='=':
                    p,phase=int(part[0]),int(part[1])
                    for house,amount in re.findall(r'([a-zA-Z])(\d*)',part[3:]):
                        units[ALPHABET.index(house)][p]=int(amount) if amount else phase
    paired=[]
    for a,b in zip(*decisions):
        if a['units']!=b['units']:
            raise ValueError(f'Players did not observe the same state: {path.name}, {len(paired)}')
        paired.append({'actions':[a['action'],b['action']],'units':a['units']})
    summaries=''.join(x or '' for x in result['summaries'])
    errors=[s for _,s in re.findall(r'\$(\d): ([^\n]+)',summaries) if s not in NORMAL]
    if result.get('failCause') or any(result.get('errors',{}).get('referee',[])):
        errors.append('referee failure')
    return {'map':data,'map_hash':key,'decisions':paired,'unpaired':[len(v)-len(paired) for v in decisions],
            'errors':errors,'scores':result['scores'],'seed':int(params['seed'])}

def sources(root):
    base=root/'experiments/2026-11-06-attack-holdout/run'
    return sorted(base.glob('*/*.json.gz'))

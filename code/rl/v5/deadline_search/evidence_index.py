"""Portable immutable lease ledger and evidence index; no Git or external writes."""
from common import *


def ledger(name):
    records=[json.loads(s) for s in (ROOT/'.context/rl4-compute/events.jsonl').read_text().splitlines()]
    total=0.;pending=None;entries=[]
    for r in records:
        if r.get('owner')!='search-teacher':continue
        if r['event']=='started':pending=r
        elif r['event']=='finished':
            if total>=INITIAL_SPENT-1e-6:
                assert pending
                entries.append({'started':pending['as_of'],'finished':r['as_of'],'command':pending['command'],
                    'allowed_seconds':pending['allowed_seconds'],'actual_seconds':r['seconds'],
                    'outcome':r['outcome'],'exit_code':r['exit_code']})
            total+=r['seconds'];pending=None
    phase=sum(e['actual_seconds'] for e in entries);assert abs(phase-(total-INITIAL_SPENT))<1e-6
    save(OUT/name,{'as_of':now(),'initial_owner_seconds':INITIAL_SPENT,'phase_completed_seconds':phase,
        'owner_completed_seconds':total,'phase_limit_seconds':10800,'owner_limit_seconds':14400,
        'completed_leases':entries,'active_lease_excluded':bool(pending),
        'external_spend':0,'budget':budget(),'source_sha256':sha(Path(__file__))})


def inventory():
    archive=json.loads((OUT/'evidence-manifest.json').read_text());assert archive['roundtrip_verified'] and archive['originals_unchanged']
    entries=list(archive['entries'])
    for name in ('evidence.tar.gz','evidence-manifest.json','lease-ledger-final.json'):
        path=OUT/name
        digest=archive['archive_sha256'] if name=='evidence.tar.gz' else sha(path)
        entries.append({'path':rel(path),'bytes':path.stat().st_size,'sha256':digest})
    save(OUT/'inventory.json',{'as_of':now(),'entries':entries,'count':len(entries),'archive_roundtrip_verified':True,
        'scope':'Portable source/evidence/scientific weights and checkpoints; compiled build/cache excluded. Mutable STATUS/HISTORY and completion remain beside this immutable inventory.',
        'protected':guard(),'budget':budget()})


if __name__=='__main__':
    if sys.argv[1]=='inventory':inventory()
    else:ledger(sys.argv[1])
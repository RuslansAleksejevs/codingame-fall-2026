"""Small closure metadata and read-only audit of coordinator-saved runtime logs."""
import statistics
from common import *
from panel import checked_freeze

def main():
    frozen=checked_freeze();guard()
    events=[json.loads(s) for s in (ROOT/'.context/rl7-compute/events.jsonl').read_text().splitlines()]
    ends=[e for e in events if e['event']=='finished' and e['owner']=='d16']
    package=json.loads((OUT/'candidate2-package.json').read_text())
    a=(OUT/'package-attempt1/bot.cpp').read_bytes();b=(OUT/'package-attempt2/bot.cpp').read_bytes()
    assert b==package['prelude'].encode()+a and sha(OUT/'package-attempt2/bot.cpp')==package['source_sha256']
    paths=['package-attempt2/bot.cpp','candidate2-package.json','package-attempt1/bot.cpp','final-freeze.json','poststop-decision.json','technical-readiness.json','PROTOCOL.md','AMENDMENT_A2.md']
    metadata={'as_of':now(),'HEAD':subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip(),'completed_d16_leases_before_this':len(ends),'completed_seconds_before_this':sum(e['seconds'] for e in ends),'source_body_exact':True,'frozen_identity_count':len(frozen['identities']),
        'raw_games':sum(len(list((OUT/n).glob('*-raw.json'))) for n in ('regression','development','confirm1','confirm2')),'portable_games':sum(len(list((OUT/n).glob('*.json.gz'))) for n in ('regression','development','confirm1','confirm2')),
        'hashes':{rel(OUT/n):sha(OUT/n) for n in paths},'training_updates':0,'new_labels':0,'paid_spend':0,'remaining_local_games_scheduled':0,'platform_owner':'Coordinator only; this script reads saved files and makes no API request.'}
    save(OUT/'local-handoff.json',metadata)
    live=ROOT/'experiments/rl/2026-11-09-d16-live';reports=[];pending=[]
    for n in (1,2,4,6,7,8):
        path=live/f'test-{n:02d}-result.json'
        if not path.exists():pending.append(n);continue
        result=json.loads(path.read_text())
        if result.get('status')!='done':pending.append(n);continue
        log=result.get('log',result);own={x['index'] for x in log['agents'] if x.get('me')};seats={}
        for p in sorted(own):
            frames=[f for f in log['frames'] if f.get('agent')==p];stdout=[f['stdout'] for f in frames if f.get('stdout')]
            stderr='\n'.join(f.get('stderr','') for f in frames);records=[json.loads(s.split('=',1)[1]) for s in stderr.splitlines() if s.startswith('deadline=')]
            assert len(records)==len(stdout),(n,p,'Missing telemetry')
            assert all(r['search']['baseline_complete']==1 and r['search']['emergency']==0 for r in records)
            rates=[r['search']['forward_us']/r['search']['forwards'] for r in records if r['search']['forwards']]
            seats[str(p)]={'outputs':len(stdout),'baseline_complete':len(records),'emergency':0,'completed_evaluations':sum(r['search']['complete'] for r in records),'turns_with_complete_evaluation':sum(r['search']['complete']>0 for r in records),'nonbaseline_selections':sum(r['search']['selected']>0 for r in records),'through_flush_us_max':max(r['through_flush_us'] for r in records),'baseline_us_max':max(r['search']['baseline_us'] for r in records),'median_forward_us_per_call':statistics.median(rates)}
        reports.append({'test':n,'attempt':1 if n<6 else 2,'game_id':log['game_id'],'path':rel(path),'sha256':sha(path),'seats':seats})
    runtime={'as_of':now(),'classification':'PROJECT_REPORTED from coordinator-saved official logs','independently_reparsed':True,'pending_test_numbers':pending,'games':reports,'qualification':'Runtime telemetry only. Coordinator audits official errors, exact requests/source/map/seat identities and owns ranking decisions. Wall times are not charged CPU; no new games/API/inference.'}
    save(OUT/'official-runtime-child-audit.json',runtime)
    print(json.dumps({'metadata':metadata,'runtime':runtime}),flush=True)

if __name__=='__main__':main()
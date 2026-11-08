"""Fresh smoke-record standalone/native parity, both absolute player orders."""
import json
import subprocess
from common import ACTOR, CRITIC, ENEMIES, OUT, ROOT, check_preserved, now, relative, save, sha
from diagnose import Native
from rl.data.replays import read
from rl.league.rollout import LIB as LEAGUE
from rl.sim.native import Simulator


def main():
    check_preserved()
    native=Native();policies={1:native.policy(count=1),4:native.policy(count=4)}
    binary=OUT/'smoke/snapshots/build/search'
    rows=[json.loads(line) for line in (OUT/'smoke/matches.jsonl').read_text().splitlines()]
    streams=[];total=0;mismatches=[]
    try:
        for row in rows:
            path=OUT/'smoke'/f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}.json.gz'
            record=read(path)
            for player in (0,1):
                for count,policy in policies.items():
                    sim=Simulator(record['map']);inputs=[];expected=[]
                    try:
                        for turn,decision in enumerate(record['decisions']):
                            inputs.append(LEAGUE.league_observation(sim.ptr,player,int(turn==0)))
                            expected.append(native.act(policy,sim,player))
                            sim.step(decision['actions'])
                    finally:sim.close()
                    command=[str(p) for p in [binary,ACTOR,CRITIC,*ENEMIES,2,count,0]]
                    result=subprocess.run(command,input=b''.join(inputs),capture_output=True,timeout=60)
                    actual=result.stdout.decode().splitlines()
                    different=sum(a!=b for a,b in zip(expected,actual))+abs(len(expected)-len(actual))
                    details={'record':relative(path),'record_sha256':sha(path),'player':player,
                             'proposals':count,'plans':len(expected),'returncode':result.returncode,
                             'mismatches':different}
                    streams.append(details);total+=len(expected)
                    if different or result.returncode:mismatches.append(details)
    finally:native.close()
    report={'as_of':now(),'passed':not mismatches,'plans_checked':total,'streams':streams,
            'mismatches':mismatches,'binary_sha256':sha(binary),'external_spend':0,
            'scope':'Unlimited-time same-input parity only; timed strength uses 30ms budget.'}
    save(OUT/'protocol-parity.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='streams'},indent=2))
    assert not mismatches


if __name__=='__main__':main()
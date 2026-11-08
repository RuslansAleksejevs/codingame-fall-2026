"""Additional fixed technical-record control audit; no new games or decisions selected."""
from common import *
from diagnose import Native
from rl.sim.native import Simulator
from rl.data.replays import read
from rl.league.rollout import LIB as LEAGUE
import subprocess


def main():
    guard();frozen=json.loads((OUT/'freeze.json').read_text())
    for p,h in frozen['sources'].items():assert sha(ROOT/p)==h
    native=Native();weights=[str(x).encode() for x in [ACTOR,CRITIC,*ENEMIES]]
    original=native.lib.search_new(*weights,2,1,0);assert original
    details=[];total=0
    try:
        for stage in ('regression','development'):
            rows=[json.loads(s) for s in (OUT/stage/'matches.jsonl').read_text().splitlines()]
            for row in rows:
                stem=f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}'
                path=OUT/stage/(stem+'.json.gz');record=read(path)
                for p in (0,1):
                    sim=Simulator(record['map']);expected=[];inputs=[]
                    try:
                        for turn,decision in enumerate(record['decisions']):
                            before=sim.state()
                            old=native.lib.search_act(original,sim.ptr,p).decode()
                            new,_=native.act(sim,p,count=1)
                            assert old==new and sim.state()==before
                            expected.append(old);inputs.append(LEAGUE.league_observation(sim.ptr,p,int(turn==0)))
                            sim.step(decision['actions'])
                    finally:sim.close()
                    command=[str(build_dir()/'bot'),*[str(x) for x in [ACTOR,CRITIC,*ENEMIES]],'1','0']
                    output=subprocess.run(command,input=b''.join(inputs),capture_output=True,timeout=30)
                    actual=output.stdout.decode().splitlines()
                    assert output.returncode==0 and actual==expected,(stem,p,'control parity')
                    details.append({'record':rel(path),'record_sha256':sha(path),'player':p,'commands':len(expected),'mismatches':0,
                        'expected_sha256':hashlib.sha256(('\n'.join(expected)+'\n').encode()).hexdigest(),
                        'actual_sha256':hashlib.sha256(output.stdout).hexdigest()})
                    total+=len(expected)
    finally:native.lib.search_delete(original);native.close()
    save(OUT/'control-parity.json',{'as_of':now(),'passed':True,'records':54,'streams':len(details),'commands':total,
        'scope':'Original frozen greedy/native D16-control/standalone D16-control on every applied technical-record turn, both absolute sides; no fresh strength evidence.',
        'details':details,'freeze_sha256':sha(OUT/'freeze.json'),'auditor_sha256':sha(Path(__file__)),'budget':budget()})
    print(json.dumps({'passed':True,'streams':len(details),'commands':total}),flush=True)


if __name__=='__main__':main()
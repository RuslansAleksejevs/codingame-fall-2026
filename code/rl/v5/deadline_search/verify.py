"""Replay all completed clean games against exact original Java full trajectories."""
import argparse
import re
import subprocess
from common import *
from maps import classpath
from run_matches import java_home
from rl.data.replays import read
from rl.sim.native import Simulator
from benchmark_public import NORMAL_ENDS


def verify(name, report_name=None):
    directory=OUT/name;rows=[json.loads(s) for s in (directory/'matches.jsonl').read_text().splitlines()]
    oracle=subprocess.Popen([str(java_home()/'bin/java'),'-Xmx1g','-cp',classpath(),'Oracle'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    states=transitions=games=0;excluded=[];failures=[];terminal_tails=[]
    try:
        for row in rows:
            stem=f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}'
            record=read(directory/(stem+'.json.gz'))
            if not row['valid'] or row['returncode'] or row['own_action_errors'] or row['opponent_action_errors'] or record['errors']:
                excluded.append(stem);continue
            # Original Referee.gameTurn checks and executes players sequentially.
            # A surviving player may emit one final command after the other is
            # eliminated; that command is never an applied joint transition.
            # Validate the tail after exact terminal-state/score comparison.
            assert sum(record['unpaired'])<=1, (stem,'unexpected unpaired output')
            actions=[d['actions'] for d in record['decisions']]
            oracle.stdin.write(json.dumps(dict(record['map'],actions=actions))+'\n');oracle.stdin.flush()
            reference=json.loads(oracle.stdout.readline());assert len(reference)==len(actions)+1
            sim=Simulator(record['map'])
            try:
                for turn,expected in enumerate(reference):
                    actual=sim.state()
                    diff=[k for k in ('turn','score','units','edges','triangles','done') if actual[k]!=expected[k]]
                    if diff:failures.append({'record':stem,'turn':turn,'fields':diff});break
                    assert actual['errors']==[0,0],(stem,turn,'native parse errors')
                    states+=1
                    if turn<len(actions):
                        assert actual['units']==record['decisions'][turn]['units']
                        sim.step(actions[turn]);transitions+=1
                actual=sim.state();assert actual['done'] and actual['score']==[record['scores'][str(p)] for p in (0,1)]
                if any(record['unpaired']):
                    survivor=record['unpaired'].index(1)
                    assert actual['score'][1-survivor]==-1 and actual['score'][survivor]>=0
                    raw=json.loads((directory/(stem+'-raw.json')).read_text())
                    text=''.join(s or '' for s in raw['summaries'])
                    endings=re.findall(r'\$'+str(1-survivor)+r': ([^\n]+)',text)
                    assert endings and all(e in NORMAL_ENDS for e in endings)
                    last_output=[s for s in raw['outputs'][str(survivor)] if s][-1]
                    terminal_tails.append({'record':stem,'survivor':survivor,'unapplied_commands':1,
                        'terminal_score':actual['score'],'normal_endings':endings,'unapplied_output':last_output,
                        'reason':'Original referee executes survivor in the terminal check loop.'})
                games+=1
            finally:sim.close()
    finally:oracle.stdin.close();oracle.wait(timeout=30)
    report={'as_of':now(),'passed':not failures,'rows':len(rows),'clean_games':games,'states':states,'transitions':transitions,
        'excluded':excluded,'mismatches':failures,'terminal_unapplied_tails':terminal_tails,'matches_sha256':sha(directory/'matches.jsonl'),
        'manifest_sha256':sha(directory/'manifest.json'),'verifier_sha256':sha(Path(__file__))}
    save(OUT/((report_name or name+'-verification')+'.json'),report);assert not failures
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage');verify(ap.parse_args().stage)
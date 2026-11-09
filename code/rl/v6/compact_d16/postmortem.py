"""Existing-evidence closure after a frozen gate failure. No new bot calls/games."""
from collections import Counter
import gzip
from common import *
from panel import checked_freeze
from analyze import own_error,points
from rl.data.replays import read
from rl.sim.native import Simulator
from rl.league.rollout import LIB as LEAGUE

def main():
    guard();checked_freeze(OUT/'final-freeze.json')
    failure=json.loads((OUT/'confirm2/failure.json').read_text());r=failure['row']
    assert r['candidate']=='candidate' and r['seed']==40016 and r['seat']==1 and r['emergency']
    stem='candidate-vs-league3m-seed40016-seat1';path=OUT/'confirm2'/(stem+'.json.gz')
    record=read(path);raw=json.loads(gzip.decompress(path.read_bytes()))
    bad=[t for t in r['deadline_measurements'] if t['search']['emergency']];assert len(bad)==1 and bad[0]['turn']==27
    output=[s.strip() for s in raw['outputs']['1'] if s][26];assert output=='WAIT'
    sim=Simulator(record['map'])
    try:
        for decision in record['decisions'][:26]:sim.step(decision['actions'])
        before=sim.state();observation=LEAGUE.league_observation(sim.ptr,1,1).decode()
        assert before['turn']==26 and before['units']==record['decisions'][26]['units']
        actions=record['decisions'][26]['actions'];assert actions[1]=='WAIT'
        sim.step(actions);after=sim.state();assert after['errors']==[0,0]
    finally:sim.close()
    stderr=''.join(s or '' for s in raw['errors']['1'])
    lines=[line for line in stderr.splitlines() if line.startswith('deadline=') and json.loads(line[9:])['turn']==27]
    assert len(lines)==1
    save(OUT/'failure-forensics.json',{'as_of':now(),'classification':'PROJECT_REPORTED','game':failure['game'],
        'turn':27,'raw_game_result':'win','raw_scores':[78,-1],'frozen_accounting_points':points(r),
        'arena_action_errors':r['own_action_errors'],'opponent_errors':r['opponent_action_errors'],
        'failed_condition':'Zero emergency fallbacks','actual_output':output,'timing':bad[0],
        'original_stderr_line':lines[0],'state_before':before,'joint_commands':actions,'state_after':after,
        'reconstructed_complete_observation':observation,'observation_bytes':len(observation.encode()),
        'evidenced_mechanism':'Input-read wall interval exhausted the16ms clock. The first D16 check stopped before any decoder or network call; the baseline was never generated.',
        'underlying_read_delay_cause':'UNKNOWN. The interval can include token receipt, blocking I/O, parsing and scheduling; it is not isolated parser CPU time.',
        'claims_not_made':['That this was a referee timeout','That inference/lookahead exhausted this turn budget','Attribution of the read delay to scheduler, arena, codec or parser CPU cost'],
        'scope':'Existing raw evidence and exact native transition only. No new game, timing rerun or bot call.',
        'bindings':{rel(p):sha(p) for p in (path,OUT/'confirm2'/(stem+'-raw.json'),OUT/'confirm2/failure.json',OUT/'final-freeze.json')}})
    verifier=module('v5_postfailure_verify',V5CODE/'verify.py');verifier.verify('confirm2')
    audit=module('v6_frozen_raw_audit',CODE/'final_audit.py');audit.audit(['confirm1','confirm2'],'final')
    run([sys.executable,'-B',CODE/'analyze.py','final'],'analyze-final-run',120)
    rows=[json.loads(s) for name in ('confirm1','confirm2') for s in (OUT/name/'matches.jsonl').read_text().splitlines()]
    def count(rr):
        return {'games':len(rr),'win':sum(points(x)==1 for x in rr),'draw':sum(points(x)==.5 for x in rr),'loss':sum(points(x)==0 for x in rr),
            'raw_wins':sum(x['outcome']=='win' for x in rr),'own_technical_games':sum(bool(own_error(x)) for x in rr),
            'arena_own_error_games':sum(bool(x['own_action_errors']) or not x['valid'] or x['returncode']!=0 for x in rr),
            'opponent_error_games':sum(bool(x['opponent_action_errors']) for x in rr)}
    all_counts={c:{'total':count([r for r in rows if r['candidate']==c]),
        'opponents':{o:{'total':count([r for r in rows if r['candidate']==c and r['opponent']==o]),
            'seats':{str(p):count([r for r in rows if r['candidate']==c and r['opponent']==o and r['seat']==p]) for p in (0,1)}}
            for o in ('lacoz','khoufou2','khoufou','v6','bc','league3m','b2m')}} for c in ('candidate','control','teacher')}
    save(OUT/'observed-final-counts.json',{'as_of':now(),'games':len(rows),'expected_games':4200,'candidates':all_counts,
        'includes_unpaired_partial_schedule_rows':True,'failed_raw_win_counted_as_loss':points(r)==0,
        'note':'All actually observed games, including the emergency record from an incomplete six-row cluster. Paired estimates use only complete clusters and do not establish final strength.'})
    save(OUT/'postmortem.json',{'as_of':now(),'decision':'REJECTED','completed_final_games':len(rows),'expected_final_games':4200,
        'new_games_after_stop':0,'retries':0,'platform_actions':0,'training_updates':0,'protected':guard(),'budget':budget(),
        'scope':'Mechanical replay, raw audit, frozen partial analysis and exact failure extraction only; all original evidence retained.'})

if __name__=='__main__':main()
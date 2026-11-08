"""Run one finite search-teacher stage inside the coordinator CPU lease."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from common import ACTOR, CRITIC, ENEMIES, EXTERNAL, OUT, ROOT, check_preserved, now, relative, save, sha
from gates import evaluate
from maps import contribute, prepare, registry


def run(command, log):
    command = [str(x) for x in command]
    started = time.monotonic()
    clean=lambda text:text.replace(str(ROOT),'${PROJECT_ROOT}').replace(str(Path.home()),'${HOME}')
    with (OUT/(log+'.log')).open('x') as stream:
        process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,text=True)
        for line in process.stdout:
            stream.write(clean(line));stream.flush()
        result=subprocess.CompletedProcess(command,process.wait())
    save(OUT/(log+'-command.json'), {'as_of':now(),'command':[clean(x) for x in command],'returncode':result.returncode,
                                  'wall_seconds':time.monotonic()-started,'log':log+'.log','external_spend':0,
                                  'driver_sha256':sha(Path(__file__))})
    print(json.dumps({'stage':log,'returncode':result.returncode,'wall_seconds':time.monotonic()-started}),flush=True)
    result.check_returncode()


def panel(name, seeds, smoke=False, confirmation=False):
    exclusions = OUT/(name+'-registry.json'); exclusion_data=registry(exclusions, include_own=not smoke)
    prepare(name,seeds,exclusion_data,reuse=smoke)
    opponents = ('lacoz','khoufou2') if smoke else (*EXTERNAL,'league3m', *(('v6','bc') if confirmation else ()))
    candidates = ('search2',) if smoke else ('greedy','search2')
    policies = {name:relative(ACTOR) for name in (*candidates,'league3m')}
    if confirmation: policies['bc']='experiments/rl/2026-11-06-bc-v1/training/weights.txt'
    configurations = {c:{'critic':relative(CRITIC),'responses':[relative(p) for p in ENEMIES],
                         'depth':2,'candidates':4 if c=='search2' else 1,'budget_ms':30 if c=='search2' else 0}
                      for c in candidates}
    spec = {'purpose':'smoke' if smoke else 'confirmation' if confirmation else 'development',
            'require_new_maps':True,'stop_at':'2026-11-09T01:59:00Z','seeds':seeds,'rotate_order':True,
            'policies':policies,'policy_variants':{c:'search' for c in candidates},
            'search_configs':configurations,'pairs':[[c,o] for c in candidates for o in opponents],
            'exclude_map_hash_files':[relative(exclusions)]}
    spec_path=OUT/(name+'-spec.json');save(spec_path,spec)
    destination=OUT/name
    run([sys.executable,'code/rl/eval/panel.py','--spec',relative(spec_path),'--out',relative(destination)],name)
    contribute(destination/'map-hashes.json')
    run([sys.executable,'code/rl/eval/verify_panel.py',relative(destination),'--out',relative(OUT/(name+'-native.json'))],name+'-native')
    run([sys.executable,'code/rl/eval/verify_java_panel.py',relative(destination),'--out',relative(OUT/(name+'-java.json'))],name+'-java')
    rows=[json.loads(line) for line in (destination/'matches.jsonl').read_text().splitlines()]
    assert not any(r['own_action_errors'] or not r['valid'] or r['returncode'] for r in rows), 'Own/control technical failure'
    return rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=('pilot','screen','confirm1','confirm2','confirm3','confirm4','decision'))
    ap.add_argument('--build-attempt',type=int,choices=(1,2),default=1)
    args=ap.parse_args();check_preserved()
    if args.stage=='pilot':
        run([sys.executable,'code/rl/v4/search_teacher/build.py','--attempt',str(args.build_attempt)],'build' if args.build_attempt==1 else 'build-retry1')
        path=OUT/'diagnostic-registry.json';exclusions=registry(path)
        maps_path=prepare('diagnostic',list(range(62001,62007)),exclusions)
        run([sys.executable,'code/rl/v4/search_teacher/diagnose.py','--registry',relative(path),'--maps',relative(maps_path)],'diagnostic')
        contribute(OUT/'diagnostic/map-hashes.json')
        rows=panel('smoke',[62001],smoke=True)
        save(OUT/'pilot-decision.json',{'as_of':now(),'passed':True,'timed_games':len(rows),
             'diagnostic_sha256':sha(OUT/'diagnostic/summary.json'),'training_performed':False,'external_spend':0})
    elif args.stage=='screen':
        assert json.loads((OUT/'pilot-decision.json').read_text())['passed']
        run([sys.executable,'code/rl/v4/search_teacher/protocol_parity.py'],'protocol-parity')
        save(OUT/'candidate.json',{'as_of':now(),'label':'frozen-search2-30ms',
            'protocol_sha256':sha(OUT/'PROTOCOL.md'),
            'sources':json.loads((OUT/'build-manifest-2.json').read_text())['sources'],
            'standalone_source_sha256':sha(ROOT/'code/rl/search/bot.cpp'),
            'weights':json.loads((OUT/'diagnostic/summary.json').read_text())['weights'],
            'depth':2,'proposals':4,'temperatures':[.15,.35,.7],'budget_ms':30,
            'score':'0.5 mean + 0.5 minimum of three response-model values',
            'margin':.02,'gamma':.995,'student':False,'submission_ready':False,
            'scope':'One frozen teacher; diagnostic depths4/8 are not promoted as candidates.'})
        rows=panel('screen',list(range(62007,62019)))
        result=evaluate(rows)
        save(OUT/'screen-decision.json',dict(result,as_of=now(),status='permits_confirmation' if result['screen_passed'] else 'rejected_screen'))
        print(json.dumps(result,indent=2),flush=True)
    elif args.stage.startswith('confirm'):
        assert json.loads((OUT/'screen-decision.json').read_text())['screen_passed']
        frozen=json.loads((OUT/'confirmation-plan.json').read_text())
        assert sha(OUT/'candidate.json')==frozen['candidate_manifest_sha256']
        assert sha(OUT/'PROTOCOL.md')==json.loads((OUT/'candidate.json').read_text())['protocol_sha256']
        index=int(args.stage[-1])-1
        if index: assert (OUT/f'confirm{index}-java.json').exists(), 'Confirmation chunks must remain ordered'
        seeds=frozen['blocks'][args.stage]
        assert seeds==list(range(62019+10*index,62029+10*index))
        panel(args.stage,seeds,confirmation=True)
    else:
        frozen=json.loads((OUT/'confirmation-plan.json').read_text())
        assert sha(OUT/'candidate.json')==frozen['candidate_manifest_sha256']
        assert sha(OUT/'PROTOCOL.md')==json.loads((OUT/'candidate.json').read_text())['protocol_sha256']
        rows=[]; bindings={}
        for index in range(1,5):
            name=f'confirm{index}'
            verification=json.loads((OUT/(name+'-java.json')).read_text())
            assert verification['passed']
            path=OUT/name/'matches.jsonl'
            assert verification['panel_matches_sha256']==sha(path)
            rows += [json.loads(line) for line in path.read_text().splitlines()]
            bindings[name]=sha(path)
        result=evaluate(rows,confirmation=True)
        save(OUT/'teacher-decision.json',dict(result,as_of=now(),evidence=bindings,
             status='confirmed_teacher_not_student' if result['teacher_strength_gate_passed'] else 'not_confirmed',
             gate_source_sha256=sha(ROOT/'code/rl/v4/search_teacher/gates.py'),
             protocol_sha256=sha(OUT/'PROTOCOL.md'),confirmation_plan_sha256=sha(OUT/'confirmation-plan.json'),
             external_spend=0,training_performed=False))
        print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    main()
"""Bounded serial conditional-pilot stages under the existing exclusive lease."""
from student_common import *


def main(stage):
    teacher_guard();python='code/arena/.venv-rl/bin/python'
    freeze_path=STUDENT/'data-training-freeze.json'
    if stage=='anchor':
        files=[CODE/n for n in ('student_common.py','student_labels.py','student_train.py','student_stage.py','trace.cpp','trace_contracts.py')]
        files += [OUT/'STUDENT_PROTOCOL.md',OUT/'student-map-reservations.json',STUDENT/'trace-contracts.json',
            build_dir()/'student-trace.dylib',ROOT/'code/rl/train/bc.py',ROOT/'code/rl/export/package.py']
        save(freeze_path,{'as_of':now(),'purpose':'Before any collection or optimizer update; fixed two-round pilot',
            'identities':{rel(p):sha(p) for p in files},'teacher_freeze_sha256':sha(OUT/'freeze.json'),
            'baseline':{rel(p):sha(p) for p in [ACTOR,ACTOR.with_name('checkpoint.pt')]},
            'configuration':'STUDENT_PROTOCOL.md: two400-update CPU rounds, one seed20261108, no outcome selection'})
    frozen=json.loads(freeze_path.read_text())
    for path,digest in frozen['identities'].items():assert sha(ROOT/path)==digest,path
    if stage in ('anchor','development','current'):
        seeds=DEV if stage=='development' else TRAIN
        hashes=json.loads((OUT/'student-anchor-map-hashes.json').read_text()) if stage=='current' else prepare(stage,seeds)
        weights=STUDENT/'round1/weights.txt' if stage=='current' else ACTOR
        try:collect(stage,seeds,stage,weights,hashes)
        finally:
            if (STUDENT/stage/'matches.jsonl').exists():run([python,'-B',rel(CODE/'verify.py'),'student/'+stage],'student-'+stage+'-verify')
        run([python,'-B',rel(CODE/'student_labels.py'),stage],'student-'+stage+'-labels')
    elif stage in ('train1','train2'):
        run([python,'-B',rel(CODE/'student_train.py'),stage[-1]],'student-'+stage)
    else:raise ValueError(stage)


if __name__=='__main__':main(sys.argv[1])
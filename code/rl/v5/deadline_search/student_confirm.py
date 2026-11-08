"""One frozen package and fixed 1680-game independent three-way comparison."""
from student_analyze import *


def freeze():
    teacher_guard()
    for name in ('package-parity','collection-package-parity','native-logit-parity'):
        assert json.loads((STUDENT/(name+'.json')).read_text())['passed']
    run(['code/arena/.venv-rl/bin/python','-B',rel(CODE/'test_student_analyze.py')],'student-analyzer-tests')
    identities=sources()
    for path in [OUT/'STUDENT_PROTOCOL.md',STUDENT/'selection.json',STUDENT/'data-training-freeze.json',
        STUDENT/'package/bot.cpp',STUDENT/'package/package.json',STUDENT/'build/verify-package/packaged',
        STUDENT/'collection-package-parity.json',STUDENT/'native-logit-parity.json',STUDENT/'package-parity.json']:
        identities[rel(path)]=sha(path)
    selected=json.loads((STUDENT/'selection.json').read_text());weights=ROOT/selected['weights_path']
    identities[rel(weights)]=sha(weights);identities[rel(weights.with_name('checkpoint.pt'))]=sha(weights.with_name('checkpoint.pt'))
    save(STUDENT/'freeze.json',{'as_of':now(),'identities':identities,'schedule':schedule(),'expected_games':1680,
        'teacher_freeze_sha256':sha(OUT/'freeze.json'),'selected_round':selected['round'],
        'sample_extension_allowed':False,'interim_strength_selection':False,'closed_global_finals':True})


def confirm(number):
    teacher_guard();frozen=json.loads((STUDENT/'freeze.json').read_text())
    for path,digest in frozen['identities'].items():assert sha(ROOT/path)==digest,path
    assert frozen['schedule']==schedule();assert 1<=number<=4
    name='confirm'+str(number);seeds=CONFIRM[(number-1)*10:number*10];hashes=prepare(name,seeds)
    commands=original_panel.commands();commands['teacher']=commands['search'];commands['student']=[rel(STUDENT/'build/verify-package/packaged')]
    original_panel.commands=lambda:commands
    entries=[r for r in frozen['schedule'] if r['seed'] in seeds]
    try:original_panel.panel('student/'+name,entries,hashes,'independent_compact_student_confirmation')
    finally:
        if (STUDENT/name/'matches.jsonl').exists():
            run(['code/arena/.venv-rl/bin/python','-B',rel(CODE/'verify.py'),'student/'+name],'student-'+name+'-verify')


if __name__=='__main__':
    if sys.argv[1]=='freeze':freeze()
    else:confirm(int(sys.argv[1]))
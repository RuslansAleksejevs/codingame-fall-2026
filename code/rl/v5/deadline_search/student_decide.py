"""Close the original fixed series; rejection never launches another trial."""
from student_common import *


def main():
    teacher_guard();frozen=json.loads((STUDENT/'freeze.json').read_text())
    for p,h in frozen['identities'].items():assert sha(ROOT/p)==h,p
    assert json.loads((STUDENT/'label-integrity-audit.json').read_text())['passed']
    python='code/arena/.venv-rl/bin/python'
    run([python,'-B',rel(CODE/'student_analyze.py')],'student-analysis')
    run([python,'-B',rel(CODE/'student_audit.py')],'student-raw-audit')
    decision=json.loads((STUDENT/'decision.json').read_text());audit=json.loads((STUDENT/'raw-audit.json').read_text())
    print(json.dumps({'decision':decision['decision'],'raw_integrity':audit['integrity_passed'],
        'student_admitted':audit['student_admitted'],'external_gain':decision['all_games']['external_gain'],
        'direct_league3m':decision['all_games']['direct_league3m'],
        'external_student_minus_teacher':decision['all_games']['external_student_minus_teacher']},indent=2),flush=True)


if __name__=='__main__':main()
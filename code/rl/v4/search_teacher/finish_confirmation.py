"""Last finite lease: final ten maps, full40 gate, and complete technical audit."""
import json
import sys
from common import OUT, relative
from run_stage import run


def main():
    assert json.loads((OUT/'confirm3-java.json').read_text())['passed']
    for stage in ('confirm4','decision'):
        run([sys.executable,'code/rl/v4/search_teacher/run_stage.py',stage],'final-'+stage)
    run([sys.executable,'code/rl/v4/search_teacher/audit.py','--out',relative(OUT/'teacher-audit.json')],'teacher-audit')
    result=json.loads((OUT/'teacher-decision.json').read_text())
    print(json.dumps({key:result[key] for key in ('status','maps','games','external_gain_pp',
        'external_gain_paired_95_pp','direct_score_percent','direct_score_95_percent',
        'teacher_strength_gate_passed')},indent=2),flush=True)


if __name__=='__main__':main()
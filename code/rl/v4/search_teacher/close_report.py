"""Close the fixed rejected series with unchanged analysis; never run a game."""
import json
import sys
from common import OUT, ROOT, check_preserved, relative, sha
from run_stage import run
from technical_errors import REJECTION_SHA


def main():
    check_preserved()
    assert sha(OUT / 'technical-rejection.json') == REJECTION_SHA
    rejection = json.loads((OUT / 'technical-rejection.json').read_text())
    assert sha(ROOT / 'code/rl/v4/search_teacher/gates.py') == rejection['gate_source_sha256']
    for index in range(1, 5):
        path = OUT / f'confirm{index}/matches.jsonl'
        assert len(path.read_text().splitlines()) == 240
        verification = json.loads((OUT / f'confirm{index}-java.json').read_text())
        assert verification['passed'] and not verification['mismatches']
        assert verification['panel_matches_sha256'] == sha(path)
    scripts = [
        ('run_stage.py', ['decision'], 'teacher-decision'),
        ('audit.py', ['--out', relative(OUT / 'teacher-audit.json')], 'teacher-audit'),
        ('technical_errors.py', [], 'technical-errors'),
        ('test_gates.py', [], 'closing-gate-tests'),
        ('test_technical_errors.py', [], 'closing-technical-tests'),
    ]
    for script, args, log in scripts:
        run([sys.executable, '-B', 'code/rl/v4/search_teacher/' + script, *args], log)
    decision = json.loads((OUT / 'teacher-decision.json').read_text())
    assert not decision['teacher_strength_gate_passed']
    assert decision['own_or_control_error_games'] >= 3
    print(json.dumps({key: decision[key] for key in (
        'status', 'games', 'maps', 'external_gain_pp', 'external_gain_paired_95_pp',
        'complete_composite_maps', 'direct_score_percent', 'direct_score_95_percent',
        'own_or_control_error_games', 'teacher_strength_gate_passed')}, indent=2))


if __name__ == '__main__':
    main()
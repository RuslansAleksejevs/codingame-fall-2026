"""Read preserved failures, including late stderr omitted from accepted-turn rows."""
import gzip
import json
import re
from common import OUT, ROOT, check_preserved, now, relative, save, sha


REJECTION_SHA = 'e1e39277d82f88ae6092f2d0187d4c30c1c7313a4d891ce943c688cc83f62c0d'


def inspect_failure(directory, row):
    name = f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}.json.gz'
    path = directory / name
    game = json.loads(gzip.decompress(path.read_bytes()))
    failed_sides = []
    for side, errors in ((row['seat'], row['own_action_errors']),
                         (1-row['seat'], row['opponent_action_errors'])):
        if not errors:
            continue
        logs = []
        outputs = game['outputs'][str(side)]
        for frame, text in enumerate(game['errors'][str(side)]):
            if not text:
                continue
            for line in text.splitlines():
                if not line.startswith('turn=') or 'plan_us=' not in line:
                    continue
                match = re.search(r'turn=(\d+).*plan_us=(\d+)', line)
                assert match, line
                logs.append({'frame': frame, 'reported_turn': int(match[1]),
                             'internal_plan_us': int(match[2]),
                             'same_frame_output_recorded': bool(outputs[frame]) if frame < len(outputs) else False,
                             'stderr': text})
        failed_sides.append({'absolute_side': side, 'is_own': side == row['seat'],
                             'errors': errors, 'last_internal_log': logs[-1] if logs else None,
                             'max_logged_internal_plan_us': max((v['internal_plan_us'] for v in logs), default=None)})
    return {'stage': directory.name, **{k: row[k] for k in (
        'candidate', 'opponent', 'seed', 'seat', 'outcome', 'score', 'opponent_score',
        'returncode', 'valid', 'own_action_errors', 'opponent_action_errors')},
        'source': relative(path), 'sha256': sha(path), 'failed_sides': failed_sides,
        'own_accepted_turn_plan_us_max': max(row['own_plan_us'], default=None),
        'referee_tooltips': game['tooltips'], 'last_referee_summaries': game['summaries'][-2:]}


def main():
    check_preserved()
    assert sha(OUT / 'technical-rejection.json') == REJECTION_SHA
    decision = json.loads((OUT / 'teacher-decision.json').read_text())
    assert decision['maps'] == 40 and decision['games'] == 960
    assert not decision['teacher_strength_gate_passed']
    rejection = json.loads((OUT / 'technical-rejection.json').read_text())
    assert sha(ROOT / 'code/rl/v4/search_teacher/gates.py') == rejection['gate_source_sha256']
    assert sha(OUT / 'confirm3/matches.jsonl') == rejection['confirm3_matches_sha256']
    failures = []
    completed_rows = 0
    stage_evidence = {}
    for index in range(1, 5):
        directory = OUT / f'confirm{index}'
        rows = [json.loads(line) for line in (directory / 'matches.jsonl').read_text().splitlines()]
        assert len(rows) == 240
        completed_rows += len(rows)
        native = json.loads((OUT / f'confirm{index}-native.json').read_text())
        java = json.loads((OUT / f'confirm{index}-java.json').read_text())
        assert not native['native_replay_mismatches'] and not java['mismatches']
        assert java['panel_matches_sha256'] == native['panel_matches_sha256'] == sha(directory / 'matches.jsonl')
        stage_evidence[directory.name] = {'games': len(rows), 'replayed_clean_games': java['clean_games_replayed'],
            'clean_subset_java_passed': java['passed'], 'technical_exclusions': java['technical_records_excluded'],
            'whole_panel_technical_pass': not any(r['own_action_errors'] or r['opponent_action_errors'] or
                not r['valid'] or r['returncode'] for r in rows),
            'matches_sha256': sha(directory / 'matches.jsonl')}
        failures.extend(inspect_failure(directory, row) for row in rows if row['own_action_errors'] or
                        row['opponent_action_errors'] or not row['valid'] or row['returncode'])
    own = sum(bool(r['own_action_errors']) for r in failures)
    assert own >= 3
    ledger = [json.loads(line) for line in (ROOT / '.context/rl4-compute/events.jsonl').read_text().splitlines()]
    runs = []
    active = None
    for entry in ledger:
        if entry['owner'] != 'search-teacher':
            continue
        if entry['event'] == 'started':
            active = entry
        elif entry['event'] == 'finished':
            assert active is not None
            runs.append({'start': active, 'finish': entry})
            active = None
    confirm3 = [r for r in runs if r['start']['command'][-1] == 'confirm3']
    assert len(confirm3) == 1 and confirm3[0]['finish']['exit_code'] == 1
    result = {'as_of': now(), 'classification': 'PROJECT_REPORTED',
        'status': 'technically_rejected_complete_descriptive_confirmation',
        'extraction_command': 'code/arena/.venv-rl/bin/python -B code/rl/v4/search_teacher/technical_errors.py',
        'extraction_source_sha256': sha(ROOT / 'code/rl/v4/search_teacher/technical_errors.py'),
        'technical_rejection_sha256': REJECTION_SHA, 'teacher_decision_sha256': sha(OUT / 'teacher-decision.json'),
        'games': completed_rows, 'own_error_games': own,
        'opponent_error_games': sum(bool(r['opponent_action_errors']) for r in failures),
        'stages': stage_evidence, 'technical_records': failures, 'completed_compute_leases': runs,
        'completed_compute_seconds_before_this_report': sum(r['finish']['seconds'] for r in runs),
        'active_lease_at_report': active,
        'interpretation': [
            'Raw stderr can retain a late planning log for a timed-out turn absent from accepted-turn own_plan_us.',
            'A logged internal duration is not the full referee deadline interval, which also includes input and output.',
            'Search checks its budget between expensive operations; the source does not enforce a hard per-turn deadline.',
            'Timeouts remain technical failures; no host fault or counterfactual game outcome is inferred.',
            'Clean-paired strategic intervals exclude whole affected opponent-map clusters under the original protocol, while every technical record remains visible.',
        ],
        'teacher_strength_gate_passed': False, 'teacher_labels': 0, 'student_training_performed': False,
        'global_final_opened': False, 'external_spend': 0}
    save(OUT / 'technical-errors.json', result)
    print(json.dumps({'status': result['status'], 'games': completed_rows, 'technical_records': len(failures),
                      'own_error_games': own, 'teacher_strength_gate_passed': False}, indent=2))


if __name__ == '__main__':
    main()
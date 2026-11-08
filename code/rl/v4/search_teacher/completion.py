"""Small final inventory after archive lease release; no games or mutation of evidence."""
from datetime import datetime, timezone
import json
from common import OUT, ROOT, STOP, check_preserved, now, relative, save, sha
from technical_errors import REJECTION_SHA


def main():
    preserved = check_preserved()
    manifest = json.loads((OUT / 'evidence-manifest.json').read_text())
    assert manifest['roundtrip_verified']
    assert sha(ROOT / manifest['archive']) == manifest['sha256']
    decision = json.loads((OUT / 'teacher-decision.json').read_text())
    assert decision['games'] == 960 and not decision['teacher_strength_gate_passed']
    assert sha(OUT / 'technical-rejection.json') == REJECTION_SHA
    ledger = [json.loads(line) for line in (ROOT / '.context/rl4-compute/events.jsonl').read_text().splitlines()]
    owned = [entry for entry in ledger if entry['owner'] == 'search-teacher']
    assert owned[-1]['event'] == 'finished' and owned[-1]['exit_code'] == 0
    assert sum(entry['event'] == 'started' for entry in owned) == sum(entry['event'] == 'finished' for entry in owned)
    seconds = sum(entry['seconds'] for entry in owned if entry['event'] == 'finished')
    stamp = datetime.now(timezone.utc)
    bindings = {name: sha(OUT / name) for name in (
        'REPORT.md', 'STATUS.md', 'HISTORY.md', 'PROTOCOL.md', 'candidate.json',
        'confirmation-plan.json', 'technical-rejection.json', 'teacher-decision.json',
        'teacher-audit.json', 'technical-errors.json', 'evidence-manifest.json',
        'closing-gate-tests.log', 'closing-technical-tests.log')}
    archived = {entry['path']: entry for entry in manifest['entries']}
    for name, digest in bindings.items():
        if name == 'evidence-manifest.json':
            continue
        assert archived[relative(OUT / name)]['original_sha256'] == digest
    result = {'as_of': now(), 'classification': 'PROJECT_REPORTED',
        'status': 'completed_rejected_no_deployable_candidate', 'teacher_strength_gate_passed': False,
        'candidate_manifest_sha256': sha(OUT / 'candidate.json'), 'bindings_sha256': bindings,
        'archive': {key: manifest[key] for key in ('archive', 'sha256', 'files', 'roundtrip_verified', 'normalized_invocations')},
        'external_gain_pp': decision['external_gain_pp'], 'external_gain_paired_95_pp': decision['external_gain_paired_95_pp'],
        'direct_score_percent': decision['direct_score_percent'], 'direct_score_95_percent': decision['direct_score_95_percent'],
        'total_timed_games': 1156, 'confirmation_maps': 40, 'confirmation_games': 960,
        'confirmation_clean_raw_games': 956, 'confirmation_complete_paired_game_records': 944,
        'own_timeout_games': 3, 'opponent_timeout_games': 1, 'pure_tests_passed': 13,
        'teacher_labels': 0, 'student_training_performed': False, 'submission_ready': False,
        'preserved': preserved, 'global_final_opened': False, 'external_spend': 0,
        'completed_heavy_seconds': seconds, 'remaining_lane_budget_seconds': 4*3600-seconds,
        'archive_lease_seconds': owned[-1]['seconds'], 'active_compute_leases': 0,
        'pending_branch_continuations': 0,
        'continuation_basis': 'Every branch-scheduled check was cancelled or delivered; no new schedule was created after confirmation.',
        'research_hard_stop': STOP.isoformat(), 'seconds_until_research_stop': (STOP-stamp).total_seconds(),
        'official_deadline': '2026-11-09T09:00:00Z',
        'seconds_until_official_deadline': (datetime(2026, 11, 9, 9, tzinfo=timezone.utc)-stamp).total_seconds(),
        'next_step': 'Integrate isolated code/docs and negative evidence only. Do not deploy teacher, generate labels, train a student, reopen global final or alter active platform/fallback.'}
    save(OUT / 'COMPLETION.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
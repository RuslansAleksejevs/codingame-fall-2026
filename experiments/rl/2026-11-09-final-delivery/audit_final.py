#!/usr/bin/env python3
"""Full final audit with explicit concurrent leaderboard-rank discrepancy.

No API, replay, bot edit or altered raw response. The preserved generic auditor
requires identical ordinal ranks from separate endpoints. Here both reads are
100%/same score/identity, but ranks differ by one. Record that disagreement;
verify completion and immutable identity separately, without polling for a
preferred rank or changing any scientific acceptance gate.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from audit import HERE, ROOT, CHOICE, LIVE, audit, telemetry, digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    output = args.out.resolve()
    assert output.is_relative_to(HERE) and not output.exists()
    # Reuse all source/history/battle/result-position checks. Final reads below
    # independently supersede the initial source/history used by this function.
    result = audit(HERE, "final-confirmed", False)
    assert result["ranking_complete"] and result["complete_snapshot_audit"]
    assert not result["missing_logs"] and not result["pending_battles"] and result["games"]

    def read(name):
        path = HERE / name
        result["proof_files"][str(path.relative_to(ROOT))] = digest(path)
        return json.loads(path.read_text())

    request = read("submission-request.json")
    sid = result["submission_id"]
    accepted = read("accepted-source-final.json")
    assert accepted["submission_id"] == sid and accepted.get("current")
    assert accepted["language"] == "C++"
    assert hashlib.sha256(accepted["code"].encode()).hexdigest() == request["source_sha256"]
    assert result["source_sha256"] == request["source_sha256"] == digest(ROOT / request["code_file"])
    old = read("submissions-before.json")["submissions"]
    history = read("submissions-final.json")["submissions"]
    old_ids = {row["submission_id"] for row in old}
    ids = {row["submission_id"] for row in history}
    assert len(ids) == len(history) and len(old_ids) == len(old)
    assert ids == old_ids | {sid} and sid not in old_ids
    assert [row["submission_id"] for row in history if row.get("current")] == [sid]
    progress = read("progress-final-confirmed.json")
    leaderboard = read("leaderboard-final-confirmed.json")
    own = leaderboard["me"]
    assert progress["percentage"] == own["percentage"] == 100
    assert progress["in_progress"] is False
    assert leaderboard["total"] == progress["total"]
    assert all(own[key] == progress[key] for key in ("league", "score", "language"))
    assert {agent["agent_id"] for game in result["games"] for agent in game["agents"]
            if agent.get("me")} == {own["agent_id"]}
    assert all(isinstance(rank, int) and 1 <= rank <= progress["total"]
               for rank in (progress["rank"], own["rank"]))
    initial_progress = read("progress-final.json")
    initial_leaderboard = read("leaderboard-final.json")
    result["leaderboard_check"] = {
        "agent_id": own["agent_id"], "identity_score_league_completion_total_match": True,
        "rank_exactly_matches": progress["rank"] == own["rank"],
        "progress_rank": progress["rank"], "leaderboard_rank": own["rank"],
        "leaderboard_minus_progress_rank": own["rank"] - progress["rank"],
        "initial_progress_rank": initial_progress["rank"],
        "initial_leaderboard_rank": initial_leaderboard["me"]["rank"],
        "caveat": "Separate live endpoint reads differ; exact ordinal-rank equality is NOT claimed. All raw responses retained."}
    result["identity_and_snapshot_consistency_verified"] = result["leaderboard_check"]["rank_exactly_matches"]
    result["source_history_battle_identity_and_completion_verified"] = True
    result["final_source_current_verified"] = True
    result["d16"] = telemetry(result["games"])
    result["own_execution_clean"] = not any(result[key] for key in
        ("own_error_games", "own_warning_games", "global_failure_games")) and result["d16"]["passed"]
    strict_clean, opponent_warnings = [], []
    for game in result["games"]:
        warnings = [seat for seat in game["seats"].values() if not seat["own"] and seat["warnings"]]
        if warnings:
            opponent_warnings.append(game["game_id"])
        if not warnings and not any(game[key] for key in
                ("own_errors", "own_warnings", "opponent_errors", "global_errors", "fail_cause")):
            strict_clean.append(game)
    result["opponent_warning_game_ids"] = opponent_warnings
    result["strict_clean_outcomes_including_opponent_warnings"] = dict(Counter(game["outcome"] for game in strict_clean))
    result["caveats"].append("Complete audit means all90 final-confirmed snapshot logs, not future passive games or final contest standings")
    result["as_of"] = datetime.now(timezone.utc).isoformat()
    for path in (Path(__file__), HERE / "audit.py", CHOICE / "audit_d16_telemetry.py", LIVE / "audit_tests.py"):
        result["proof_files"][str(path.relative_to(ROOT))] = digest(path)
    with output.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    summary = {key: value for key, value in result.items() if key not in
               ("games", "proof_files", "before_progress", "d16")}
    summary["d16"] = {key: value for key, value in result["d16"].items() if key != "games"}
    print(json.dumps(summary, indent=2))
    return int(not result["own_execution_clean"])


if __name__ == "__main__":
    raise SystemExit(main())
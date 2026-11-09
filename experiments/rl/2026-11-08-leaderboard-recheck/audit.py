#!/usr/bin/env python3
"""Audit this single selected submission from saved official responses only."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "code/platform"))
from analyze_v3_tests import analyze, sha


def read(name):
    return json.loads((HERE / name).read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    request = read("submission-request.json")
    response = read("submission-response.json")
    accepted_name = "accepted-source-final.json" if args.require_complete else "accepted-source.json"
    accepted = read(accepted_name)
    sid = response["submission_id"]
    assert sid == accepted["submission_id"]
    source_sha = hashlib.sha256(accepted["code"].encode()).hexdigest()
    assert source_sha == request["source_sha256"] == sha(ROOT / request["code_file"])
    before_source = read("previous-source.json")
    assert before_source["submission_id"] == request["previous_submission_id"]
    assert hashlib.sha256(before_source["code"].encode()).hexdigest() == request["previous_source_sha256"]
    progress_name = f"progress-{args.snapshot}.json"
    progress = read(progress_name)
    assert progress["submission_id"] == sid
    page = read(f"battles-{args.snapshot}.json")
    assert page["submission_id"] == sid
    # This run has fewer than 100 battles. Refuse silent pagination truncation.
    assert not page.get("next_before"), "Additional battle pages must be saved and supported explicitly"
    records = page["battles"]
    assert len({row["game_id"] for row in records}) == len(records)
    pending, missing, games, expected = [], [], [], Counter()
    for battle in records:
        gid = battle["game_id"]
        if not battle.get("done"):
            pending.append(gid)
            continue
        mine = [p for p in battle["players"] if p.get("me")]
        other = [p for p in battle["players"] if not p.get("me")]
        assert len(mine) == 1 and len(other) == 1
        outcome = ("win" if mine[0]["position"] < other[0]["position"] else
                   "draw" if mine[0]["position"] == other[0]["position"] else "loss")
        expected[outcome] += 1
        path = HERE / "games" / f"{gid}.json"
        if not path.exists():
            missing.append(gid)
            continue
        item = analyze(path)
        assert item["game_id"] == gid and item["status"] == "done"
        assert item["outcome"] == outcome
        assert [a["agent_id"] for a in item["agents"] if a.get("me")] == [mine[0]["agent_id"]]
        assert sorted(a["agent_id"] for a in item["agents"] if not a.get("me")) == [other[0]["agent_id"]]
        games.append(item)
    old = read("submissions-before.json")["submissions"]
    history_name = "submissions-final.json" if args.require_complete else "submissions-after.json"
    new = read(history_name)["submissions"]
    old_ids, new_ids = {s["submission_id"] for s in old}, {s["submission_id"] for s in new}
    assert new_ids - old_ids == {sid} and old_ids <= new_ids
    assert [s["submission_id"] for s in new if s.get("current")] == [sid]
    complete = progress.get("percentage") == 100 and progress.get("in_progress") is False
    leaderboard_check = None
    if args.require_complete:
        assert complete and not missing and not pending
        leaderboard = read("leaderboard-final.json")
        own = leaderboard["me"]
        assert own["percentage"] == 100 and leaderboard["total"] == progress["total"]
        assert all(own[k] == progress[k] for k in ("rank", "league", "score"))
        assert {a["agent_id"] for g in games for a in g["agents"] if a.get("me")} == {own["agent_id"]}
        leaderboard_check = {"matches_progress": True, "rank": own["rank"],
                             "total": leaderboard["total"], "agent_id": own["agent_id"]}
    clean = [g for g in games if not any(g[k] for k in
             ("own_errors", "own_warnings", "opponent_errors", "global_errors", "fail_cause"))]
    timing = [s["planning_us_max"] for g in games for s in g["seats"].values()
              if s["own"] and s["planning_us_max"] is not None]
    proof_paths = [Path(__file__), ROOT / "code/platform/analyze_v3_tests.py",
                   HERE / progress_name, HERE / f"battles-{args.snapshot}.json",
                   HERE / history_name, HERE / "submission-request.json", HERE / accepted_name]
    if args.require_complete:
        proof_paths.append(HERE / "leaderboard-final.json")
    result = {
        "as_of": datetime.now(timezone.utc).isoformat(), "provenance": "PROJECT_REPORTED",
        "source": "Saved official CodinGame API responses; no new matches",
        "submission_id": sid, "source_sha256": source_sha,
        "exactly_one_new_submission": True, "old_submission_history_preserved": True,
        "ranking_complete": complete,
        "leaderboard_check": leaderboard_check,
        "progress": {k: progress.get(k) for k in ("percentage", "in_progress", "rank", "total",
                     "league", "league_rank", "league_total", "score", "eligible_for_promotion")},
        "before_progress": read("progress-before.json"),
        "snapshot_battles": len(records), "completed_battles": sum(expected.values()),
        "pending_battles": pending, "missing_logs": missing,
        "snapshot_outcomes": dict(expected), "audited_battles": len(games),
        "own_error_games": sum(bool(g["own_errors"]) for g in games),
        "own_warning_games": sum(bool(g["own_warnings"]) for g in games),
        "opponent_error_games": sum(bool(g["opponent_errors"]) for g in games),
        "global_failure_games": sum(bool(g["global_errors"] or g["fail_cause"]) for g in games),
        "clean_outcomes": dict(Counter(g["outcome"] for g in clean)),
        "own_turn_outputs": sum(s["turns"] for g in games for s in g["seats"].values() if s["own"]),
        "internal_planning_us_max": max(timing, default=None),
        "technical_test": analyze(HERE / "test-result.json"),
        "proof_files": {str(p.relative_to(ROOT)): sha(p) for p in proof_paths},
        "caveats": ["Ongoing-contest snapshot, not final contest standing",
                    "Before/after ranks are not a paired causal comparison",
                    "Internal planning time is not total platform CPU time"],
        "games": games,
    }
    destination = args.out.resolve()
    assert destination.is_relative_to(HERE)
    with destination.open("x") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in
                    ("games", "before_progress", "proof_files", "technical_test")}, indent=2))


if __name__ == "__main__":
    main()
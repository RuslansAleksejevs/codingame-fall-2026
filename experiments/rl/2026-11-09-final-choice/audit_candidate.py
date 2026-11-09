#!/usr/bin/env python3
"""Audit saved ranked-candidate evidence, never submit or replay a game.

Adapted from the preserved 8 November league3m audit; supports pagination and
does not invent a new technical test when compatibility evidence was reused.
"""
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


def audit(directory, snapshot, require_complete):
    proof = [Path(__file__), ROOT / "code/platform/analyze_v3_tests.py"]

    def read(name):
        path = directory / name
        proof.append(path)
        return json.loads(path.read_text())

    request = read("submission-request.json")
    response = read("submission-response.json")
    sid = response["submission_id"]
    accepted = read("accepted-source-final.json" if require_complete else "accepted-source.json")
    assert accepted["submission_id"] == sid and accepted.get("current")
    source_sha = hashlib.sha256(accepted["code"].encode()).hexdigest()
    source_path = ROOT / request["code_file"]
    assert source_sha == request["source_sha256"] == sha(source_path)
    proof.append(source_path)
    previous = read(request.get("previous_source_file", "previous-source.json"))
    assert previous["submission_id"] == request["previous_submission_id"]
    assert hashlib.sha256(previous["code"].encode()).hexdigest() == request["previous_source_sha256"]
    before = read(request.get("before_progress_file", "progress-before.json"))
    assert before["submission_id"] == previous["submission_id"]
    progress = read(f"progress-{snapshot}.json")
    assert progress["submission_id"] == sid
    history = read("submissions-final.json" if require_complete else "submissions-after.json")["submissions"]
    old_history = read(request.get("previous_history_file", "submissions-before.json"))["submissions"]
    old_ids, new_ids = {r["submission_id"] for r in old_history}, {r["submission_id"] for r in history}
    assert len(new_ids) == len(history) and len(old_ids) == len(old_history)
    assert old_ids <= new_ids and new_ids - old_ids == {sid}
    assert [r["submission_id"] for r in history if r.get("current")] == [sid]
    records, page_number = [], 1
    while True:
        suffix = "" if page_number == 1 else f"-page{page_number:02d}"
        page = read(f"battles-{snapshot}{suffix}.json")
        assert page["submission_id"] == sid
        records.extend(page["battles"])
        if not page.get("next_before"):
            break
        page_number += 1
        assert page_number <= 20
    assert len({row["game_id"] for row in records}) == len(records)
    games, missing, pending, outcomes = [], [], [], Counter()
    for row in records:
        gid = row["game_id"]
        if not row.get("done"):
            pending.append(gid)
            continue
        own = [p for p in row["players"] if p.get("me")]
        other = [p for p in row["players"] if not p.get("me")]
        assert len(own) == len(other) == 1
        outcome = "win" if own[0]["position"] < other[0]["position"] else "draw" if own[0]["position"] == other[0]["position"] else "loss"
        outcomes[outcome] += 1
        path = directory / "games" / f"{gid}.json"
        if not path.exists():
            missing.append(gid)
            continue
        game = analyze(path)
        assert game["game_id"] == gid and game["status"] == "done" and game["outcome"] == outcome
        assert [a["agent_id"] for a in game["agents"] if a.get("me")] == [own[0]["agent_id"]]
        assert [a["agent_id"] for a in game["agents"] if not a.get("me")] == [other[0]["agent_id"]]
        positions = {p["agent_id"]: p["position"] for p in row["players"]}
        assert all(game["ranking"][a["index"]] == positions[a["agent_id"]] for a in game["agents"])
        games.append(game)
    ranking_complete = progress.get("percentage") == 100 and progress.get("in_progress") is False
    leaderboard_check = None
    if require_complete:
        assert ranking_complete and not pending and not missing and games
        leaderboard = read("leaderboard-final.json")
        own = leaderboard["me"]
        assert own["percentage"] == 100 and leaderboard["total"] == progress["total"]
        assert all(own[key] == progress[key] for key in ("rank", "league", "score"))
        assert {a["agent_id"] for g in games for a in g["agents"] if a.get("me")} == {own["agent_id"]}
        leaderboard_check = {"matches_progress": True, "agent_id": own["agent_id"]}
    clean = [g for g in games if not any(g[k] for k in
             ("own_errors", "own_warnings", "opponent_errors", "global_errors", "fail_cause"))]
    timing = [s["planning_us_max"] for g in games for s in g["seats"].values()
              if s["own"] and s["planning_us_max"] is not None]
    return {"as_of": datetime.now(timezone.utc).isoformat(), "provenance": "PROJECT_REPORTED",
            "submission_id": sid, "source_sha256": source_sha,
            "identity_and_snapshot_consistency_verified": True,
            "exactly_one_new_submission": True, "old_submission_history_preserved": True,
            "ranking_complete": ranking_complete,
            "complete_snapshot_audit": ranking_complete and not missing and not pending,
            "leaderboard_check": leaderboard_check,
            "progress": {k: progress.get(k) for k in ("percentage", "in_progress", "rank", "total",
                         "league", "league_rank", "league_total", "score")},
            "before_progress": before, "snapshot_battles": len(records),
            "completed_battles": sum(outcomes.values()), "audited_battles": len(games),
            "missing_logs": missing, "pending_battles": pending,
            "snapshot_outcomes": dict(outcomes), "clean_outcomes": dict(Counter(g["outcome"] for g in clean)),
            "own_error_games": sum(bool(g["own_errors"]) for g in games),
            "own_warning_games": sum(bool(g["own_warnings"]) for g in games),
            "opponent_error_games": sum(bool(g["opponent_errors"]) for g in games),
            "global_failure_games": sum(bool(g["global_errors"] or g["fail_cause"]) for g in games),
            "all_audited_games_technically_clean": len(clean) == len(games),
            "own_turn_outputs": sum(s["turns"] for g in games for s in g["seats"].values() if s["own"]),
            "internal_planning_us_max": max(timing, default=None),
            "proof_files": {str(path.relative_to(ROOT)): sha(path) for path in proof}, "games": games,
            "caveats": ["Frozen ongoing-contest snapshot, not final contest standing or future passive matches",
                        "Sequential ranks and win rates are unpaired and use different opponents/maps",
                        "Internal planning time is not official whole-turn CPU",
                        "Audit consistency does not assert technical cleanliness; inspect the separate error counts"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=HERE / "league3m")
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    directory, output = args.directory.resolve(), args.out.resolve()
    assert directory.is_relative_to(ROOT / "experiments") and output.is_relative_to(HERE)
    result = audit(directory, args.snapshot, args.require_complete)
    with output.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("games", "proof_files", "before_progress")}, indent=2))


if __name__ == "__main__":
    main()
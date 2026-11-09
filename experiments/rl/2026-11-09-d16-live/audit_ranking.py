#!/usr/bin/env python3
"""Audit one D16 submission from saved responses; no platform writes or reruns."""
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
from audit_tests import d16_telemetry


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
    sid = response["submission_id"]
    accepted_name = "accepted-source-final.json" if args.require_complete else "accepted-source.json"
    accepted = read(accepted_name)
    assert sid == accepted["submission_id"] and accepted.get("current")
    source_sha = hashlib.sha256(accepted["code"].encode()).hexdigest()
    assert source_sha == request["source_sha256"] == sha(ROOT / request["code_file"])
    previous_name = request.get("previous_source_file", "previous-source.json")
    previous = read(previous_name)
    assert previous["submission_id"] == request["previous_submission_id"]
    assert hashlib.sha256(previous["code"].encode()).hexdigest() == request["previous_source_sha256"]
    progress_name = f"progress-{args.snapshot}.json"
    progress = read(progress_name)
    assert progress["submission_id"] == sid
    pages, rows, page_index = [], [], 1
    page_name = f"battles-{args.snapshot}.json"
    while True:
        page = read(page_name)
        assert page["submission_id"] == sid
        pages.append(page_name)
        rows.extend(page["battles"])
        if not page.get("next_before"):
            break
        page_index += 1
        assert page_index <= 20, "Unexpected pagination; inspect the saved snapshot"
        page_name = f"battles-{args.snapshot}-page{page_index:02d}.json"
        assert (HERE / page_name).exists(), f"Missing next page: before={page['next_before']}"
    assert len({row["game_id"] for row in rows}) == len(rows), "Duplicate battle pages"
    pending, missing, games, outcomes = [], [], [], Counter()
    for battle in rows:
        gid = battle["game_id"]
        if not battle.get("done"):
            pending.append(gid)
            continue
        own = [player for player in battle["players"] if player.get("me")]
        other = [player for player in battle["players"] if not player.get("me")]
        assert len(own) == len(other) == 1
        outcome = "win" if own[0]["position"] < other[0]["position"] else "draw" if own[0]["position"] == other[0]["position"] else "loss"
        outcomes[outcome] += 1
        path = HERE / "games" / f"{gid}.json"
        if not path.exists():
            missing.append(gid)
            continue
        item = analyze(path)
        assert item["game_id"] == gid and item["status"] == "done" and item["outcome"] == outcome
        assert [a["agent_id"] for a in item["agents"] if a.get("me")] == [own[0]["agent_id"]]
        assert [a["agent_id"] for a in item["agents"] if not a.get("me")] == [other[0]["agent_id"]]
        raw = json.loads(path.read_text())
        item["d16"] = d16_telemetry(raw.get("log", raw))
        games.append(item)
    previous_history_name = request.get("previous_history_file", "submissions-before.json")
    old = read(previous_history_name)["submissions"]
    history_name = "submissions-final.json" if args.require_complete else "submissions-after.json"
    new = read(history_name)["submissions"]
    old_ids, new_ids = {row["submission_id"] for row in old}, {row["submission_id"] for row in new}
    assert new_ids - old_ids == {sid} and old_ids <= new_ids
    assert [row["submission_id"] for row in new if row.get("current")] == [sid]
    complete = progress.get("percentage") == 100 and progress.get("in_progress") is False
    leaderboard_check = None
    if args.require_complete:
        assert complete and not pending and not missing
        leaderboard = read("leaderboard-final.json")
        me = leaderboard["me"]
        assert me["percentage"] == 100 and leaderboard["total"] == progress["total"]
        assert all(me[key] == progress[key] for key in ("rank", "league", "score"))
        assert {a["agent_id"] for game in games for a in game["agents"] if a.get("me")} == {me["agent_id"]}
        leaderboard_check = {"matches_progress": True, "rank": me["rank"], "agent_id": me["agent_id"]}
    clean = [game for game in games if not any(game[key] for key in
             ("own_errors", "own_warnings", "opponent_errors", "global_errors", "fail_cause"))]
    telemetry = [seat for game in games for seat in game["d16"]["seats"].values()]
    proof_names = [progress_name, accepted_name, history_name, previous_name, previous_history_name, "submission-request.json", "submission-response.json", *pages]
    if args.require_complete:
        proof_names.append("leaderboard-final.json")
    baseline_name = request.get("before_progress_file", "progress-before-submit.json" if (HERE / "progress-before-submit.json").exists() else "progress-before.json")
    proof_names.append(baseline_name)
    result = {"as_of": datetime.now(timezone.utc).isoformat(), "provenance": "PROJECT_REPORTED",
              "submission_id": sid, "source_sha256": source_sha, "exactly_one_new_submission": True,
              "old_submission_history_preserved": True, "ranking_complete": complete,
              "progress": {key: progress.get(key) for key in ("percentage", "in_progress", "rank", "total", "league", "league_rank", "league_total", "score", "eligible_for_promotion")},
              "before_progress": read(baseline_name), "leaderboard_check": leaderboard_check,
              "snapshot_battles": len(rows), "completed_battles": sum(outcomes.values()),
              "pending_battles": pending, "missing_logs": missing, "audited_battles": len(games),
              "snapshot_outcomes": dict(outcomes), "clean_outcomes": dict(Counter(g["outcome"] for g in clean)),
              "own_error_games": sum(bool(g["own_errors"]) for g in games),
              "own_warning_games": sum(bool(g["own_warnings"]) for g in games),
              "opponent_error_games": sum(bool(g["opponent_errors"]) for g in games),
              "global_failure_games": sum(bool(g["global_errors"] or g["fail_cause"]) for g in games),
              "d16_telemetry_issue_games": [g["game_id"] for g in games if not g["d16"]["passed"]],
              "d16_outputs": sum(s["outputs"] for s in telemetry),
              "d16_records": sum(s["records"] for s in telemetry),
              "d16_nonbaseline_selections": sum(s["nonbaseline_selections"] for s in telemetry),
              "d16_complete_search_evaluations": sum(s["complete_search_evaluations_total"] for s in telemetry),
              "d16_complete_depth2_evaluations": sum(s["complete_search_evaluations_total"] for s in telemetry),
              "d16_complete_shallow_evaluations": sum(s["complete_shallow_search_evaluations_total"] for s in telemetry),
              "d16_paired_comparison_turns": sum(s["paired_comparison_turns"] for s in telemetry),
              "d16_selected_tier_counts": dict(sum((Counter(s["selected_tier_counts"]) for s in telemetry), Counter())),
              "d16_nonbaseline_tier_counts": dict(sum((Counter(s["nonbaseline_tier_counts"]) for s in telemetry), Counter())),
              "d16_process_cpu_us_max": max((s["process_cpu_us_max"] for s in telemetry if s["process_cpu_us_max"] is not None), default=None),
              "d16_nonfirst_wall_over_20ms_turns": sum(len(s["nonfirst_wall_over_20ms_turns"]) for s in telemetry),
              "d16_emergency_records": sum(len(s["emergency_records"]) for s in telemetry),
              "d16_through_flush_us_max": max((s["through_flush_us_max"] for s in telemetry if s["through_flush_us_max"] is not None), default=None),
              "proof_files": {str(p.relative_to(ROOT)): sha(p) for p in [Path(__file__), HERE / "audit_tests.py", ROOT / "code/platform/analyze_v3_tests.py", *[HERE / name for name in proof_names]]},
              "games": games,
              "caveats": ["Audit consistency is not a guarantee of bot quality or zero technical errors",
                          "Moving before/after ranks are not a paired causal estimate",
                          "Internal post-first-token wall timings are not official charged CPU time",
                          "Ongoing contest snapshot, not the final contest result"]}
    destination = args.out.resolve()
    assert destination.is_relative_to(HERE)
    with destination.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in ("games", "proof_files", "before_progress")}, indent=2))


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Audit saved platform logs and D16-specific telemetry; no API or new games."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "code/platform"))
from analyze_v3_tests import analyze, sha


def read(path):
    return json.loads(path.read_text())


def properties(text):
    result = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        key, value = line.split("=", 1)
        assert key not in result
        result[key] = value
    return result


def d16_telemetry(log):
    """Both selfplay agents are ours; preserve every stderr fragment in order."""
    seats, issues = {}, []
    for agent in log["agents"]:
        if not agent.get("me"):
            continue
        seat = agent["index"]
        frames = [f for f in log["frames"] if f.get("agent") == seat]
        outputs = sum("stdout" in f for f in frames)
        text = "".join(f.get("stderr", "") for f in frames)
        records, malformed = [], []
        for line in text.splitlines():
            if line.startswith("deadline="):
                try:
                    records.append(json.loads(line[len("deadline="):]))
                except json.JSONDecodeError:
                    malformed.append(line)
        baseline_failures = [i for i, row in enumerate(records)
                             if row.get("search", {}).get("baseline_complete") != 1]
        emergencies = [i for i, row in enumerate(records)
                       if row.get("search", {}).get("emergency") != 0]
        flush = [row.get("through_flush_us") for row in records]
        valid_flush = [value for value in flush if isinstance(value, (int, float))]
        entry = {"outputs": outputs, "records": len(records), "malformed": malformed,
                 "incomplete_baseline_records": baseline_failures, "emergency_records": emergencies,
                 "optional_stops": sum(row.get("search", {}).get("stopped") == 1 for row in records),
                 "nonbaseline_selections": sum(row.get("search", {}).get("selected", 0) > 0 for row in records),
                 "turns_with_complete_search_evaluation": sum(row.get("search", {}).get("complete", 0) > 0 for row in records),
                 "complete_search_evaluations_total": sum(row.get("search", {}).get("complete", 0) for row in records),
                 "through_flush_us_max": max(valid_flush, default=None),
                 "baseline_us_max": max((row.get("search", {}).get("baseline_us", 0) for row in records), default=None),
                 "post_flush_samples": len(re.findall(r"post_flush_us=([0-9.]+)", text))}
        # Additive A3 diagnostics: complete/values still mean depth2 only.
        a3 = [row for row in records if "shallow_complete" in row.get("search", {})]
        tier_issues = []
        for row in a3:
            s = row["search"]
            tier = 2 if s["complete"] >= 2 else 1 if s["shallow_complete"] >= 2 else 0
            values = s["values"] if tier == 2 else s["shallow_values"] if tier == 1 else [0]
            valid = (s.get("selected_tier") == tier and bool(s.get("paired")) == bool(tier)
                     and len(s["values"]) == s["complete"]
                     and len(s["shallow_values"]) == s["shallow_complete"]
                     and 0 <= s["selected"] < len(values))
            if valid and s["selected"]:
                valid = (values[s["selected"]] >= max(values)-1e-8
                         and values[s["selected"]] > values[0]+.02-1e-8)
            if not valid:
                tier_issues.append(row.get("turn"))
        entry.update(a3_records=len(a3), a3_tier_issue_turns=tier_issues,
                     complete_shallow_search_evaluations_total=sum(r["search"]["shallow_complete"] for r in a3),
                     paired_comparison_turns=sum(bool(r["search"].get("paired")) for r in a3),
                     selected_tier_counts=dict(Counter(str(r["search"].get("selected_tier")) for r in a3)),
                     nonbaseline_tier_counts=dict(Counter(str(r["search"].get("selected_tier")) for r in a3 if r["search"]["selected"] > 0)),
                     process_cpu_us_max=max((r.get("process_cpu_us", 0) for r in a3), default=None),
                     nonfirst_wall_over_20ms_turns=[r.get("turn") for r in a3 if r.get("turn") != 1 and r.get("through_flush_us", 0) > 20000])
        if tier_issues or (a3 and len(a3) != len(records)):
            issues.append(f"D16 seat{seat} inconsistent A3 completed-tier telemetry")
        if outputs != len(records) or not outputs or malformed or baseline_failures or emergencies:
            issues.append(f"D16 seat{seat} incomplete/unsafe telemetry")
        if len(valid_flush) != len(records):
            issues.append(f"D16 seat{seat} missing through-flush measurements")
        seats[str(seat)] = entry
    if not seats:
        issues.append("No own D16 agent")
    return {"seats": seats, "issues": issues, "passed": not issues,
            "caveat": "Internal post-first-token through-flush wall time, not full official CPU time"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--plan", type=Path, default=HERE / "test-requests.json")
    args = parser.parse_args()
    plan_path = args.plan.resolve()
    assert plan_path.is_relative_to(HERE)
    plan = read(plan_path)
    games, issues, pending = [], [], []
    for item in plan["tests"]:
        index = item["number"]
        final = HERE / f"test-{index:02d}-complete.json"
        initial = HERE / f"test-{index:02d}-result.json"
        path = final if final.exists() else initial
        if not path.exists():
            pending.append(index)
            continue
        data = read(path)
        if data.get("status") == "running":
            pending.append(index)
            continue
        game = analyze(path)
        game["test_number"] = index
        game["role"] = item["role"]
        if game["status"] != "done":
            issues.append(f"Test{index} did not complete: {game.get('failure')}")
            games.append(game)
            continue
        log = data["log"]
        if any(game[key] for key in ("own_errors", "own_warnings", "opponent_errors", "global_errors", "fail_cause")):
            issues.append(f"Test{index} has technical errors/warnings")
        expected = properties(item["expected_game_options"])
        actual = properties(log["game_options"])
        game["map_options_match"] = all(actual.get(k) == v for k, v in expected.items())
        if not game["map_options_match"]:
            issues.append(f"Test{index} map mismatch")
        expected_seats = [0, 1] if item["expected_own_seat"] == "both" else [item["expected_own_seat"]]
        if game["own_seats"] != expected_seats:
            issues.append(f"Test{index} own-seat mismatch")
        if "expected_opponent_ids" in item:
            actual_opponents = [a["agent_id"] for a in log["agents"] if not a.get("me")]
            if actual_opponents != item["expected_opponent_ids"]:
                issues.append(f"Test{index} pinned opponent mismatch")
        body = item["command"]["body"]
        if body.get("opponents") == [6844184]:
            if [a["agent_id"] for a in log["agents"] if not a.get("me")] != [6844184]:
                issues.append(f"Test{index} opponent mismatch")
        if body.get("replay_game_id") == 918815295:
            if [a["agent_id"] for a in log["agents"] if not a.get("me")] != [6850587]:
                issues.append(f"Test{index} fallback opponent mismatch")
        if item["role"] == "candidate":
            game["d16"] = d16_telemetry(log)
            issues.extend(f"Test{index}: {problem}" for problem in game["d16"]["issues"])
        actual_sha = sha(ROOT / item["command"]["code_file"])
        game["source_identity_matches"] = actual_sha == item["source_sha256"]
        if not game["source_identity_matches"]:
            issues.append(f"Test{index} source changed")
        games.append(game)
    complete = len(games) == len(plan["tests"]) and not pending
    if args.require_complete and not complete:
        issues.append("All tests in the selected predeclared plan are required")
    result = {"as_of": datetime.now(timezone.utc).isoformat(), "classification": "PROJECT_REPORTED",
              "completed": sum(g["status"] == "done" for g in games), "pending": pending,
              "planned": len(plan["tests"]), "all_requested_complete": complete,
              "issues": issues, "passed": not issues,
              "games": games, "proof": {str(p.relative_to(ROOT)): sha(p) for p in
                (Path(__file__), ROOT / "code/platform/analyze_v3_tests.py", plan_path)},
              "caveats": ["Technical old-map tests, not independent strength or ranking",
                          "Selfplay compares same-source copies, not D16 against league3m",
                          "No source/time thresholds were retuned from these results"]}
    output = args.out.resolve()
    assert output.is_relative_to(HERE)
    with output.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    summary = {k: v for k, v in result.items() if k not in ("games", "proof")}
    summary["games"] = [{k: g.get(k) for k in ("test_number", "role", "status", "outcome", "own_errors", "own_warnings", "opponent_errors", "d16")} for g in games]
    print(json.dumps(summary, indent=2))
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
"""Resolve the five predeclared tests from saved reads; performs no network calls."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(path):
    return json.loads(path.read_text())


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    plan_path = ROOT / "experiments/rl/2026-11-09-rl7/d16/official-test-requests.json"
    plan = read(plan_path)
    previous = read(HERE / "previous-source.json")
    progress = read(HERE / "progress-before.json")
    assert previous["submission_id"] == progress["submission_id"] == 41671805
    assert previous.get("current") and progress["percentage"] == 100
    assert digest(previous["code"]) == plan["control_sha256"]
    for role in ("candidate", "control"):
        assert digest((ROOT / plan[f"{role}_source"]).read_text()) == plan[f"{role}_sha256"]
    available = {row["agent_id"] for row in read(HERE / "opponents-before.json")["opponents"]}
    battles = read(HERE / "battles-before.json")["battles"]
    eligible_history = {p["agent_id"] for row in battles if row.get("done")
                        for p in row["players"] if not p.get("me")}
    use_fallback = 6844184 not in available | eligible_history
    if use_fallback:
        assert 6850587 in available | eligible_history, "Both fixed opponents unavailable"
        assert any(row["game_id"] == 918815295 and row.get("done") for row in battles)
    tests = []
    for index, item in enumerate(plan["tests"], 1):
        body = dict(plan["defaults"])
        if "historical-timeout" in item["name"] and use_fallback:
            body["replay_game_id"] = 918815295
            fixture = "experiments/rl/2026-11-08-leaderboard-recheck/games/918815295.json"
            options = read(ROOT / fixture)["game_options"]
            expected_seat = 1
        else:
            body["opponents"] = item["opponents"]
            fixture = item.get("game_options_from")
            if fixture:
                name, key = fixture.split(":", 1)
                value = read(ROOT / name)
                for part in key.split("."):
                    value = value[part]
                options = value
            else:
                options = item["game_options"]
            body["game_options"] = options
            expected_seat = "both" if item["opponents"] == ["me"] else 0
        role = item["source"]
        command = {"method": "POST", "path": plan["endpoint"],
                   "code_file": plan[f"{role}_source"], "body": body,
                   "save": str((HERE / f"test-{index:02d}-result.json").relative_to(ROOT)),
                   "keys": ["test_game_id", "status", "failure", "hint", "poll_url"]}
        tests.append({"number": index, "name": item["name"], "role": role,
                      "source_sha256": plan[f"{role}_sha256"], "expected_own_seat": expected_seat,
                      "fixture": fixture, "expected_game_options": options, "command": command})
    result = {"as_of": datetime.now(timezone.utc).isoformat(), "classification": "PROJECT_REPORTED",
              "original_plan_sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
              "captainseb_available": not use_fallback, "fallback_used": use_fallback,
              "tests": tests, "total_game_cap": 5,
              "selfplay_caveat": "me runs the submitted test source twice, not the deployed source",
              "competitive_submission": False}
    with (HERE / "test-requests.json").open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"prepared": len(tests), "fallback_used": use_fallback,
                      "candidate_sha256": plan["candidate_sha256"],
                      "previous_source_verified": True, "network_calls": 0}))


if __name__ == "__main__":
    main()
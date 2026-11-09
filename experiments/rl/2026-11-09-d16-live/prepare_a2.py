#!/usr/bin/env python3
"""Prepare the three prospective compiler-only tests; no network operations."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = "experiments/rl/2026-11-09-rl7/d16/package-attempt2/bot.cpp"
SHA = "d36aba4daa02580b1a20e5e1d000954cea330a852d8adbae1bb8f593572c9d15"


def read(path):
    return json.loads(path.read_text())


def main():
    source = (ROOT / SOURCE).read_bytes()
    assert hashlib.sha256(source).hexdigest() == SHA
    assert hashlib.sha256(source[79:]).hexdigest() == "aba2d6f2ae4bcd92eb79f38fd6bd643be9973b714b135c7b532a3e9fd9a80701"
    original = read(HERE / "test-requests.json")
    tests = []
    for number, old_number in ((6, 1), (7, 2), (8, 4)):
        item = deepcopy(original["tests"][old_number - 1])
        completed = read(HERE / f"test-{old_number:02d}-result.json")
        assert completed["status"] == "done"
        log = completed["log"]
        item.update(number=number, name="a2-" + item["name"], source_sha256=SHA,
                    previous_test_number=old_number, expected_game_options=log["game_options"],
                    expected_opponent_ids=[a["agent_id"] for a in log["agents"] if not a.get("me")])
        command = item["command"]
        command["code_file"] = SOURCE
        command["save"] = str((HERE / f"test-{number:02d}-result.json").relative_to(ROOT))
        if old_number in (1, 2):
            # One own player: official replay preserves exact map, opponent and seat.
            command["body"].pop("opponents")
            command["body"].pop("game_options")
            command["body"]["replay_game_id"] = completed["test_game_id"]
        else:
            # Explicit same-source selfplay; do not replay potentially mixed own seats.
            command["body"]["opponents"] = ["me"]
            command["body"]["game_options"] = log["game_options"]
        tests.append(item)
    plan = {"as_of": datetime.now(timezone.utc).isoformat(), "classification": "PROJECT_REPORTED",
            "amendment": "AMENDMENT_A2.md", "candidate_source": SOURCE, "candidate_sha256": SHA,
            "only_change_bytes": 79, "tests": tests, "additional_game_cap": 3,
            "phase_total_game_cap": 8, "competitive_submission": False}
    with (HERE / "test-requests-a2.json").open("x") as stream:
        stream.write(json.dumps(plan, indent=2) + "\n")
    combined = {"as_of": plan["as_of"], "tests": original["tests"] + tests,
                "phase_total_game_cap": 8, "amendment": "AMENDMENT_A2.md"}
    with (HERE / "test-requests-all.json").open("x") as stream:
        stream.write(json.dumps(combined, indent=2) + "\n")
    print(json.dumps({"prepared": 3, "candidate_sha256": SHA, "body_matches_attempt1": True, "network_calls": 0}))


if __name__ == "__main__":
    main()
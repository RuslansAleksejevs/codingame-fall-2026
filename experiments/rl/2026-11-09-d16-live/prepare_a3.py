"""Resolve exactly three A3 technical requests from saved valid A2 fixtures."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from audit_tests import properties

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()
    source = (ROOT / args.source).resolve()
    assert source.is_relative_to(ROOT / "experiments/rl/2026-11-09-rl7/d16")
    assert sha(source) == args.sha256 and len(args.sha256) == 64
    units = len(source.read_text().encode("utf-16-le")) // 2
    assert units < 98000
    previous = read(HERE / "test-requests-a2-corrected.json")
    assert [t["number"] for t in previous["tests"]] == [6, 7, 9]
    assert sha(ROOT / previous["candidate_source"]) == previous["candidate_sha256"]
    assert read(HERE / "tests-audit-a2-corrected-final.json")["passed"]
    plan = {
        "as_of": datetime.now(timezone.utc).isoformat(), "classification": "PROJECT_REPORTED",
        "candidate_source": args.source, "candidate_sha256": args.sha256,
        "source_utf16": units, "amendment": "AMENDMENT_A3.md",
        "amendment_sha256": sha(HERE / "AMENDMENT_A3.md"),
        "previous_plan_sha256": sha(HERE / "test-requests-a2-corrected.json"),
        "additional_game_cap": 3, "actual_phase_game_cap": 12,
        "functional_requirements": {"complete_same_tier_comparison_turns_min": 10,
                                    "nonself_nonbaseline_min": 1,
                                    "own_errors_warnings_emergencies_max": 0,
                                    "normal_nonfirst_through_flush_us_investigate_above": 20000},
        "competitive_submission": False, "tests": [],
    }
    for number, old in zip((10, 11, 12), previous["tests"]):
        result = read(HERE / f'test-{old["number"]:02d}-result.json')
        assert result["status"] == "done"
        assert properties(result["log"]["game_options"]) == properties(old["expected_game_options"])
        item = deepcopy(old)
        item.update(number=number, name="a3-" + old["name"].removeprefix("a2-"),
                    source_sha256=args.sha256, previous_test_number=old["number"],
                    previous_test_game_id=result["test_game_id"])
        item.pop("correction_for_test", None)
        item["command"]["code_file"] = args.source
        item["command"]["save"] = str((HERE / f"test-{number:02d}-result.json").relative_to(ROOT))
        assert not (ROOT / item["command"]["save"]).exists()
        for flag in ("show_in_ide", "overwrite_ide_code", "overwrite_ide_game_parameters"):
            assert item["command"]["body"][flag] is False
        if number == 12:
            assert item["command"]["body"]["opponents"] == ["me"]
            assert properties(item["command"]["body"]["game_options"]) == properties(old["expected_game_options"])
            assert "22,27_22,29" in item["command"]["body"]["game_options"]
            assert "22,27,22,29" not in item["command"]["body"]["game_options"]
        plan["tests"].append(item)
    destinations = [HERE / "test-requests-a3.json"] + [HERE / f"test-{n:02d}-wire-request.json" for n in (10, 11, 12)]
    assert not any(p.exists() for p in destinations)
    save(destinations[0], plan)
    for path, item in zip(destinations[1:], plan["tests"]):
        save(path, item["command"])
    print(json.dumps({"prepared": [10, 11, 12], "source_sha256": args.sha256,
                      "source_utf16": units, "plan_sha256": sha(destinations[0]),
                      "notes": "Saved structured fixture options reused; no API request issued"}))


if __name__ == "__main__":
    main()
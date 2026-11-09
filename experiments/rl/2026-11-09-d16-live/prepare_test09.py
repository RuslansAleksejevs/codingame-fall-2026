#!/usr/bin/env python3
"""Preserve an execution-input error and prepare its one exact correction."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from audit_tests import properties

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text())


def write_once(name, value):
    with (HERE / name).open("x") as stream:
        stream.write(json.dumps(value, indent=2) + "\n")


def main():
    original = read("test-requests-a2.json")
    wrong_result = read("test-08-result.json")
    assert wrong_result["test_game_id"] == 918850573 and wrong_result["status"] == "done"
    item = deepcopy(original["tests"][2])
    expected = item["command"]["body"]["game_options"]
    assert expected.count("22,27_22,29") == 1
    malformed = expected.replace("22,27_22,29", "22,27,22,29")
    actual = wrong_result["log"]["game_options"]
    assert properties(actual) == properties(malformed), "Inspect any additional execution-input difference"
    wrong_wire = deepcopy(item["command"])
    wrong_wire["body"]["game_options"] = malformed
    record = {"as_of": datetime.now(timezone.utc).isoformat(), "classification": "PROJECT_REPORTED",
              "test_game_id": 918850573, "stage": "request transcription, not bot/referee failure",
              "planned_segment": "22,27_22,29", "actual_segment": "22,27,22,29",
              "actual_options_match_reconstructed_wire": True, "option_property_order_ignored": True,
              "actual_wire_request": wrong_wire,
              "preserve": ["test-08-result.json", "tests-audit-a2-map-error.json", "test-requests-a2.json"],
              "decision": "Exclude test08 from the fixed-map transfer comparison; retain all results and count its cost. Perform exactly one corrected selfplay test09, unchanged source/algorithm/weights/map/opponents.",
              "actual_total_game_cap": 9, "intended_valid_checks": 8,
              "no_outcome_selection": True, "ranking_submissions_so_far": 0}
    write_once("test-08-request-error.json", record)
    item["number"] = 9
    item["name"] = "a2-corrected-historical-selfplay-candidate"
    item["correction_for_test"] = 8
    item["command"]["save"] = "experiments/rl/2026-11-09-d16-live/test-09-result.json"
    corrected = dict(original, tests=original["tests"][:2] + [item],
                     correction="test-08-request-error.json", actual_phase_game_cap=9)
    write_once("test-requests-a2-corrected.json", corrected)
    first = read("test-requests.json")
    write_once("test-requests-valid.json", {"tests": first["tests"] + corrected["tests"],
               "correction": "test-08-request-error.json", "actual_phase_game_cap": 9})
    print(json.dumps({"preserved_wrong_test": 8, "corrected_test": 9,
                      "network_calls": 0, "source_unchanged": True}))


if __name__ == "__main__":
    main()
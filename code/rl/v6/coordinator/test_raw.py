"""Synthetic raw-referee fixtures; does not open or generate contest maps."""
import copy
import json
import unittest

from raw import board_from_raw, normalize


def fixture(own=10, enemy=0, messages=""):
    timing = {"through_flush_us": 16010.5, "search": {"emergency": 0}}
    raw = {"gameParameters": ["nodes=0,0_1,0\nunits=2,0\nedges=0,1\n"],
           "scores": {"0": own, "1": enemy}, "summaries": [messages],
           "errors": {"0": ["deadline=" + json.dumps(timing) + "\n"], "1": [""], "referee": []},
           "outputs": {"0": ["WAIT\n"], "1": ["WAIT\n"]}}
    row = {"candidate": "candidate", "opponent": "lacoz", "seed": 0, "seat": 0,
           "returncode": 0, "valid": True, "score": own, "opponent_score": enemy,
           "outcome": "win" if own > enemy else "loss" if own < enemy else "draw",
           "own_action_errors": [], "opponent_action_errors": [], "referee_errors": [],
           "fail_cause": None, "map_content_sha256": board_from_raw(raw)[1],
           "own_output_count": 1, "deadline_measurements": [timing]}
    return raw, row


class RawAuditTests(unittest.TestCase):
    def test_normal_termination_is_not_error(self):
        raw, row = fixture(-1, 10, "$0: is dominated\n")
        normalized, details = normalize(raw, row)
        self.assertEqual(normalized["points"], 0.)
        self.assertFalse(normalized["own_error"])
        self.assertTrue(details["complete_timing"])

    def test_score_draw_and_favorable_error(self):
        raw, row = fixture(10, 10)
        self.assertEqual(normalize(raw, row)[0]["points"], .5)
        raw, row = fixture(10, -1, "$0: Invalid action\n")
        row["own_action_errors"] = ["Invalid action"]
        result = normalize(raw, row)[0]
        self.assertTrue(result["own_error"] and result["own_invalid"])
        self.assertEqual(result["points"], 0.)

    def test_opponent_timeout_not_silently_clean(self):
        raw, row = fixture(10, -1, "$1: Timeout\n")
        row["opponent_action_errors"] = ["Timeout"]
        result = normalize(raw, row)[0]
        self.assertTrue(result["opponent_error"])
        self.assertFalse(result["own_error"])
        self.assertEqual(result["points"], 1.)

    def test_mismatched_score_and_missing_timing_rejected(self):
        raw, row = fixture()
        changed = copy.deepcopy(row)
        changed["score"] += 1
        with self.assertRaises(AssertionError):
            normalize(raw, changed)
        raw["errors"]["0"] = []
        row["deadline_measurements"] = []
        with self.assertRaises(AssertionError):
            normalize(raw, row)

    def test_actual_failure_allows_incomplete_telemetry_but_zero_points(self):
        raw, row = fixture()
        row["returncode"] = 1
        raw["errors"]["0"] = []
        row["deadline_measurements"] = []
        result, details = normalize(raw, row)
        self.assertEqual(result["points"], 0.)
        self.assertTrue(result["own_error"])
        self.assertFalse(details["complete_timing"])

    def test_emergency_blocks_strategic_win(self):
        raw, row = fixture()
        row["deadline_measurements"][0]["search"]["emergency"] = 1
        raw["errors"]["0"] = ["deadline=" + json.dumps(row["deadline_measurements"][0])]
        result = normalize(raw, row)[0]
        self.assertTrue(result["emergency"])
        self.assertEqual(result["points"], 0.)


if __name__ == "__main__":
    unittest.main(verbosity=2)
"""Synthetic checks only: does not open any saved/reserved game maps."""
import copy
import unittest

from paired import CANDIDATES, ERROR_FIELDS, OPPONENTS, analyze, estimate, strength_gates


def fixture(n=12):
    return [{"candidate": c, "opponent": o, "seed": s, "seat": p,
             "points": 0. if c == "control" else 1., "map_content_sha256": f"synthetic-{s}",
             **{field: False for field in ERROR_FIELDS}}
            for s in range(n) for o in OPPONENTS for c in CANDIDATES for p in (0, 1)]


def evaluate(rows, n=12, stage="development", **checks):
    return analyze(rows, range(n), stage=stage,
                   raw_identity_pass=checks.get("raw", True),
                   replay_pass=checks.get("replay", True), package_pass=checks.get("package", True))


class IndependentPairedTests(unittest.TestCase):
    def test_bootstrap_constant_and_empty(self):
        self.assertEqual(estimate([.5] * 10), {"maps": 10, "point_percent": 50., "map_95_percent": [50., 50.]})
        self.assertIsNone(estimate([])["point_percent"])

    def test_both_seats_are_one_map(self):
        rows = fixture()
        for row in rows:
            if row["candidate"] == "candidate":
                row["points"] = float(row["seat"])
        result = evaluate(rows)
        self.assertEqual(result["all_games"]["direct_league3m"]["map_95_percent"], [50., 50.])
        self.assertEqual(result["all_games"]["direct_league3m"]["maps"], 12)
        self.assertFalse(result["gate_passed"])

    def test_clear_positive_series(self):
        result = evaluate(fixture())
        self.assertTrue(result["gate_passed"])
        self.assertEqual(result["completed_games"], 504)
        self.assertEqual(result["all_games"]["external_gain"]["point_percent"], 100.)
        self.assertEqual(result["all_games"]["external_candidate_minus_teacher"]["point_percent"], 0.)

    def test_one_error_drops_six_row_cluster_not_one_row(self):
        rows = fixture()
        row = next(r for r in rows if r["candidate"] == "control" and r["opponent"] == "lacoz" and r["seed"] == 0 and r["seat"] == 1)
        row["opponent_error"] = True
        result = evaluate(rows)
        self.assertTrue(result["gate_passed"])
        self.assertEqual(result["all_games"]["external_gain"]["maps"], 12)
        self.assertEqual(result["clean_paired"]["external_gain"]["maps"], 11)
        for c in CANDIDATES:
            self.assertEqual(sum(result["clean_paired"]["per_opponent"]["lacoz"]["candidates"][c]["results"].values()), 22)
        self.assertEqual(result["clean_paired"]["per_opponent"]["khoufou2"]["complete_maps"], 12)

    def test_composite_coverage_uses_intersection(self):
        rows = fixture()
        for seed, opponent in ((0, "lacoz"), (1, "khoufou2")):
            next(r for r in rows if r["seed"] == seed and r["opponent"] == opponent)["opponent_error"] = True
        result = evaluate(rows)
        self.assertTrue(all(x["complete_maps"] >= 11 for x in result["clean_paired"]["per_opponent"].values()))
        self.assertEqual(result["clean_paired"]["external_gain"]["maps"], 10)
        self.assertFalse(result["checks"]["clean_coverage_pass"])

    def test_own_emergency_and_missing_evidence_reject(self):
        rows = fixture()
        rows[0]["emergency"] = True
        self.assertFalse(evaluate(rows)["gate_passed"])
        self.assertFalse(evaluate(fixture(), replay=False)["gate_passed"])
        self.assertFalse(evaluate(fixture(), raw=False)["gate_passed"])
        self.assertFalse(evaluate(fixture(), package=False)["gate_passed"])

    def test_incomplete_is_not_promoted(self):
        result = evaluate(fixture()[:-1])
        self.assertFalse(result["gate_passed"])
        self.assertEqual(len(result["missing_rows"]), 1)

    def test_duplicate_unknown_and_hash_collision_rejected(self):
        rows = fixture()
        with self.assertRaises(AssertionError):
            evaluate(rows + [rows[0]])
        altered = copy.deepcopy(rows)
        altered[0]["candidate"] = "posthoc"
        with self.assertRaises(AssertionError):
            evaluate(altered)
        altered = copy.deepcopy(rows)
        for row in altered:
            row["map_content_sha256"] = "same-map"
        with self.assertRaises(AssertionError):
            evaluate(altered)

    def test_final_requires_b2m_and_strict_lower_bounds(self):
        view = evaluate(fixture())["all_games"]
        self.assertTrue(all(strength_gates(view, "final").values()))
        view["direct_b2m"] = {"maps": 100, "point_percent": 55., "map_95_percent": [50., 60.]}
        self.assertFalse(strength_gates(view, "final")["direct_b2m_lower_above50"])
        view["external_candidate_minus_teacher"] = {"maps": 100, "point_percent": -2., "map_95_percent": [-5., 1.]}
        gates = strength_gates(view, "final")
        self.assertTrue(gates["teacher_retention_point_at_least_minus2"])
        self.assertFalse(gates["teacher_retention_lower_above_minus5"])
        view["external_gain"] = {"maps": 100, "point_percent": 3., "map_95_percent": [0., 6.]}
        gates = strength_gates(view, "final")
        self.assertTrue(gates["external_gain_at_least3"])
        self.assertFalse(gates["external_lower_positive"])

    def test_final_exact_95_percent_coverage(self):
        # 20 maps suffice to exercise the 95% boundary without reading any data.
        rows = fixture(20)
        rows[0]["opponent_error"] = True
        result = evaluate(rows, 20, "final")
        self.assertEqual(result["minimum_clean_maps"], 19)
        self.assertTrue(result["gate_passed"])
        next(r for r in rows if r["seed"] == 1)["opponent_error"] = True
        self.assertFalse(evaluate(rows, 20, "final")["gate_passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
"""Independent prospective v6 map-paired statistics; no experiment imports.

Input rows must be independently normalized from raw referee results. ``points``
is 0/0.5/1, not the in-game troop score. Clean pairing removes all six
candidate/control/teacher x seat rows of an affected opponent/map cluster.
No games are generated, retried, selected or discarded from the all-game view.
"""
from collections import Counter
import math

import numpy as np

CANDIDATES = ("candidate", "control", "teacher")
OPPONENTS = ("lacoz", "khoufou2", "khoufou", "v6", "bc", "league3m", "b2m")
EXTERNAL = OPPONENTS[:3]
BOOTSTRAP_SEED = 20261109
RESAMPLES = 10_000
ERROR_FIELDS = ("own_error", "opponent_error", "own_invalid", "opponent_invalid",
                "emergency", "referee_error")


def key(row):
    return row["candidate"], row["opponent"], row["seed"], row["seat"]


def estimate(values):
    """Resample complete maps, including both seats in each supplied value."""
    values = np.asarray(values, dtype=np.float64)
    assert values.ndim == 1 and np.isfinite(values).all()
    if not len(values):
        return {"maps": 0, "point_percent": None, "map_95_percent": [None, None]}
    generator = np.random.default_rng(BOOTSTRAP_SEED)
    indices = generator.integers(0, len(values), size=(RESAMPLES, len(values)))
    means = values[indices].mean(axis=1)
    return {"maps": len(values), "point_percent": float(values.mean() * 100),
            "map_95_percent": (np.quantile(means, [.025, .975]) * 100).tolist()}


def at_least(value, threshold):
    # Decimal percentage boundaries are prospective; tolerate only roundoff.
    return value is not None and value >= threshold - 1e-12


def above(value, threshold):
    return value is not None and value > threshold + 1e-12


def strength_gates(view, stage):
    gain = view["external_gain"]
    retained = view["external_candidate_minus_teacher"]
    base = view["direct_league3m"]
    live = view["direct_b2m"]
    regressions = [entry["gain"]["point_percent"] for entry in view["per_opponent"].values()]
    if stage == "development":
        return {
            "external_positive": above(gain["point_percent"], 0),
            "direct_league3m_majority": above(base["point_percent"], 50),
            "teacher_retention_point": at_least(retained["point_percent"], -5),
            "no_opponent_regression_below_minus10": all(at_least(x, -10) for x in regressions),
        }
    assert stage == "final"
    return {
        "external_gain_at_least3": at_least(gain["point_percent"], 3),
        "external_lower_positive": above(gain["map_95_percent"][0], 0),
        "direct_league3m_at_least55": at_least(base["point_percent"], 55),
        "direct_league3m_lower_above50": above(base["map_95_percent"][0], 50),
        "direct_b2m_at_least55": at_least(live["point_percent"], 55),
        "direct_b2m_lower_above50": above(live["map_95_percent"][0], 50),
        "no_opponent_regression_below_minus5": all(at_least(x, -5) for x in regressions),
        "teacher_retention_point_at_least_minus2": at_least(retained["point_percent"], -2),
        "teacher_retention_lower_above_minus5": above(retained["map_95_percent"][0], -5),
    }


def analyze(rows, seeds, *, stage, raw_identity_pass, replay_pass, package_pass):
    """Calculate all and clean estimates, preserving incomplete/failed evidence.

    Technical evidence booleans are required, with no optimistic defaults. Their
    backing artifacts and hashes must be checked separately by the raw auditor.
    An incomplete schedule can be described but can never pass admission.
    """
    assert stage in ("development", "final")
    seeds = tuple(seeds)
    assert seeds and len(seeds) == len(set(seeds))
    expected = {(c, o, s, p) for c in CANDIDATES for o in OPPONENTS for s in seeds for p in (0, 1)}
    by = {}
    map_hashes = {}
    for row in rows:
        identity = key(row)
        assert identity in expected, ("Unexpected row", identity)
        assert identity not in by, ("Duplicate row", identity)
        assert row["points"] in (0, .5, 1), identity
        assert type(row["seat"]) is int and type(row["seed"]) is int
        assert all(type(row[name]) is bool for name in ERROR_FIELDS), identity
        assert isinstance(row["map_content_sha256"], str) and row["map_content_sha256"]
        assert map_hashes.setdefault(row["seed"], row["map_content_sha256"]) == row["map_content_sha256"]
        by[identity] = row
    assert len(set(map_hashes.values())) == len(map_hashes), "Duplicate map content"

    counts = {c: {o: dict(Counter({"win": 0, "draw": 0, "loss": 0}) +
                              Counter({0: "loss", .5: "draw", 1: "win"}[r["points"]]
                                      for r in rows if r["candidate"] == c and r["opponent"] == o))
                  for o in OPPONENTS} for c in CANDIDATES}
    # Counter addition drops zero entries; keep an explicit full outcome schema.
    for opponents in counts.values():
        for results in opponents.values():
            for label in ("win", "draw", "loss"):
                results.setdefault(label, 0)

    def points(candidate, opponent, seed, seat):
        return by[candidate, opponent, seed, seat]["points"]

    def map_score(candidate, opponent, seed):
        return (points(candidate, opponent, seed, 0) + points(candidate, opponent, seed, 1)) / 2

    views = {}
    for clean_only in (False, True):
        per = {}
        dropped = {}
        for opponent in OPPONENTS:
            kept = []
            dropped[opponent] = {}
            for seed in seeds:
                cluster = [(c, opponent, seed, p) for c in CANDIDATES for p in (0, 1)]
                if any(k not in by for k in cluster):
                    dropped[opponent][str(seed)] = "incomplete_cluster"
                    continue
                errors = [k for k in cluster if any(by[k][field] for field in ERROR_FIELDS)]
                if clean_only and errors:
                    dropped[opponent][str(seed)] = [list(k) for k in errors]
                    continue
                kept.append(seed)
            candidates = {}
            for candidate in CANDIDATES:
                outcomes = Counter({0: "loss", .5: "draw", 1: "win"}[points(candidate, opponent, s, p)]
                                   for s in kept for p in (0, 1))
                candidates[candidate] = {
                    "score": estimate([map_score(candidate, opponent, s) for s in kept]),
                    "results": {label: outcomes[label] for label in ("win", "draw", "loss")},
                    "seats": {str(p): estimate([points(candidate, opponent, s, p) for s in kept]) for p in (0, 1)},
                }
            per[opponent] = {
                "retained_seeds": kept, "complete_maps": len(kept), "candidates": candidates,
                "gain": estimate([map_score("candidate", opponent, s) - map_score("control", opponent, s) for s in kept]),
                "candidate_minus_teacher": estimate([map_score("candidate", opponent, s) - map_score("teacher", opponent, s) for s in kept]),
            }
        external_maps = [s for s in seeds if all(s in per[o]["retained_seeds"] for o in EXTERNAL)]
        view = {
            "per_opponent": per, "excluded_clusters": dropped, "external_maps": external_maps,
            "external_gain": estimate([sum(map_score("candidate", o, s) - map_score("control", o, s) for o in EXTERNAL) / 3 for s in external_maps]),
            "external_candidate_minus_teacher": estimate([sum(map_score("candidate", o, s) - map_score("teacher", o, s) for o in EXTERNAL) / 3 for s in external_maps]),
            "direct_league3m": per["league3m"]["candidates"]["candidate"]["score"],
            "direct_b2m": per["b2m"]["candidates"]["candidate"]["score"],
        }
        view["gates"] = strength_gates(view, stage)
        view["strength_passed"] = all(view["gates"].values())
        views["clean_paired" if clean_only else "all_games"] = view
    clean = views["clean_paired"]
    minimum = math.ceil(len(seeds) * (.95 if stage == "final" else .90))
    coverage = len(clean["external_maps"]) >= minimum and all(x["complete_maps"] >= minimum for x in clean["per_opponent"].values())
    technical = {name: sum(row[name] for row in rows) for name in ERROR_FIELDS}
    own_failures = sum(any(row[name] for name in ("own_error", "own_invalid", "emergency", "referee_error")) for row in rows)
    complete = set(by) == expected
    strength = views["all_games"]["strength_passed"] and (stage == "development" or clean["strength_passed"])
    checks = {
        "complete_fixed_schedule": complete,
        "zero_own_control_teacher_errors": own_failures == 0,
        "raw_identity_pass": bool(raw_identity_pass), "replay_pass": bool(replay_pass),
        "package_pass": bool(package_pass), "clean_coverage_pass": coverage,
        "prospective_strength_pass": strength,
    }
    return {
        "stage": stage, "gate_passed": all(checks.values()), "checks": checks,
        "completed_games": len(rows), "expected_games": len(expected), "expected_maps": len(seeds),
        "minimum_clean_maps": minimum, "technical_error_game_counts": technical,
        "own_control_teacher_error_games": own_failures,
        "observed_counts": counts, "missing_rows": [list(k) for k in sorted(expected - set(by))],
        "bootstrap": {"seed": BOOTSTRAP_SEED, "resamples": RESAMPLES, "unit": "whole map, both seats"},
        **views,
    }
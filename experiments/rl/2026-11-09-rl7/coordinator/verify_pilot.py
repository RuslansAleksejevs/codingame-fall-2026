"""Independent saved-raw/cluster-statistics audit; no new games or learning."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "experiments/rl/2026-11-09-rl7/diversity"
ARMS = ("narrow1", "broad1", "narrow2", "broad2", "base")
OPPONENTS = ("lacoz", "khoufou2", "khoufou", "league3m", "b2m")
NORMAL = {"is dominated", "no units or triangles left", "can't score any more points"}


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    target = Path(sys.argv[1])
    assert not target.exists()
    frozen = read(DATA / "candidate-freeze.json")
    decision = read(DATA / "gamedev-decision.json")
    for path, expected in {**frozen["identities"], **decision["data_bindings"]}.items():
        assert digest(ROOT / path) == expected, path
    values = np.full((5, 5, 16, 2), np.nan)
    rows = []
    raw_hashes = {}
    states = transitions = 0
    canonical = {}
    for block in range(1, 5):
        folder = DATA / f"gamedev{block}"
        part = [json.loads(line) for line in (folder / "matches.jsonl").read_text().splitlines()]
        spec = read(folder / "panel-spec.json")
        identity = [{k: row[k] for k in ("candidate", "opponent", "seed", "seat")} for row in part]
        assert identity == spec["schedule"]
        replay = read(DATA / f"gamedev{block}-verification.json")
        assert replay["passed"] and replay["clean_games"] == 200
        assert not replay["excluded"] and not replay["mismatches"]
        assert replay["matches_sha256"] == digest(folder / "matches.jsonl")
        states += replay["states"]
        transitions += replay["transitions"]
        for row in part:
            arm, opponent, seed, seat = (row[k] for k in ("candidate", "opponent", "seed", "seat"))
            stem = f"{arm}-vs-{opponent}-seed{seed}-seat{seat}"
            path = folder / (stem + "-raw.json")
            raw = read(path)
            summaries = "".join(s or "" for s in raw["summaries"])
            for player in (0, 1):
                messages = re.findall(r"\$" + str(player) + r": ([^\n]+)", summaries)
                assert not [m for m in messages if m not in NORMAL], stem
            assert not any(raw["errors"].get("referee", [])) and not raw.get("failCause"), stem
            own, enemy = raw["scores"][str(seat)], raw["scores"][str(1-seat)]
            outcome = "win" if own > enemy else "loss" if own < enemy else "draw"
            assert row["outcome"] == outcome and row["score"] == own and row["opponent_score"] == enemy
            assert row["returncode"] == 0 and row["valid"]
            assert not row["own_action_errors"] and not row["opponent_action_errors"]
            assert row["own_output_count"] == sum(bool(s) for s in raw["outputs"][str(seat)])
            options = dict(line.split("=", 1) for line in "".join(raw["gameParameters"]).splitlines() if "=" in line)
            board = {k: [list(map(int, r.split(","))) for r in options[k].split("_") if r] for k in ("nodes", "units", "edges")}
            map_hash = hashlib.sha256(json.dumps(board, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            assert map_hash == row["map_content_sha256"] == spec["expected_map_hashes"][str(seed)]
            assert canonical.setdefault(seed, map_hash) == map_hash
            index = (ARMS.index(arm), OPPONENTS.index(opponent), seed-73301, seat)
            assert np.isnan(values[index]), ("duplicate", stem)
            values[index] = 1 if own > enemy else 0 if own < enemy else .5
            raw_hashes[str(path.relative_to(ROOT))] = digest(path)
        rows.extend(part)
    assert [{k: row[k] for k in ("candidate", "opponent", "seed", "seat")} for row in rows] == frozen["schedule"]
    assert len(rows) == 800 and not np.isnan(values).any() and len(set(canonical.values())) == 16
    assert decision["all"] == decision["clean"]
    # Paired map resampling independently reconstructed from raw terminal scores.
    indices = np.random.default_rng(20261109).integers(0, 16, size=(10000, 16))
    metrics = {}

    def compare(label, vector, expected):
        actual = {"point": float(vector.mean()), "ci95": np.quantile(vector[indices].mean(axis=1), [.025, .975]).tolist()}
        assert np.allclose([actual["point"], *actual["ci95"]], [expected["point"], *expected["ci95"]], atol=1e-12, rtol=0), label
        metrics[label] = actual

    external = values[:, :3].mean(axis=(1, 3))
    for a, arm in enumerate(ARMS):
        compare(arm, external[a], decision["all"]["external"][arm])
        for o, opponent in enumerate(OPPONENTS):
            vector = values[a, o].mean(axis=1)
            expected = decision["all"]["per_opponent"][arm + "-vs-" + opponent]
            compare(arm + "-vs-" + opponent, vector, expected)
            assert expected["wdl"] == [int((values[a, o] == v).sum()) for v in (1, .5, 0)]
    mean_delta = ((external[1]-external[0]) + (external[3]-external[2]))/2
    mean_base = ((external[1]-external[4]) + (external[3]-external[4]))/2
    compare("broad-minus-narrow", mean_delta, decision["all"]["broad-minus-narrow"])
    compare("broad-minus-base", mean_base, decision["all"]["broad-minus-base"])
    gates = {
        "complete_and_clean": True,
        "mean_broad_over_narrow": bool(mean_delta.mean() > 0),
        "mean_broad_not_below_base": bool(mean_base.mean() >= 0),
        "each_seed_at_least_minus_5pp": all(float((external[i]-external[4]).mean()) >= -.05-1e-12 for i in (1, 3)),
        "seed1_over_narrow": bool((external[1]-external[0]).mean() > 0),
        "seed1_not_below_base": bool((external[1]-external[4]).mean() >= 0),
        "seed1_direct_at_least_half": bool(values[1, 3].mean() >= .5),
        "seed1_no_opponent_drop_over_5pp": bool(np.min((values[1]-values[4]).mean(axis=(1, 2))) >= -.05-1e-12),
    }
    assert all(gates.values()) == decision["promise"] == False
    assert not list(DATA.glob("final[1-4]")) and not (DATA / "final-freeze.json").exists()
    result = {
        "as_of": datetime.now(timezone.utc).isoformat(), "classification": "PROJECT_REPORTED",
        "passed": True, "scientific_promise": False, "games": len(rows), "maps": len(canonical),
        "raw_scores_errors_maps_and_full_schedule_rechecked": True,
        "freeze_identities_checked": len(frozen["identities"]), "decision_bindings_checked": len(decision["data_bindings"]),
        "existing_java_receipts": {"games": 800, "states": states, "transitions": transitions, "rerun": False},
        "gate_checks": gates, "metrics": metrics, "raw_sha256": raw_hashes,
        "decision_sha256": digest(DATA / "gamedev-decision.json"), "script_sha256": digest(Path(__file__)),
        "caveats": ["No new games, training or Java execution", "Two seeds and sixteen maps do not establish universal failure of diversity", "Zero CI endpoints include numerical floating-point zero"],
    }
    with target.open("x") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    print(json.dumps({k: result[k] for k in ("passed", "scientific_promise", "games", "maps", "gate_checks", "existing_java_receipts")}))


if __name__ == "__main__":
    main()
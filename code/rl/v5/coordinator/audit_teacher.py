"""Independent raw-score, evidence-coverage and paired-bootstrap teacher audit.

Read-only toward the frozen experiment. No import of its analyzer or simulator.
Writes one new coordinator report; never reruns games or replaces old evidence.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "experiments/rl/2026-11-08-rl5/deadline-search"
OUT = ROOT / "experiments/rl/2026-11-08-rl5/coordinator/teacher-audit.json"
NORMAL = {"is dominated", "no units or triangles left", "can't score any more points"}
OPPONENTS = ("lacoz", "khoufou2", "khoufou", "v6", "bc", "league3m", "b2m")


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(row):
    return tuple(row[k] for k in ("candidate", "opponent", "seed", "seat"))


def estimate(values):
    # Separate implementation: explicit whole-map paired values from raw scores.
    array = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(20261108)
    indices = rng.integers(0, array.size, size=(10000, array.size))
    means = array[indices].sum(axis=1) / array.size
    return {"maps": int(array.size), "point_percent": float(array.mean() * 100),
            "map_95_percent": (np.quantile(means, [0.025, 0.975]) * 100).tolist()}


def compare(actual, recorded):
    assert actual["maps"] == recorded["maps"]
    for name in ("point_percent", "map_95_percent"):
        assert np.allclose(actual[name], recorded[name], atol=1e-10, rtol=0), (name, actual, recorded)


def main():
    began = time.monotonic()
    assert not OUT.exists(), "Keep previous audit immutable"
    frozen = read(DATA / "freeze.json")
    decision = read(DATA / "decision.json")
    assert sha(DATA / "freeze.json") == "3a8a360441013efe735d7f2f3d27e4bdd11e66b84b83323938991bf36987f532"
    identities = {}
    for section in ("sources", "weights", "binaries", "dependencies", "protected"):
        identities.update(frozen[section])
    for name, expected in identities.items():
        assert sha(ROOT / name) == expected, name
    assert sha(DATA / "PROTOCOL.md") == frozen["protocol_sha256"]
    rows = []; values = {}; groups = Counter(); evidence = {}; map_ids = {}
    java_states = java_transitions = raw_outputs = raw_timing = 0
    for block in range(1, 5):
        directory = DATA / f"confirm{block}"
        current = [json.loads(line) for line in (directory / "matches.jsonl").read_text().splitlines()]
        report = read(DATA / f"confirm{block}-verification.json")
        manifest = read(directory / "manifest.json")
        assert len(current) == report["rows"] == report["clean_games"] == 280
        assert report["passed"] and not report["excluded"] and not report["mismatches"]
        assert report["states"] == report["transitions"] + 280
        assert report["matches_sha256"] == sha(directory / "matches.jsonl")
        assert report["manifest_sha256"] == sha(directory / "manifest.json")
        assert report["verifier_sha256"] == sha(ROOT / "code/rl/v5/deadline_search/verify.py")
        assert list(map(key, current)) == list(map(key, manifest["schedule"]))
        novelty = read(DATA / f"confirm{block}-novelty.json")
        registry = read(DATA / f"confirm{block}-registry.json")
        assert novelty["passed"] and not novelty["overlaps"]
        assert novelty["registry_sha256"] == sha(DATA / f"confirm{block}-registry.json")
        known = set(registry["canonical"])
        java_states += report["states"]; java_transitions += report["transitions"]
        evidence[f"confirm{block}"] = {"raw_rows_sha256": report["matches_sha256"],
                                       "verification_sha256": sha(DATA / f"confirm{block}-verification.json")}
        for row in current:
            assert row["valid"] and row["returncode"] == 0
            assert not row["own_action_errors"] and not row["opponent_action_errors"]
            stem = f'{row["candidate"]}-vs-{row["opponent"]}-seed{row["seed"]}-seat{row["seat"]}'
            raw = read(directory / f"{stem}-raw.json")
            assert not raw.get("failCause") and not any(raw["errors"].get("referee", []))
            endings = re.findall(r"\$[01]: ([^\n]+)", "".join(s or "" for s in raw["summaries"]))
            assert all(message in NORMAL for message in endings), (stem, endings)
            seat = row["seat"]
            own, enemy = raw["scores"][str(seat)], raw["scores"][str(1 - seat)]
            assert (own, enemy) == (row["score"], row["opponent_score"])
            outcome = "win" if own > enemy else "loss" if own < enemy else "draw"
            assert outcome == row["outcome"]
            k = key(row); assert k not in values
            values[k] = (1 if own > enemy else -1 if own < enemy else 0) / 2 + 0.5
            groups[row["candidate"], row["opponent"], outcome] += 1
            properties = dict(line.split("=", 1) for line in "".join(raw["gameParameters"]).splitlines() if "=" in line)
            board = {field: [list(map(int, part.split(","))) for part in properties[field].split("_") if part]
                     for field in ("nodes", "units", "edges")}
            digest = hashlib.sha256(json.dumps(board, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            assert digest == row["map_content_sha256"] and digest not in known
            assert map_ids.setdefault(row["seed"], digest) == digest
            outputs = sum(bool(x) for x in raw["outputs"][str(seat)])
            timing = [line for line in "".join(x or "" for x in raw["errors"][str(seat)]).splitlines()
                      if line.startswith("deadline=")]
            assert outputs == row["own_output_count"] == len(timing) == len(row["deadline_measurements"])
            raw_outputs += outputs; raw_timing += len(timing)
        rows.extend(current)
    assert list(map(key, rows)) == list(map(key, frozen["schedule"])) and len(rows) == 1120
    assert len(map_ids) == len(set(map_ids.values())) == 40
    seeds = list(range(70101, 70141)); gains = {}; counted = {}
    for opponent in OPPONENTS:
        gains[opponent] = [sum(values["search", opponent, seed, seat] - values["control", opponent, seed, seat]
                               for seat in (0, 1)) / 2 for seed in seeds]
        counted[opponent] = {}
        for candidate in ("search", "control"):
            counts = {outcome: groups[candidate, opponent, outcome] for outcome in ("win", "draw", "loss")}
            assert sum(counts.values()) == 80
            counted[opponent][candidate] = counts
            for mode in ("all_games", "clean_paired"):
                expected = decision[mode]["per_opponent"][opponent]["candidates"][candidate]["results"]
                assert all(counts[outcome] == expected[outcome] for outcome in counts)
    external = estimate([sum(gains[opponent][i] for opponent in OPPONENTS[:3]) / 3 for i in range(40)])
    direct = estimate([sum(values["search", "league3m", seed, seat] for seat in (0, 1)) / 2 for seed in seeds])
    by_opponent = {opponent: estimate(v) for opponent, v in gains.items()}
    for mode in ("all_games", "clean_paired"):
        compare(external, decision[mode]["external_gain"])
        compare(direct, decision[mode]["direct_league3m"])
        for opponent, result in by_opponent.items():
            compare(result, decision[mode]["per_opponent"][opponent]["gain"])
    independent_gate = (external["point_percent"] >= 5 and external["map_95_percent"][0] > 0
                        and direct["point_percent"] >= 55 and direct["map_95_percent"][0] > 50
                        and all(v["point_percent"] >= -5 for v in by_opponent.values()))
    assert independent_gate == decision["teacher_gate_passed"]
    result = {"as_of": datetime.now(timezone.utc).isoformat(), "classification": "PROJECT_REPORTED",
              "passed": True, "teacher_gate_independently_confirmed": bool(independent_gate),
              "raw_games": len(rows), "unique_maps": len(map_ids), "technical_errors": 0,
              "raw_outputs": raw_outputs, "raw_timing_records": raw_timing,
              "replay_clean_games": len(rows), "replay_excluded": 0,
              "java_states_reported_and_hash_bound": java_states, "java_transitions_reported_and_hash_bound": java_transitions,
              "external_gain": external, "direct_league3m": direct, "per_opponent_gain": by_opponent,
              "raw_counts": counted, "frozen_identity_files_checked": len(identities),
              "freeze_sha256": sha(DATA / "freeze.json"), "decision_sha256": sha(DATA / "decision.json"),
              "audit_source_sha256": sha(Path(__file__)), "evidence": evidence,
              "numpy_version": np.__version__, "seconds": time.monotonic() - began,
              "scope": "Independent raw score/error/content/timing/schedule audit and bootstrap reimplementation. Existing Java replay coverage and identity checked; Java trajectories not rerun. Not platform evidence or deployability approval."}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("x") as stream:
        json.dump(result, stream, indent=2); stream.write("\n")
    print(json.dumps({k: result[k] for k in ("passed", "teacher_gate_independently_confirmed", "raw_games",
          "external_gain", "direct_league3m", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
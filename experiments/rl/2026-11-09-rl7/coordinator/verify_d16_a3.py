"""Independent raw-score, timing and paired-statistics check of the fixed A3 guard."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "experiments/rl/2026-11-09-rl7/d16"
NORMAL = {"is dominated", "no units or triangles left", "can't score any more points"}
ROLES, OPPONENTS = ("candidate", "control"), ("lacoz", "khoufou2", "khoufou")


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(sys.argv[1])
    assert not out.exists()
    frozen = load(DATA / "a3-freeze.json")
    report = load(DATA / "a3-gross-decision.json")
    assert sha(DATA / "a3-freeze.json") == report["freeze_sha256"]
    assert report["source_sha256"] == sha(DATA / "package-attempt3/bot.cpp") == "94f0d426de787f7ed29a0ce87fa03fd3e0bae2ebb27c7d76548f4624f67ab4f8"
    for path, expected in {**frozen["identities"], **report["raw_bindings"]}.items():
        assert sha(ROOT / path) == expected, path
    rows = [json.loads(s) for s in (DATA / "a3-gross/matches.jsonl").read_text().splitlines()]
    assert len(rows) == 96
    assert [{k: r[k] for k in ("candidate", "opponent", "seed", "seat")} for r in rows] == frozen["schedule"]
    values = np.full((2, 3, 8, 2), np.nan)
    bindings, maps, records = {}, {}, []
    for row in rows:
        c, o, s, p = (row[k] for k in ("candidate", "opponent", "seed", "seat"))
        path = DATA / "a3-gross" / f"{c}-vs-{o}-seed{s}-seat{p}-raw.json"
        raw = load(path)
        assert sha(path) == row["raw_sha256"]
        bindings[str(path.relative_to(ROOT))] = sha(path)
        text = "".join(t or "" for t in raw["summaries"])
        for seat in (0, 1):
            assert not [t for t in re.findall(r"\$" + str(seat) + r": ([^\n]+)", text) if t not in NORMAL]
        assert not raw.get("failCause") and not any(raw["errors"].get("referee", []))
        assert row["returncode"] == 0 and row["valid"] and not row["own_action_errors"] and not row["opponent_action_errors"]
        a, b = raw["scores"][str(p)], raw["scores"][str(1-p)]
        outcome = "win" if a > b else "loss" if a < b else "draw"
        assert outcome == row["outcome"] and a == row["score"] and b == row["opponent_score"]
        index = ROLES.index(c), OPPONENTS.index(o), s-72005, p
        assert np.isnan(values[index])
        values[index] = 1 if a > b else 0 if a < b else .5
        props = dict(t.split("=", 1) for t in "".join(raw["gameParameters"]).splitlines() if "=" in t)
        board = {k: [list(map(int, t.split(","))) for t in props[k].split("_") if t] for k in ("nodes", "units", "edges")}
        digest = hashlib.sha256(json.dumps(board, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        assert digest == row["map_content_sha256"] == maps.setdefault(s, digest)
        assert row["baseline_complete_pass"] and row["timing_coverage_pass"] and row["internal_margin_pass"]
        if c == "candidate":
            stderr = "".join(t or "" for t in raw["errors"][str(p)])
            current = [json.loads(t.split("=", 1)[1]) for t in stderr.splitlines() if t.startswith("deadline=")]
            assert len(current) == sum(bool(t) for t in raw["outputs"][str(p)])
            for record in current:
                x = record["search"]
                assert x["baseline_complete"] == 1 and x["emergency"] == 0
                tier = 2 if x["complete"] >= 2 else 1 if x["shallow_complete"] >= 2 else 0
                assert x["selected_tier"] == tier and bool(x["paired"]) == bool(tier)
                scores = x["values"] if tier == 2 else x["shallow_values"] if tier == 1 else [0]
                assert 0 <= x["selected"] < len(scores)
                if x["selected"]:
                    assert scores[x["selected"]] >= max(scores)-1e-8 and scores[x["selected"]] > scores[0]+.02-1e-8
            records.extend(current)
    assert not np.isnan(values).any() and len(set(maps.values())) == 8
    assert report["all_games"] == report["common_clean"]
    for mode in ("all_games", "common_clean"):
        view = report[mode]
        assert view["points"] == {c: int(values[i].sum()) for i, c in enumerate(ROLES)}
        for i, opponent in enumerate(OPPONENTS):
            assert view["per_opponent"][opponent]["points"] == {c: int(values[j, i].sum()) for j, c in enumerate(ROLES)}
    gains = (values[0]-values[1]).mean(axis=(0, 2))
    indices = np.random.default_rng(20261109).integers(0, 8, size=(10000, 8))
    metric = {"point_percent": float(gains.mean()*100), "map_95_percent": (np.quantile(gains[indices].mean(axis=1), [.025, .975])*100).tolist()}
    expected = report["all_games"]["paired_external_gain"]
    assert np.allclose([metric["point_percent"], *metric["map_95_percent"]], [expected["point_percent"], *expected["map_95_percent"]], atol=1e-10, rtol=0)
    assert values[0].sum() >= values[1].sum() and np.all(values[0].sum(axis=(1, 2)) >= values[1].sum(axis=(1, 2))-2)
    assert report["local_guard_pass"] and report["technical_pass"] and report["gross_guard_pass"]
    replay = report["replay"]
    assert replay["passed"] and replay["clean_games"] == 96 and not replay["excluded"] and not replay["mismatches"]
    assert replay["matches_sha256"] == sha(DATA / "a3-gross/matches.jsonl")
    result = {"as_of": datetime.now(timezone.utc).isoformat(), "classification": "PROJECT_REPORTED",
              "passed": True, "local_gross_guard_passed": True, "games": 96, "maps": 8,
              "points": report["all_games"]["points"], "paired_external_gain": metric,
              "candidate_outputs": len(records), "candidate_changed_outputs": sum(r["search"]["selected"] > 0 for r in records),
              "fixed_identity_count": len(frozen["identities"]), "raw_sha256": bindings,
              "decision_sha256": sha(DATA / "a3-gross-decision.json"), "script_sha256": sha(Path(__file__)),
              "java_receipt": {"games": 96, "states": replay["states"], "transitions": replay["transitions"], "rerun": False},
              "caveats": ["Eight-map gross guard, not strong independent proof", "No new games, training or Java rerun", "Platform functional gate separately audited"]}
    with out.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k != "raw_sha256"}, indent=2))


if __name__ == "__main__":
    main()
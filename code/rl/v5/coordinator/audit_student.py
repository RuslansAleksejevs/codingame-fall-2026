"""Independent complete/clean student-series audit, without experiment imports.

Reparse original referee scores and timing, check identity/replay coverage, and
reimplement all paired map estimates. Refuse partial or technically dirty series
instead of silently treating missing/failed games as clean. Never rerun games.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import time

import numpy as np

from audit_teacher import ROOT, DATA, NORMAL, OPPONENTS, read, sha, key, estimate, compare

STUDENT = DATA / "student"
OUT = DATA.parent / "coordinator/student-audit.json"
CANDIDATES = ("student", "control", "teacher")
SEEDS = tuple(range(70401, 70441))


def outcome(own, enemy):
    return "win" if own > enemy else "loss" if own < enemy else "draw"


def main():
    began = time.monotonic()
    assert not OUT.exists(), "Preserve previous audit"
    frozen = read(STUDENT / "freeze.json")
    teacher = read(DATA / "freeze.json")
    decision = read(STUDENT / "decision.json")
    assert sha(STUDENT / "freeze.json") == "15c74bc0ee784dfa2533a776f047687e9ba8851cd1edde6be0542eff6b00de80"
    assert sha(DATA / "freeze.json") == frozen["teacher_freeze_sha256"] == "3a8a360441013efe735d7f2f3d27e4bdd11e66b84b83323938991bf36987f532"
    identities = dict(frozen["identities"])
    for section in ("sources", "weights", "binaries", "dependencies", "protected"):
        for name, digest in teacher[section].items():
            assert identities.setdefault(name, digest) == digest
    for name, digest in identities.items():
        assert sha(ROOT / name) == digest, name
    for name in ("package-parity", "collection-package-parity", "native-logit-parity"):
        assert read(STUDENT / (name + ".json"))["passed"]
    source = STUDENT / "package/bot.cpp"
    assert sha(source) == "5502b574b459560722b77e4c21335ad2a0afd41ac9e816e262a7f83196774ccc"
    units = len(source.read_text().encode("utf-16-le")) // 2
    assert units == 80252 and units < 100000
    rows, values, map_ids, evidence = [], {}, {}, {}
    counts, outputs, log_counts = Counter(), Counter(), Counter()
    timing_max, emergencies = Counter(), Counter()
    states = transitions = 0
    expected_commands = None
    raw_digest = hashlib.sha256()
    for block in range(1, 5):
        directory = STUDENT / f"confirm{block}"
        current = [json.loads(line) for line in (directory / "matches.jsonl").read_text().splitlines()]
        report = read(STUDENT / f"confirm{block}-verification.json")
        manifest = read(directory / "manifest.json")
        assert len(current) == report["rows"] == report["clean_games"] == 420
        assert report["passed"] and not report["excluded"] and not report["mismatches"]
        assert report["states"] == report["transitions"] + 420
        assert report["matches_sha256"] == sha(directory / "matches.jsonl")
        assert report["manifest_sha256"] == sha(directory / "manifest.json")
        assert report["verifier_sha256"] == sha(ROOT / "code/rl/v5/deadline_search/verify.py")
        assert list(map(key, current)) == list(map(key, manifest["schedule"]))
        assert manifest["parallel_games"] == 1 and manifest["external_spend"] == 0
        if expected_commands is None:
            expected_commands = manifest["commands"]
        assert manifest["commands"] == expected_commands
        for section in ("sources", "weights", "dependency_sha256"):
            for name, digest in manifest[section].items():
                assert sha(ROOT / name) == digest, name
        novelty = read(STUDENT / f"confirm{block}-novelty.json")
        registry_path = DATA / f"student-confirm{block}-registry.json"
        registry = read(registry_path)
        assert novelty["passed"] and not novelty["overlaps"]
        assert novelty["registry_sha256"] == sha(registry_path)
        assert datetime.fromisoformat(novelty["as_of"]) > datetime.fromisoformat(frozen["as_of"])
        known = set(registry["canonical"])
        states += report["states"]
        transitions += report["transitions"]
        evidence[f"confirm{block}"] = {
            "matches_sha256": report["matches_sha256"],
            "verification_sha256": sha(STUDENT / f"confirm{block}-verification.json"),
            "novelty_sha256": sha(STUDENT / f"confirm{block}-novelty.json"),
        }
        for row in current:
            assert row["valid"] and row["returncode"] == 0
            assert not row["own_action_errors"] and not row["opponent_action_errors"]
            candidate, opponent, seed, seat = key(row)
            stem = f"{candidate}-vs-{opponent}-seed{seed}-seat{seat}"
            raw_path = directory / (stem + "-raw.json")
            raw = read(raw_path)
            raw_digest.update((str(raw_path.relative_to(ROOT)) + " " + sha(raw_path) + "\n").encode())
            assert not raw.get("failCause") and not any(raw["errors"].get("referee", []))
            endings = re.findall(r"\$[01]: ([^\n]+)", "".join(s or "" for s in raw["summaries"]))
            assert all(message in NORMAL for message in endings), (stem, endings)
            own, enemy = raw["scores"][str(seat)], raw["scores"][str(1-seat)]
            assert (own, enemy) == (row["score"], row["opponent_score"])
            result = outcome(own, enemy)
            assert result == row["outcome"]
            assert key(row) not in values
            values[key(row)] = {"win": 1., "draw": .5, "loss": 0.}[result]
            counts[candidate, opponent, result] += 1
            props = dict(line.split("=", 1) for line in "".join(raw["gameParameters"]).splitlines() if "=" in line)
            board = {field: [list(map(int, part.split(","))) for part in props[field].split("_") if part]
                     for field in ("nodes", "units", "edges")}
            digest = hashlib.sha256(json.dumps(board, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            assert digest == row["map_content_sha256"] and digest not in known
            assert map_ids.setdefault(seed, digest) == digest
            output_count = sum(bool(x) for x in raw["outputs"][str(seat)])
            assert output_count == row["own_output_count"]
            stderr = "".join(s or "" for s in raw["errors"][str(seat)])
            if candidate == "student":
                logs = list(map(int, re.findall(r"plan_us=(\d+)", stderr)))
                assert logs == row["own_plan_us"] and len(logs) == output_count
                maximum = max(logs, default=0)
            else:
                logs = [json.loads(line.split("=", 1)[1]) for line in stderr.splitlines() if line.startswith("deadline=")]
                assert logs == row["deadline_measurements"] and len(logs) == output_count
                maximum = max((log["through_flush_us"] for log in logs), default=0)
                emergencies[candidate] += sum(log["search"]["emergency"] for log in logs)
            outputs[candidate] += output_count
            log_counts[candidate] += len(logs)
            timing_max[candidate] = max(timing_max[candidate], maximum)
        rows.extend(current)
    assert list(map(key, rows)) == list(map(key, frozen["schedule"])) and len(rows) == 1680
    assert set(map_ids) == set(SEEDS) and len(set(map_ids.values())) == 40
    assert not any(emergencies.values())
    differences, retention, count_report = {}, {}, {}
    for opponent in OPPONENTS:
        differences[opponent] = [sum(values["student", opponent, seed, p] - values["control", opponent, seed, p]
                                     for p in (0, 1)) / 2 for seed in SEEDS]
        retention[opponent] = [sum(values["student", opponent, seed, p] - values["teacher", opponent, seed, p]
                                   for p in (0, 1)) / 2 for seed in SEEDS]
        count_report[opponent] = {}
        for candidate in CANDIDATES:
            observed = {name: counts[candidate, opponent, name] for name in ("win", "draw", "loss")}
            assert sum(observed.values()) == 80
            count_report[opponent][candidate] = observed
            for mode in ("all_games", "clean_paired"):
                expected = decision[mode]["per_opponent"][opponent]["candidates"][candidate]
                assert all(expected["results"][name] == observed[name] for name in observed)
                compare(estimate([sum(values[candidate, opponent, s, p] for p in (0, 1))/2 for s in SEEDS]), expected["score"])
                for p in (0, 1):
                    compare(estimate([values[candidate, opponent, s, p] for s in SEEDS]), expected["seats"][str(p)]["score"])
    external = estimate([sum(differences[o][i] for o in OPPONENTS[:3])/3 for i in range(40)])
    retained = estimate([sum(retention[o][i] for o in OPPONENTS[:3])/3 for i in range(40)])
    direct = estimate([sum(values["student", "league3m", s, p] for p in (0, 1))/2 for s in SEEDS])
    by_opponent = {o: {"gain": estimate(differences[o]), "student_minus_teacher": estimate(retention[o])} for o in OPPONENTS}
    for mode in ("all_games", "clean_paired"):
        compare(external, decision[mode]["external_gain"])
        compare(retained, decision[mode]["external_student_minus_teacher"])
        compare(direct, decision[mode]["direct_league3m"])
        for o, estimates in by_opponent.items():
            for name, value in estimates.items():
                compare(value, decision[mode]["per_opponent"][o][name])
            for p in (0, 1):
                compare(estimate([values["student", o, s, p] - values["control", o, s, p] for s in SEEDS]),
                        decision[mode]["per_opponent"][o]["seat_gains"][str(p)])
    strength = (external["point_percent"] >= 5 and external["map_95_percent"][0] > 0
                and direct["point_percent"] >= 55 and direct["map_95_percent"][0] > 50
                and all(v["gain"]["point_percent"] >= -5 for v in by_opponent.values()))
    retention_pass = retained["point_percent"] >= -2 and retained["map_95_percent"][0] > -5
    admission = strength and retention_pass
    assert admission == decision["student_gate_passed"]
    for mode in ("all_games", "clean_paired"):
        assert retention_pass == decision[mode]["retention_passed"]
        assert admission == decision[mode]["strategic_thresholds_passed"]
    assert decision["java_native_states"] == states and decision["java_native_transitions"] == transitions
    report = {
        "as_of": datetime.now(timezone.utc).isoformat(), "classification": "PROJECT_REPORTED", "passed": True,
        "student_gate_independently_confirmed": bool(admission), "strength_thresholds_passed": bool(strength),
        "retention_threshold_passed": bool(retention_pass), "raw_games": len(rows), "unique_maps": len(map_ids),
        "technical_errors": 0, "replay_clean_games": len(rows), "replay_excluded": 0,
        "java_states_reported_and_hash_bound": states, "java_transitions_reported_and_hash_bound": transitions,
        "all_games_equals_clean_paired": True, "external_gain": external, "direct_league3m": direct,
        "external_student_minus_teacher": retained, "per_opponent": by_opponent, "raw_counts": count_report,
        "raw_outputs": dict(outputs), "raw_timing_records": dict(log_counts), "maximum_timing_us": dict(timing_max),
        "search_emergencies": dict(emergencies), "package_utf16_units": units,
        "frozen_identity_files_checked": len(identities), "student_freeze_sha256": sha(STUDENT / "freeze.json"),
        "teacher_freeze_sha256": sha(DATA / "freeze.json"), "decision_sha256": sha(STUDENT / "decision.json"),
        "audit_source_sha256": sha(Path(__file__)), "audit_helper_sha256": sha(Path(__file__).with_name("audit_teacher.py")),
        "original_raw_file_aggregate_sha256": raw_digest.hexdigest(), "evidence": evidence,
        "numpy_version": np.__version__, "seconds": time.monotonic()-began,
        "scope": "Independent complete-clean raw score/content/error/timing/schedule audit and paired map bootstrap. No child analyzer import. Existing Java replay reports identity/coverage checked, Java not rerun. Student plan_us excludes input and flush; teacher/control through_flush_us starts at first input token. No platform or leaderboard evidence.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("x") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({name: report[name] for name in ("passed", "student_gate_independently_confirmed", "raw_games",
        "external_gain", "direct_league3m", "external_student_minus_teacher", "seconds")}, indent=2))


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        assert outcome(1, 0) == "win" and outcome(0, 1) == "loss" and outcome(1, 1) == "draw"
        compare(estimate([.5]*40), {"maps": 40, "point_percent": 50., "map_95_percent": [50., 50.]})
        compare(estimate([-.02]*40), {"maps": 40, "point_percent": -2., "map_95_percent": [-2., -2.]})
        print("PASS: outcome and fixed-map bootstrap self-tests")
    else:
        main()
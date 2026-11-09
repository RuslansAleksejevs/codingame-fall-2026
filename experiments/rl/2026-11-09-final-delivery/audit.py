#!/usr/bin/env python3
"""Audit saved final D16 delivery; no API, bot execution or source changes."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHOICE = HERE.parent / "2026-11-09-final-choice"
LIVE = HERE.parent / "2026-11-09-d16-live"
sys.path.insert(0, str(CHOICE))
from audit_candidate import audit
from audit_d16_telemetry import decode, digest, self_test
from audit_tests import d16_telemetry


def telemetry(games):
    self_test()
    totals, tiers, changes = Counter(), Counter(), Counter()
    maxima = {"through_flush_us": 0, "process_cpu_us": 0}
    details, issues = [], []
    for game in games:
        path = ROOT / game["file"]
        assert digest(path) == game["file_sha256"]
        raw = json.loads(path.read_text())
        log = raw.get("log", raw)
        own = [agent for agent in log["agents"] if agent.get("me")]
        assert len(own) == 1
        seat = own[0]["index"]
        frames = [frame for frame in log["frames"] if frame.get("agent") == seat]
        outputs = sum("stdout" in frame for frame in frames)
        text = "".join(frame.get("stderr", "") for frame in frames)
        entry = {"game_id": game["game_id"], "file_sha256": digest(path), "outputs": outputs}
        totals["outputs"] += outputs
        try:
            records = decode(text)
            assert [row["turn"] for row in records] == list(range(1, outputs + 1)), "Turn/output identity"
            assert len(re.findall(r"post_flush_us=([0-9.]+)", text)) == outputs, "Post-flush marker coverage"
            assert all(row["player"] == seat for row in records), "Player identity"
            # Only JSON boundaries are normalized; safety checks and numeric data are reused.
            normalized = {"agents": own, "frames": [
                {"agent": seat, "stdout": "", "stderr": "deadline=" + json.dumps(row) + "\npost_flush_us=0\n"}
                for row in records]}
            safety = d16_telemetry(normalized)
            entry.update(records=len(records), safety_passed=safety["passed"], safety_issues=safety["issues"])
            issues.extend({"game_id": game["game_id"], "issue": item} for item in safety["issues"])
            over20 = []
            for row in records:
                search = row["search"]
                totals["records"] += 1
                totals["complete_d1_evaluations"] += search["shallow_complete"]
                totals["complete_d2_evaluations"] += search["complete"]
                totals["paired_comparison_turns"] += bool(search["paired"])
                totals["deep_comparison_turns"] += search["complete"] >= 2
                totals["nonbaseline_selections"] += search["selected"] > 0
                totals["emergencies"] += search["emergency"]
                totals["incomplete_baselines"] += search["baseline_complete"] != 1
                tiers[str(search["selected_tier"])] += 1
                if search["selected"] > 0:
                    changes[str(search["selected_tier"])] += 1
                if row["turn"] != 1 and row["through_flush_us"] > 20000:
                    over20.append({"turn": row["turn"], "wall_us": row["through_flush_us"],
                                   "cpu_us": row["process_cpu_us"]})
                for key in maxima:
                    maxima[key] = max(maxima[key], row[key])
            totals["nonfirst_wall_over_20ms"] += len(over20)
            entry["nonfirst_wall_over_20ms"] = over20
        except (AssertionError, json.JSONDecodeError, KeyError, TypeError) as error:
            entry["parse_or_identity_error"] = str(error)
            issues.append({"game_id": game["game_id"], "issue": type(error).__name__ + ": " + str(error)})
        details.append(entry)
    if totals["records"] != totals["outputs"]:
        issues.append({"issue": "Decoded record count differs from actual outputs"})
    return {"passed": bool(games) and not issues, "totals": dict(totals), "maxima_us": maxima,
            "selected_tier_counts": dict(tiers), "nonbaseline_tier_counts": dict(changes),
            "issues": issues, "games": details, "synthetic_checks": 5,
            "caveats": ["Exact JSON boundaries and frozen A3 safety checks; raw logs are never rewritten",
                        "Normalized post-flush values are placeholders; original marker counts are checked separately",
                        "Internal post-first-token wall/CPU instrumentation is not official charged whole-turn CPU",
                        "Ordinary wall time above20ms is disclosed, not automatically called an official timeout"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    output = args.out.resolve()
    assert output.is_relative_to(HERE) and not output.exists()
    result = audit(HERE, args.snapshot, args.require_complete)
    result["d16"] = telemetry(result["games"])
    result["as_of"] = datetime.now(timezone.utc).isoformat()
    for path in (Path(__file__), CHOICE / "audit_d16_telemetry.py", LIVE / "audit_tests.py"):
        result["proof_files"][str(path.relative_to(ROOT))] = digest(path)
    result["own_execution_clean"] = not any(result[key] for key in
        ("own_error_games", "own_warning_games", "global_failure_games")) and result["d16"]["passed"]
    with output.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    summary = {key: value for key, value in result.items() if key not in
               ("games", "proof_files", "before_progress", "d16")}
    summary["d16"] = {key: value for key, value in result["d16"].items() if key != "games"}
    print(json.dumps(summary, indent=2))
    return int(not result["own_execution_clean"])


if __name__ == "__main__":
    raise SystemExit(main())
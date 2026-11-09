"""Saved-log A3 same-tier functionality and timing audit; no API actions."""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path

from audit_tests import HERE, ROOT, analyze, d16_telemetry, properties, read, sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    plan = read(HERE / "test-requests-a3.json")
    assert [t["number"] for t in plan["tests"]] == [10, 11, 12]
    assert sha(ROOT / plan["candidate_source"]) == plan["candidate_sha256"]
    issues, timing_review, pending, games, bindings = [], [], [], [], {}
    paired_turns = nonself_nonbaseline = outputs = 0
    for item in plan["tests"]:
        number = item["number"]
        path = HERE / f"test-{number:02d}-complete.json"
        if not path.exists():
            path = HERE / f"test-{number:02d}-result.json"
        if not path.exists() or read(path).get("status") == "running":
            pending.append(number)
            continue
        bindings[path.name] = sha(path)
        data = read(path)
        game = analyze(path)
        game["test_number"] = number
        games.append(game)
        if game["status"] != "done":
            issues.append(f"Test{number}: status {game['status']}")
            continue
        log = data["log"]
        if any(game[k] for k in ("own_errors", "own_warnings", "opponent_errors", "global_errors", "fail_cause")):
            issues.append(f"Test{number}: official error/warning")
        if properties(log["game_options"]) != properties(item["expected_game_options"]):
            issues.append(f"Test{number}: map mismatch")
        seats = [0, 1] if item["expected_own_seat"] == "both" else [item["expected_own_seat"]]
        if game["own_seats"] != seats:
            issues.append(f"Test{number}: own seats mismatch")
        opponents = [a["agent_id"] for a in log["agents"] if not a.get("me")]
        if opponents != item["expected_opponent_ids"]:
            issues.append(f"Test{number}: pinned opponent mismatch")
        integrity = d16_telemetry(log)
        issues.extend(f"Test{number}: {s}" for s in integrity["issues"])
        game["d16_integrity"] = integrity
        game["tiers"] = {}
        for seat in seats:
            text = "".join(f.get("stderr", "") for f in log["frames"] if f.get("agent") == seat)
            records = [json.loads(s.split("=", 1)[1]) for s in text.splitlines() if s.startswith("deadline=")]
            stats = {"outputs": len(records), "paired_turns": 0, "nonbaseline": 0,
                     "selected_tier_counts": {"0": 0, "1": 0, "2": 0},
                     "complete_shallow_evaluations": 0, "complete_deep_evaluations": 0,
                     "wall_us_max": 0, "process_cpu_us_max": 0}
            for row in records:
                s = row["search"]
                shallow, deep, selected, tier = (s[k] for k in ("shallow_complete", "complete", "selected", "selected_tier"))
                expected_tier = 2 if deep >= 2 else 1 if shallow >= 2 else 0
                paired = shallow >= 2 or deep >= 2
                prefix = f"Test{number} seat{seat} turn{row['turn']}"
                if tier != expected_tier or bool(s["paired"]) != paired:
                    issues.append(prefix + ": inconsistent completed tier")
                if len(s["values"]) != deep or len(s["shallow_values"]) != shallow:
                    issues.append(prefix + ": missing completed values")
                if not all(math.isfinite(v) for v in s["values"] + s["shallow_values"]):
                    issues.append(prefix + ": nonfinite score")
                values = s["values"] if tier == 2 else s["shallow_values"] if tier == 1 else []
                if selected:
                    if not values or selected >= len(values) or selected < 0:
                        issues.append(prefix + ": selected incomplete plan")
                    elif values[selected] < values[0] + .02 - 1e-8 or max(values) > values[selected] + 1e-8:
                        issues.append(prefix + ": selected score fails same-tier rule")
                elif values and max(values) > values[0] + .02 + 1e-8:
                    issues.append(prefix + ": missed a completed improving plan")
                cpu, wall = row.get("process_cpu_us"), row.get("through_flush_us")
                if not isinstance(cpu, (float, int)) or not math.isfinite(cpu) or cpu < 0:
                    issues.append(prefix + ": missing/invalid processCPU")
                else:
                    stats["process_cpu_us_max"] = max(stats["process_cpu_us_max"], cpu)
                if not isinstance(wall, (float, int)) or not math.isfinite(wall) or wall < 0:
                    issues.append(prefix + ": missing/invalid wall time")
                else:
                    stats["wall_us_max"] = max(stats["wall_us_max"], wall)
                    if row["turn"] != 1 and wall > 20000:
                        timing_review.append({"test": number, "seat": seat, "turn": row["turn"],
                                              "wall_us": wall, "process_cpu_us": cpu,
                                              "parse_us": row.get("parse_us"), "baseline_us": s["baseline_us"]})
                stats["paired_turns"] += paired
                stats["nonbaseline"] += selected > 0
                stats["selected_tier_counts"][str(tier)] += 1
                stats["complete_shallow_evaluations"] += shallow
                stats["complete_deep_evaluations"] += deep
                paired_turns += paired
                outputs += 1
                if number != 12:
                    nonself_nonbaseline += selected > 0
            game["tiers"][str(seat)] = stats
    complete = not pending and len(games) == 3 and all(g["status"] == "done" for g in games)
    if args.require_complete and not complete:
        issues.append("All three fixed tests required")
    functional = complete and paired_turns >= 10 and nonself_nonbaseline >= 1
    result = {"as_of": datetime.now(timezone.utc).isoformat(), "classification": "PROJECT_REPORTED",
              "complete": complete, "pending": pending, "issues": issues,
              "technical_integrity_passed": not issues, "functional_passed": functional,
              "timing_review_required": timing_review, "outputs": outputs,
              "complete_same_tier_comparison_turns": paired_turns,
              "nonself_nonbaseline_selections": nonself_nonbaseline,
              "platform_admission_passed": complete and not issues and functional and not timing_review,
              "games": games, "result_bindings": bindings,
              "plan_sha256": sha(HERE / "test-requests-a3.json"), "script_sha256": sha(Path(__file__)),
              "caveats": ["Old-map technical functionality, not independent strength or ranking",
                          "ProcessCPU and internal wall exclude startup/pre-first-token/final stderr; neither is official chargedCPU",
                          "Any >20ms normal non-first wall observation needs explicit investigation"]}
    destination = args.out.resolve()
    assert destination.is_relative_to(HERE)
    with destination.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("games", "result_bindings", "script_sha256", "plan_sha256")}, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
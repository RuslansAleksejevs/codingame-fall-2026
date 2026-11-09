"""Post-stop audit of the incomplete v6 final, not a new experiment.

Added after the frozen candidate stopped. The six prospective coordinator
modules remain unchanged. Reads all656 original raw games, binds the existing
Java reports, and uses the unchanged prospective statistics for a descriptive
partial report. It cannot promote a failed/incomplete series to deployment.
"""
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import time

from audit_series import ROOT, DATA, V5, TEACHER_FREEZE, read, sha, portable, compare
from paired import analyze, estimate, key, CANDIDATES, OPPONENTS
from raw import normalize

OUT = DATA / "coordinator/final-stop-audit-attempt2.json"
FAILED_STEM = "candidate-vs-league3m-seed40016-seat1"


def audit():
    frozen = read(DATA / "final-freeze.json")
    assert sha(DATA / "final-freeze.json") == "fb5a052360a1d1932445ced22b2c85c0290e961983b5358069f37fc77c183e47"
    assert sha(V5 / "freeze.json") == TEACHER_FREEZE
    identities = dict(frozen["identities"])
    teacher = read(V5 / "freeze.json")
    for section in ("sources", "weights", "binaries", "dependencies", "protected"):
        for path, digest in teacher[section].items():
            assert identities.setdefault(path, digest) == digest
    for path, digest in frozen["technical_evidence"].items():
        assert identities.setdefault(path, digest) == digest
    for path, digest in identities.items():
        assert sha(ROOT / path) == digest, ("Frozen identity changed", path)
    assert sha(DATA / "PROTOCOL.md") == frozen["protocol_sha256"]
    decision = read(DATA / "final-decision.json")
    assert not decision["gate_passed"] and decision["completed_games"] == 656
    assert decision["own_control_teacher_error_games"] == 1
    assert not decision["checks"]["complete_fixed_schedule"]
    assert not decision["checks"]["zero_own_control_teacher_errors"]
    assert read(DATA / "execution/confirm1-finished.json")["exit_code"] == 0
    assert read(DATA / "execution/confirm2-finished.json")["exit_code"] == 1
    assert not (DATA / "execution/complete.json").exists()
    for n in range(3, 11):
        assert not (DATA / f"confirm{n}").exists()
        assert not (DATA / f"confirm{n}-maps.json").exists()
        assert not (DATA / f"execution/confirm{n}-started.json").exists()
    rows, normalized, evidence = [], [], {}
    maps_seen, opened = {}, set()
    totals = Counter()
    timings, maxima = Counter(), Counter()
    aggregate = hashlib.sha256()
    failure_detail = None
    commands = None
    mandatory = set(read(DATA / "development-map-hashes.json").values())
    for path in V5.rglob("*-map-hashes.json"):
        mandatory.update(read(path).values())
    for number, expected_count in ((1, 420), (2, 236)):
        name = f"confirm{number}"
        directory = DATA / name
        p = directory / "matches.jsonl"
        current = [json.loads(line) for line in p.read_text().splitlines()]
        assert len(current) == expected_count
        manifest = read(directory / "manifest.json")
        assert list(map(key, current)) == list(map(key, manifest["schedule"][:expected_count]))
        assert manifest["parallel_games"] == 1 and manifest["external_spend"] == 0
        assert manifest["first_turn_ms"] == 1000 and manifest["turn_ms"] == 50
        commands = manifest["commands"] if commands is None else commands
        assert manifest["commands"] == commands
        for path, digest in manifest["identities"].items():
            assert identities[path] == digest == sha(ROOT / path)
        novelty, registry = read(DATA / f"{name}-novelty.json"), read(DATA / f"{name}-registry.json")
        assert novelty["passed"] and not novelty["overlaps"]
        assert novelty["registry_sha256"] == sha(DATA / f"{name}-registry.json")
        assert novelty["map_sha256"] == sha(DATA / f"{name}-maps.json")
        assert datetime.fromisoformat(frozen["as_of"]) < datetime.fromisoformat(novelty["as_of"])
        assert datetime.fromisoformat(read(DATA / "parent-final-approval.json")["as_of"]) < datetime.fromisoformat(novelty["as_of"])
        known = set(registry["canonical"])
        assert mandatory <= known and set(maps_seen.values()) <= known
        generated = {r["seed"]: r["hash"] for r in read(DATA / f"{name}-maps.json")["maps"]}
        opened.update(generated)
        replay = read(DATA / f"{name}-verification.json")
        assert replay["passed"] and not replay["mismatches"]
        assert replay["rows"] == len(current)
        assert replay["matches_sha256"] == sha(p)
        assert replay["manifest_sha256"] == sha(directory / "manifest.json")
        assert replay["verifier_sha256"] == sha(ROOT / "code/rl/v5/deadline_search/verify.py")
        transitions = 0
        excluded = set()
        for row in current:
            c, o, seed, seat = key(row)
            stem = f"{c}-vs-{o}-seed{seed}-seat{seat}"
            path, zipped = directory / f"{stem}-raw.json", directory / f"{stem}.json.gz"
            raw = read(path)
            assert json.loads(gzip.decompress(zipped.read_bytes())) == portable(raw)
            record, timing = normalize(raw, row)
            assert not any(record[k] for k in ("own_error", "own_invalid", "referee_error"))
            assert timing["complete_timing"] and row["timing_coverage_pass"] and row["internal_margin_pass"]
            assert record["map_content_sha256"] == generated[seed] and record["map_content_sha256"] not in known
            assert maps_seen.setdefault(seed, record["map_content_sha256"]) == record["map_content_sha256"]
            output_lists = [[x for x in raw["outputs"][str(p)] if x] for p in (0, 1)]
            if record["opponent_error"]:
                excluded.add(stem)
            else:
                assert abs(len(output_lists[0]) - len(output_lists[1])) <= 1
                transitions += min(map(len, output_lists))
            totals["opponent_engine_error_games"] += record["opponent_error"]
            totals["emergency_games"] += record["emergency"]
            totals["emergency_turns"] += timing["emergencies"]
            totals["outputs"] += timing["outputs"]
            totals["timing_records"] += timing["timing_records"]
            timings[c] += timing["timing_records"]
            maxima[c] = max(maxima[c], timing["maximum_through_flush_us"] or 0)
            if record["emergency"]:
                assert name == "confirm2" and stem == FAILED_STEM
                exceptional = [t for t in row["deadline_measurements"] if t["search"]["emergency"]]
                assert len(exceptional) == 1
                event = exceptional[0]
                assert event["turn"] == 27 and event["parse_us"] == 17774.5
                assert event["search"]["forwards"] == event["search"]["generated"] == event["search"]["complete"] == 0
                assert event["search"]["checks"] == 1
                assert output_lists[seat][26].strip() == "WAIT"
                assert row["valid"] and row["outcome"] == "win" and (row["score"], row["opponent_score"]) == (78, -1)
                assert record["points"] == 0
                failure_detail = {
                    "record": stem, "raw_sha256": sha(path), "portable_sha256": sha(zipped),
                    "engine_valid": True, "engine_outcome": "win", "engine_score": [78, -1],
                    "engine_timeout_or_invalid": False, "protocol_points": 0,
                    "actual_turn27_output": output_lists[seat][26], "telemetry": event,
                    "measured_parse_interval": "Wall-clock time from first score token through the remaining read_turn; not CPU-only parsing time.",
                    "confirmed_mechanism": "The first decode check observes the already expired16ms budget. It throws before network evaluation or a complete baseline; initialized WAIT is returned.",
                    "cause_of_long_input_read": "UNKNOWN; existing telemetry cannot separate parsing, input waiting and OS scheduling. No rerun or post-hoc timing correction.",
                }
            normalized.append(record)
            rows.append(row)
            aggregate.update((str(path.relative_to(ROOT)) + " " + sha(path) + "\n" + str(zipped.relative_to(ROOT)) + " " + sha(zipped) + "\n").encode())
        assert set(replay["excluded"]) == excluded and len(replay["excluded"]) == len(excluded)
        assert replay["clean_games"] == len(current) - len(excluded)
        assert replay["transitions"] == transitions and replay["states"] == transitions + replay["clean_games"]
        totals["java_states"] += replay["states"]
        totals["java_transitions"] += replay["transitions"]
        evidence[name] = {"games": len(current), "matches_sha256": sha(p),
                          "verification_sha256": sha(DATA / f"{name}-verification.json"),
                          "java_replay_included": replay["clean_games"], "excluded": sorted(excluded), "transitions": transitions}
    assert len(rows) == 656 and list(map(key, rows)) == list(map(key, frozen["schedule"][:656]))
    assert totals["emergency_games"] == totals["emergency_turns"] == 1 and failure_detail is not None
    assert totals["opponent_engine_error_games"] == 1
    assert opened == set(range(40001, 40021)) and set(maps_seen) == set(range(40001, 40017))
    assert len(set(maps_seen.values())) == len(maps_seen)
    result = analyze(normalized, range(40001, 40101), stage="final", raw_identity_pass=True,
                     replay_pass=True, package_pass=True)
    assert not result["gate_passed"] and result["own_control_teacher_error_games"] == 1
    assert len(result["missing_rows"]) == 3544
    for mode in ("all_games", "clean_paired"):
        actual, recorded = result[mode], decision[mode]
        assert actual["external_maps"] == recorded["external_maps"]
        for metric in ("external_gain", "external_candidate_minus_teacher", "direct_league3m", "direct_b2m"):
            compare(actual[metric], recorded[metric])
        for opponent in OPPONENTS:
            one, two = actual["per_opponent"][opponent], recorded["per_opponent"][opponent]
            assert one["retained_seeds"] == two["retained_seeds"]
            compare(one["gain"], two["gain"])
            compare(one["candidate_minus_teacher"], two["candidate_minus_teacher"])
            for candidate in CANDIDATES:
                a, b = one["candidates"][candidate], two["candidates"][candidate]
                assert all(a["results"][v] == b["results"][v] for v in ("win", "draw", "loss"))
                compare(a["score"], b["score"])
                for seat in ("0", "1"):
                    compare(a["seats"][seat], b["seats"][seat]["score"])
    result.update(passed=True, classification="PROJECT_REPORTED", conclusion="REJECTED_INCOMPLETE_FINAL",
                  strength_conclusion="INCONCLUSIVE; partial series is descriptive only, not the planned100-map confirmation.",
                  native_replay_individually_included_games=655, native_replay_excluded_games=1,
                  failure=failure_detail, evidence=evidence, technical_totals=dict(totals),
                  timing_records_by_candidate=dict(timings), maximum_through_flush_us=dict(maxima),
                  maps_generated=len(opened), maps_actually_played=len(maps_seen),
                  fully_scheduled_maps_completed=15, unopened_final_seeds_inclusive=[40021, 40100],
                  reserve65001_65040="CLOSED", frozen_identity_files_checked=len(identities),
                  freeze_sha256=sha(DATA / "final-freeze.json"), decision_sha256=sha(DATA / "final-decision.json"),
                  original_raw_portable_aggregate_sha256=aggregate.hexdigest(),
                  prior_audit_attempt="final-stop-audit.json preserved: post-stop auditor incorrectly assumed no opponent errors/all656 Java-included. Corrected only this non-frozen audit, not candidate/protocol/data/gates. Actual235/236 inclusion and the single opponent-error exclusion are now checked explicitly.",
                  scope="Independent all656 raw/portable scores/errors/timing/map content and complete-prefix audit; unchanged prospective whole-map statistics matched against the partial child report. Existing Java report identity/coverage checked, Java not rerun. Engine win retained as source fact; protocol emergency counted as failure. No new games, fitting, source edits, platform actions or promotion.")
    return result


def main():
    assert not OUT.exists(), "Preserve every audit attempt"
    began = time.monotonic()
    try:
        result = audit()
    except Exception as error:
        result = {"passed": False, "gate_passed": False, "error_type": type(error).__name__,
                  "audit_error": portable(str(error)), "classification": "PROJECT_REPORTED"}
    result.update(as_of=datetime.now(timezone.utc).isoformat(), seconds=time.monotonic()-began,
                  post_stop_auditor_sha256=sha(Path(__file__)),
                  frozen_helper_sha256={p.name: sha(p) for p in Path(__file__).parent.glob("*.py") if p != Path(__file__)})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: result[k] for k in ("passed", "gate_passed", "conclusion", "completed_games", "audit_error", "seconds") if k in result}, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
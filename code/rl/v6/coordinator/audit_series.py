"""Independent complete v6-series audit, without child analyzer imports.

Reads existing results only. Binds raw/portable trajectories, source identities,
novelty, exact schedule, telemetry and Java replay coverage; recomputes paired
whole-map estimates. A failed audit is preserved, never repaired by replaying a
game. Run under the coordinator compute lease after the relevant panel exits.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import time

import numpy as np

from paired import CANDIDATES, OPPONENTS, analyze, estimate, key
from raw import normalize

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "experiments/rl/2026-11-08-rl6/compact-d16"
V5 = ROOT / "experiments/rl/2026-11-08-rl5/deadline-search"
TEACHER_FREEZE = "3a8a360441013efe735d7f2f3d27e4bdd11e66b84b83323938991bf36987f532"


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def portable(value):
    if isinstance(value, str):
        return value.replace(str(ROOT), "${PROJECT_ROOT}").replace(str(Path.home()), "${HOME}")
    if isinstance(value, list):
        return [portable(v) for v in value]
    if isinstance(value, dict):
        return {k: portable(v) for k, v in value.items()}
    return value


def compare(actual, recorded):
    assert actual["maps"] == recorded["maps"], (actual, recorded)
    for field in ("point_percent", "map_95_percent"):
        if actual["maps"]:
            assert np.allclose(actual[field], recorded[field], atol=1e-10, rtol=0), (field, actual, recorded)
        else:
            assert actual[field] == recorded[field]


def audit(stage):
    frozen_path = DATA / f"{stage}-freeze.json"
    frozen, decision = read(frozen_path), read(DATA / f"{stage}-decision.json")
    seeds = tuple(range(71001, 71013)) if stage == "development" else tuple(range(40001, 40101))
    names = ["development"] if stage == "development" else [f"confirm{i}" for i in range(1, 11)]
    assert frozen["seeds"] == list(seeds) and not frozen["maps_generated"]
    assert frozen["games"] == len(seeds) * 42 and frozen["bootstrap_seed"] == 20261109
    assert sha(DATA / "PROTOCOL.md") == frozen["protocol_sha256"]
    identities = dict(frozen["identities"])
    assert sha(V5 / "freeze.json") == TEACHER_FREEZE
    teacher = read(V5 / "freeze.json")
    for section in ("sources", "weights", "binaries", "dependencies", "protected"):
        for name, digest in teacher[section].items():
            assert identities.setdefault(name, digest) == digest
    for name, digest in frozen["technical_evidence"].items():
        assert identities.setdefault(name, digest) == digest
    for name, digest in identities.items():
        assert sha(ROOT / name) == digest, ("Changed identity", name)
    for source in Path(__file__).parent.glob("*.py"):
        assert identities[str(source.relative_to(ROOT))] == sha(source), ("Unfrozen coordinator source", source.name)
    contracts = read(DATA / "contracts.json")
    assert contracts["passed"] and contracts["saved_games"] >= 100
    assert contracts["nonbaseline_partial_stop_cases"] > 0 and contracts["bitexact_logit_pairs"] > 0
    storage_path = DATA / "coordinator/storage-audit-attempt2.json"
    storage = read(storage_path)
    package = read(DATA / "package-attempt2.json")
    assert storage["passed"] and package["passed"]
    assert storage["package_manifest_sha256"] == sha(DATA / "package-attempt2.json")
    source = ROOT / package["source"]
    assert sha(source) == storage["source_sha256"] == package["source_sha256"] == frozen["source_sha256"]
    assert len(source.read_text().encode("utf-16-le")) // 2 == storage["source_utf16"] <= 98000
    for name in ("regression",):
        report = read(DATA / f"{name}-verification.json")
        assert report["passed"] and report["clean_games"] == 6 and not report["excluded"] and not report["mismatches"]
    mandatory_v5 = set()
    for path in V5.rglob("*-map-hashes.json"):
        mandatory_v5.update(read(path).values())
    assert mandatory_v5, "No v5 map-registry coverage"
    if stage == "final":
        mandatory_v5.update(read(DATA / "development-map-hashes.json").values())
    normalized, raw_rows, evidence = [], [], {}
    maps_seen = {}
    output_counts, telemetry_counts, timing_max, emergency_counts = Counter(), Counter(), Counter(), Counter()
    raw_aggregate = hashlib.sha256()
    total_states = total_transitions = total_included = total_excluded = 0
    expected_commands = None
    technical_telemetry_pass = True
    for name in names:
        directory = DATA / name
        row_path, manifest_path = directory / "matches.jsonl", directory / "manifest.json"
        rows = [json.loads(line) for line in row_path.read_text().splitlines()]
        manifest, verification = read(manifest_path), read(DATA / f"{name}-verification.json")
        novelty, registry = read(DATA / f"{name}-novelty.json"), read(DATA / f"{name}-registry.json")
        assert list(map(key, rows)) == list(map(key, manifest["schedule"]))
        assert verification["passed"] and not verification["mismatches"]
        assert verification["rows"] == len(rows)
        assert verification["matches_sha256"] == sha(row_path)
        assert verification["manifest_sha256"] == sha(manifest_path)
        assert verification["verifier_sha256"] == sha(ROOT / "code/rl/v5/deadline_search/verify.py")
        assert manifest["parallel_games"] == 1 and manifest["external_spend"] == 0
        assert manifest["first_turn_ms"] == 1000 and manifest["turn_ms"] == 50
        if expected_commands is None:
            expected_commands = manifest["commands"]
        assert manifest["commands"] == expected_commands
        for path, digest in manifest["identities"].items():
            assert sha(ROOT / path) == digest == identities[path], ("Manifest/freeze identity mismatch", path)
        assert novelty["passed"] and not novelty["overlaps"]
        assert novelty["registry_sha256"] == sha(DATA / f"{name}-registry.json")
        assert novelty["map_sha256"] == sha(DATA / f"{name}-maps.json")
        assert datetime.fromisoformat(frozen["as_of"]) < datetime.fromisoformat(novelty["as_of"])
        assert datetime.fromisoformat(novelty["as_of"]) <= datetime.fromisoformat(manifest["as_of"])
        known = set(registry["canonical"])
        assert mandatory_v5 <= known, ("Omitted exposed v5/v6 maps", len(mandatory_v5 - known))
        assert set(maps_seen.values()) <= known, "Prior final blocks omitted from registry"
        generated = {entry["seed"]: entry["hash"] for entry in read(DATA / f"{name}-maps.json")["maps"]}
        expected_excluded, tails = set(), {}
        block_transitions = block_included = 0
        for row in rows:
            candidate, opponent, seed, seat = key(row)
            stem = f"{candidate}-vs-{opponent}-seed{seed}-seat{seat}"
            raw_path, portable_path = directory / f"{stem}-raw.json", directory / f"{stem}.json.gz"
            raw = read(raw_path)
            assert portable(raw) == json.loads(gzip.decompress(portable_path.read_bytes())), (name, stem, "Portable copy")
            record, telemetry = normalize(raw, row)
            digest = record["map_content_sha256"]
            assert digest == generated[seed] and digest not in known
            assert maps_seen.setdefault(seed, digest) == digest
            props = dict(line.split("=", 1) for line in "".join(raw["gameParameters"]).splitlines() if "=" in line)
            assert int(props["seed"]) == seed
            stderr = "".join(x or "" for x in raw["errors"][str(seat)])
            post = [float(x) for x in re.findall(r"post_flush_us=([0-9.]+)", stderr)]
            plans = [int(x) for x in re.findall(r"plan_us=(\d+)", stderr)]
            assert row["post_flush_us"] == post and row["own_plan_us"] == plans
            coverage = telemetry["complete_timing"] and len(post) == telemetry["outputs"]
            margin = all(t["through_flush_us"] < 40000 for t in row["deadline_measurements"])
            assert row["timing_coverage_pass"] == coverage and row["internal_margin_pass"] == margin
            assert bool(row["emergency"]) == record["emergency"]
            technical_telemetry_pass &= coverage and margin
            output_counts[candidate] += telemetry["outputs"]
            telemetry_counts[candidate] += telemetry["timing_records"]
            timing_max[candidate] = max(timing_max[candidate], telemetry["maximum_through_flush_us"] or 0)
            emergency_counts[candidate] += telemetry["emergencies"]
            if record["own_error"] or record["opponent_error"] or record["referee_error"]:
                expected_excluded.add(stem)
            else:
                counts = [sum(bool(x) for x in raw["outputs"][str(p)]) for p in (0, 1)]
                assert abs(counts[0] - counts[1]) <= 1, (stem, "Multiple unpaired outputs")
                block_transitions += min(counts)
                block_included += 1
                if counts[0] != counts[1]:
                    survivor = int(counts[1] > counts[0])
                    scores = [raw["scores"][str(p)] for p in (0, 1)]
                    assert scores[1-survivor] == -1 and scores[survivor] >= 0
                    tails[stem] = (survivor, scores, [x for x in raw["outputs"][str(survivor)] if x][-1])
            normalized.append(record)
            raw_rows.append(row)
            for path in (raw_path, portable_path):
                raw_aggregate.update((str(path.relative_to(ROOT)) + " " + sha(path) + "\n").encode())
        assert set(verification["excluded"]) == expected_excluded and len(verification["excluded"]) == len(expected_excluded)
        assert verification["clean_games"] == block_included
        assert verification["transitions"] == block_transitions
        assert verification["states"] == block_transitions + block_included
        actual_tails = {r["record"]: r for r in verification["terminal_unapplied_tails"]}
        assert set(actual_tails) == set(tails) and len(actual_tails) == len(verification["terminal_unapplied_tails"])
        for stem, (survivor, scores, output) in tails.items():
            item = actual_tails[stem]
            assert item["survivor"] == survivor and item["unapplied_commands"] == 1
            assert item["terminal_score"] == scores and item["unapplied_output"] == output
        total_states += verification["states"]
        total_transitions += block_transitions
        total_included += block_included
        total_excluded += len(expected_excluded)
        evidence[name] = {"matches_sha256": sha(row_path), "manifest_sha256": sha(manifest_path),
                          "verification_sha256": sha(DATA / f"{name}-verification.json"),
                          "novelty_sha256": sha(DATA / f"{name}-novelty.json"),
                          "raw_games": len(rows), "replay_included": block_included,
                          "replay_excluded": sorted(expected_excluded)}
    assert list(map(key, raw_rows)) == list(map(key, frozen["schedule"]))
    assert set(maps_seen) == set(seeds) and len(set(maps_seen.values())) == len(seeds)
    result = analyze(normalized, seeds, stage=stage, raw_identity_pass=True,
                     replay_pass=True, package_pass=technical_telemetry_pass)
    assert result["gate_passed"] == decision["gate_passed"], "Independent admission disagreement"
    by = {key(row): row for row in normalized}
    for mode in ("all_games", "clean_paired"):
        actual, recorded = result[mode], decision[mode]
        for metric in ("external_gain", "external_candidate_minus_teacher", "direct_league3m", "direct_b2m"):
            compare(actual[metric], recorded[metric])
        assert actual["external_maps"] == recorded["external_maps"]
        for opponent in OPPONENTS:
            entry, other = actual["per_opponent"][opponent], recorded["per_opponent"][opponent]
            assert entry["retained_seeds"] == other["retained_seeds"]
            compare(entry["gain"], other["gain"])
            compare(entry["candidate_minus_teacher"], other["candidate_minus_teacher"])
            for candidate in CANDIDATES:
                one, two = entry["candidates"][candidate], other["candidates"][candidate]
                assert all(one["results"][label] == two["results"][label] for label in ("win", "draw", "loss"))
                compare(one["score"], two["score"])
                for seat in ("0", "1"):
                    compare(one["seats"][seat], two["seats"][seat]["score"])
        teacher_gain = estimate([sum(by["teacher", o, s, p]["points"] - by["control", o, s, p]["points"]
                                    for o in OPPONENTS[:3] for p in (0, 1))/6 for s in actual["external_maps"]])
        compare(teacher_gain, recorded["external_teacher_minus_control"])
        actual["external_teacher_minus_control"] = teacher_gain
    result.update(passed=True, classification="PROJECT_REPORTED", evidence=evidence,
                  frozen_identity_files_checked=len(identities), freeze_sha256=sha(frozen_path),
                  package_source_sha256=sha(source), package_utf16=storage["source_utf16"],
                  decision_sha256=sha(DATA / f"{stage}-decision.json"),
                  original_raw_portable_aggregate_sha256=raw_aggregate.hexdigest(),
                  java_states_reported_and_hash_bound=total_states,
                  java_transitions_reported_and_hash_bound=total_transitions,
                  individual_replay_included=total_included, individual_replay_excluded=total_excluded,
                  raw_outputs=dict(output_counts), raw_timing_records=dict(telemetry_counts),
                  maximum_through_flush_us=dict(timing_max), emergencies=dict(emergency_counts),
                  independently_checked_v5_exposed_map_hashes=len(mandatory_v5),
                  scope="Independent all-raw outcome/telemetry/identity/schedule/novelty and whole-map bootstrap. Existing Java replay identity and exact inclusion/exclusion/transition coverage bound to the same raw files; Java was not rerun. No platform evidence.")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=("development", "final"))
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    assert not args.out.exists(), "Preserve earlier audit attempts"
    began = time.monotonic()
    try:
        result = audit(args.stage)
    except Exception as error:
        result = {"passed": False, "gate_passed": False, "audit_error": portable(str(error)),
                  "error_type": type(error).__name__, "classification": "PROJECT_REPORTED"}
    result.update(as_of=datetime.now(timezone.utc).isoformat(), seconds=time.monotonic()-began,
                  numpy_version=np.__version__,
                  audit_sources={str(p.relative_to(ROOT)): sha(p) for p in sorted(Path(__file__).parent.glob("*.py"))})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: result[k] for k in ("passed", "gate_passed", "completed_games", "audit_error", "seconds") if k in result}, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
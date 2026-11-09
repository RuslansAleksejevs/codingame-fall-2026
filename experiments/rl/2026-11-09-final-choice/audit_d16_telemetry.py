#!/usr/bin/env python3
"""Supplement the frozen D16 audit: decode JSON objects across stderr chunks."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LIVE = HERE.parent / "2026-11-09-d16-live"
sys.path.insert(0, str(LIVE))
from audit_tests import d16_telemetry


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(text):
    decoder = json.JSONDecoder()
    records = []
    for marker in re.finditer(r"deadline=", text):
        record, end = decoder.raw_decode(text, marker.end())
        assert isinstance(record, dict)
        assert not text[end:] or text[end:].startswith(("\n", "\r", "post_flush_us="))
        records.append(record)
    return records


def self_test():
    a = {"turn": 1, "search": {"values": []}}
    b = {"turn": 2, "search": {"values": [0.5]}}
    for separator in ("\n", "post_flush_us=1.0\n", "post_flush_us=1.0turn=2\n"):
        assert decode("deadline=" + json.dumps(a) + separator + "deadline=" + json.dumps(b)) == [a, b]
    try:
        decode('deadline={"turn":')
    except json.JSONDecodeError:
        pass
    else:
        raise AssertionError("Truncated JSON must not pass")
    try:
        decode('deadline={"turn":1}unexpected')
    except AssertionError:
        pass
    else:
        raise AssertionError("Unrecognized trailing data must not pass")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    self_test()
    audit_path = LIVE / "audit-final.json"
    original = json.loads(audit_path.read_text())
    totals, tiers, changes, recovered, games = Counter(), Counter(), Counter(), [], []
    maxima = {"through_flush_us": 0, "process_cpu_us": 0}
    for game in original["games"]:
        path = ROOT / game["file"]
        assert digest(path) == game["file_sha256"]
        raw = json.loads(path.read_text())
        log = raw.get("log", raw)
        old = d16_telemetry(log)
        own = [agent for agent in log["agents"] if agent.get("me")]
        assert len(own) == 1
        seat = own[0]["index"]
        frames = [frame for frame in log["frames"] if frame.get("agent") == seat]
        outputs = sum("stdout" in frame for frame in frames)
        text = "".join(frame.get("stderr", "") for frame in frames)
        records = decode(text)
        assert [row["turn"] for row in records] == list(range(1, outputs + 1))
        assert len(re.findall(r"post_flush_us=([0-9.]+)", text)) == outputs
        old_records = []
        for line in text.splitlines():
            if line.startswith("deadline="):
                try:
                    old_records.append(json.loads(line[len("deadline="):]))
                except json.JSONDecodeError:
                    pass
        by_turn = {row["turn"]: row for row in records}
        assert all(by_turn[row["turn"]] == row for row in old_records)
        extra = sorted(set(by_turn) - {row["turn"] for row in old_records})
        if extra:
            recovered.append({"game_id": game["game_id"], "turns": extra,
                              "records": [by_turn[turn] for turn in extra]})
        # Normalize boundaries only in memory, then reuse every frozen safety check.
        normalized = {"agents": own, "frames": [{"agent": seat, "stdout": "", "stderr":
            "deadline=" + json.dumps(row) + "\npost_flush_us=0\n"} for row in records]}
        safety = d16_telemetry(normalized)
        assert safety["passed"], safety
        for row in records:
            assert row["player"] == seat
            search = row["search"]
            totals["records"] += 1
            totals["complete_d1_evaluations"] += search["shallow_complete"]
            totals["complete_d2_evaluations"] += search["complete"]
            totals["paired_comparison_turns"] += bool(search["paired"])
            totals["nonbaseline_selections"] += search["selected"] > 0
            totals["emergencies"] += search["emergency"]
            totals["incomplete_baselines"] += search["baseline_complete"] != 1
            totals["nonfirst_wall_over_20ms"] += row["turn"] != 1 and row["through_flush_us"] > 20000
            tiers[str(search["selected_tier"])] += 1
            if search["selected"] > 0:
                changes[str(search["selected_tier"])] += 1
            for key in maxima:
                maxima[key] = max(maxima[key], row[key])
        totals["outputs"] += outputs
        games.append({"game_id": game["game_id"], "file_sha256": digest(path),
                      "outputs": outputs, "records": len(records), "recovered_turns": extra,
                      "old_parser_passed": old["passed"], "normalized_safety_passed": safety["passed"]})
    assert totals["records"] == totals["outputs"] == original["d16_outputs"]
    result = {"as_of": datetime.now(timezone.utc).isoformat(), "classification": "PROJECT_REPORTED",
              "passed": True, "games": games, "totals": dict(totals), "maxima_us": maxima,
              "selected_tier_counts": dict(tiers), "nonbaseline_tier_counts": dict(changes),
              "recovered_records": recovered, "synthetic_checks": 5,
              "explanation": "Five complete JSON objects were followed by another stderr fragment without a newline. Decode the exact JSON boundary; retain all original bytes and the first audit. All formerly parsed records remain identical.",
              "caveat": "Internal timing is not official charged CPU. No game was replayed, no bot or original auditor changed. The normalized safety check uses synthetic post-flush markers only; original marker counts were independently checked.",
              "proof_files": {str(path.relative_to(ROOT)): digest(path) for path in
                              (Path(__file__), LIVE / "audit_tests.py", audit_path)}}
    output = args.out.resolve()
    assert output.is_relative_to(HERE)
    with output.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in ("games", "proof_files", "recovered_records")}, indent=2))


if __name__ == "__main__":
    main()
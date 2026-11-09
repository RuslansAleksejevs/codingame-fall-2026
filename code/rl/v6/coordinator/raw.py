"""Independent raw-referee normalization, not the experiment's row analyzer."""
import hashlib
import json
import math
import re

NORMAL_ENDS = {"is dominated", "no units or triangles left", "can't score any more points"}


def board_from_raw(raw):
    props = dict(line.split("=", 1) for line in "".join(raw["gameParameters"]).splitlines() if "=" in line)
    board = {field: [list(map(int, item.split(","))) for item in props[field].split("_") if item]
             for field in ("nodes", "units", "edges")}
    digest = hashlib.sha256(json.dumps(board, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return board, digest


def normalize(raw, row):
    """Verify recorded scores/errors/telemetry and derive a statistical row.

    A genuine own technical failure is retained as zero points in the all-game
    estimate even if the engine happened to supply a favorable partial score.
    Opponent failures retain engine outcomes only in all-games. They invalidate
    the full six-game paired cluster in the separate clean estimate.
    """
    seat = row["seat"]
    assert type(seat) is int and seat in (0, 1)
    own, enemy = raw.get("scores", {}).get(str(seat)), raw.get("scores", {}).get(str(1 - seat))
    referee_errors = [x for x in raw.get("errors", {}).get("referee", []) if x]
    numeric = all(type(x) in (int, float) and math.isfinite(x) for x in (own, enemy))
    valid = numeric and not raw.get("failCause") and not referee_errors
    outcome = ("win" if own > enemy else "loss" if own < enemy else "draw") if valid else "invalid"
    summaries = "".join(x or "" for x in raw.get("summaries", []))
    messages = [re.findall(r"\$" + str(p) + r": ([^\n]+)", summaries) for p in (0, 1)]
    errors = [[message for message in player if message not in NORMAL_ENDS] for player in messages]
    for field, actual in (("valid", bool(valid)), ("score", own), ("opponent_score", enemy),
                          ("outcome", outcome), ("own_action_errors", errors[seat]),
                          ("opponent_action_errors", errors[1-seat]), ("referee_errors", referee_errors),
                          ("fail_cause", raw.get("failCause"))):
        assert field in row and row[field] == actual, (field, row.get(field), actual)
    own_error = bool(not valid or row["returncode"] != 0 or errors[seat])
    opponent_error = bool(errors[1-seat])
    _, map_hash = board_from_raw(raw)
    assert map_hash == row["map_content_sha256"]
    outputs = [x for x in raw.get("outputs", {}).get(str(seat), []) if x]
    assert len(outputs) == row["own_output_count"]
    stderr = "".join(x or "" for x in raw.get("errors", {}).get(str(seat), []))
    timing = [json.loads(line.split("=", 1)[1]) for line in stderr.splitlines() if line.startswith("deadline=")]
    assert timing == row["deadline_measurements"]
    # Timing coverage can be incomplete when an actual engine failure occurred.
    # Such a game cannot pass deployment, but remains in the report without rerun.
    complete_timing = len(timing) == len(outputs)
    if not own_error:
        assert complete_timing, "Missing telemetry in a nominally valid game"
    for measurement in timing:
        assert type(measurement["through_flush_us"]) in (int, float)
        assert math.isfinite(measurement["through_flush_us"]) and measurement["through_flush_us"] >= 0
        assert type(measurement["search"]["emergency"]) in (int, bool)
    emergencies = sum(bool(t["search"]["emergency"]) for t in timing)
    points = 0. if own_error or emergencies else {"win": 1., "draw": .5, "loss": 0.}[outcome]
    normalized = {name: row[name] for name in ("candidate", "opponent", "seed", "seat")}
    normalized.update(points=points, map_content_sha256=map_hash,
                      own_error=own_error, opponent_error=opponent_error,
                      own_invalid=any("invalid" in x.lower() for x in errors[seat]),
                      opponent_invalid=any("invalid" in x.lower() for x in errors[1-seat]),
                      emergency=bool(emergencies), referee_error=bool(referee_errors or raw.get("failCause")))
    return normalized, {"outputs": len(outputs), "timing_records": len(timing),
                        "complete_timing": complete_timing, "emergencies": emergencies,
                        "maximum_through_flush_us": max((x["through_flush_us"] for x in timing), default=None),
                        "own_messages": messages[seat], "opponent_messages": messages[1-seat]}
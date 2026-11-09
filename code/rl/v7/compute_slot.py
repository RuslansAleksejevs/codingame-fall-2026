#!/usr/bin/env python3
"""Finite RL-v7 allocation; shares the old global lock, never resets old ledgers."""
import argparse
from datetime import datetime, timezone
import fcntl
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[3]
LOCK = ROOT / ".context/rl4-compute/slot.lock"
STATE = ROOT / ".context/rl7-compute"
CUTOFF_TEXT = "2026-11-09T06:00:00Z"
CUTOFF = datetime(2026, 11, 9, 6, tzinfo=timezone.utc).timestamp()
CAPS = {"d16": 90 * 60, "diversity": 120 * 60, "coordinator": 15 * 60}


def stamp():
    return datetime.now(timezone.utc).isoformat()


def append(path, record):
    with path.open("a") as stream:
        stream.write(json.dumps(record) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def usage(records):
    """Unclosed reservations are charged fully; a crash cannot refresh a budget."""
    starts, finishes = {}, {}
    for record in records:
        if record["event"] == "started":
            assert record["lease_id"] not in starts, "Duplicate lease"
            starts[record["lease_id"]] = record
        elif record["event"] == "finished":
            assert record["lease_id"] not in finishes, "Duplicate completion"
            finishes[record["lease_id"]] = record
    assert finishes.keys() <= starts.keys(), "Completion without reservation"
    spent = {owner: 0.0 for owner in CAPS}
    incomplete = []
    for identity, start in starts.items():
        owner = start["owner"]
        if identity in finishes:
            end = finishes[identity]
            assert end["owner"] == owner
            seconds = end["seconds"]
        else:
            seconds = start["allowed_seconds"]
            incomplete.append(identity)
        assert math.isfinite(seconds) and seconds >= 0
        spent[owner] += seconds
    return spent, incomplete


def terminate_group(process):
    # Only this wrapper's newly created process group is targeted.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", choices=CAPS)
    parser.add_argument("--minutes", type=float, default=25)
    parser.add_argument("--status", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not args.status and (not args.owner or not command or not 0 < args.minutes <= 25):
        parser.error("Use --owner, --minutes in (0,25], and -- command")
    cwd = Path.cwd().resolve()
    if not cwd.is_relative_to(ROOT):
        parser.error("Run inside the original repository")
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    STATE.mkdir(parents=True, exist_ok=True)
    events = STATE / "events.jsonl"
    with LOCK.open("a+") as lease:
        try:
            fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            lease.seek(0)
            print(json.dumps({"status": "busy", "holder": lease.read(), "retry": "wait durably; do not bypass"}), flush=True)
            return 0 if args.status else 75
        records = [json.loads(line) for line in events.read_text().splitlines()] if events.exists() else []
        spent, incomplete = usage(records)
        if args.status:
            print(json.dumps({"status": "available", "spent_seconds": spent, "caps_seconds": CAPS,
                              "unclosed_charged_leases": incomplete, "cutoff": CUTOFF_TEXT}), flush=True)
            return 0
        if incomplete:
            print(json.dumps({"status": "unclosed_lease_requires_scoped_process_check", "leases": incomplete}), flush=True)
            return 77
        allowed = min(args.minutes * 60, CUTOFF - time.time(), CAPS[args.owner] - spent[args.owner])
        if allowed <= 0:
            print(json.dumps({"status": "budget_or_cutoff_reached", "owner": args.owner}), flush=True)
            return 76
        record = {"event": "started", "lease_id": uuid.uuid4().hex, "as_of": stamp(),
                  "owner": args.owner, "phase": "rl7", "wrapper_pid": os.getpid(),
                  "cwd": str(cwd.relative_to(ROOT)), "command": command, "allowed_seconds": allowed}
        lease.seek(0)
        lease.truncate()
        lease.write(json.dumps(record))
        lease.flush()
        append(events, record)
        process = None
        began = time.monotonic()
        outcome, exit_code = "finished", 1

        def interrupted(signum, frame):
            raise KeyboardInterrupt(f"signal {signum}")

        signal.signal(signal.SIGTERM, interrupted)
        signal.signal(signal.SIGINT, interrupted)
        try:
            process = subprocess.Popen(command, start_new_session=True)
            print(json.dumps({"status": "started", "lease_id": record["lease_id"],
                              "owner": args.owner, "child_pid": process.pid, "allowed_seconds": allowed}), flush=True)
            try:
                exit_code = process.wait(timeout=allowed)
            except subprocess.TimeoutExpired:
                outcome, exit_code = "timeout", 124
        except KeyboardInterrupt:
            outcome, exit_code = "interrupted", 130
        except OSError as error:
            outcome = "launch_failed"
            print(json.dumps({"status": outcome, "error": str(error)}), flush=True)
        finally:
            if process is not None:
                terminate_group(process)
            ended = {"event": "finished", "lease_id": record["lease_id"], "as_of": stamp(),
                     "owner": args.owner, "seconds": time.monotonic() - began,
                     "outcome": outcome, "exit_code": exit_code}
            append(events, ended)
            lease.seek(0)
            lease.truncate()
            lease.write(json.dumps(ended))
            lease.flush()
            print(json.dumps(ended), flush=True)
        return exit_code if exit_code >= 0 else 128 - exit_code


if __name__ == "__main__":
    sys.exit(main())
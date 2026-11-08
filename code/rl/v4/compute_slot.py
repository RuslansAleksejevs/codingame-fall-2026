#!/usr/bin/env python3
"""One bounded local CPU job across the three RL-v4 research lanes."""
import argparse
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
STATE = ROOT / ".context/rl4-compute"
CUTOFF = datetime(2026, 11, 9, 2, tzinfo=timezone.utc).timestamp()
OWNERS = ("exploiters", "curriculum", "search-teacher", "coordinator")


def stamp():
    return datetime.now(timezone.utc).isoformat()


def append(path, record):
    with path.open("a") as output:
        output.write(json.dumps(record) + "\n")
        output.flush()
        os.fsync(output.fileno())


def terminate_group(process):
    # Only this wrapper's newly-created process group is ever targeted.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", choices=OWNERS)
    parser.add_argument("--minutes", type=float, default=25)
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--state-dir", type=Path, default=STATE, help=argparse.SUPPRESS)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    state = args.state_dir.resolve()
    if not state.is_relative_to(ROOT / ".context"):
        parser.error("State must remain inside the repository .context directory")
    state.mkdir(parents=True, exist_ok=True)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not args.status and (not args.owner or not command or not 0 < args.minutes <= 25):
        parser.error("Provide --owner, --minutes in (0,25], and -- command")
    with (state / "slot.lock").open("a+") as lease:
        try:
            fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            lease.seek(0)
            print(json.dumps({"status": "busy", "holder": lease.read(), "retry": "schedule another check; do not bypass"}), flush=True)
            return 0 if args.status else 75
        events = state / "events.jsonl"
        spent = {owner: 0.0 for owner in OWNERS}
        if events.exists():
            for line in events.read_text().splitlines():
                record = json.loads(line)
                if record.get("event") == "finished":
                    spent[record["owner"]] += record["seconds"]
        if args.status:
            print(json.dumps({"status": "available", "spent_seconds": spent, "cutoff": "2026-11-09T02:00:00Z"}), flush=True)
            return 0
        remaining = min(args.minutes * 60, CUTOFF - time.time(), 4 * 3600 - spent[args.owner])
        if remaining <= 0:
            print(json.dumps({"status": "budget_or_cutoff_reached", "owner": args.owner}), flush=True)
            return 76
        cwd = Path.cwd().resolve()
        if not cwd.is_relative_to(ROOT):
            parser.error("Run the command inside the original repository")
        record = {"event": "started", "as_of": stamp(), "owner": args.owner,
                  "wrapper_pid": os.getpid(), "command": command,
                  "cwd": str(cwd.relative_to(ROOT)), "allowed_seconds": remaining}
        lease.seek(0)
        lease.truncate()
        lease.write(json.dumps(record))
        lease.flush()
        append(events, record)
        process = None
        began = time.monotonic()
        outcome = "finished"
        exit_code = 1

        def interrupted(signum, frame):
            raise KeyboardInterrupt(f"signal {signum}")

        signal.signal(signal.SIGTERM, interrupted)
        signal.signal(signal.SIGINT, interrupted)
        try:
            process = subprocess.Popen(command, start_new_session=True)
            print(json.dumps({"status": "started", "owner": args.owner, "child_pid": process.pid,
                              "allowed_seconds": remaining}), flush=True)
            try:
                exit_code = process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                outcome, exit_code = "timeout", 124
                terminate_group(process)
        except KeyboardInterrupt:
            outcome, exit_code = "interrupted", 130
            if process is not None:
                terminate_group(process)
        except OSError as error:
            outcome = "launch_failed"
            print(json.dumps({"status": outcome, "error": str(error)}), flush=True)
        finally:
            # No detached grandchildren may continue after the exclusive lease ends.
            if process is not None:
                terminate_group(process)
            ended = {"event": "finished", "as_of": stamp(), "owner": args.owner,
                     "seconds": time.monotonic() - began, "outcome": outcome, "exit_code": exit_code}
            append(events, ended)
            lease.seek(0)
            lease.truncate()
            lease.write(json.dumps(ended))
            lease.flush()
            print(json.dumps(ended), flush=True)
        return exit_code if exit_code >= 0 else 128 - exit_code


if __name__ == "__main__":
    sys.exit(main())
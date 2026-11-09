#!/usr/bin/env python3
"""Small live-lock tests, charged to the coordinator's new allocation."""
import fcntl
import json
import subprocess
import sys
from pathlib import Path
import compute_slot as slot


def invoke(*args):
    result = subprocess.run([sys.executable, str(Path(slot.__file__)), *args],
                            text=True, capture_output=True, cwd=slot.ROOT, timeout=10)
    print(result.stdout, end="")
    return result


def main():
    spent, incomplete = slot.usage([
        {"event": "started", "lease_id": "a", "owner": "d16", "allowed_seconds": 10},
        {"event": "finished", "lease_id": "a", "owner": "d16", "seconds": 2},
        {"event": "started", "lease_id": "b", "owner": "diversity", "allowed_seconds": 20},
    ])
    assert spent == {"d16": 2, "diversity": 20, "coordinator": 0}
    assert incomplete == ["b"]
    assert invoke("--owner", "coordinator", "--minutes", "0.1", "--", sys.executable, "-c", "pass").returncode == 0
    assert invoke("--owner", "coordinator", "--minutes", "0.005", "--", sys.executable, "-c", "import time; time.sleep(2)").returncode == 124
    with slot.LOCK.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = invoke("--owner", "coordinator", "--minutes", "0.1", "--", sys.executable, "-c", "pass")
        assert result.returncode == 75
        assert json.loads(result.stdout)["status"] == "busy"
    result = invoke("--status")
    assert result.returncode == 0
    assert not json.loads(result.stdout)["unclosed_charged_leases"]
    print("PASS: accounting, normal exit, bounded timeout, shared lock, released lease")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""Regenerate the reproducibility manifest for the explicitly staged snapshot."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    unstaged = subprocess.check_output(["git", "diff", "--name-only", "-z"], cwd=ROOT)
    if any(p and p != b"CHECKSUMS.json" for p in unstaged.split(b"\0")):
        raise SystemExit("Stage the selected tracked changes before generating their checksums")
    paths = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    checks = {p.decode(): hashlib.sha256((ROOT / p.decode()).read_bytes()).hexdigest()
              for p in paths.split(b"\0") if p and p != b"CHECKSUMS.json"}
    (ROOT / "CHECKSUMS.json").write_text(json.dumps(checks, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"sha256_entries": len(checks)}))


if __name__ == "__main__":
    main()
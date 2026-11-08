#!/usr/bin/env python3
"""Offline tracked-snapshot integrity and current documentation checks; no jobs or API."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
ENTRY_DOCS = ("README.md", "docs/STATUS.md", "docs/QUICKSTART.md", "docs/ARCHIVE.md", "docs/rl/README.md",
              "docs/rl/LAST_DAY_OPTIONS.md", "docs/rl/AI_COMPETITION_EDGE.md")


def check(skip_checksums=False):
    paths = [p.decode() for p in subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).split(b"\0") if p]
    tracked = set(paths)
    problems = []
    links = 0
    for name in paths:
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            problems.append([name, "missing file or unexpected symlink"])
        elif path.stat().st_size >= 100 * 1024 * 1024:
            problems.append([name, "GitHub file size limit"])
    for name in ENTRY_DOCS:
        path = ROOT / name
        if not path.exists():
            problems.append([name, "missing current entry document"])
            continue
        text = re.sub(r"```.*?```", "", path.read_text(), flags=re.S)
        for destination in re.findall(r"\]\(([^)]+)\)", text):
            target = destination.split("#", 1)[0].strip("<>")
            if not target or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            resolved = (path.parent / unquote(target)).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                problems.append([name, "broken local link", destination])
                continue
            relative = str(resolved.relative_to(ROOT))
            if resolved.is_file() and relative not in tracked:
                problems.append([name, "link target is not staged/tracked", destination])
            elif resolved.is_dir() and not any(p.startswith(relative + "/") for p in tracked):
                problems.append([name, "linked directory has no tracked files", destination])
            links += 1
    for name in ("code/split_evidence.py", "code/check_repository.py", "code/rl/inspect_teacher_storage.py"):
        ast.parse((ROOT / name).read_text(), filename=name)
    checksum_count = 0
    if not skip_checksums:
        checks = json.loads((ROOT / "CHECKSUMS.json").read_text())
        if set(checks) != tracked - {"CHECKSUMS.json"}:
            problems.append(["CHECKSUMS.json", "tracked path coverage differs"])
        for name, expected in checks.items():
            path = ROOT / name
            if not path.is_file():
                continue
            with path.open("rb") as source:
                actual = hashlib.file_digest(source, "sha256").hexdigest()
            if actual != expected:
                problems.append([name, "SHA256 mismatch"])
            checksum_count += 1
    result = {"passed": not problems, "tracked_files": len(paths), "local_links_checked": links,
              "sha256_entries_checked": checksum_count, "problems": problems}
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-checksums", action="store_true", help="For review before regenerating the staged manifest")
    raise SystemExit(check(parser.parse_args().skip_checksums))
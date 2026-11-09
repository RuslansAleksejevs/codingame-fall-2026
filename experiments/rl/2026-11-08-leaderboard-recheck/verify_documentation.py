#!/usr/bin/env python3
"""Read-only documentation/source checks; write a new audit receipt on request."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
DOCS = ["README.md", "docs/STATUS.md", "docs/rl/README.md",
        "docs/EXPERIMENT_TIMELINE.md",
        "experiments/rl/2026-11-08-leaderboard-recheck/REQUEST.md",
        "experiments/rl/2026-11-08-leaderboard-recheck/REPORT.md",
        "experiments/rl/2026-11-08-leaderboard-recheck/COMMANDS.md"]
PROTECTED = {
    "submissions/ppo-v2-league3m.cpp":
        "199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1",
    "experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/checkpoint.pt":
        "9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663",
    "experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt":
        "dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb",
    "experiments/rl/2026-11-07-ppo-v3/handoff-b2m/bot.cpp":
        "b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    checks, links, issues = {}, [], []
    for name in DOCS:
        path = ROOT / name
        text = path.read_text()
        checks[name] = {"sha256": sha(path), "lines": len(text.splitlines())}
        for target in re.findall(r"\[[^\]\n]*\]\(([^)]+)\)", text):
            if re.match(r"[a-zA-Z]+:|#", target):
                continue
            resolved = (path.parent / unquote(target.split("#", 1)[0])).resolve()
            ok = resolved.is_relative_to(ROOT) and resolved.exists()
            links.append({"document": name, "target": target, "exists": ok})
            if not ok:
                issues.append(f"Missing local link: {name} -> {target}")
        if re.search(r"[\u0400-\u04ff]", text):
            issues.append(f"Unexpected Cyrillic prose: {name}")
        if re.search(r"/Users/|cgp_[A-Za-z0-9]{42}|device_code|access_token", text):
            issues.append(f"Private-path/credential-field marker: {name}")
    identities = {}
    for name, expected in PROTECTED.items():
        actual = sha(ROOT / name)
        identities[name] = {"sha256": actual, "matches_expected": actual == expected}
        if actual != expected:
            issues.append(f"Protected identity mismatch: {name}")
    source = (ROOT / "submissions/ppo-v2-league3m.cpp").read_text()
    size = {"utf8_bytes": len(source.encode()),
            "utf16_units": len(source.encode("utf-16-le")) // 2}
    if size["utf16_units"] != 80247:
        issues.append("Unexpected selected package size")
    whitespace = subprocess.run(["git", "diff", "--check"], cwd=ROOT,
                                capture_output=True, text=True)
    if whitespace.returncode:
        issues.append(whitespace.stdout + whitespace.stderr)
    result = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "classification": "PROJECT_REPORTED",
        "scope": "Changed navigation/timeline and protected source identities only; no new games",
        "python": platform.python_version(), "documents": checks,
        "local_link_count": len(links), "links": links,
        "protected_artifacts": identities, "selected_source_size": size,
        "git_diff_check_pass": whitespace.returncode == 0,
        "issues": issues, "passed": not issues,
        "limitations": ["Does not fetch external links or verify every historical measurement anew",
                        "Credential marker check is heuristic, not a comprehensive security audit",
                        "Does not refresh GitHub, run Java or claim a live ranking result"],
    }
    if args.out:
        destination = args.out.resolve()
        assert destination.is_relative_to(Path(__file__).resolve().parent)
        with destination.open("x") as handle:
            handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("links", "documents")}, indent=2))
    raise SystemExit(bool(issues))


if __name__ == "__main__":
    main()
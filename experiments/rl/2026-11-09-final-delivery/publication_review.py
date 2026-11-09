#!/usr/bin/env python3
"""Review only the requested final-delivery publication; never stage or push."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOCS = {
    "README.md", "docs/BOT_PORTFOLIO.md", "docs/CONTEST_DELIVERY.md",
    "docs/EXPERIMENT_TIMELINE.md", "docs/STATUS.md", "docs/rl/README.md",
    "docs/rl/v7/D16.md", "docs/rl/v7/PLAN.md",
    "experiments/rl/2026-11-09-d16-live/REPORT.md",
}
PREFIXES = (
    "experiments/rl/2026-11-09-final-choice/",
    "experiments/rl/2026-11-09-final-delivery/",
    "experiments/rl/2026-11-09-d16-live/",
)
SECRET = re.compile(r"cgp_[A-Za-z0-9]{42}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
PRIVATE_PATH = re.compile(r"/(?:Users|home)/[^\s\"']+")
CREDENTIAL_KEY = re.compile(r'"(?:access_token|refresh_token|device_code|user_code|verification_uri_complete|registration_form|email)"\s*:')


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def paths(*args):
    return [item.decode() for item in git(*args).split(b"\0") if item]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    output = args.out.resolve()
    assert output.is_relative_to(HERE) and not output.exists()
    assert not paths("diff", "--cached", "--name-only", "-z"), "Review expects an empty index"
    tracked_changes = set(paths("diff", "--name-only", "-z"))
    assert tracked_changes <= DOCS, sorted(tracked_changes - DOCS)
    untracked = paths("ls-files", "--others", "--exclude-standard", "-z")
    copies = [p for p in untracked if re.search(r" 2(?:\.|$)", Path(p).name)]
    new = [p for p in untracked if p not in copies and p.startswith(PREFIXES)]
    unrelated = set(untracked) - set(copies) - set(new)
    selected = sorted(tracked_changes | set(new))
    problems, links, hashes, sizes = [], [], {}, {}
    for name in selected:
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            problems.append([name, "Unexpected link or missing file"])
            continue
        if path.suffix not in {".md", ".json", ".py"}:
            problems.append([name, "Unexpected new publication format"])
        size = path.stat().st_size
        if size >= 100 * 1024 * 1024:
            problems.append([name, "GitHub file-size limit"])
        hashes[name], sizes[name] = digest(path), size
        text = path.read_text()
        for label, pattern in (("credential-value marker", SECRET), ("personal path", PRIVATE_PATH),
                               ("credential/personal JSON field", CREDENTIAL_KEY)):
            if pattern.search(text):
                problems.append([name, label])
        if path.suffix == ".json":
            json.loads(text)
        elif path.suffix == ".py":
            compile(text, name, "exec")
        elif path.suffix == ".md":
            if re.search(r"[\u0400-\u04ff]", text):
                problems.append([name, "Non-English documentation"])
            for target in re.findall(r"\[[^\]\n]*\]\(([^)]+)\)", text):
                if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:|#", target):
                    continue
                resolved = (path.parent / unquote(target.split("#", 1)[0].strip("<>"))).resolve()
                ok = resolved.is_relative_to(ROOT) and resolved.exists()
                links.append({"document": name, "target": target, "exists": ok})
                if not ok:
                    problems.append([name, "Broken link", target])
    old = json.loads(git("show", "HEAD:CHECKSUMS.json"))
    unchanged = 0
    for name, expected in old.items():
        if name in tracked_changes:
            continue
        if digest(ROOT / name) != expected:
            problems.append([name, "Previously published non-document content changed"])
        unchanged += 1
    whitespace = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True)
    if whitespace.returncode:
        problems.append(["git diff --check", whitespace.stdout, whitespace.stderr])
    result = {
        "as_of": datetime.now(timezone.utc).isoformat(), "provenance": "PROJECT_REPORTED",
        "passed": not problems, "selected_count": len(selected), "selected_paths": selected,
        "sha256": hashes, "sizes": sizes, "total_selected_bytes": sum(sizes.values()),
        "old_nonchanged_sha256_verified": unchanged, "local_links_checked": len(links),
        "links": links, "excluded_suffix_copies": len(copies),
        "other_unrelated_untracked_excluded": sorted(unrelated), "problems": problems,
        "head_before": git("rev-parse", "HEAD").decode().strip(),
        "caveats": ["Read-only selection review, not a Git publication or live submission",
                    "Privacy heuristics supplement manual review; no exhaustive privacy guarantee",
                    "Excluded suffix copies are preserved; their content identity/origin is unknown",
                    "This receipt is added separately and receives its hash in the staged CHECKSUMS manifest"]}
    with output.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key not in
                     ("selected_paths", "sha256", "sizes", "links")}, indent=2))
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
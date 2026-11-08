"""Read-only independent archive/original coverage audit; no extraction or Git."""
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "experiments/rl/2026-11-08-rl5/deadline-search"
CODE = ROOT / "code/rl/v5/deadline_search"
OUT = DATA.parent / "coordinator/archive-audit.json"
MUTABLE = {"evidence.tar.gz", "evidence-manifest.json", "COMPLETION.json", "inventory.json", "STATUS.json", "HISTORY.md"}
LATE_CLOSEOUT = {"experiments/rl/2026-11-08-rl5/deadline-search/lease-ledger-final.json"}
MAGIC = (b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\x7fELF", b"\xca\xfe\xba\xbe")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def scan(data, name):
    assert str(ROOT).encode() not in data and str(Path.home()).encode() not in data, ("host_path", name)
    assert not data.startswith(MAGIC), ("executable", name)
    assert not re.search(rb"(?i)(?:bearer\s+[a-z0-9._~-]{24,}|sk-[a-z0-9_-]{32,})", data), ("credential_form", name)


def main():
    began = time.monotonic()
    assert not OUT.exists(), "Preserve earlier audit"
    manifest_path = DATA / "evidence-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    archive_path = DATA / "evidence.tar.gz"
    assert archive_path.stat().st_size == manifest["compressed_bytes"]
    archive_sha = digest(archive_path.read_bytes())
    assert archive_sha == manifest["archive_sha256"] == "1af8db533a3cdfa7c501373e1053c016d6a401324df169bd1f551b3f94b53728"
    entries = {entry["path"]: entry for entry in manifest["entries"]}
    assert len(entries) == len(manifest["entries"]) == manifest["members"] == 12244
    expected = set()
    excluded = []
    for root in (CODE, DATA):
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            relative = str(path.relative_to(ROOT))
            if ("build" in path.relative_to(root).parts or "__pycache__" in path.parts
                    or path.name in MUTABLE or path.suffix in (".dylib", ".so", ".pyc", ".class")):
                excluded.append(relative)
            else:
                expected.add(relative)
    expected.add("docs/rl/v5/DEADLINE_SEARCH.md")
    inventory_path = DATA / "inventory.json"
    inventory = json.loads(inventory_path.read_text())
    inventory_entries = {entry["path"]: entry for entry in inventory["entries"]}
    late = {}
    for name in expected & LATE_CLOSEOUT:
        data = (ROOT / name).read_bytes()
        ledger = json.loads(data)
        assert datetime.fromisoformat(ledger["as_of"]) > datetime.fromisoformat(manifest["as_of"])
        assert digest(data) == inventory_entries[name]["sha256"]
        scan(data, name)
        late[name] = digest(data)
    expected.difference_update(late)
    assert expected == set(entries), {"uncovered": sorted(expected-set(entries)), "unexpected": sorted(set(entries)-expected)}
    seen = set()
    raw_games = scientific_members = compressed_text_members = content_bytes = 0
    with tarfile.open(archive_path, "r|gz") as archive:
        for member in archive:
            assert member.isfile() and member.name not in seen and member.name in entries
            assert not Path(member.name).is_absolute() and ".." not in Path(member.name).parts
            seen.add(member.name)
            original_path = ROOT / member.name
            assert original_path.resolve().is_relative_to(ROOT)
            data = archive.extractfile(member).read()
            entry = entries[member.name]
            assert len(data) == member.size == entry["bytes"]
            assert digest(data) == entry["sha256"] == digest(original_path.read_bytes()), member.name
            scan(data, member.name)
            suffix = Path(member.name).suffix
            if suffix == ".gz":
                scan(gzip.decompress(data), member.name)
                compressed_text_members += 1
            if suffix in (".pt", ".npz"):
                with zipfile.ZipFile(io.BytesIO(data)) as scientific:
                    for inside in scientific.namelist():
                        scan(scientific.read(inside), member.name + ":" + inside)
                scientific_members += 1
            raw_games += member.name.endswith("-raw.json")
            content_bytes += len(data)
    assert seen == expected
    for name, entry in inventory_entries.items():
        assert digest((ROOT / name).read_bytes()) == entry["sha256"], name
    for path, expected_sha in manifest["protected"].items():
        assert digest((ROOT / path).read_bytes()) == expected_sha, path
    report = {
        "as_of": datetime.now(timezone.utc).isoformat(), "classification": "PROJECT_REPORTED", "passed": True,
        "archive_sha256": archive_sha, "manifest_sha256": digest(manifest_path.read_bytes()),
        "members_checked": len(seen), "original_files_checked": len(seen), "coverage_missing": 0,
        "compressed_bytes": manifest["compressed_bytes"], "content_bytes": content_bytes,
        "raw_game_json_members": raw_games, "compressed_text_members": compressed_text_members,
        "scientific_checkpoint_dataset_members": scientific_members,
        "late_closeout_outside_archive_bound_to_inventory": late,
        "inventory_entries_checked": len(inventory_entries), "inventory_sha256": digest(inventory_path.read_bytes()),
        "excluded_paths": excluded, "protected_files_checked": len(manifest["protected"]),
        "security_scan": "Each archived original plus decompressedgzip and scientificPT/NPZ members checked for current home/repository prefixes, executable magic and common credential forms. Heuristic bounded scan, not a universal security guarantee.",
        "scope": "Independent streaming archive hash/member hash/current original hash and exact declared eligible-tree coverage. No files extracted, deleted, normalized or modified; no game reruns, new data, Git or publication.",
        "audit_source_sha256": digest(Path(__file__).read_bytes()), "seconds": time.monotonic()-began,
    }
    with OUT.open("x") as output:
        json.dump(report, output, indent=2)
        output.write("\n")
    print(json.dumps({name: report[name] for name in ("passed", "members_checked", "original_files_checked", "coverage_missing", "compressed_bytes", "raw_game_json_members", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
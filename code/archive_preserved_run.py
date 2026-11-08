#!/usr/bin/env python3
"""Archive raw run records without modifying immutable local evidence.

Only personal-path normalization is applied to exported copies. A provenance
ledger maps each original SHA to its archived SHA, including unchanged members.
"""
import argparse
from collections import defaultdict
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
from archive_run import normalized

ROOT = Path(__file__).resolve().parents[1]
SECRET = re.compile(rb"(?:sk-(?:proj-)?[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{25,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    folder = args.folder.resolve()
    assert folder.is_relative_to(ROOT / "experiments")
    target = folder / "archive-snapshot.json"
    assert not target.exists(), "Refusing to replace an archival snapshot"
    groups = defaultdict(list)
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or any(p in path.parts for p in ("build", "__pycache__")):
            continue
        if path.name.endswith(".tar.gz"):
            raise RuntimeError(f"Existing archive: {path.relative_to(ROOT)}")
        if path.suffix in (".gz", ".log", ".jsonl") or path.name.endswith("-spec.json") or path.name == "matches.json":
            groups[path.parent].append(path)
    records, archives = [], {}
    changed = 0
    for directory, paths in sorted(groups.items()):
        archive_path = directory / "records.tar.gz"
        assert not archive_path.exists()
        expected = {}
        with archive_path.open("xb") as output, gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w") as archive:
                for path in paths:
                    original = path.read_bytes()
                    text = gzip.decompress(original) if path.suffix == ".gz" else original
                    cleaned = normalized(text)
                    assert b"/Users/" not in cleaned and b"/home/" not in cleaned, path.relative_to(ROOT)
                    assert not SECRET.search(cleaned), f"Sensitive literal in {path.relative_to(ROOT)}"
                    data = original if cleaned == text else gzip.compress(cleaned, mtime=0) if path.suffix == ".gz" else cleaned
                    info = tarfile.TarInfo(path.name)
                    info.size, info.mtime, info.mode = len(data), 0, 0o644
                    archive.addfile(info, io.BytesIO(data))
                    original_hash, archive_hash = digest(original), digest(data)
                    records.append({"path": str(path.relative_to(folder)), "original_sha256": original_hash,
                                    "archived_sha256": archive_hash})
                    expected[path.name] = archive_hash
                    changed += original_hash != archive_hash
                    assert digest(path.read_bytes()) == original_hash, "Original changed during archive"
        with tarfile.open(archive_path) as archive:
            actual = {member.name: digest(archive.extractfile(member).read()) for member in archive.getmembers()}
            assert actual == expected
        archives[str(archive_path.relative_to(folder))] = digest(archive_path.read_bytes())
    result = {"method": "Personal paths normalized only in archive copies; all original loose files retained byte-for-byte.",
              "limitations": "Historical verifier SHA fields refer to original loose files. Use this ledger to distinguish exported path-normalized bytes. Restore into a fresh clone; existing originals are intentionally not overwritten.",
              "records": records, "archives": archives, "normalized_records": changed}
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"archives": len(archives), "records": len(records), "normalized_records": changed,
                      "archive_bytes": sum((folder / p).stat().st_size for p in archives),
                      "manifest_sha256": digest(target.read_bytes())}))


if __name__ == "__main__":
    main()
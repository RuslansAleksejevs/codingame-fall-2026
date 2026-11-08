#!/usr/bin/env python3
"""Preserve a large evidence archive as verified, non-overwriting Git-sized parts."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PART_BYTES = 48 * 1024 * 1024


def file_sha(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def verify(manifest_path, consume=None):
    manifest = json.loads(manifest_path.read_text())
    combined = hashlib.sha256()
    total = 0
    names = set()
    for entry in manifest["parts"]:
        name = entry["file"]
        assert Path(name).name == name and name not in names, "Unsafe or repeated part name"
        names.add(name)
        part = manifest_path.parent / name
        assert not part.is_symlink() and part.is_file()
        own = hashlib.sha256()
        size = 0
        with part.open("rb") as source:
            for data in iter(lambda: source.read(1024 * 1024), b""):
                own.update(data)
                combined.update(data)
                size += len(data)
                if consume is not None:
                    consume(data)
        assert size == entry["bytes"] and own.hexdigest() == entry["sha256"], name
        assert size <= manifest["part_size_limit_bytes"]
        total += size
    assert total == manifest["original_bytes"]
    assert combined.hexdigest() == manifest["original_sha256"]
    return manifest


def create(source, directory):
    assert source.is_file() and not source.is_symlink()
    assert source.resolve().is_relative_to(ROOT)
    assert directory.resolve().is_relative_to(ROOT)
    directory.mkdir(parents=True, exist_ok=False)
    entries = []
    combined = hashlib.sha256()
    with source.open("rb") as incoming:
        while data := incoming.read(PART_BYTES):
            name = f"evidence.tar.gz.part-{len(entries):03d}"
            with (directory / name).open("xb") as output:
                output.write(data)
            combined.update(data)
            entries.append({"file": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    manifest = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "classification": "PROJECT_REPORTED",
        "format": "Concatenate parts in listed order; byte-exact original gzip/tar, no normalization.",
        "original_path": str(source.resolve().relative_to(ROOT)),
        "original_bytes": source.stat().st_size,
        "original_sha256": combined.hexdigest(),
        "part_size_limit_bytes": PART_BYTES,
        "parts": entries,
        "original_preserved": True,
    }
    assert file_sha(source) == manifest["original_sha256"]
    manifest_path = directory / "manifest.json"
    with manifest_path.open("x") as output:
        json.dump(manifest, output, indent=2)
        output.write("\n")
    verify(manifest_path)
    return manifest


def join(manifest_path, output_path):
    manifest = verify(manifest_path)
    assert output_path.resolve().is_relative_to(ROOT), "Restore inside the repository"
    assert not output_path.exists(), "Never overwrite an existing file"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("xb") as output:
        verify(manifest_path, output.write)
    assert file_sha(output_path) == manifest["original_sha256"]
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    make = sub.add_parser("create")
    make.add_argument("source", type=Path)
    make.add_argument("directory", type=Path)
    check = sub.add_parser("verify")
    check.add_argument("manifest", type=Path)
    restore = sub.add_parser("join")
    restore.add_argument("manifest", type=Path)
    restore.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.action == "create":
        manifest = create(args.source, args.directory)
    elif args.action == "join":
        manifest = join(args.manifest, args.out)
    else:
        manifest = verify(args.manifest)
    print(json.dumps({"passed": True, "action": args.action, "parts": len(manifest["parts"]),
                      "bytes": manifest["original_bytes"], "sha256": manifest["original_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
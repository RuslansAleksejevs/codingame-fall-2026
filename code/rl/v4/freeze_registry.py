#!/usr/bin/env python3
"""Freeze prior map exposure including the newer archived platform games."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code"))
from rl.v3.map_registry import build


def main():
    target = ROOT / "experiments/rl/2026-11-08-rl4/map-registry-base.json"
    if target.exists():
        raise SystemExit("Refusing to overwrite the frozen base registry")
    result = build(target)
    canonical, legacy = set(result["canonical"]), set(result["legacy"])

    def visit(value):
        if isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            for key, item in value.items():
                if key in ("game_options", "gameParameters"):
                    text = "".join(item) if isinstance(item, list) else item
                    if isinstance(text, str):
                        properties = dict(line.split("=", 1) for line in text.splitlines() if "=" in line)
                        if all(k in properties for k in ("nodes", "units", "edges")):
                            properties = {k: properties[k] for k in ("nodes", "units", "edges")}
                            board = {k: [list(map(int, row.split(","))) for row in v.split("_") if row]
                                     for k, v in properties.items()}
                            legacy.add(hashlib.sha256(json.dumps(properties, sort_keys=True).encode()).hexdigest())
                            canonical.add(hashlib.sha256(json.dumps(board, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
                visit(item)

    base = ROOT / "experiments/rl/2026-11-07-ppo-v3"
    extra = sorted([*(base / "platform").rglob("*.json"), *(base / "live-submission").rglob("*.json")])
    for path in extra:
        raw = path.read_bytes()
        visit(json.loads(raw))
        result["sources"][str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    result.update({"as_of": datetime.now(timezone.utc).isoformat(), "canonical": sorted(canonical), "legacy": sorted(legacy),
                   "v4_note": "Previous registry plus all saved v3 platform game_options; no reserved final maps generated."})
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"canonical": len(canonical), "legacy": len(legacy), "sources": len(result["sources"]),
                      "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
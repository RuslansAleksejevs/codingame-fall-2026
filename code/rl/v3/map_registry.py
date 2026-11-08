#!/usr/bin/env python3
"""Freeze all known map-content hashes, including archived platform game options."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
KEYS = ('nodes', 'units', 'edges')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build(exclude=None):
    canonical, legacy, sources = set(), set(), {}

    def board(properties):
        if not all(k in properties for k in KEYS):
            return
        if all(isinstance(properties[k], str) for k in KEYS):
            props = {k: properties[k] for k in KEYS}
            legacy.add(sha(json.dumps(props, sort_keys=True).encode()))
            data = {k: [list(map(int, r.split(','))) for r in props[k].split('_') if r] for k in KEYS}
        elif all(isinstance(properties[k], list) for k in KEYS):
            data = {k: properties[k] for k in KEYS}
        else:
            return
        canonical.add(sha(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()))

    def visit(value):
        if isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            board(value)
            for key, item in value.items():
                if key in ('game_options', 'gameParameters'):
                    text = ''.join(item) if isinstance(item, list) else item
                    if isinstance(text, str):
                        board(dict(line.split('=', 1) for line in text.splitlines() if '=' in line))
                if key in ('new_canonical_hashes_by_seed',):
                    canonical.update(item.values())
                elif key in ('new_legacy_hashes_by_seed', 'new_content_sha256_by_seed'):
                    legacy.update(item.values())
                elif key in ('map_hash',) and isinstance(item, str):
                    canonical.add(item)
                elif key == 'content_sha256' and isinstance(item, str):
                    legacy.add(item)
                elif key == 'hash' and 'map' in value:
                    canonical.add(item)
                elif key == 'canonical' and isinstance(item, list):
                    canonical.update(item)
                elif key == 'legacy' and isinstance(item, list):
                    legacy.update(item)
                visit(item)

    candidates = []
    for p in (ROOT / 'experiments').rglob('*.json'):
        if 'snapshots' in p.parts or 'sources' in p.parts or p == exclude:
            continue
        if (p.name in ('map-hashes.json', 'maps.json', 'maps-2000.json', 'dataset.json', 'historical-maps.json', 'selection.json')
                or 'verification' in p.name or p.name.startswith('map-registry')
                or '2026-11-06-live-ppo-v2' in p.parts and p.name.startswith('test-')):
            candidates.append(p)
    # All available saved platform games are already exposed, not new holdout data.
    candidates.extend((ROOT / 'experiments/rl/2026-11-06-live-ppo-v2/games').glob('*.json.gz'))
    for p in sorted(set(candidates)):
        raw = p.read_bytes()
        value = json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)
        if p.name == 'map-hashes.json':
            canonical.update(value.values())
        visit(value)
        sources[str(p.relative_to(ROOT))] = sha(raw)
    assert all(len(v) == 64 for v in canonical | legacy)
    return {'as_of': datetime.now(timezone.utc).isoformat(), 'provenance': 'PROJECT_REPORTED',
            'method': 'Canonical nodes/units/edges and legacy property hashes; manifests plus saved platform options; seeds alone are not identity.',
            'canonical': sorted(canonical), 'legacy': sorted(legacy), 'sources': sources}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    assert not args.out.exists()
    result = build(args.out.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'canonical_maps': len(result['canonical']), 'legacy_maps': len(result['legacy']),
                      'source_files': len(result['sources']), 'sha256': sha(args.out.read_bytes())}))


if __name__ == '__main__':
    main()
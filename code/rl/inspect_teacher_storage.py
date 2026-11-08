#!/usr/bin/env python3
"""Read-only size diagnostic for existing frozen teacher weights; no inference or training."""
import hashlib
import json
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[2]


def main():
    freeze = json.loads((ROOT / "experiments/rl/2026-11-08-rl5/deadline-search/freeze.json").read_text())
    payloads = []
    records = []
    for name, expected in freeze["weights"].items():
        source = (ROOT / name).read_bytes()
        assert hashlib.sha256(source).hexdigest() == expected
        tokens = source.decode().split()
        assert tokens[0] == "TRYANGLE_MLP_V1"
        layers = int(tokens[1])
        dims = list(map(int, tokens[2:3 + layers]))
        values = list(map(float, tokens[3 + layers:]))
        assert len(values) == sum((a + 1) * b for a, b in zip(dims, dims[1:]))
        raw = struct.pack("<" + "f" * len(values), *values)
        payloads.append(raw)
        records.append({"path": name, "sha256": expected, "parameters": len(values), "float32_bytes": len(raw)})
    raw = b"".join(payloads)
    byte_planes = b"".join(raw[i::4] for i in range(4))
    xor_delta = payloads[0] + b"".join(bytes(x ^ y for x, y in zip(payloads[0], p)) for p in payloads[1:])
    compressed = {"plain_float32": zlib.compress(raw, 9), "byte_planes": zlib.compress(byte_planes, 9),
                  "xor_to_first_network": zlib.compress(xor_delta, 9)}
    n = sum(row["parameters"] for row in records)
    output = {
        "classification": "PROJECT_REPORTED", "kind": "READ_ONLY_STORAGE_DIAGNOSTIC",
        "networks": records, "unique_sets": len(records), "total_parameters": n,
        "float32_bytes": len(raw), "uncompressed_15bit_symbols": (len(raw) * 8 + 14) // 15,
        "lossless_zlib_variants": {k: {"bytes": len(v), "15bit_symbols_before_code": (len(v) * 8 + 14) // 15} for k, v in compressed.items()},
        "hypothetical_storage_only": {
            "float16_15bit_symbols_before_code": (n * 16 + 14) // 15,
            "int8_15bit_symbols_before_code_or_scales": (n * 8 + 14) // 15,
        },
        "limitations": "No quantization, packaged bot, decoder, inference, games or accuracy test was performed. Hypothetical sizes exclude metadata, scales, code and loader. Failure of these three lossless encodings is not impossibility of all compression.",
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
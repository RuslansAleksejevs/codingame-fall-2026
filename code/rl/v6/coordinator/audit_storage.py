"""Independent inspection of an already-built compact-D16 storage package.

No builder/codec imports, compilation, inference, map reads or games. Recompute
declared row quantization from the immutable original float32 weights and decode
the actual C++ Unicode payload through a separately implemented bit reader.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "experiments/rl/2026-11-08-rl6/compact-d16"
ORIGINALS = (
    "experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt",
    "experiments/rl/2026-11-07-ppo-v3/search/frozen-critic/critic.txt",
    "experiments/rl/2026-11-06-ppo-v2/control-long/step-03002813/weights.txt",
    "experiments/rl/2026-11-06-ppo-v2/league-a/step-04836947/weights.txt",
)
ORIGINAL_HASHES = (
    "dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb",
    "91fd5a290dd4a015fade1abdfe8840e1b580b4480c50102b4f7a3fb14f1f6680",
    "c02c08c67e17ab8bdbbb37fc77eafd646da40d96de306a94ef013778eb359094",
    "ca3a2d89183f9ce69391baca328f34c6719879a6348e614b622b4129c580c507",
)
DIMS = (128, 128, 64, 1)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def originals():
    result = []
    for name, digest in zip(ORIGINALS, ORIGINAL_HASHES):
        path = ROOT / name
        assert sha(path) == digest, name
        fields = path.read_text().split()
        assert fields[:6] == ["TRYANGLE_MLP_V1", "3", "128", "128", "64", "1"]
        values = np.asarray(fields[6:], dtype=np.float32)
        assert len(values) == 24833 and np.isfinite(values).all()
        layers, offset = [], 0
        for n, m in zip(DIMS[:-1], DIMS[1:]):
            matrix = values[offset:offset+n*m].reshape(m, n)
            offset += n*m
            biases = values[offset:offset+m]
            offset += m
            layers.append((matrix, biases))
        assert offset == len(values)
        result.append(layers)
    return result


def decode_payload(source, size):
    literals = re.findall(r'R"CGW\(([\s\S]*?)\)CGW"', source)
    assert literals, "No literal payload in the actual source"
    symbols = "".join(literals).replace("\n", "")
    assert all(0x4000 <= ord(x) <= 0xbfff for x in symbols)
    # A different implementation from the builder: one complete integer stream.
    stream = 0
    for symbol in symbols:
        stream = (stream << 15) | (ord(symbol) - 0x4000)
    pad = len(symbols) * 15 - size * 8
    assert 0 <= pad < 15 and stream & ((1 << pad) - 1) == 0
    return (stream >> pad).to_bytes(size, "big")


def decode_weights(payload, width):
    stream = int.from_bytes(payload, "little")
    position = 0

    def bits(n):
        nonlocal position
        assert position + n <= len(payload) * 8
        result = (stream >> position) & ((1 << n) - 1)
        position += n
        return result

    def number():
        return np.float32(struct.unpack("<f", bits(32).to_bytes(4, "little"))[0])

    result = []
    for _ in range(4):
        for n, m in zip(DIMS[:-1], DIMS[1:]):
            scales = [number() for _ in range(m)] if width != 32 else None
            for j in range(m):
                for _ in range(n):
                    if width == 32:
                        result.append(number())
                    else:
                        value = bits(width)
                        if value >= 1 << (width-1):
                            value -= 1 << width
                        assert abs(value) <= (1 << (width-1))-1, "Unused negative sentinel encountered"
                        result.append(np.float32(np.float32(value) * scales[j]))
            result.extend(number() for _ in range(m))
    assert position == len(payload) * 8
    array = np.asarray(result, dtype="<f4")
    assert len(array) == 4 * 24833 and np.isfinite(array).all()
    return array.tobytes()


def expected_weights(networks, width):
    values = []
    for network in networks:
        for matrix, biases in network:
            for row in matrix:
                if width == 32:
                    values.extend(row)
                    continue
                qmax = (1 << (width-1)) - 1
                scale = np.float32(np.max(np.abs(row)) / np.float32(qmax))
                if scale == 0:
                    scale = np.float32(1)
                for weight in row:
                    # np.rint implements the declared nearest-even rule.
                    integer = int(np.rint(np.float32(weight / scale)))
                    integer = max(-qmax, min(qmax, integer))
                    values.append(np.float32(np.float32(integer) * scale))
            values.extend(biases)
    return np.asarray(values, dtype="<f4").tobytes()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, default=DATA / "package.json")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    assert not args.out.exists(), "Never replace an earlier audit"
    began = time.monotonic()
    record = json.loads(args.package.read_text())
    assert record["passed"]
    attempts = record["attempts"]
    assert [r["width"] for r in attempts if r["width"] != 32] == [12, 11, 10, 9, 8]
    fits = [r for r in attempts if r["width"] != 32 and r["source_utf16"] <= 98000 and r["compiled"] and r["codec_exact"]]
    assert fits and record["selected_width"] == max(r["width"] for r in fits)
    selected = ROOT / record["source"]
    source = selected.read_text()
    assert sha(selected) == record["source_sha256"]
    assert len(source.encode("utf-16-le")) // 2 == record["source_utf16"] <= 98000
    checks = []
    networks = originals()
    for width in (record["selected_width"], 32):
        attempt = next(r for r in attempts if r["width"] == width)
        path = selected.parent.parent / f"b{width}" / "bot.cpp"
        text = path.read_text()
        assert sha(path) == attempt["source_sha256"]
        assert len(text.encode("utf-16-le")) // 2 == attempt["source_utf16"]
        payload = decode_payload(text, attempt["payload_bytes"])
        decoded = decode_weights(payload, width)
        expected = expected_weights(networks, width)
        assert decoded == expected, ("Independent payload/quantization discrepancy", width)
        actual = path.parent / "decoded-f32.bin"
        assert actual.read_bytes() == expected, ("Native decoded discrepancy", width)
        assert (path.parent / "expected-f32.bin").read_bytes() == expected
        checks.append({"width": width, "floats": len(expected)//4,
                       "bytes": len(expected), "dequantized_sha256": hashlib.sha256(expected).hexdigest(),
                       "original_source_sha256": attempt["source_sha256"], "passed": True})
    result = {"as_of": datetime.now(timezone.utc).isoformat(), "classification": "PROJECT_REPORTED",
              "passed": True, "source": record["source"], "source_sha256": sha(selected),
              "source_utf16": record["source_utf16"], "selected_width": record["selected_width"],
              "package_manifest_sha256": sha(args.package), "checks": checks,
              "audit_source_sha256": sha(Path(__file__)), "numpy_version": np.__version__,
              "original_weight_identities": dict(zip(ORIGINALS, ORIGINAL_HASHES)),
              "seconds": time.monotonic()-began,
              "scope": "Independent original-float quantization and actual-source payload decode; no child codec import. No new compilation/inference/game, no strength/platform claim. Source semantics/timing and final identity freezing are separate gates."}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
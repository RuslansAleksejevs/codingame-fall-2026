"""Small deterministic tests; no large scientific archive is modified."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import split_evidence as archive


class EvidencePartsTest(unittest.TestCase):
    def test_roundtrip_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "original.tar.gz"
            content = bytes(range(256)) * 11
            source.write_bytes(content)
            with patch.object(archive, "ROOT", root), patch.object(archive, "PART_BYTES", 1024):
                manifest = archive.create(source, root / "parts")
                self.assertEqual(len(manifest["parts"]), 3)
                restored = root / "restored.tar.gz"
                archive.join(root / "parts/manifest.json", restored)
                self.assertEqual(restored.read_bytes(), content)
                self.assertEqual(source.read_bytes(), content)
                with self.assertRaises(AssertionError):
                    archive.join(root / "parts/manifest.json", restored)

    def test_reject_corrupt_and_unsafe_part(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "original"
            source.write_bytes(b"evidence")
            with patch.object(archive, "ROOT", root):
                archive.create(source, root / "parts")
                manifest_path = root / "parts/manifest.json"
                manifest = json.loads(manifest_path.read_text())
                part = root / "parts" / manifest["parts"][0]["file"]
                part.write_bytes(b"modified")
                with self.assertRaises(AssertionError):
                    archive.verify(manifest_path)
                manifest["parts"][0]["file"] = "../original"
                manifest_path.write_text(json.dumps(manifest))
                with self.assertRaises(AssertionError):
                    archive.verify(manifest_path)


if __name__ == "__main__":
    unittest.main()
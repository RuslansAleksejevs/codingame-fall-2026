"""Small process/lock tests; no training or arena games."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = Path(__file__).with_name("compute_slot.py")


class Slots(unittest.TestCase):
    def setUp(self):
        (ROOT / ".context").mkdir(exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(prefix="slot-test-", dir=ROOT / ".context")
        self.base = [sys.executable, str(SCRIPT), "--state-dir", self.directory.name]

    def tearDown(self):
        self.directory.cleanup()

    def command(self, body, minutes="1"):
        return self.base + ["--owner", "coordinator", "--minutes", minutes, "--", sys.executable, "-c", body]

    def test_exit_code_and_ledger(self):
        run = subprocess.run(self.command("raise SystemExit(7)"), cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 7)
        events = [json.loads(line) for line in (Path(self.directory.name) / "events.jsonl").read_text().splitlines()]
        self.assertEqual(events[-1]["exit_code"], 7)
        self.assertGreater(events[-1]["seconds"], 0)

    def test_timeout_releases_lease(self):
        run = subprocess.run(self.command("import time; time.sleep(10)", ".003"), cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 124)
        status = subprocess.run(self.base + ["--status"], cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(status.stdout)["status"], "available")

    def test_exclusive(self):
        first = subprocess.Popen(self.command("import time; time.sleep(10)"), cwd=ROOT, stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(json.loads(first.stdout.readline())["status"], "started")
            second = subprocess.run(self.command("pass"), cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(second.returncode, 75)
            self.assertEqual(json.loads(second.stdout)["status"], "busy")
        finally:
            first.terminate()
            first.communicate(timeout=8)


if __name__ == "__main__":
    unittest.main()
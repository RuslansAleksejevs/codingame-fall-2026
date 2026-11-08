"""Branch-local paths, records and a persistent original-referee oracle."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'experiments/rl/2026-11-08-rl4/curriculum'
BUILD = HERE / 'build'
BASE = ROOT / 'experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173'
sys.path.insert(0, str(ROOT / 'code'))
from run_matches import REPO, java_home


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def classpath():
    return ':'.join(map(str, [BUILD, ROOT / 'code/build', REPO / 'target/classes'])) + ':' + (REPO / 'classpath.txt').read_text().strip()


class Oracle:
    def __init__(self, name='RestoreOracle'):
        self.process = subprocess.Popen([str(java_home() / 'bin/java'), '-Xmx512m', '-cp', classpath(), name],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

    def run(self, job):
        p = self.process
        p.stdin.write(json.dumps(job) + '\n')
        p.stdin.flush()
        line = p.stdout.readline()
        if not line:
            raise RuntimeError(f'Java oracle stopped: {p.poll()}')
        return json.loads(line)

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)
        self.process.stdout.close()
        assert self.process.returncode == 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
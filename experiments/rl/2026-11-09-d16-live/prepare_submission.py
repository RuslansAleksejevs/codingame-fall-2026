"""Preflight one explicitly authorized A3 ranking submission; this never calls API."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = "experiments/rl/2026-11-09-rl7/d16/package-attempt3/bot.cpp"
EXPECTED = "94f0d426de787f7ed29a0ce87fa03fd3e0bae2ebb27c7d76548f4624f67ab4f8"
BASE_SHA = "199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE / name).read_text())


assert not (HERE / "submission-request.json").exists()
assert not (HERE / "submission-response.json").exists(), "Never duplicate a submission"
source = ROOT / SOURCE
assert sha(source) == EXPECTED
assert len(source.read_text().encode("utf-16-le"))//2 < 98000
challenge = read("challenge-before-submit.json")
assert challenge["status"] == "ongoing" and challenge["registered"] and challenge["league"] == "Gold"
assert challenge["end"] == "2026-11-09T09:00:00Z"
assert datetime.now(timezone.utc) < datetime.fromisoformat(challenge["end"].replace("Z", "+00:00"))
progress = read("progress-before-submit.json")
assert progress["submission_id"] == 41671805 and progress["percentage"] == 100 and progress["in_progress"] is False
previous = read("previous-source-before-submit.json")
assert previous["submission_id"] == 41671805 and previous["current"] and previous["language"] == "C++"
assert hashlib.sha256(previous["code"].encode()).hexdigest() == BASE_SHA == sha(ROOT / "submissions/ppo-v2-league3m.cpp")
history = read("submissions-before-submit.json")["submissions"]
assert [r["submission_id"] for r in history if r.get("current")] == [41671805]
assert {r["submission_id"] for r in history} == {r["submission_id"] for r in read("submissions-before.json")["submissions"]}
assert all(w["remaining"] > 0 for w in read("limits-before-submit.json")["submits"])
technical = read("tests-audit-a3-final.json")
assert technical["platform_admission_passed"] and not technical["issues"] and not technical["timing_review_required"]
local_path = ROOT / "experiments/rl/2026-11-09-rl7/coordinator/d16-a3-audit.json"
local = json.loads(local_path.read_text())
assert local["passed"] and local["local_gross_guard_passed"] and local["games"] == 96
proof = [source, local_path, HERE / "tests-audit-a3-final.json", HERE / "test-requests-a3.json",
         HERE / "AMENDMENT_A3.md", HERE / "challenge-before-submit.json",
         HERE / "progress-before-submit.json", HERE / "previous-source-before-submit.json",
         HERE / "submissions-before-submit.json", HERE / "limits-before-submit.json"]
request = {
    "as_of": datetime.now(timezone.utc).isoformat(), "authorization": "USER_CONFIRMED",
    "authorization_scope": "Finish D16 and make one real leaderboard submission; no automatic rollback",
    "selection": "A3 complete-ensemble anytime D1 then original D2, exact9-bit weights,16ms",
    "code_file": SOURCE, "source_sha256": EXPECTED,
    "previous_submission_id": 41671805, "previous_source_sha256": BASE_SHA,
    "previous_source_file": "previous-source-before-submit.json",
    "previous_history_file": "submissions-before-submit.json",
    "before_progress_file": "progress-before-submit.json",
    "local_guard": "46/48 candidate versus41/48 control on8fresh maps; gain10.4167pp CI[0,27.0833]",
    "platform_guard": "102clean outputs,17complete comparisons,1nonselfnonbaseline; no >20ms normal turn",
    "caveats": ["Exploratory ranked measurement, not an independently proved improvement",
                "Platform search remains rare and mostly shallow; local full-depth capacity did not transfer",
                "Moving rank snapshots are not paired causal comparisons",
                "Old A2 failure and359/1200 STOP remain unchanged"],
    "command": {"method": "POST", "path": "/challenges/fall-challenge-2026/submissions",
                "code_file": SOURCE, "body": {"language": "C++"},
                "save": str((HERE / "submission-response.json").relative_to(ROOT)),
                "keys": ["submission_id", "progress_url", "hint"]},
    "proof_sha256": {str(p.relative_to(ROOT)): sha(p) for p in proof},
    "external_spend": 0, "git_commit_push": False, "overwrite_ide": False,
}
with (HERE / "submission-request.json").open("x") as stream:
    json.dump(request, stream, indent=2)
    stream.write("\n")
print(json.dumps({"ready": True, "source_sha256": EXPECTED, "previous_submission": 41671805,
                  "before": {k: progress[k] for k in ("rank", "total", "league", "league_rank", "league_total", "score")},
                  "request_sha256": sha(HERE / "submission-request.json"), "api_called": False}))
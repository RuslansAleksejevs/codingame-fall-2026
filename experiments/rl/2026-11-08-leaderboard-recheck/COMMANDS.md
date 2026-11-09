# Execution record

8 November 2026, UTC. Work from the existing repository root, main at
`531c59385ec7370ed6f44c4ab923c2144de71221`. Historical experiment commands were
read, not rerun. External compute spend0; no new training or arena games.

## Readiness and documentation

```sh
git status --short
git branch --show-current
git rev-parse HEAD
python3 code/rl/v4/compute_slot.py --status
python3 experiments/rl/2026-11-08-leaderboard-recheck/verify_documentation.py --out experiments/rl/2026-11-08-leaderboard-recheck/documentation-audit-001.json
clang++ -std=c++17 -O2 -fsyntax-only submissions/ppo-v2-league3m.cpp
```

The documentation audit passed at22:44:22Z:169 local links exist, four protected
hashes match, package186,203UTF8bytes /80,247UTF16units, diff whitespace clean.
The first syntax-check process exited0 but emitted a sandbox xcrun cache error;
that is not counted as a clean verification. The reviewed identical check then
exited0 with no diagnostics. Compiler:Apple Clang17.0.0, arm64-apple-darwin25.6.0.
Python3.14.6. No executable was produced and no policy changed.

Compute slot was available. A scoped process-list check was unavailable in the
sandbox; its reviewed read-only repeat found no old finite-final, compact-D16
panel, PPO-v3 campaign/continuation, BenchmarkMatch or search-teacher lease jobs.
This is a scoped observation, not a claim about every process on the host.

## Official session

```sh
python3 -u code/platform/codingame_session.py --allow-submit
```

The initial sandbox session could not resolve the official host and exited
cleanly. A reviewed network session was then started. `auth_start` returned200;
browser approval is still pending as of22:44Z. `auth_poll` returned the official
authorization_pending response. Login/device codes and tokens are not archived.
The official API reference was freshly read at
<https://www.codingame.com/api/v1/docs/api>. Its suggested token-on-disk storage
is not used: this task requires process-memory-only credentials.

No authenticated challenge, test or submission request has yet run. The saved
previous deadline is not presented as newly reverified. Next: browser approval,
fresh official state/limits/source reads, then the single selected submission
only if necessary. Exact requests and sanitized responses will be kept here.

## Subsequent authentication and submission,23:01–23:07UTC

The first code expired before approval. That client exited; a second reviewed
client obtained approval with read/play/submit. Tokens remained only in memory.
Fresh official reads are saved as challenge/limits/progress/submissions-before,
previous-source and historical-league3m-source. Deadline9November09:00UTC,
Gold full actions, C++ and1000/50ms were confirmed. Both prior source hashes
match their preserved files. PrecedingB2M:380/1036,Gold232/428,score14.59.

The fresh API reference explicitly describes submission as replacing the active
arena bot, without overwritingIDE. It did not expose a numeric source-size limit;
no claim of newly reverified100k is made. One exact-source technical request
([test-request](test-request.json)) returned done918805589: clean loss toGoldBoss,
no own/opponent/global technical errors or warnings. Actual source acceptance
and compilation establish compatibility for this unchanged package.

The one [submission request](submission-request.json) returned201,
submission41671805 at23:04:07.095UTC. GET accepted-source matches199c6a2d exactly;
submission history contains precisely one newID and preserves all four oldIDs.
No POST retry or automatic rollback occurred. Ranking is not complete yet.

```sh
python3 experiments/rl/2026-11-08-leaderboard-recheck/audit.py --snapshot 002 --out experiments/rl/2026-11-08-leaderboard-recheck/audit-002.json
```

The first audit checks12completed logs from the13-battle snapshot:5W/7L,
zero technical events. Pending games are not counted as completed. The reusable
analyzer is read-only and checks identities/outcomes/coverage; its imports do
not replay games. Each GET log is saved under its exact official gameID.

## Completed ranking and closure,23:25–23:30UTC

The first100% progress was369/1036. The final saved progress and independent
leaderboard read then agreed on368/1036,Gold221/428,score15.11. All92 final
battles are complete and have saved logs; no pagination or pending games remain.
Final history and accepted source confirm current41671805 and one new submit.

```sh
python3 experiments/rl/2026-11-08-leaderboard-recheck/audit.py --snapshot final --require-complete --out experiments/rl/2026-11-08-leaderboard-recheck/audit-final.json
```

Executed23:27:02UTC, exit0.52W/40L, zero technical events; all92 identities and
outcomes agree.3,373own outputs; max internal planning16,693µs, not whole CPU.
The final analyzer explicitly checks the final source readback and leaderboard;
the same unchanged older parser handles the game logs. No game replay was run.

The JSONL `exit` command closed the authenticated client cleanly. A product
query returned no pending scheduled messages; expired/delivered checks did not
cause duplicate submissions. No active research process was started in this
task. All new files remain local, with no commit/push or changes to old archives.
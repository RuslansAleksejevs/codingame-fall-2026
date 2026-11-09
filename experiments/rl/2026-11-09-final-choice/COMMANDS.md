# Final-choice execution ledger

9November2026. Credentials and short-lived codes are excluded; the official
client keeps the token in process memory. Earlier repository publication is
complete; this run has not made a new commit or push.

## Login and current D16 readback,05:27–05:31UTC

- `python3 -u code/platform/codingame_session.py --allow-submit`; the new device
  flow was confirmed, `auth_poll`200 with read/play/submit. No restart or stored
  token. The old pending-login cleanup control was cancelled.
- GET challenge/limits/progress: ongoing, registered, Gold, deadline09UTC;
  current41672652 at369/1042,Gold205/422,score15.82,100%/notinprogress. Saved
  `challenge-before.json`, `limits-before.json`, `progress-d16-before.json`.
- Saved D16's history/source/battle list in its original live-evidence directory
  under previously absent final filenames. Six history entries, only41672652
  current; accepted code SHA94f0d426 matches the frozen package.98completed
  battles, no pending or next page.26logs already present;72missing.
- The first24game GETs mistakenly omitted `format=json`. The endpoint defaults
  to plain text; the JSON-only client reported `JSONDecodeError` and saved no
  files. Response bodies were not retained. This is a request-format error,
  not a game failure or an unexecuted permission review. Corrected GETs use
  `/games/{id}?format=json`, saving only absent files. No ranking POST occurred.
- An initial `jq -r .code | shasum` diagnostic added a newline; it was not used
  as source-identity evidence. `jq -j .code | shasum` and the preserved auditor's
  exact UTF8 hashing give the correct94f0d426 identity.

## D16 full snapshot audit,05:37–05:39UTC

All98snapshot logs were saved. Final progress and independent leaderboard agree:
371/1042,Gold207/422,score15.77,100%/notinprogress. The complete audit exited0:
55W/43L,zero official own/opponent/global errors or warnings. Its old line-based
telemetry parser flagged five concatenated stderr records; this was not hidden
or treated as a new bot failure.

```sh
python3 -B experiments/rl/2026-11-09-d16-live/audit_ranking.py --snapshot final --require-complete --out experiments/rl/2026-11-09-d16-live/audit-final.json
python3 -B experiments/rl/2026-11-09-final-choice/audit_d16_telemetry.py --out experiments/rl/2026-11-09-final-choice/d16-telemetry-supplement.json
```

The additive parser uses exact JSON-object boundaries, preserves all original
records and checks contiguous turn identities. Five synthetic checks passed;
all3209outputs now have exact complete records,0emergencies/incomplete baselines,
143nonbaseline choices (allD1),940paired turns,3418D1/247D2evaluations. Maximum
internal wall22.097ms/CPU22.026ms,2ordinary turns>20ms,not official timeouts.
The old audit and raw files are unchanged. Full coverage means the frozen98-game
snapshot, not future passive matches after the snapshot.

Fresh league3m-control preflight reads: all six old history IDs retained,
onlyD16current, exact94f0d426 source; progress370/1042,Gold206/422,15.77. This
one-place movement after the full audit is retained as its separate snapshot.
league3m local source independently hashes to199c6a2d,186203UTF8/80247UTF16.
One fresh control is selected; its preserved Gold compatibility checks are
reused and explicitly not described as new executions. No B2M/student sweep.
The request was recorded before the POST. HTTP201 accepted41673756 at05:39:45;
readback SHA199c6a2d and history exactly+1/all six earlier IDs preserved passed.
No unknown-response retry, second POST, IDE write or automatic restoration.

## Fresh league3m control, running from05:39UTC

New `audit_candidate.py` reuses the frozen official-log analyzer, adds explicit
pagination and verifies each agent's result position. It does not claim a new
technical test. A regression on the old92-game final reproduces52W40L,
zero technical events,3373outputs,maxinternal16693us exactly; no game replayed.

```sh
python3 -B experiments/rl/2026-11-09-final-choice/audit_candidate.py --directory experiments/rl/2026-11-08-leaderboard-recheck --snapshot final --require-complete --out experiments/rl/2026-11-09-final-choice/auditor-regression-league3m.json
python3 -B experiments/rl/2026-11-09-final-choice/audit_candidate.py --snapshot 001 --out experiments/rl/2026-11-09-final-choice/league3m/audit-001.json
python3 -B experiments/rl/2026-11-09-final-choice/audit_candidate.py --snapshot 002 --out experiments/rl/2026-11-09-final-choice/league3m/audit-002.json
python3 -B experiments/rl/2026-11-09-final-choice/audit_candidate.py --snapshot 003 --out experiments/rl/2026-11-09-final-choice/league3m/audit-003.json
```

Saved progress00111%,00220%,00334%,00445% are intermediate, not selected outcomes.
Audit003 covers31done games21W10L:0own errors/warnings,1opponent timeout. The
opponent error was GoldenGlove6858015, game918937207, no opponent command; the
win is retained in gross results and excluded from clean results20W10L.
Missing completed logs are downloaded once as `/games/{id}?format=json`.

At05:48 the existing documentation checker, with the new report/portfolio/D16
report added to its in-memory scope and frozenA3 hash added, passed305local
links, five protected identities, English/privacy markers and whitespace.
No old checker file was edited. Root `contest.py index` and `contest.py check`
both passed11contests/16TickTicklinks; no calendar operation ran.
Local main and rl/research remain e5cd7b4. New work is uncommitted/unpushed;
unrelated copies and old research artifacts were not touched.

## Final control audit and cleanup,05:59–06:00UTC

Interim progress00561%,00670%,00782%,00890%,00998% was retained without changing
the source or selecting a stopping point. Read-only `audit_candidate.py` receipts
004–009 cover their saved completed logs; new files only. First complete010
and final progress/independent leaderboard agree:433/1042,Gold269/422,13.37.
Final source/current and all seven history IDs verified; exactly one new POST.
All93final battles done, no further page, all full logs present.

```sh
python3 -B experiments/rl/2026-11-09-final-choice/audit_candidate.py --snapshot final --require-complete --out experiments/rl/2026-11-09-final-choice/league3m/audit-final.json
```

Executed06:00:07UTC, exit0:49W44L,0own errors/warnings/global failures,1opponent
timeout (same918937207), clean-only48W44L.3514own outputs, maxinternal11.101ms.
Full coverage/identity/consistency passed; `all_audited_games_technically_clean`
is correctly false because of the opponent's error, not a candidate failure.

Recommendation: preserved D16 A3; active bot remains league3m41673756. No final
restoration, second control POST, B2M/student submission or training. JSONL
`exit` closed OAuth with code0; the outstanding finite control was cancelled
before delivery. Credentials were never stored. Final documentation/root checks
follow; no commit/push belongs to this task.

Final06:04:43UTC documentation check expanded to delivery rules and bothv7
navigation pages:334local links/five protected identities/English/privacy
heuristics/whitespace PASS. Helper syntax and COMPLETION-versus-audit metrics
also passed. The product query returned zero pending scheduled messages.
Only nine previously tracked documentation files changed; new evidence/helpers
are separate. Local main/research stay e5cd7b4, with no Git writes in this task.
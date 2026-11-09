# D16 platform command ledger

9November2026, coordinator-owned. Credentials/codes are not written here.
The official OAuth client holds them only in process memory.

- Read the complete `code/platform/codingame_session.py`, existing live audit and
  platform log parser. Read D16technical-readiness and the fixedfive-test plan.
- `shasum -a 256 experiments/rl/2026-11-09-rl7/d16/package-attempt1/bot.cpp`:
  exact `aba2d6f2ae4bcd92eb79f38fd6bd643be9973b714b135c7b532a3e9fd9a80701`.
- Reviewed execution: `python3 -u code/platform/codingame_session.py --allow-submit`.
  Client ready; `auth_start`200, official short-lived link displayed only in chat.
  First `auth_poll`authorization_pending; human confirmation not yet received.
- Fresh public GET of official API reference, test-games/submissions sections:
  numeric-opponent eligibility, same-source `me`, explicit allfalseIDEflags and
  test-versus-ranking distinction confirmed. No authenticated GET or game yet.

Status: waiting for OAuth and the independent local final. New platform tests0,
ranking submissions0. External compute spend0; subscription/electricity unmeasured.

## Authenticated checks and initial tests,00:31–00:42UTC

- The user confirmed login; `auth_poll`200/authenticated/read/play/submit. Token
  remains in client memory. Saved challenge/limits/progress/history/source/opponents/
  battles as distinct `*-before.json` files. Ongoing/registered/Gold/full actions,
  deadline09:00UTC,1000ms first/50ms later; C++ and quotas available.
- Fresh league3m41671805 before:377/1039,Gold226/427,score15.10,100% complete.
  `prepare_tests.py` verified exact unchanged199c6a2d source, all source identities,
  Captainseb6844184 eligibility and resolved precisely five tests. No fallback.
- Test01 D16/GoldBoss,seed120008:918842926,done,clean loss;29outputs,complete search0.
- Test02 D16/Captainseb,exact historical timeout map:918843981,done,clean win;
  14outputs,complete search0; ordinary-turn wall baseline up to71.446ms.
- Test03 unchangedleague3m against the same Captainseb/map/seat, via exact test02
  replay:918845208,done,clean win. Exact wire request preserved separately.
- Test04 attempt1same-source selfplay:918846348,done; analysis pending at this entry.
- Test05 unchangedleague3m same-source selfplay: POST issued once; result pending
  at this entry. Check saved result/client before any additional request.
- `audit_tests.py` audits saved logs only; receipts001–003 preserve progressive
  coverage. Added descriptive search-completion/nonbaseline counters after the
  first log; old audit output kept, no gate or raw-game rewrite. Official errors
  and internal wall measurements are deliberately separated.
- Read-only comparison identified missing guardedGCCO3 in attempt1; local build
  was alreadyO3. [A2](AMENDMENT_A2.md) prospectively authorizes exactly one compiler-
  only corrected package and three additional fixed technical tests (total8),
  preserving the incomplete359-game local final and original protocol failure.
  Ranking POST still0; no automatic rollback or source/time-budget tuning.

## Completed A2 technical checks,00:47–01:03UTC

- Candidate2 source is exactly `d36aba4daa02580b1a20e5e1d000954cea330a852d8adbae1bb8f593572c9d15`,
  94468UTF16/219328UTF8bytes. Its only source change is the79-byte guardedGCCO3
  prefix; independent body hash equals the unchanged A1 source. Child local
  numerical/stream/forced-prefix contracts passed; these are not new-map wins.
- Original test05 completed918846888. All five initial games were technically
  clean, with104D16 outputs and zero completed search evaluations/selections.
- `prepare_a2.py` recorded exactly three fixed old-map candidate-only tests.
  Test06 completed918849391, GoldBoss, clean loss; test07 completed918849860,
  Captainseb, clean win. Actual IDs are taken from saved responses, not notes.
- Test08 completed918850573 on a **wrong map**: the coordinator transcribed
  `22,27_22,29` as `22,27,22,29`. The source and bot ran without official errors,
  but the exact-map audit failed. This is a request execution error, not a bot
  failure or a successful fixed-map check. Raw output and failed audit remain.
- `prepare_test09.py` recorded that exact one-delimiter mismatch, ignoring API
  property order, and one corrective unchanged-source/map/opponents request.
  The first byte-order assertion failed before writing; property-based checking
  then proved the exact mutation. No outcome-based map selection was performed.
  [Error/correction record](test-08-request-error.json). Actual cost9games,
  intended valid checks8; this explicitly exceeds the prior8-game execution cap
  by one correction, not an undisclosed new candidate test.
- Corrected test09 completed918851925. `tests-audit-a2-corrected-final.json` and
  `tests-audit-valid-eight.json` pass map/source/seat/technical integrity.
  Valid A2tests06/07/09 have104outputs,0official errors/warnings/timeouts,
  baseline_complete104,emergency0. Only14complete evaluations in13turns;
  **nonbaseline selections0**. Max internal through-flush17.5611ms; internal
  wall time is not charged platformCPU. Compiler correction markedly improved
  runtime, but the prospective working-search requirement is **not passed**.
- Ranking POST remains0, deployed league3m41671805 unchanged. A separate bounded
  read-only diagnosis was requested; no third source, timer/budget change or
  further game series is automatically launched. OAuth remains active in memory
  under coordinator control while both requested workstreams are in progress.

## A3 fixed checks and accepted ranking,01:17–01:50UTC

- The prospective `AMENDMENT_A3.md` was frozen before implementation. Complete
  depth1 comparisons precede original depth2 with the same weights/16ms/20k.
  Exact source94f0d426…/95540UTF16 passed old-state contracts and one frozen
  96-game gross guard:46/48 versus41/48, all clean,8maps,CI[0,27.0833]pp.
  `verify_d16_a3.py` independently rechecked raw results, identities and gate;
  Java receipts were checked, not replayed again.
- `prepare_a3.py` created fixed requests10/11/12 from the valid structured
  old-map fixtures. Actual games918858744/918859067/918859399:102clean outputs,
  17complete paired comparisons,1nonself depth1 change, no depth2 comparison.
  `audit_a3.py` and additive telemetry audit passed the prospective gate.
  There were12actual technical games in total, including the preserved wrong08.
- Fresh challenge/limits/source/history/progress were saved before ranking:
  ongoing/Gold/deadline09UTC, unchangedleague3m41671805 at380/1039,score14.89.
  `prepare_submission.py` verified exact package/gates/quotas/previous identity
  and saved the rationale before the only rankingPOST.
- POST201 accepted41672652 at01:31:03.050UTC. GET accepted source matches the
  frozen A3 exactly; history retains five old IDs and adds exactly one new ID.
  Progress001/002/003 were6/20/28%. No subsequent POST, rollback or IDE change.
- Saved18complete game logs. `audit_ranking.py --snapshot 002 --out audit-002.json`
  reports10W/8L,543outputs,28D1changes,167pairedturns,0official errors/warnings/
  emergencies. This is incomplete ranking evidence. Two non-first internal wall
  observations exceed20ms; maximum22.097ms, underlying atomic-delay causeUNKNOWN.
- A GET-only batch for eight missing003logs and progress004/battles004 was
  **not executed** because the review service was temporarily unavailable.
  One exact retry was also explicitly unexecuted. No third attempt or alternate
  route. This local execution blocker is not a CodinGame rejection or expiry of
  the user's already-confirmed login. Credential transport/review transcripts
  are not part of the published evidence.
- Running summary: [REPORT](REPORT.md). Final100%/source/leaderboard/full-log
  audit remains pending; do not promote a partial snapshot to a final result.
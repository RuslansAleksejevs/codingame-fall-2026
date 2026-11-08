# PPO-v3 live execution control

Last verified 2026-11-08T07:11:47Z. External spend zero.
Stopped on explicit request; the original full objective was not completed.

## Separately authorized B2M submission: complete

Exactly one authorized POST accepted41665776. Final snapshot382/989Gold,
score12.90,100%/in_progress=false; previous league3m was356/987,score13.51.
All95 battle logs were audited:41 wins/54 losses, no errors/timeouts/warnings.
Exact accepted sourceb87388ad and preserved fallback199c6a2d were verified.
No live improvement was shown. B2M remains active; no automatic rollback.
See live-submission/REPORT.md, audit-final.json and STATUS.json. Client236
exited cleanly, pending scheduled messages0. Ignore stale monitoring messages.
No research restart, Git commit/push or paid resource was performed.

## Separately authorized platform tests: complete

All10 test-games finished, no errors/timeouts/warnings. B2M2/4 versus base3/4
in paired archived replays; B2M lost to the Gold boss. No strength gain is
established. See platform/REPORT.md and verification.json. Fresh deadline
GET confirms9Nov09UTC. Published41657621 source hash is unchanged; live snapshot
348/986Gold. Read/play client184 exited cleanly, credentials were memory-only.
No new submit/IDE write, no research restart and no pending automatic work.

## STOP — no automatic continuation

Own exec150/driver4075/trainer52162 were stopped and verified absent. B recovery
is valid at3,610,194 decisions/82,560games/iteration1290; two later history rows
remain preserved. Do not mistake B's old completed summary for the stopped
second-block state. See `user-stop.json`. No files/checkpoints were deleted.
All scheduled checks cancelled; persistent goal cleared, not marked complete.

Handoff is the first full40-map winner `b2000416`, not an unevaluated late weight.
`handoff-b2m/bot.cpp` compiled;24,833 float32 values exact and4,978/4,978 replay
commands match on100 saved games. Source80,252UTF-16 units. No new games were
played for this handoff. Original base and fallback hashes still match.

B block2 screen/full40dev2 and independent2,200-game final remain unperformed.
Fresh official deadline GET and bounded platform tests were subsequently done
under separate authorization above. Final100 maps remain closed.
A competitive B2M submission was later separately authorized and completed
above. No further submission, rollback or research is authorized. Do not resume
from the historical active-stage notes below.

## Active second-block campaign

05:21:05UTC check: B3,308,728 cumulative decisions (+1,308,312 new),75,520games,
5,846.26 cumulative seconds. All12 frozen sources matched at05:03; no subsequent
training-code edits. Next check05:40UTC. No new blocker; final100 closed.
`REPORT.md` now collects the measured results, versions, commands and caveats;
it is explicitly ongoing, with final confirmation/platform work still pending.

**Current stage: B resumed04:40:50UTC; A screen/native/Java completed.** All984 A
games clean,24,502 transitions/25,486 states exact. IncumbentA1,501,957 still
leads(primary85.42%); new admissible challengerA3,000,798(primary77.08%) joins
it in full40dev2. Average primary86.46% butBC22/24 versus24/24base(-8.33pp)
fails the frozen safeguard; finalA4M also failsBC. No demonstrated A improvement.
All24 repeated incumbent direct results/scores/map hashes agree across the two
screens and first full panel. No post-result guard changes or selective reruns.
B latest2,115,285 cumulative decisions/48,000games/3,660.18s; target4,000,416,
cumulative cap178.0318min adds120 new minutes. B pre-resume backup hashes match.
Next durable check05:03UTC. Chief received the material A result/B start.
Platform documentation now accurately states read/play-only default; submit
requires a separately authorized flag. OAuth readiness still pending.

Earlier second-block observations follow.

**A block2 complete; serial984-game A screen since04:25:56UTC.** The block added
2,002,588 decisions/46,208 games/722updates in3,267.81s(54.46min), cumulative
A4,004,538 decisions/91,520games/6,596.16s. Local Lacoz+4,393games/+155,888calls,
errors[]; parentRSS1.34GB. All6exports passed1,000/1,000argmax (max logiterror
3.06e-5),12 frozen sources and pre-resume backup hashes matched. Average uses
3,750,930/4,001,815/4,004,538: the last two snapshots are only2,723 decisions
apart due to final-rollout overshoot; retain this provenance and do not retune
after screening. B begins only after A screen/native/Java. Next check04:44UTC.
Chief received the material A completion. Finalist/final maps remain unopened.

Earlier second-block observations follow.

04:07:06UTC check: A3,313,095 cumulative decisions (+1,311,145 new),75,520games,
5,468.26 cumulative training seconds. Target4,001,950. All12 frozen training
sources matched at03:49; no subsequent code edits. No finalist/final panel
exists. Next durable check04:26UTC near the expected training completion.
No new blocker; routine counters were kept local.

**Current process: exec150, driverPID4075, train-a-block2 since03:31:19UTC.**
A resumed from2,001,950 decisions, now2,007,470; target4,001,950. Cumulative
time cap175.472539min adds120 new minutes to recorded first-block time.
`continuation-block2/before-a` preserves latest files with SHA256 (5.2MB).
All12 trainer sources and original base/fallback hashes passed preflight.
No training/panel process remained before launch. Next durable check03:49UTC.

The command is `caffeinate -s code/arena/.venv-rl/bin/python
code/rl/v3/continue_blocks.py --block 2`. Read `continuation-block2-status.json`,
`continuation-block2-events.jsonl`, and the indicated stage log. The sequence is
A train/average/export/984-game screen/native/Java, independent B likewise,
then full40-map block2. No parallel heavy training/timed evaluations. No third
block automatically starts. Synthetic limits/checkpoint-selection/retention/
error-stop tests passed in `continuation-tests-2.log`. See `CONTINUATION.md`.
Retain prior full-panel incumbents A1,501,957/B2,000,416 plus at most one new
screen leader per seed. All immutable prior results remain preserved.

Full block1 finished:2,320 games, zero own errors, two Lacoz errors in other
candidates excluded;60,994 transitions/63,312 Java states matched on2,318
clean games. B2M leads:60/80Lacoz(base58),77/80newkh(base71),76/80old(base72),
76/80v6(base74),77/80BC(base74score),57/80direct. External gain+4.25pp;
individual intervals still include zero. A1.502M external+3.50pp, Lacoz-3.75pp,
four other opponents improved. This is adaptive development, not independent
confirmation. Chief received the full result and actual continuation start.
Finalist/final maps remain unopened. OAuth readiness pending; no local blocker.

## Earlier full-development panel checks

03:06:30UTC check:1,205/2,320 games, no own/opponent/invalid/process failure.
All12 frozen training sources match. The panel is still active; no partial
score selection. Next durable check03:25UTC. Finalist/final panel absent.
For any later resume, the120-minute new block cap must be added to recorded
cumulative elapsed time, not blindly multiplied by the block number.

**Current process: full development, driverPID36549/panelPID36567.** The actual
status records start02:46:38UTC; read-only process inspection02:49 confirmed it
alive with no concurrent heavy training. Do not rely on stale shell-session IDs.
Four shortlisted policies,40 known development maps,2,320 games;250 logged at
this check. Read `full-dev-block1-status.json` and `full-dev-block1.log`, then
the native/Java reports and ranking. Next durable check03:06UTC. No finalist or
reserved map has been opened. Decide further bounded training from full results.

Search closed at02:40:31UTC:288screen +448confirmation games,21,009 transitions /
21,745 Java states exact, no technical exclusions. On28 other development maps,
search2 external equal-weight gain+7.1429pp, map95%CI[0,15.4762]. The required
strict lower bound>0 failed. `search/decision.json` is `not_confirmed`; do not
generate teacher data or reopen/tune the pilot. The four-hour limit was respected.
This is inconclusive evidence, not proof of no effect. Search/direct success is
not a deployable multi-network package. Chief received the material outcome.
Read/play OAuth readiness remains pending; it does not block local evaluation.

## Earlier first-block and search snapshots

**Current process: external search session124, started02:24:14UTC.** The A/B
driver45 exited0 at02:21:15. Both840-game screens clean;43,129 transitions /
44,809 full states matched Java. Bshortlist `b2000416`, `b1502461`; Ashortlist
`a1002368`, `a1501957`. B2M19/24Lacoz (base18),23/24newkh(base20),22/24oldkh
(base20), v6/BC tied, direct19/24(map95%58.3--95.8). Adaptive selection only.
Neither average advanced into the full-development shortlist.

`caffeinate -s code/arena/.venv-rl/bin/python code/rl/search/run_external.py`
is running; driver stdout `search/external-campaign.log`, current stage log
`search/external-screen.log`. At the check204/288 games, no technical failure.
Only if the preliminary gate passes, the script starts448 confirmation games
on the other28 development maps. Hard stop04UTC, no teacher data yet.
No concurrent heavy training/timed panels. After session124 exits and its
`decision.json` exists, run `code/rl/v3/full_development.py --block 1` for the
four shortlisted PPO policies (2,320 games/40maps). No final freeze/holdout yet.
Next durable check02:39UTC. Milestones reported; OAuth readiness still pending.

Earlier stage snapshots follow.

**Current stage: B completed; serial B screen since02:05:31UTC.** B finished
2,000,416decisions/45,376games/709updates in3,481.91s(58.03min). Local Lacoz:
4,254games/150,669calls/zero errors. B average1,502,461/1,751,552/2,000,416 and
five1,000-group exports passed. TotalsA+B4,002,366decisions/90,688games/6,810.26s.
All12sources and base checkpoint/weights/deployed fallback hashes reverified.
The screen has840planned games (100 logged at this check); do not overlap
timed panels. After the entire driver exits, immediately start external search
within the04UTC hard cap, then full40-map development. Next check02:22UTC.
Training completion was reported. Read/play OAuth readiness was requested;
do not issue another short-lived code until acceptance can be coordinated.
No final freeze/holdout yet; goal remains active and no submission authorized.

Earlier stage snapshots follow.

**Current stage: independent B training since01:07:20UTC.** A's screen finished
all840 games clean in850.73s;20,911 transitions/21,751 full states matched Java.
Shortlist: `a1002368`, `a1501957`. Top A1.002M won21/24 versus Lacoz (base18/24),
24/24 versus each khoufou (base20/24),24/24v6 (base22/24),24/24BC (base24/24),
and16/24 directly versus base (map95%CI41.7--87.5%). This is adaptive12-map
selection only. External paired gain intervals include zero; no independent
strength claim. The average was weaker and is not advanced by default.
B uses seed202611075, verified same9ba362b2 base checkpoint, not an A weight.
Latest B1,416,196decisions/32,000games/2,442.67s; checkpoints251,611/502,221/751,890/
1,001,679/1,250,948 saved. Source hashes matched01:30, no later code edit.
Stage milestones were reported; routine counters stay local. Next check02:06UTC.
No final maps opened.

Earlier stage snapshots follow.

**Current stage: A completed, serial A screen running.** A ended00:53:00UTC:
2,001,950 additional decisions,45,312 games,708updates,3,328.35s (55.47min).
Parent RSS1,392,607,232bytes; Lacoz4,250 games/148,716calls/zero errors.
Nearby average1,501,957/1,750,414/2,001,950 and all five1,000-group exports passed.
The 840-game screen began00:53:05;205 games at the current check, no own,
opponent, invalid or process errors. Do not interpret incomplete strength data.
No other heavy/timed work during the screen. Independent B starts automatically
after A verification/ranking. A completion was reported; next check01:12UTC.

Historical launch and intermediate observations follow.

Shell session 45, driver PID 36711, started 2026-11-07T23:57:29.729707Z.
The command is:

```sh
caffeinate -s code/arena/.venv-rl/bin/python code/rl/v3/campaign.py --arms a b
```

Driver stdout: `campaign-first-blocks.log`. Per-stage logs are exclusive new
files, with live `campaign-status.json` and append-only `campaign-events.jsonl`.
At this check A had 1,076,325 additional decisions / 24,320 games / 1,806.69 s.
Saved checkpoints: 250,246; 502,810; 751,928; 1,002,368. An earlier operational
note said 750,240 for checkpoint three; the actual saved directory is 751,928.
The next phases are A averaging/export/serial screen, then independent B and
its averaging/export/serial screen. Neither screening result exists yet.

All 12 frozen training source hashes match `seed-a/source-sha256.json`.
Do not edit them during this campaign or a resume. The base checkpoint, weights
and deployed fallback hashes match the frozen protocol. No Git refs changed.
No other project's process was stopped. No final-holdout map was opened.

## Search pilot

Hard window 2026-11-08T00:00:00Z--04:00:00Z. Do not extend it.
`search/native-scout/summary.json`: 216 untimed games, 6,663 Java states;
search2 won 23/24 versus base, 21/24 versus long3m, 22/24 versus extended.
These opponents are the search response models, not independent validation.

The first standalone protocol check failed in 8 streams / 618 checked plans.
`search/protocol-before-fix/summary.json` preserves it. The parser now validates
the official initial placement and recovers absolute player order, including
all relative fields. Unknown custom starts fail explicitly. The new check
`search/protocol-absolute-order/summary.json` passed all 618 plans on both seats
for greedy / one-turn / two-turn policies. The native search library is bitwise
unchanged (SHA256 a2aebf9bf844d7efb1f69174c78f17deae0ae2c972d3082d5d656e8231030078),
so this is a standalone-input repair, not a retuned native scout.

Reproduction commands, each output directory created exclusively:

```sh
code/arena/.venv-rl/bin/python code/rl/search/protocol_check.py --out experiments/rl/2026-11-07-ppo-v3/search/protocol-before-fix
python3 code/rl/search/build.py
code/arena/.venv-rl/bin/python code/rl/search/protocol_check.py --out experiments/rl/2026-11-07-ppo-v3/search/protocol-absolute-order
```

The pre-fix command intentionally exited 1; the repaired check exited 0.
Compiler execution used reviewed access for macOS temporary files. No network
or external compute was used. The separate seed30012 check passed all 1,368
plans at 00:29:10Z: combined post-repair parity is 1,986/1,986 plans, no mismatch.

Only after the entire A/B driver reaches `first_blocks_finished`, run:

```sh
code/arena/.venv-rl/bin/python code/rl/search/run_external.py
```

The script requires at least 30 minutes before the search cutoff, checks source
and binary parity hashes, runs a 288-game external screen, and conditionally a
448-game independent-from-search-selection confirmation. It records a failure
decision on incomplete validation and never starts teacher training. Full search
cannot yet satisfy the contest source-size limit. See `search/PROTOCOL.md`.

## Next PPO comparison

`code/rl/v3/full_development.py --block 1` is prepared, not started. It requires
the A/B driver and a recorded search decision to avoid concurrent timed panels.
It compares at most two screened networks per seed on all 40 development maps,
verifies native/Java states, and writes provisional rankings. It does not open
the final holdout or promote/deploy anything. Synthetic paired-statistics,
one-point tie ordering, and technical-error rejection tests passed on 8 Nov.
Review broad gains before another bounded continuation or freezing a finalist.

The final 40001--40100 maps remain closed. Rebuild the content exclusion union
immediately before a single frozen finalist's final evaluation. Research stops
by 2026-11-09T02:00:00Z, seven hours before the saved official deadline09:00Z.
The exact deadline still awaits a fresh authenticated API read.

## Packaging tool smoke, 2026-11-08T00:35Z

The explicit candidate mode of `code/rl/export/package.py` requires weights,
their expected SHA256, and a new experiment output directory. It does not touch
the selected policy or deployed fallback. The legacy invocation is unchanged.
`package-smoke-base` tested only the old base network, not a new finalist:
24,833 float32 parameters exact, 890/890 commands equal on 20 saved games,
80,252 UTF-16 source units below 100,000. Existing-output rejection was tested.
No new games, timing claims, platform calls or submissions were involved.

```sh
code/arena/.venv-rl/bin/python code/rl/export/package.py --weights experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt --sha256 dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb --out experiments/rl/2026-11-07-ppo-v3/package-smoke-base
code/arena/.venv-rl/bin/python code/rl/v3/verify_package.py --manifest experiments/rl/2026-11-07-ppo-v3/package-smoke-base/package.json --panel experiments/rl/2026-11-07-ppo-v3/baseline-dev --records 20 --out experiments/rl/2026-11-07-ppo-v3/package-smoke-base/verification
```

The later A check was 1,330,497 decisions / 30,080 games / 2,232.44 s, with an
additional checkpoint at 1,250,503. It was still the first training block.
Keep routine counters/SHA checks locally; send coordination messages only for
completed A/B, evaluation/search outcomes, user action/blockers, a frozen final
candidate, or deadline risk. Continue normal supervision and durable checks.

## Continuity and authority

### Final-run tooling prepared, not executed (00:49Z)

`freeze_finalist.py`, `run_final.py`, `final_evidence.py`, and `FINAL_GATES.md`
implement a single frozen finalist, known-map package parity before any final
game, the 2,200-game panel using both packaged candidate/base, map-content
exclusion, native/Java verification, and fixed promotion criteria. A 90% clean
coverage guard is conservative; it cannot relax the original gates. No final
candidate has been frozen, no final map opened, no promotion or submission.

Eleven synthetic criteria tests passed (`final-gate-tests.log`); they contain
no generated/read maps. `baseline-binding-verification.json` reverified all
400 already played baseline games / 10,637 transitions and binds results to
panel/spec/matches SHA256. `package-harness-build` tested packaged integration
on an empty seed list: binaries compiled, **zero games/maps**. Full timed use
remains a later serial stage. The learning sources are unchanged.

Once research really ends, inspect active processes, then use the leading
admissible entry of the final full-development ranking:

```sh
code/arena/.venv-rl/bin/python code/rl/v3/freeze_finalist.py --ranking <full-dev-ranking.json> --candidate <ranked-name> --research-complete
code/arena/.venv-rl/bin/python code/rl/v3/run_final.py --research-complete
```

Do not run those commands during the first blocks or before the search/full-dev
decisions. The final driver requires 100 known-record checks per package before
opening any held-out map, stops on failure and leaves platform work pending.

At 00:49:17Z A was 1,837,806 decisions / 41,600 games / 3,064.09 s, still
training toward 2M. All 12 source hashes matched. The next stage check is00:56Z.

The durable execution goal is active. The next scheduled check is
2026-11-08T02:39:00Z; inspect processes/logs and arrange the next check if active.
Report measurable progress and blockers to the coordinating agent. Keep this
checkout; no extra LLM chats, copies, commits, pushes, publication or submission.
OAuth expired without approval; its unauthenticated process was closed and no
token obtained. Local work is not blocked. Start a new official read/play-only
flow when platform verification is ready and the user can accept it.
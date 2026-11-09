# A3: one bounded anytime-search delivery repair

Recorded9November2026,01:13UTC, before any A3 implementation, inference, map or
platform result. This is a coordinated next implementation step within the
explicit request to finish D16 and test one ranked bot, not an automatic old
campaign restart. The A2 actual-search gate remains FAILED; its source, logs,
correction and the359/1200 local STOP are preserved. No A3 result is assumed.

## Why this specific change

[Read-only diagnosis](../2026-11-09-rl7/d16/A2_SEARCH_DIAGNOSIS.md) found that the
first full baseline/alternative comparison requires17 complete policy decodes.
Valid A2 official tests06/07/09 contain104outputs but only one evaluated
alternative, tied with baseline. This is search starvation, not a selection bug.
Simply increasing16ms is not justified by the measured cost distribution.

One candidate only: complete-three-response, one-turn evaluation first; then
original two-turn evaluation if time remains. The first shallow comparison
needs5policy decodes, but can still be too expensive on some positions.
This is an explicit **timed-policy/horizon-fallback change**, not an exact A2
optimization and not a claim to retain the old teacher's measured strength.

## Implementation and invariants

- Preserve all four exact9-bit networks, three response models, full legal
  decoder, deterministic .15/.35/.7 proposals, .5mean+.5minimum aggregation,
  .02margin, .995discount,16ms first-score-token origin and20000cumulative cap.
  Keep the mandatory useful greedy baseline; no clock reset, budget increase,
  fast-math, target pragma, architecture or learning change.
- First evaluate baseline and each distinct proposal after one complete step
  against ALLthree models. Only a fully compared alternative may replace the
  current legal baseline. Never compare scores from different horizons or
  incomplete model subsets.
- After the finite shallow pass, reuse exactly those plans and evaluate the
  original depth2 in the original order. Retain shallow incumbent until a full
  deep baseline/alternative comparison exists; then completed deep comparisons
  take precedence, including a return to baseline. Unlimited final actions and
  complete depth2 scores must match A2 exactly.
- Record distinct shallow/deep counts and selected tier. Never label a shallow
  result a completed original-depth evaluation. Add process-CPU diagnostics;
  state what they exclude and do not equate them with official chargedCPU.
- Save new isolated source/package/hash/readable implementation. Target<98000
  UTF16. Preserve A1/A2 and all historical frozen files/binaries.

## Fixed contracts and fresh gross-regression check

One initial build/contract lease<=5min, within the existing90min D16 total cap.
The original20disclosed games/both seats, exact weight dump,1156root unlimited
plans/scores, hidden state/root immutability/legality are required. Independently
verify the one-turn ensemble oracle, deterministic interruption at partial-model,
deep-baseline and deep-alternative boundaries, and20/30ms delayed-input useful
baseline. Fixing a contract implementation error must retain the failed evidence;
no alternate strategy or outcome-based source selection is authorized.

Freeze this ONE source/config/schedule before opening the previously allocated,
unused72005–72012: **8maps ×3opponents (Lacoz/newkh/oldkh) ×2seats ×2roles
(A3/unchangedleague3m) =96 original-referee games**. Original1000/50ms limits.
Interleave matched roles, audit canonical novelty and exact Java replay. No new
large final, reserve maps, repeated games, extra variants or checkpoint selection.

Prospective coarse sanity guard, on both all and common-clean whole-map scores:
candidate external total>=control; no opponent's candidate total below control
by more than2points (draw=.5) on the selected paired set. Require>=7/8common-clean
maps and zero candidate/control own technical errors/emergencies; any own/control
failure stops without rerun. Opponent-only errors remain in all-game accounting,
exclude the whole paired map in clean estimates, and are not replaced. Report
all points and whole-map uncertainty;8clusters are **not independent proof of a
strength improvement**. No threshold/seed extension after observing results.

## Exactly three additional official technical tests

Coordinator only, same intended GoldBoss/Captainseb/selfplay maps and seats as
valid06/07/09. Derive requests from saved structured options; audit exact maps,
source and opponents. No manual delimiter edits or opponent search. All IDE flags
false. A3 adds exactly3technicalgames; cumulative phase cost12 including the
preserved erroneous08. It authorizes no fourth test or another candidate sweep.

Functional gate: at least10own turns containing a complete same-tier
baseline/alternative three-model comparison, and>=1actual nonbaseline selection
in a non-self game. Every selected action must identify a completed tier; all
outputs baseline-complete,0official own errors/warnings/timeouts/emergencies.
Normal non-first internal through-flush>20ms requires investigation and is not
silently called safe. ProcessCPU is descriptive, not official accounting.
The nominal remaining30ms does not establish a hard real-time guarantee.

If contracts, coarse local guard and functional/technical platform checks pass,
the already authorized **single exploratory ranking submission** may proceed with
the incomplete strength evidence disclosed. Refresh current source/history/
progress/limits before it; verify accepted source, wait for100%/in_progressfalse,
save/audit every completed final-snapshot battle. No automatic rollback.

If this bounded candidate fails, report the actual blocker/negative result. Do
not begin A4, raise time, add training, reopen a failed final or submit an inert
baseline as demonstrated D16 search. Another substantive strategy would require
a new explicit direction. Diversity is already COMPLETE/NO-GO and is not resumed.
No Git commit/push, paid resources, IDE writes or extra chats. Existing06UTC local
research cutoff and09UTC verified official deadline remain unchanged.
# D16: A3 submitted once; final ranking pending

Coordinator update01:31UTC: authorized single submission41672652 accepted201,
exact frozen A3 source verified. Initial progress6%/in_progress=true; no final
ranking yet. Fresh immediate league3m comparison baseline,01:29:34UTC:
380/1039 overall,Gold228/428,score14.89. Earlier368/15.11 remains historical.

Later preliminary ranking audit records a normal22.097ms internal wall turn
(processCPU22.026ms) in game918861381,seat1,turn18, with no official error or
emergency. Atomic-operation delay cause UNKNOWN. The16ms cooperative limit is
not a hard response bound; details retained in [A3 report](A3_REPORT.md).

Latest2026-11-09T01:27UTC: A3 contracts, all96clean fresh gross-check games and
three official functional/technical tests pass. A3 wins46/48 versus unchanged
league3m41/48, paired gain+10.4167pp95%CI[0,27.0833], not strength proof.
Official102outputs contain17paired comparisons and one non-self shallow change;
no completed deep comparison there. Exact source95540UTF16/SHA94f0d426…ab4f8
is unchanged and READY for the coordinator's one exploratory ranking.
[A3 current report](A3_REPORT.md). No ranking result is assumed.
Historical A2 failure and A1 incomplete final below remain unchanged.

Current update2026-11-09: candidate1's final stopped359/1200 after a CONTROL
league3m timeout, not a D16 error. Candidate1 then exposed a platform performance
blocker: zero completed search evaluations in its first43official turns.
One separately authorized compiler-only candidate2 passed local contracts under
[A2](AMENDMENT_A2.md), but valid official tests06/07/09 produced104baseline-complete
outputs,14completed evaluations and0nonbaseline choices. The actual-nonbaseline
criterion is not met. No ranking submission yet; the old1200-game gate is false.
[Read-only diagnosis and one unimplemented proposal](A2_SEARCH_DIAGNOSIS.md).

Early technical state as of2026-11-09T00:17:24Z follows. PROJECT_REPORTED local
results, not a platform result unless explicitly attributed to official logs.
This is new authorized finite work. Historical v5/v6 gates and failures remain
unchanged. No training or precision/response-model change in this lane.

## Exact source and repair

[Standalone source](package-attempt1/bot.cpp),94389UTF16/219249UTF8bytes,
SHA256`aba2d6f2ae4bcd92eb79f38fd6bd643be9973b714b135c7b532a3e9fd9a80701`.
The four unique networks retain the exact v6 b9 payload. All397328decoded bytes
match oldb9, SHA256`ac5532cfc76dbd05b3a6a493c4892d2206abb19d80a114d0fad8cd3bd78868e5`.

Only the completed greedy baseline is mandatory. Optional cooperative stopping
still uses16ms from the first score token and20000cumulative forwards, including
baseline cost. The origin is not moved. The baseline can be a legitimate WAIT;
`baseline_complete` and exact greedy equality distinguish it from an emergency.
Full timing includes input/restore/baseline/optional work/flush. Startup,
pre-first-token time and the final diagnostic write are not internally measured.
No hard-real-time guarantee under arbitrary OS/input delay is claimed.

## Completed technical evidence

- Exact unlimited parity on20disclosed saved games, both seats:1156roots,
  2312actual stream commands. Hidden-state restoration/root immutability passed.
- 328forced cap/expired/tiny-budget calls return the exact completed greedy plan;
  20nonbaseline partial-search selections passed legal/complete-prefix contracts.
- Real piped delay on the original40016/seat1/turn27prefix: repaired output is
  the full non-WAIT greedy plan with280forwards. Nominal20/30ms delay measured
  input25.5111/35.6145ms, through-flush26.151/36.3055ms, baseline.629/.672ms,
  emergency0. Oldb9 under the same nominal injection emits actual emergencyWAIT,
  0forwards. This demonstrates the repaired mechanism, not the unknown cause of
  the historical17.7745ms input observation.
- Six disclosed old-map regressions plus72fresh technical games on72001–72004:
  78/78clean, zero own/control/teacher/opponent errors.867candidate outputs,
  baseline_complete1 on every output, emergency0, through-flush maximum16.630ms,
  baseline maximum3.163417ms. Original1000/50ms referee limits unchanged.
- Exact Java/native replay:2071states/1993transitions across all78games. Four
  pre-freeze statistics tests pass. Development winrates did not select a source.

[Contracts](contracts.json) · [Technical readiness/raw bindings](technical-readiness.json)
· [Commands/failures](COMMANDS.md).

## Frozen next stage and platform boundary

[Final freeze](final-freeze.json) recorded00:17:24UTC before final generation.
One unchanged source/config/analyzer;40maps72101–72140,1200games, both seats,
candidate/league3m-control/originalFP32teacher against three external opponents
and directleague3m/B2M. Four serial300-game blocks; no interim strength selection.
Paired all/clean whole-map intervals and separate technical outcomes follow.
72005–72012,40021–40100 and65001–65040 remain unused by this lane.

Early source/readiness plus [five fixed official requests](official-test-requests.json)
were sent to the coordinator, who alone owns OAuth/API/submission. No platform
call occurred in this lane. Local strength is not yet measured on the independent
set; an inconclusive honest result may support the authorized exploratory single
ranking only after technical checks and the prospective sanity review.

All work is local under RL-v7 d16 leases, cap5400s, each<=25min, cutoff06UTC.
Protected league3m/B2M/checkpoint/oldb9 identities match. Git/IDE/paid compute/
rollback/new agents0. Final compute ledger, process/timer closure and ranking
result remain pending; they are not implied by this technical milestone.

## Independent execution log (technical progress only)

2026-11-09T00:29:20Z: confirm1 completed300/300 on72101–72110, all300clean,
9343states/9043transitions exactly replayed, no mismatch/exclusion. Lease442.038421s.
Slot released to the separate diversity lane. No interim strength analysis or
source/config change. Remaining fixed final900games are not yet completed.

2026-11-09T00:34:04Z: confirm2 stopped59/300; total359/1200,841unplayed. Control
league3m/Lacoz72112seat0 incurred an actual referee timeout. Four internal timing
records but three accepted outputs; last baseline.416834ms, input21.4848ms,
through-flush21.9147ms. Full timeout cause UNKNOWN. No rerun, source change or
confirm3/4. Twenty maps generated,12played,11complete;72121–72140 remain unopened.

Post-stop existing-data audit/replay completed00:39:15Z:358eligible trajectories,
10970states/10612transitions, exact; only control timeout excluded. All119D16
games clean (94W25L),3540baseline-complete outputs,0emergency,491nonbaseline
selected actions, maxthrough-flush16.2416ms. All original FP32reference hashes
match the v5 freeze. [Audit](poststop-decision.json) · [Forensics](control-timeout-forensics.json).

Descriptive partial estimates, NOT a completed final: external11map gain
+12.1212pp,95%CI[approximately0,24.2424]; the stored lower2.5e-16 is numerical
zero, not proof of a positive lower bound. Teacher retention−3.0303pp
[−9.0909,3.0303]. Directleague3m19/24=79.1667%[54.1667,100]; B2M16/24=66.6667%
[45.8333,87.5]. All/clean estimates coincide on complete clusters; the failed
control cluster is incomplete and remains in observed error accounting.

Platform runtime diagnosis is separate: actual league3m and D16 contain the
same FastNetwork kernel, but only league3m has guarded GCCO3. Localclang-O3
masked the omission. [Diagnosis](RUNTIME_DIAGNOSIS.md) records actual official
timings and the UNKNOWN platform compiler flags. A2 must be measured before
claiming the missing prelude caused the observed slowdown.

## Compiler-only A2 delivery, completed00:47:48UTC

Current source: [package-attempt2/bot.cpp](package-attempt2/bot.cpp),94468UTF16,
219328UTF8bytes, SHA256
`d36aba4daa02580b1a20e5e1d000954cea330a852d8adbae1bb8f593572c9d15`.
Exactly79bytes of guarded GCCO3 prelude were added. All219249bytes of the A1
body are identical. No weights,16ms budget, response models, loop order or
telemetry changed; no fast-math/target pragma was introduced.

Appleclang17-O3 version and flags match A1. A fresh unchanged A1 diagnostic was
also built. A2 production, diagnostic and weight-dump executable hashes each
exactly match their A1 counterpart on this local compiler. API-library file hash
differs; its numerical contracts, not file-byte identity, are asserted. All
397328decoded weight bytes match the old9-bit reference.

On the same20disclosed games/both seats:1156roots and2312actual stream commands
match;320paired forced-baseline cases and20nonbaseline completed-prefix cases
match, including hidden state, immutable roots and legal actions. Full inputs,
outputs, stderr and detailed cases are retained in candidate2-contracts/.
[A2 manifest](candidate2-package.json). No new local game, map or learning update.

An initial test-harness syntax error failed before source generation or compilation
(.048119s); it was corrected without changing any candidate. Successful reviewed
build/contracts lease56.984693s. Existing A1 binaries/source/freeze/STOP evidence
remain unchanged. Exact A2 handoff has been sent for three fixed coordinator-only
official tests on the same boss/Captainseb/selfplay fixtures. Original five A1/
control tests all completed without official errors; all104A1outputs had no
completed search evaluation. Actual A2 runtime improvement is not assumed before
those new measurements. No ranking POST by this lane.

## Additive A2 platform result and scope correction, 01:09UTC

The paragraph above records the pre-test handoff, not the current outcome.
Valid unchanged-source A2 tests06/07/09 are918849391,918849860 and918851925.
Test08 used a mistakenly transcribed map option; its request/result and the
earlier child audit remain preserved, but its data are excluded from the current
fixed-panel conclusion. The corrected three tests contain104own outputs,
104completed baselines,0emergencies,14complete evaluations over13turns and
0nonbaseline decisions. Parent audit reports no official errors/timeouts.

Read-only trace shows99turns generated no distinct alternative. Ninety-one
never completed a baseline evaluation; the sole completely evaluated alternative
tied baseline exactly. Root response preparation and full baseline depth2 work
starve alternative generation. This is not evidence of a broken selection test.
Compiler optimization helped runtime, but A2's prospective transfer gate failed.

The diagnosis proposes one ensemble-preserving one-turn-then-two-turn schedule
at the unchanged16ms deadline, explicitly a new timed-policy fallback requiring
a bounded coordinated amendment. It is NOT implemented or tested. No automatic
third fix, budget increase, new final, or ranking follows from the proposal.
# A3: submitted once; ranking in progress

2026-11-09T01:31UTC, current stage: coordinator reports the one exploratory
submission accepted201, ID41672652, exact source verified; initial ranking6% and
in_progress=true, not a final result. This follows the
coordinator's [prospective amendment](../../2026-11-09-d16-live/AMENDMENT_A3.md),
SHA256 `78d746d47cdba10ca5702572af62355947af81e81c49aa5a15fe110887fb1273`.
A1/A2, A2's failed functional gate, test08 correction and359/1200STOP remain.

## Exact delivery

[Standalone source](package-attempt3/bot.cpp):95540UTF16,220400UTF8bytes, SHA256
`94f0d426de787f7ed29a0ce87fa03fd3e0bae2ebb27c7d76548f4624f67ab4f8`.
[Manifest](candidate3-package.json), SHA256
`1073069f6e4915030ad302defa1d809582de1501d72ed4841e10651204cfbc4b`.
All397328decoded weight bytes exactly equal the old9-bit payload, SHA256
`ac5532cfc76dbd05b3a6a493c4892d2206abb19d80a114d0fad8cd3bd78868e5`.

This is an explicit timed-policy change: first compare complete one-step plans
against all three committed root-response models, retaining the best complete
same-tier result; then evaluate the same plans through the original two-step
procedure. A deep baseline alone cannot overwrite the shallow incumbent.
A complete deep baseline/alternative comparison takes precedence, including
returning to baseline. No incomplete ensemble or cross-depth comparison.

Mandatory greedy, all four networks, exact precision, deterministic proposals/
temperatures, robust aggregation/.02margin/.995discount and first-score-token
16ms/20000cumulative cap are unchanged. Unlimited final deep choices/scores
match A2. This does not transfer A1's incomplete strength result to A3.

`search.complete`/`values` still mean original depth2 ONLY. New fields:
`shallow_complete`, `shallow_values`, `selected_tier`(0greedy/1shallow/2deep),
`paired`(a complete baseline/alternative ensemble comparison exists). A changed
decision must belong to a completed tier with at least two compared plans.
Top-level `process_cpu_us` is std::clock from first score token through stdout
flush, excluding startup/initial map/pre-first-token/final stderr. It is not
official charged CPU. Wall accounting is unchanged.

## Fixed contract result, completed01:22:07UTC

- Twenty disclosed games/both seats:1156roots with exact unlimited A2 final
  depth2 actions/scores and hidden-state restoration/root immutability.
- 1156actual stream commands; all1156independent one-turn ensemble oracles pass.
- 328forced baseline cases;542deterministic interruption cases, including
  11selected shallow incumbents,15selected deep incumbents,70deep-baseline-only
  holds and206incomplete shallow cases. Legal complete-tier outputs throughout.
- Actual20/30ms delayed input on original40016/seat1/turn27 returns the exact
  useful non-WAIT greedy plan,280forwards,emergency0. Through-flush22.9202/
  31.7559ms; baseline.612833/.658667ms; processCPU.868/.922ms. This verifies the
  repair under injected delay, not the UNKNOWN historical input-delay cause.

Full streams, stderr, oracle results, cap cases and delayed-input records are in
candidate3-contracts/. Appleclang17-O3, same local compiler as A1/A2.

One contract-harness compile failed before tests: the compact base class omits
its unused `evaluate` member. The independent test oracle was corrected to
construct its value features explicitly. Failed api.cpp, compile log and receipt
are retained. The standalone source and its already-built binaries were NOT
changed. First lease3.890876s; successful same-strategy contract retry46.349158s.

## Frozen fresh gross-regression guard

[A3 freeze](a3-freeze.json), SHA256
`af707fb28e3f2eb352953aeec813f68d9ad237b032dd7006997ddd4c639cc8ae`, recorded before
opening72005–72012. Four analyzer tests passed. Eight maps x3public opponents
(Lacoz/newkh/oldkh) x2seats x2roles(A3/unchangedleague3m)=96games, one source,
fixed interleaved schedule, original1000/50ms referee and exact Java replay.
Canonical novelty includes all current v7 claims and all saved official test
maps, including the preserved erroneous08. No replacement or reserve maps.

Prospective guard, both all-game and common-clean whole-map views: candidate
total>=control; no opponent deficit>2points; >=7common-clean maps; zero own/control
technical failures/emergencies. Any such failure stops without rerun. Opponent-
only failures remain in all accounting and exclude the whole map from clean
estimates. Eight map clusters can guard gross regression, not establish strength.

Coordinator alone runs exactly three official fixed tests and owns the single
authorized exploratory ranking. Required platform functional counts and safety
checks are in the amendment. Local result and platform result are still pending
at the initial handoff; completed results follow. No A4, sweep, budget increase,
new learning or automatic rollback.

## Completed96-game result, 01:26:25UTC

All96games clean,8/8common-clean maps, zero own/control/opponent technical
failures or emergencies. Canonical novelty passes against3164canonical and
1288legacy identities,156bound source files. Exact original Java/native replay:
2611states/2515transitions, zero mismatches/exclusions. All raw JSON, portable
records, commands, stderr and per-turn measurements are retained under a3-gross/.

| Opponent | A3 wins/games | Unchangedleague3m wins/games |
|---|---:|---:|
|Lacoz|14/16|11/16|
|Newkh|16/16|14/16|
|Oldkh|16/16|16/16|
|Total|46/48|41/48|

No draws. All-game and common-clean estimates coincide. Paired whole-map gain
+10.4167percentage points,95%bootstrap interval[0,27.0833]. This passes the
predeclared gross guard, **not proof of a positive strength effect**; only eight
map clusters. No maps/source/thresholds were replaced or extended.

Local A3:1289outputs,1130complete paired comparisons,193changed decisions
(185deep,8shallow),0emergencies. Maximum internal through-flush16.5209ms,
processCPU16.102ms, mandatory baseline2.537792ms. These local search-capacity
figures do not describe platform capacity.

[Full raw audit/decision](a3-gross-decision.json), SHA256
`df62ccaafe2f6c5a6c4586795015834505a5a1a44a4c96f30deee869241148ca`.
Matches SHA256 `00a497f1c2b4661ad8ba09f22296af14ffd532e784693b87376a4b1b074b2123`.
Manifest SHA256 `875c0cd57c68012207a93a07630f1313535fb254a53b1f4a89bc6c7e126cd1a6`.

## Official fixed technical result, independently reparsed01:27UTC

Coordinator-only tests10/11/12:918858744/918859067/918859399. Parent audit verifies
exact source, maps, seats and opponents, with zero official own errors/warnings/
timeouts. Own read-only reparse of all saved telemetry agrees:

- 102outputs, every baseline complete,0emergencies.
- 17complete same-tier baseline/alternative comparisons:10boss,3Captainseb,
  4selfplay. One actual nonbaseline choice, in the non-self Captainseb game.
- That changed action used tier1. **No complete depth2 comparison** occurred on
  these platform tests. Functional search exists but is rare; no assertion that
  the full local D16 search capacity or strength transferred.
- Maximum internal wall through-flush16.4098ms, processCPU16.202ms; no normal
  non-first turn exceeded20ms. CPU remains descriptive, not official accounting.

The prospective functional+technical gate passes. Technical outcomes were boss
loss, Captainseb win, selfplay stress; these are not strength estimates. No more
technical tests or source changes are authorized for this candidate.

Saved official raw SHA256 bindings:

- test10: `2213b0730475cd53899ef54acf060e37728d85a63649e12074d0887379d18aec`
- test11: `8fd6ba4e4a2a5684f333d9cbc16b88bc981156cbe86f840f8bfd61723f3df403`
- test12: `2f9ac486bd9f1d39ad902bb63870d36b23d1b4e879192ec730614c83e65da506`
- parent tests-audit-a3-final.json:
  `64c363d34d2734ab4eaad49dc653e295be5942163459a3bca21da0b6bdd5613e`

## Resource/authority handoff

All new local D16 game records:533rawJSON+533portable records (437A1+96A3).
No training, new distillation labels, paid compute, Git mutation, IDE write or
API/submission by this lane. Protected sources/weights and A1/A2 frozen identities
remain unchanged. Total20completed leases968.06575754seconds (16.13min of90).
No local compute remains scheduled. Contract timer canceled; panel timer already
delivered after completion, not an ongoing job. Coordinator owns ranking and
root organizational updates. Available for saved ranking-log analysis.
Final scoped process check returned `No matching D16 workers`; the product's
pending scheduled-message list was empty. No cleanup/deletion or rollback.

## Authorized ranking accepted, awaiting final result

PROJECT_REPORTED from coordinator rade46b18ac74a5003f254d, as_of2026-11-09T01:31UTC:
exactly one POST accepted201, submission41672652. Accepted source is the frozen
A3 SHA94f0d426…ab4f8; active source verified. History retains all five prior IDs
and exactly one new ID. Initial progress6%,in_progress=true; no final rank or
strength claim. Coordinator continues GET-only completion/log auditing.

Use the **fresh immediate pre-submission league3m snapshot**,01:29:34UTC, for
the eventual comparison:380/1039 overall, Gold228/428, score14.89. The earlier
368/1036,Gold221/428,score15.11 snapshot remains dated historical context, not
the immediate baseline. No rollback, additional submission or local work.

Two delayed reminder deliveries for confirm1 and the A3 panel were checked
against their saved completed reports. confirm1 remains300clean; the old final
remains stopped359/1200 on the control timeout. A3 remains96clean/PASS. Neither
series was restarted. Pending scheduled messages were again empty.

## Preliminary ranking runtime caveat, not a final result

PROJECT_REPORTED by coordinator during GET-only ranking audit: the first six
audited games are clean, with173own outputs,13nonbaseline choices (all tier1)
and one complete depth2 comparison. These are an incomplete prefix, not final
ranking counts or a selected strength sample.

A real normal-turn internal wall observation exceeds the20ms investigation
threshold: saved official [game918861381](../../2026-11-09-d16-live/games/918861381.json),
own seat1,turn18. Its data use root-level `frames`, not a `log` wrapper.
Through-flush22.097ms, processCPU22.026ms, parse.050373ms, mandatory baseline
1.695861ms, optional stopped1, emergency0, shallow_complete2/selected1,deep0.
Official own errors/warnings remain0; this is **not an official timeout**.

Measured maximum atomic interval7.538665ms exceeds the totals for decoder
(3.438489ms), features(3.423127ms), simulation(1.365327ms) and value(3.524951ms).
Total inference11.889917ms is consistent with the largest interval being inside
the inference meter. The underlying interval cause remains **UNKNOWN**; no
hardware/scheduler cause is asserted. Cooperative checks run around operations,
not inside each neural evaluation, so16ms is not a hard response-time bound or
an official charged-CPU guarantee. Preserve this later observation alongside,
not instead of, the earlier fixed-test maximum16.4098ms.

No source change, rollback, extra experiment, CPU lease or additional platform
request by this lane. Coordinator continues only the authorized ranking audit.
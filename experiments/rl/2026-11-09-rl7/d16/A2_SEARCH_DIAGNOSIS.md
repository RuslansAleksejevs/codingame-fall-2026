# A2 search starvation: read-only diagnosis and one proposed remedy

As of 2026-11-09T01:09Z. PROJECT_REPORTED from saved official telemetry and
exact source inspection. Proposed effects below are MODEL_INFERENCE, not tested
results. No candidate source, configuration, package, executable or frozen gate
was changed for this diagnosis. No inference, game, map generation or API call.

## Corrected official scope (additive correction)

The earlier `official-runtime-child-audit.json` remains historical evidence but
its A2 aggregate used test08. The coordinator identified a map transcription
error in that request and preserved it. Exclude08, do not overwrite or relabel
it. The valid fixed A2 tests are **06/07/09**, with unchanged source
`d36aba4daa02580b1a20e5e1d000954cea330a852d8adbae1bb8f593572c9d15`.

| Test | Official game | Own outputs | Complete evaluations | Nonbaseline outputs |
|---|---:|---:|---:|---:|
|06, boss|918849391|29|5|0|
|07, Captainseb|918849860|14|3|0|
|09, corrected selfplay, both seats|918851925|61|6|0|
|Total| |104|14|0|

All104 outputs have completed baseline and emergency0. Parent source/map/seat
audit reports zero official own errors/warnings. These old-map technical tests
are not an independent strength estimate. The original A2 actual-nonbaseline
criterion is **not met**, and no ranking submission has occurred in this lane.

Independent parsing command is preserved verbatim in the new compute ledger,
lease `43cd0b385fba4d67bb7e9991bfea880e`, .047634s. Input SHA256 bindings:

- test06: `07843e820d63a54b7b5151cdf3affab257e0566568d2f16461c7757f828841c0`
- test07: `9160ecca22b283e55168acf5380e3e26a23975b4c43c0bdfad04e8d9329a08e6`
- test09: `6fc9afa390b5da50cf2529966565d26ce36557a66a28aa8dbc130077a577140f`
- parent `tests-audit-a2-corrected-final.json`:
  `ef272fef571ca8a8ac457cd6031ffa7e0fa1a91b47988dc99ef5278507a54720`

## Cause, not a selection bug

Exact readable A1 body, also present byte-for-byte in A2 after its79-byte
compiler prelude: `package-attempt1/search-readable.hpp`, lines123–178.

Current order:

1. Complete the mandatory greedy plan.
2. Decode **all three** root opponent plans before any simulation.
3. Evaluate the greedy plan through two simultaneous turns against all three
   response models, recomputing both future policies in every branch.
4. Only now sample the .15-temperature alternative. If distinct, fully evaluate
   it against all three models. Then try .35 and .7, in this fixed order.
5. Select only a fully evaluated alternative beating baseline by more than .02
   under the unchanged .5mean+.5minimum score. Duplicate plans are skipped.

For nonterminal branches, first full baseline/alternative comparison therefore
requires **17 complete policy decodes plus12 critic forwards**: greedy1,
root responses3, baseline future6, sampled alternative1, alternative future6.
The critic also constructs state features/decoders. Later alternatives each
need another sampled decode plus6 future decodes and6 critic forwards.

Observed104-turn breakdown:

- 99 turns generated no distinct alternative at all; only5 generated two plans.
- 37 turns performed zero transitions: root-response preparation or its immediate
  boundary consumed the budget. No per-model timing exists to separate that
  boundary precisely; this is not a claim about which particular model stopped.
- Another54 turns stopped before completing even the baseline value.
- Twelve turns completed only one evaluation; one completed two.
- The sole fully evaluated alternative, test06/turn2, tied the baseline exactly:
  both `0.07850472888`. Keeping baseline is correct. There is no evidence of an
  incorrect threshold/comparison, and no basis for lowering the .02 margin.

The proposal order is conservative sampled .15, then .35, then .7, **not a
critic-ranked promise queue**. Only0.023s of the1.664s measured total reached
proposal generation. Reordering temperatures alone cannot repair the91 turns
that never reached a complete baseline value.

| Disjoint search stage | Total across104 turns | Median per turn | Maximum |
|---|---:|---:|---:|
|Mandatory baseline|381.859ms|2.961ms|12.202ms|
|Root responses|838.672ms|8.786ms|15.263ms|
|Future policy decoding|326.735ms|1.610ms|10.476ms|
|Sampled proposals|22.833ms|0ms|3.321ms|

These stages are censored by the16ms deadline; their medians cannot simply be
added to predict full execution. A second, overlapping cost decomposition is
feature calculation738.386ms, neural inference628.851ms, decoder construction
144.669ms, simulation36.455ms. Do not add these to the stage table. Input parsing
totals only7.490ms (median.056ms, maximum.793ms), so the present functional failure
is not the historical delayed-input failure. Maximum atomic measured operation
is2.965ms. Full internal through-flush maximum is17.5611ms.

Median measured inference cost is7.767us/forward; total internal cost divided by
forward count is20.086us, p90 28.957us. The latter includes many non-neural costs
and is only a rough capacity proxy, not a CPU model. The nominal16ms service
supports roughly800 such units at the median,550 at p90, with state variation.

The saved20-game unlimited A2 fixture logs contain1156 roots,219 nonbaseline
choices, median3130.5 forwards (p90 5386). Existing successful nonbaseline cap
fixtures first expose changes at1712–4607 forwards. These are **sampled sufficient
caps, not the exact minimum**; no new cap search was performed. This makes a
blind16→32ms budget increase unconvincing: many useful full-depth comparisons
would still be too expensive. Forward cap20000 is not the observed bottleneck.
Saved-fixture arithmetic lease `0541ebcab1b3452aa9396866575e7508`, .090010s.

## One best bounded proposal: ensemble-preserving iterative deepening at16ms

Recommend one separately amended candidate, **not implemented or authorized by
this document**: use a complete one-turn ensemble comparison as an anytime
incumbent, then deepen to the original two-turn comparison when time remains.
Keep the same16ms cumulative first-score-token wall deadline and20000 cumulative
forward cap. Do not move the clock or increase the allowance.

- Mandatory greedy baseline remains exact and unconditional.
- Keep all four networks, exact9-bit payload, all three response models, fixed
  .15/.35/.7 samples and RNG, robust .5mean+.5minimum aggregation, .02 margin and
  .995 discount. Root responses are committed from the original root as before.
- First pass evaluates baseline and each distinct proposal after **one** complete
  simultaneous step against **all three** responses. Accept no incomplete model
  subset and mix no one-turn and two-turn values.
- The best fully compared one-turn plan is a safe legal incumbent on interruption.
  Once the finite shallow pass completes, reuse its identical proposals and
  perform the original full two-turn evaluation in the original plan order.
- Retain the shallow incumbent until a complete baseline/alternative two-turn
  comparison exists. Thereafter the highest completed two-turn comparison takes
  precedence, including a return to baseline if all those alternatives fail the
  margin. Unlimited output and final two-turn scores must equal A2 exactly.
- Keep separate tier, evaluated-plan and selected-plan telemetry. A shallow
  result must never be reported as a completed original-depth evaluation.

This is an **explicit timed-policy/horizon-fallback change**, not a semantics-
preserving A2 optimization. The historical teacher and incomplete359-game
evidence do not establish its strength. All response models remain present in
every accepted comparison; no model is silently dropped. The old gates remain
unchanged, and no claim of strength improvement is made.

Why this specific scheduling change: the first shallow baseline/alternative
comparison needs only5 policy decodes (greedy1+root responses3+proposal1), versus
17 currently. It removes12 future-policy decodes from that critical path while
preserving complete three-model comparisons. Extra shallow critic evaluations
cost time, and the37 root-preparation-starved turns can still remain greedy.
Consequently material transfer is plausible, **not guaranteed**. A1/A2 full-depth
local advantages cannot be copied onto this proposed timed policy. Earlier v4
depth1 diagnostics were small, correlated and did not prove fresh strength.

### Falsifiable fixed technical test, if amendment is approved

One source/config, no sweep, no fresh final maps, no new learning. One compile/
contract lease capped5minutes, then parent-owned official tests on the exact
same three intended boss/Captainseb/selfplay requests (06/07/09 options; reuse
serialized options, do not transcribe them). Do not select among candidates by
winrate or silently extend the budget if this fails.

Local contracts reuse the same20 disclosed streams/both seats, original40016
delayed-input fixture and preserved v4 failures:

- Exact decoded weight bytes; unlimited final two-turn plans/scores equal A2;
  hidden-state restoration, immutable roots, legal command/export contracts.
- Forced exhausted time/cap and actual20/30ms input delay return the same complete
  greedy baseline, never an emergency or partially decoded proposal.
- Independently recompute the one-turn three-model score in the existing native
  machinery. Test tier boundaries with deterministic caps; no selection from a
  partial ensemble, no cross-depth comparison. Report failures without retries.
- Record whole-stream outputs, per-tier counters, and wall plus process-CPU
  diagnostics. Compilation/size acceptance is not functional success.

Suggested prospective platform acceptance: all own outputs baseline-complete,
zero official errors/timeouts/emergencies, at least10 turns with a complete
baseline/alternative three-model comparison, and at least one actual nonbaseline
decision in a non-self game. Every selected output must name its completed tier.
These thresholds must be fixed by the coordinator **before** execution; they
are proposed here, not a retroactive relaxation of A2.

Requested smallest fresh gross-regression guard, also only proposed: freeze the
one source before generating allocated unused72005–72006, audit canonical-content
novelty, then2maps x3opponents(Lacoz/newkh/oldkh) x2seats x2roles(A3/unchanged
league3m)=24 original-referee games. Any technical failure stops. Suggested coarse
sanity bound: A3 total points >=control points minus2 across12games each, with
draw=.5. Report paired whole-map results and uncertainty; two map clusters cannot
establish strength. No replacement maps, source variants or reopening of the
stopped1200-game final. No fresh map/game has been generated for this proposal.

Safety envelope: retain16ms, so optional search is not given extra time. Require
normal non-first through-flush observations <=20ms on these fixed tests and
report process CPU separately; investigate any breach, do not relabel it.
This leaves a nominal30ms wall reserve to50ms for unmeasured work, but **does
not prove30ms of platform-charged CPU headroom**. The actual platform accounting,
pre-first-token work and scheduling remain partly unknown. Existing A2 measured
baseline<=12.202ms and atomic operation<=2.965ms support this conservative test,
not an arbitrary-delay hard-real-time guarantee. Source must still fit98000UTF16
and actual platform acceptance. A2 has3532UTF16 of conservative size headroom.

## Resource and authority boundary

This diagnosis used .137644s in two read-only leases; D16 total now792.662224s
(13.211min),15 finished leases. No inference/training/generation/arena/API call,
no source/package change, no new timer. Pending owned timers:0. No local worker
was launched except the completed metadata processes. All437 raw games and437
portable game records remain; final359/1200 STOP remains in force. Await the
coordinator's bounded amendment or other direction before implementation.
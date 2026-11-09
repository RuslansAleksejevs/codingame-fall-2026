# Compact D16 — REJECTED incomplete final

8 November 2026. Classification: PROJECT_REPORTED local measurements.

The single-file packaging experiment succeeded, but the deployment candidate
is rejected. The frozen final stopped at656/4200games after one emergency WAIT
before baseline generation. There was **no referee timeout or illegal action**
in that game. Final strength is inconclusive; no improved/deployable bot is
claimed. No new games, retries, training, platform calls or submission followed
the stop. The preserved B2M source was not changed.

| Gate | Actual outcome |
| --- | --- |
| Single-file size, compilation, exact weight codec | PASS:9bits,94123UTF16 |
| Old-game FP32/quantized-reference/standalone contracts | PASS |
| Six disclosed original-referee regressions | PASS |
| Fixed504-game development admission | PASS; independently audited |
| Zero emergency fallbacks in the final | REJECTED:one observed emergency |
| Complete4200-game final and95%clean-map coverage | NOT COMPLETED |
| Independent diverse strength/retention | INCONCLUSIVE |
| Platform/ranking/student work | NOT RUN |

## What actually ran

All heavy work used the original exclusive compute wrapper, owner
`search-teacher`, unchanged state directory and cumulative4-hour cap. Each
lease was at most25minutes; this separately authorized phase was capped at
9000seconds. The same GPT-6 Astra/max/codex_second runtime was retained.

- Two preserved static assembly attempts, including a signed-decoder
  portability correction before any new game.
- 100saved complete games, both sides:5544roots,22176actual stream commands,
 114500bitexact logit pairs,200deterministic-cap root contracts and89nonbaseline
 partial-stop cases.
- Six original-referee regression games on62041/62044/62046,both seats.
- 504fresh development games:71001–71012, candidate/control/teacher against
  seven opponents, both seats, serial alternating order.
- 656final games:full420-game block1 plus236games in block2. Blocks3–10 never ran.

Total new local games:1166. Development and final evidence are not pooled, nor
combined with v4/v5 results. Old trajectories are technical fixtures, not fresh
strength evidence. No labels or policy updates were produced.

## Static representation and exact contracts

The original actor, critic and all three response roles remain present.
Actor/response0 share one stored weight set:four unique networks, no response
removal. Symmetric per-output-row9-bit matrices use float32 scales and biases;
float32 weights are reconstructed once at startup. Activations, inference,
features, simulator and search rule are unchanged. There are no external
weight files or runtime downloads in the standalone source.

The same deterministic assembly generated12/11/10/9/8-bit packages before
strength outcomes. Attempt2 sizes are113937/107330/100733/94123/87528UTF16.
The highest fitting precision is9bits. The exact candidate is
`package-attempt2/b9/bot.cpp`, SHA256
`22ccbbe3fedd8cdb7bae8c232b62269ee5b7cde838b23afb4405692b92e5a5c9`.
All397328restored weight bytes match the quantized reference. The independent
coordinator separately implemented quantization and decoding and agreed.

Attempt1 remains intact. Its unsigned-to-signed subtraction was replaced with
strictly defined signed subtraction in attempt2. No strength result was used
to select precision or choose this correction. Exact commands, compiler/Python/
NumPy versions, dimensions, source spans and identities are in
[package-attempt2.json](package-attempt2.json) and compiler command/log records.

Original FP32 D16 equals the new FP32 storage shim; quantized-text D16 equals
the actual compact program. Tests cover both absolute seats, complete input
streams, hidden-state restoration, immutable roots, legal selected commands,
finite logits and deterministic forward-cap fallback. Quantization itself
changed2897/5544unlimited plans(52.2547%); maximum observed logit difference
was2.17236328125. Export equality does not establish strength preservation.
See [contracts.json](contracts.json).

The search retains depth2, four proposals, three responses, temperatures
.15/.35/.7, mean/minimum weights.5/.5, margin.02, gamma.995, a16ms clock from
the first score token and a20000-forward cap. Only completed evaluated plans
can replace the baseline. One output line is emitted per observation.

## Development admission, not final proof

The fixed504games completed with zero own/control/teacher errors or emergencies.
One Lacoz error occurred in candidate/71006/seat0. All-games data retain it;
clean analysis excludes the entire six-row opponent/map cluster.

| Development metric | All games | Clean paired |
| --- | --- | --- |
| External candidate-control gain | +6.9444pp[-1.3889,15.2778] | +4.5455pp[-3.0303,12.1212] |
| External candidate-teacher difference | -1.3889pp[-6.9444,4.1667] | -1.5152pp[-7.5758,4.5455] |
| Direct league3m score | 21/24,87.5%[75,100] | same |
| Direct B2M score | 13/24,54.1667%[33.3333,75] | same |

Intervals are whole-map95%bootstrap intervals. Clean external coverage was
11/12maps. These passed the prospective development admission, which is weaker
than the final gate. The coordinator independently reparsed all504raw records,
recomputed intervals and approved the sole frozen final before opening it.

## Exact stop mechanism and limits of diagnosis

The failed record is `candidate-vs-league3m-seed40016-seat1`, turn27:

| Recorded field | Value |
| --- | --- |
| Input-read wall interval | 17774.5us |
| Restore / output flush | 4.042us /8.375us |
| Through stdout flush | 17812.6us |
| Search checks / forwards | 1 /0 |
| Generated / complete plans | 0 /0 |
| Emergency flag / actual output | 1 /`WAIT` |
| Referee errors / raw result | 0 /win78:-1 |

The first budget check stopped before any decoder or network call. The16ms
clock had expired during the input-read interval, so a completed baseline was
never available. This is a reliability-contract failure, not a referee timeout
and not a demonstrated inference slowdown. The source D16 fallback does not
guarantee a completed baseline when input handling already consumes its clock.

The underlying reason for the17.77ms input-read wall interval is UNKNOWN.
It may include token receipt, blocking I/O, parsing and scheduling; this is not
isolated parser CPU time. No blame is assigned to the scheduler, arena or codec.
No timing rerun or repair was used to erase the observation.

All44original outputs/timing records are preserved. The27th raw output is
actually WAIT, and its joint transition was replayed exactly. The forensic
fixture also contains a reconstructed complete observation including the
static map header; that is not a measurement of actual turn27input byte count.
See [failure-forensics.json](failure-forensics.json) and
[confirm2/failure.json](confirm2/failure.json).

Candidate final timing covers5778/5778outputs. Through-flush p50/p95/p99/max
are16.0134/16.0882/16.1442/26.6488ms; input-read max17.7745ms. There were2908
budget stops and one emergency. These internal wall measurements exclude
startup, pre-first-token scheduling and the final diagnostic write. They are
not official platform CPU measurements. Full component percentiles and all
roles are in [final-timing.json](final-timing.json).

## Incomplete final: descriptive results only

The source and full4200schedule were frozen with SHA256
`fb5a052360a1d1932445ced22b2c85c0290e961983b5358069f37fc77c183e47`.
The [parent approval](parent-final-approval.json) binds source, protocol,
development decision and independent audit. No interim strength selection
occurred. The driver stopped on the first technical failure without starting
another game. There are3544unplayed scheduled games.

Twenty final maps were generated and novelty-audited; sixteen were played,
fifteen have all42rows. Maps40017–40020 were generated but not played;
40021–40100 and65001–65040 were never opened by this experiment.

| Partial final metric | All complete pairs | Clean complete pairs |
| --- | --- | --- |
| External candidate-control gain | +1.1111pp[-4.4444,6.6667],15maps | +2.3810pp[-3.5714,8.3333],14maps |
| External candidate-teacher difference | 0pp[-4.4444,4.4444] | +1.1905pp[-2.3810,4.7619] |
| Direct league3m score | 24/30,80%[60,96.6667] | same |
| Direct B2M score | 16/30,53.3333%[33.3333,73.3333] | same |

These are truncated-series diagnostics, not a passed100-map final. The frozen
analysis uses10000whole-map resamples, seed20261109, both seats together.
Clean inference removes full candidate/control/teacher×seat opponent/map
clusters; the external composite uses the intersection across three opponents.

| Opponent | Complete maps all/clean | Candidate-control gain, all95%CI | Clean95%CI |
| --- | --- | --- | --- |
| Lacoz7f190183 | 15/14 | -3.3333pp[-20,13.3333] | 0pp[-17.8571,17.8571] |
| newkhoufou070bc128 | 16/16 | +6.25pp[0,15.625] | same |
| oldkhoufou372c1cd6 | 16/16 | 0pp[0,0] | same |
| v6 guard | 16/16 | 0pp[0,0] | same |
| BC guard | 16/16 | +6.25pp[0,18.75] | same |
| league3m | 15/15 | +30pp[10,46.6667] | same |
| B2M | 15/15 | +3.3333pp[-16.6667,23.3333] | same |

The emergency game's six-row cluster is incomplete, so it cannot enter paired
estimates. It is nevertheless retained and counted as a loss in all observed
game accounting, and it independently rejects the gate:

| Role | Observed games | Technical-adjusted W/D/L | Raw wins | Own engine errors /emergencies |
| --- | --- | --- | --- | --- |
| Candidate | 219 | 192/0/27 | 193 | 0 /1 |
| Control | 218 | 179/0/39 | 179 | 0 /0 |
| Original teacher | 219 | 198/0/21 | 198 | 0 /0 |

These unbalanced observed totals are not an alternative strength metric.
One final opponent error occurred in control/Lacoz/40013/seat0. Its whole
comparison cluster is excluded from clean inference. Full per-opponent and
per-seat counts/CIs, exclusions and missing rows are in
[final-decision.json](final-decision.json) and
[observed-final-counts.json](observed-final-counts.json).
Wins awarded after opponent errors are not evidence of strategic superiority.

## Replay and independent audit

Original Java/native verification passed655of656final trajectories:18631states,
17976transitions, no state/score mismatch. The sole excluded trajectory is the
opponent-error game. The separate emergency-WAIT game is engine-valid and is
included in exact replay. Across regression/development/final,1164of1166new
games were replay-eligible:32808states/31644transitions; the other two retain
their original opponent-error logs.

The frozen child analyzer's `replay_pass=false` reflects absent unplayed final
blocks, not a Java mismatch in completed games. The independent closing audit
separately confirms actual replay coverage and rejects the incomplete final.
Both implementations agree on raw/portable identities, all observed counts,
partial paired intervals, one emergency and the rejected deployment decision.

The first parent post-stop audit had an incorrect assumption that there were
no opponent errors. Its failed report is preserved. Only the additional
post-stop auditor was corrected; none of the six frozen parent modules,
candidate, original logs or gates changed. The corrected independent report is
[coordinator/final-stop-audit-attempt2.json](coordinator/final-stop-audit-attempt2.json),
with [correction note](coordinator/closing-audit-correction.md).

## Preservation, resource use and remaining uncertainty

All frozen v5 artifacts remain untouched. The four protected SHA256 identities
are rechecked at every stage and again during closure:

- league3m checkpoint: `9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663`
- league3m weights: `dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb`
- league3m submitted source: `199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1`
- preserved B2M source: `b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214`

Before final archive/closure, this phase consumed2031.888728actual heavy seconds
(33.8648minutes), far below its9000second limit. The final ledger and
[COMPLETION.json](COMPLETION.json) include archive/closure overhead. Compiler
commands and finite-stage receipts are preserved; external paid spend is0.
The existing compute owner/state/cap were never reset or renamed.

The portable archive includes all owned source/evidence and independent audit
records, including failed attempts. Compiled binaries/environments and mutable
closure records are excluded. Personal host paths in portable log copies are
normalized; exact local originals remain intact, with both hashes recorded in
[inventory.json](inventory.json). Archive contents are read back and checked
against every inventory digest; [archive.json](archive.json) binds the result.

No Git mutation, IDE write, OAuth, read/play API, ranking submission, rollback,
paid resource, new chat, subagent, policy training or sample extension occurred
in this implementation phase. The coordinator owns organizational updates and
any future authorization. All older gates remain closed and unmodified.

Reusable outcome: a source-size-compliant, exact9-bit D16 storage/export route
with extensive contracts and a precise failure fixture. Unproven: final diverse
advantage, superiority to deployed B2M, zero-emergency reliability and official
platform transfer. A revised clock/baseline policy would be a new candidate
requiring new authorization and fresh evidence; it was not implemented here.
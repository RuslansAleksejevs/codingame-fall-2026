# A2: compiler-only delivery repair, before its results

Recorded9November2026, approximately00:40UTC. This changes the remaining delivery
work, not the frozen local-final interpretation. It is within the requested D16
repair/deployment task and the existing compute/time limits; no new paid resources,
architecture, search sweep or ranking submission is authorized by this amendment.

## Observations that motivated the change

Attempt1 source `aba2d6f2…` passed local technical contracts and78technical games.
Its independent local final stopped at359/1200 because the **control** timed out
on72112seat0. D16 itself had119clean games,3540complete-baseline outputs,0emergency,
491nonbaseline selections. The incomplete local result remains incomplete; the
old full gate is not declared passed. The cause of the control timeout is UNKNOWN.

Official attempt1 tests01/02 completed without recorded errors, warnings or
timeouts, but D16 had **0 completed search evaluations and0 nonbaseline selections
in all43outputs**. Test01 lost toGoldBoss; test02 beatCaptainseb. In test02 ordinary
turns12–14, internal through-flush wall times were58.788/68.497/71.600ms, mostly
baseline computation. These are not official charged CPU times; no timeout is
invented from them. The implementation therefore has a measured platform transfer
problem even though it outputs a valid baseline.

Read-only source comparison found the exact optimized FastNetwork kernel in both
packages, but the D16 standalone lacked the guarded GCC O3 prelude present in the
actually deployed league3m source. Local commands already used `clang++ -O3`, hiding
that packaging difference. Actual platform compiler flags are UNKNOWN. The flag
omission is a concrete difference and a testable explanation, not yet a measured
causal repair. Raw test logs and audits001–003 are preserved.

## Single allowed correction and evaluation

- Create attempt2 by adding ONLY the exact guarded `#pragma GCC optimize("O3")`
  prelude used by league3m, before definitions. No fast-math, target pragma, changed
  sum order, weights, decoder,16ms budget, responses or instrumentation.
- Preserve attempt1/source/freeze/raw/failed local final. Save a new source/hash/
  size/manifest and exact decoded-weight, unlimited-command, forced-budget and
  completed-prefix parity checks on exposed fixtures. Document that both local
  variants use the same existing optimized compilation configuration.
- Complete the original fixedfive official tests as attempt1/control evidence.
  Test03 uses `replay_game_id=918843981` to preserve exactly test02's map/seat/
  Captainseb; its separate wire request is recorded before execution.
- Then permit exactly **three additional candidate-only technical tests** for
  attempt2: the same GoldBoss/map, Captainseb/map/seat and same-source selfplay/map.
  Existing unchanged-league3m controls are retained, not claimed simultaneous.
  Total platform technical-game cap for this delivery phase becomes8, not an
  open-ended candidate/opponent sweep. Resolve and save requests before execution.
- Audit source identities, every output/baseline/emergency and official errors,
  completed search evaluations and actual nonbaseline selections. The intended
  runtime repair must be demonstrated, not inferred merely from successful build
  or absence of timeouts. No16ms increase to force the desired measurement.

No new large local final is started by this amendment. Old local evidence plus
exact numerical contracts provide context, not a completed independent strength
proof for the new package. If the bounded runtime correction works and technical
readiness is sound, the already authorized **single exploratory ranking submission**
can proceed with this uncertainty disclosed. If not, report the blocker; no
automatic further architecture/source/timer changes or rollback.
# Bounded simultaneous-search pilot

Started 2026-11-08T00:00:00Z; hard stop **2026-11-08T04:00:00Z** (four hours).
Implementation and pilot only. No policy distillation before broad independent
opponent gains. Frozen PPO-v3 training files and weights remain untouched.

Use the frozen league3m actor and its existing terminal-outcome critic. Generate
up to four resource-consistent complete plans: greedy, then samples at fixed
temperatures .15/.35/.7. Root enemy plans come from league3m, long3m and extended
league, all from the original state before any own plan is applied. Apply both
players' plans jointly in a deep-cloned exact state. Recompute both plans after
every future state change; never replay stale responses. Horizon one or two.

Leaf estimate is the clipped antisymmetric critic `(V(own)-V(enemy))/2`, with
terminal outcomes exact and gamma .995. Aggregate three models as half mean,
half worst case. Keep greedy unless a fully evaluated alternative exceeds it
by .02. The production-compatible experiment has a 30ms internal budget;
incomplete candidates are discarded. Also inspect an untimed version to
separate search quality from runtime limits. Neither is assumed stronger.

First verify root immutability, deep-copy isolation, valid actions, native/Java
transitions, identical greedy behavior, state-value antisymmetry, and local
protocol consistency. Diagnostics under training load are **not** uncontended
timing evidence. Inspect candidate choices and critic ranking/calibration.

Protocol audit 2026-11-08: the initial standalone parser used relative player
labels, unlike native search. The pre-fix 618-plan test failed in 8 streams.
The official pinned Board generator places player 0 at the three leftmost nodes
and player 1 at their exact mirrors. Standalone now validates that start and
restores absolute player order, including units, scores and triangle flags,
before searching. Unknown/custom starts fail explicitly. This preserves exact
simultaneous ordering and the native deterministic RNG; the search algorithm,
critic, PPO training and native scout are not changed. A new both-seat protocol
test is required before original-arena evaluation. Keep pre-fix evidence.

Only with heavy training stopped, compare the frozen search variants and greedy
against league3m, Lacoz and both khoufou versions on development maps, both seats.
Keep all errors and timeouts separate from strategic outcomes. Use the already
exposed development maps; never inspect the final 40001--40100 holdout here.

Continue toward runtime search/distillation only if the search beats greedy on
the equal-weight multi-opponent score by at least five points, has no >5-point
matchup regression, and at least 55% direct score against greedy. Treat small
pilot intervals honestly; a plausible pilot needs a separate expanded check.
Runtime inclusion also requires the original 50ms constraints and source-size
verification. Otherwise terminate the search branch within the four-hour cap.
No large new evaluator or afterstate pipeline will be built to rescue it.

The full prototype loads five networks (actor, critic, three response models),
so current exact-weight source packing is expected to exceed the live code-size
limit. It is an offline quality experiment first; timing alone cannot establish
deployability. A distillation branch is permitted only after the strength gate.

## External confirmation routing (frozen before external games)

The untimed 216-game native screen passed its preliminary gate, but all tested
opponents were also response models. It is not independent strength evidence.
Run `code/rl/search/run_external.py` only after the main A/B campaign exits; the
script checks its terminal first-block status. It does not interrupt training.

First screen the 30ms-bounded one- and two-turn variants against greedy on
30001--30012, Lacoz/new khoufou/old khoufou and direct league3m (288 games).
If neither passes the preliminary external gate, stop. Otherwise freeze one by
equal mean of the three external score rates (prefer one-turn within one point),
then confirm it on 30013--30040 (448 additional games including control).
These 28 maps were not used for search selection or code tuning, although the
frozen baseline had already played them; the final 100-map holdout stays closed.

Only the latter 28-map confirmation permits teacher data: external mean gain at
least five points, map-paired composite 95% lower bound above zero, direct score
at least 55% with map-clustered lower bound above 50%, no >5-point external
regression, no own technical failure, at least 20 complete six-game map pairs.
All technical outcomes remain in records; no selective reruns. If these gates
fail, keep the search branch as an unconfirmed experiment, not a trained teacher.
The panel stops starting games at 03:58Z, with 90-second match timeout and the
04:00Z pilot cutoff. Do not start the expansion with fewer than 20 minutes left.
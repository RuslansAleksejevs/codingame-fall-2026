# Development roadmap

As of 2026-11-06. Proposed work, not completed experiments. The current selection and measurements are in the [fresh ATTACK report](../experiments/2026-11-06-attack-holdout/REPORT.md). Local results do not establish contest ranking.

## What has already been copied

The complete public game files from Lacoz and khoufou are already present, unchanged, under [code/opponents/public](../code/opponents/public/README.md), with pinned revisions and hashes. They run as opponents. Neither whole algorithm has been adopted as the main bot.

The main C++ family uses a much simpler planner. v3 adds multiple spawns; v4 tries a restricted triangle reset; v5 adds a local protection pass; v6 adds one attack. These are small implementations of individual ideas, not faithful reproductions of either complete competitor. The v4/v5 regressions show that these implementations did not help this base; they do not establish that resetting triangles or protecting units is a bad idea.

There is no architectural need to rewrite a working Java or Python bot in C++ before using it as a candidate. An unchanged copy is useful as a baseline, but is not an original algorithm or a demonstrated improvement. Preserve its source credit and the changes made on top of it. Before any platform submission of third-party code, establish applicable contest rules and permission to reuse it; neither repository currently exposes an explicit license. This issue does not change the status of the existing local measurements.

## Why the complete planners matter

| Component | Current C++ family | Frozen public implementations |
|---|---|---|
| Assigning the army | Greedy triangle choices; limited coordination between targets | khoufou tracks assigned destinations and shared corner demand. Lacoz assigns units to targets and evaluates the combined final position. |
| Reusing a spent triangle | The experimental v4 clears one triangle early, blocking arrivals | khoufou clears only after higher-priority assignments and checks safe exits. Lacoz can move a whole group off shared corners together. |
| Economy | Simple army-size cap and income reserve | khoufou considers remaining demand and enemy army size. Lacoz combines spawning with its movement evaluation and risk penalties. |
| Combat | v6 performs at most one attack, then runs v3 | khoufou coordinates surrounding kills and can issue multiple attacks. Lacoz scores surrounding risk, stack exposure and enemy behavior. |
| Choosing a turn | One constructed greedy plan | Lacoz improves single-unit and grouped moves within a time budget. The new khoufou revision compares several plans by simulating two turns. |

These are source-code differences, not isolated causal measurements. In particular, copying an attack threshold without copying resource allocation, resets and planning does not reproduce the same strategy. The time-limited search in Lacoz can vary between identical reruns.

A concrete coordination gap: empty target triangles ABC and ACD share corners A and C. Four suitably placed units can occupy all required corners. The current planner reserves separate troops for each target and can allocate six; khoufou's `destined` counts let the second target reuse the assignments to A and C. Fixing this is a specific hypothesis to measure, not an already demonstrated gain.

## Recommended next sequence

1. **Find a stronger complete baseline.** Freeze the new khoufou revision `070bc12803f10099755d35eb773c6724bd305434` separately from the existing opponent. Compare it with frozen Lacoz, old khoufou, the selected C++ bot and an exact upstream boss snapshot. Start with a small legality/timing smoke run, then a balanced tournament. Keep each implementation in its original language initially. The present runner accepts C++ candidates, so add a generic frozen command/source specification first, preserving the existing v3/v6 protocol.
2. **Select on measured strength and reliability.** Use identical maps, both seats and sequential matches. Report the complete opponent-by-opponent matrix, clean wins/draws/losses, technical outcomes and latency. These two public bots have not yet been compared head-to-head here; the current evidence does not rank them against each other. Keep the old opponents pinned for historical comparisons.
3. **Make one focused improvement to the selected base.** First inspect losing games. For a heuristic base, prioritize coordinated corner demand, safe group resets and immediate surrounding opportunities. For the new search base, test more than one plausible enemy response and the value of search itself. Compare lookahead disabled/enabled before claiming that deeper search caused the gain; a newer revision may contain other changes.
4. **Confirm on untouched maps.** Use development maps to debug/tune, then freeze code and a promotion rule before opening a new holdout. Compare against the current main bot across a diverse opponent pool. Report confidence intervals clustered by map, both seats, own failures and opponent failures. Do not repeatedly tune on the holdout or extend a run because its result is close.
5. **Prepare a contest candidate.** Verify the actual contest IDE, available libraries, full response-time limit, code-reuse conditions and the exact file to send. Local measurements alone do not prove platform compatibility. Preserve the previous candidate for rollback. Submission is a separate action.

The upstream author reports a large gain for the new khoufou revision, but that gain has not been reproduced here. Its source explicitly omits ADD_PATH and REMOVE_PATH from simulated future actions, and by default assumes the enemy uses its own base heuristic. Lacoz changes roads, so both limitations matter when assessing this candidate. See the [source review](../sources/2026-11-06-algorithm-review.md).

## Development options

| Route | First useful deliverable | Relative work | Main limitation |
|---|---|---|---|
| Adopt a complete public base | A frozen Java/Python candidate and tournament report | Lowest implementation effort; benchmarking still required | Reuse terms must be settled before submission; an exact copy is not an improvement over its source. |
| Keep the compact C++ bot | Shared target demand, then coordinated reset/combat, each measured separately | Medium; clearest route for understanding the planner | Individual ports may miss interactions and can remain far behind the full bots. |
| Search over whole turn plans | Candidate plans scored after one or two simulated turns | Medium to high; lower if an existing simulator is reused | Simulation bugs, inaccurate enemy models and response-time overruns. |
| Explore road tactics | Measured ADD_PATH/REMOVE_PATH choices in the full plan | Medium to high, after a reliable base | Changes graph distances and scoring opportunities; gains may be opponent-specific. |
| Imitation or reinforcement learning | A dataset and an offline policy evaluation | Highest; suitable as a later research branch | Needs a stable simulator, broad data and a compute plan; no paid compute is assumed or authorized. |

The shortest route to a stronger bot is to benchmark the complete public bases first, then improve the strongest reliable one. If maintaining a small, understandable C++ implementation is the primary constraint, the next module should coordinate destinations and resource use before adding more isolated tactical rules.

## Checks before trusting search

- Differential-test simulated turns against the original referee on saved and randomized legal states, including simultaneous attacks, shared units, spawn timing, surrounding, capture flags and scoring. Verify road changes before modeling them.
- Keep a legal baseline plan ready; stop search with margin before the full response deadline. Measure whole-response reliability as well as internal planning time, including Python imports or Java warm-up.
- Test beyond mirrors and one opponent model. A model of old khoufou may work against itself and fail against Lacoz's road changes or coordinated local search.
- Preserve every run, frozen source, map seed, seat, referee version and failure. Author-reported numbers and independently measured results must remain separate.

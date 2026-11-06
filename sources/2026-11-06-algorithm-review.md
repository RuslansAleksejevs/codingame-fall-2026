# Public algorithm review

As of 2026-11-06. SOURCE_VERIFIED for repository contents and quoted metadata; MODEL_INFERENCE for priorities and anticipated limitations. No new opponent tournament was run as part of this review.

## Versions and reuse status

| Source | Frozen local opponent | Latest revision checked | Local status |
|---|---|---|---|
| [Lacoz/cg2026](https://github.com/Lacoz/cg2026) | `7f1901834d2ffc16532e083edfec8cbdb5941ab6` | Same revision | Complete unchanged `bot.py`, used for benchmarks |
| [khoufou/Codingame_2026-11_FallChallenge](https://github.com/khoufou/Codingame_2026-11_FallChallenge) | `372c1cd6738d456513cb50705b98549eedfdfad8` | `070bc12803f10099755d35eb773c6724bd305434` | Old complete `Player.java` used for benchmarks; latest source read, not executed here |

GitHub repository metadata returned no license, and no explicit license file was present in either root listing. This observation is not a determination of the applicable reuse rights. The existing private copies retain exact source provenance. Do not describe a copied algorithm as an original contribution.

## Frozen khoufou: coordinated heuristic

Source: [Player.java at 372c1cd6](https://github.com/khoufou/Codingame_2026-11_FallChallenge/blob/372c1cd6738d456513cb50705b98549eedfdfad8/Player.java).

- `play` orders attacks, threatened-triangle spawns, surrounding kills, captures, resets, idle moves and army growth.
- `supplyDemands` uses flow to coordinate troops for a surrounding kill. `evaluate` and `destined` share assigned troops between capture targets.
- `vacateUsedTriangles` runs after capture assignments and respects stays/arrivals and safe exits. This differs materially from the isolated v4 reset.
- `growArmy` uses unfilled demand, enemy force size and immediate tactical opportunities. `oppCanTakeAll` checks whether enemy supply can cover several threatened corners jointly.
- Several ATTACK commands can be planned. The simple v6 uses at most one and retains at least three units afterward.

## Frozen Lacoz: joint position evaluation and local search

Source: [bot.py at 7f190183](https://github.com/Lacoz/cg2026/blob/7f1901834d2ffc16532e083edfec8cbdb5941ab6/bot.py).

- Shared target assignment can use SciPy's assignment solver. Troop destinations and spawn choices become tokens in a combined position.
- `house_eval` and `tri_term` score captures, resets, surrounding, stack risk and enemy threats. `eval_moves` computes the change in total value for a group of moves.
- `single_pass` improves individual choices. `composite_pass` captures triangles or empties groups of spent triangles together; random perturbations then escape local optima within a 30 ms search budget.
- The `learn` function updates simple enemy-behavior probabilities from observed turns. This is not a trained neural policy.
- ATTACK and road additions/removals are supported. The search budget is wall-clock based, so outcomes need not be bit-for-bit repeatable.

## New khoufou: two-turn plan selection

Sources: [commit 070bc128](https://github.com/khoufou/Codingame_2026-11_FallChallenge/commit/070bc12803f10099755d35eb773c6724bd305434), [Player.java](https://github.com/khoufou/Codingame_2026-11_FallChallenge/blob/070bc12803f10099755d35eb773c6724bd305434/Player.java). Repository metadata reported a push on 2026-11-06.

The implementation generates variants of a base heuristic plan, simulates the first turn and another base-policy turn, and scores points, held triangles, units and capture potential. Its default enemy model is the base heuristic; the code also supports a boss-like model and minimum/average aggregation over models. The normal search budget is 30 ms, with first-turn JIT warm-up. ADD_PATH and REMOVE_PATH are explicitly excluded from simulated future actions.

The commit reports approximately 96% wins against its previous bot across two 300-game samples, and approximately 80–85% against its boss3. It also reports no simulation mismatches over 8,300 tested turns and normal-turn computation below 15 ms on an unloaded machine. **These are upstream claims, not local replications, and their engine/environment are not assumed equivalent to this arena.** Read the linked commit for the exact figures and setup.

Inference: this is a promising next candidate because it extends an already coordinated planner. A faithful local test is still needed, particularly against Lacoz and under the original response limits. Its simplified opponent and road assumptions may make simulated plans overoptimistic.

## Contest context

The [official contest page](https://www.codingame.com/contests/fall-challenge-2026) was checked again. The public [AI-rules discussion](https://forum.codingame.com/t/fall-challenge-2026-ai-rules/208706) contains an AI-allowed response but does not establish permission to submit a verbatim third-party solution. A [historical code-sharing discussion](https://forum.codingame.com/t/cg-stance-regarding-code-sharing-alts/2564) records a permissive platform stance in 2017; it is not the specific 2026 contest rulebook or a source-code license. Current submission conditions still require verification before any such submission.

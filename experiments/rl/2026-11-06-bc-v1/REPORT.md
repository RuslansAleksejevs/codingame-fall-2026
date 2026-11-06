# BC v1: native simulator, small teacher-trained policy, fresh-map tournament

**2026-11-06 · PROJECT_REPORTED · MacBook Air M4, 24 GB · `rl/research`**

The trained bot beats v6 and closes most of the gap to the frozen khoufou on this panel. Lacoz remains much stronger. This is **behavior cloning**, the first stage of the learning route; no PPO/self-play, value learning or search was run.

## Results

The checkpoint was frozen before opening seeds **6001–6050**. Every matchup uses all 50 maps and both seats. The original Java referee, league 3 and original 1000/50 ms process limits were used. Games ran sequentially, interleaving BC and v6 controls.

| Opponent | BC wins / games | BC losses | v6 control wins / games |
|---|---:|---:|---:|
| v6 | **75 / 100** | 25 | — |
| khoufou `372c1cd6` | **51 / 100** | 49 | 9 / 100 |
| Lacoz `7f190183` | **3 / 100** | 97 | 0 / 100 |

**500 confirmation games, no draws, no command errors, no timeouts and no referee failures.** All are clean comparisons. The 20 preceding functional smoke games on old maps are separate and are not included in this table.

- Against v6 directly, BC's win rate is 75%, with a whole-map bootstrap 95% interval of **63–86%**.
- Against khoufou, the matched improvement over v6 is **+42 percentage points**, interval **+29 to +55**. Of 100 paired outcomes, 43 improve and one worsens. A 51% record is approximately parity with khoufou, not evidence of clear superiority over it.
- Against Lacoz, the matched difference is **+3 points**, interval **0 to +8**. Three wins do not establish a reliable improvement; 97 losses remain the central result.

Intervals resample all observations of a map together, keeping both seats, with 10,000 replicates and seed 20261106. They describe game/map uncertainty for this one trained checkpoint, not variation across training seeds. Zero-event arms have degenerate empirical bootstrap intervals; zero observed v6 wins does not prove its underlying win probability is zero.

All 50 map contents differ from the **325 previously inspected maps**, including the training and validation layouts. Exact sources and model hashes were frozen in the run manifest. The native simulator also replayed all **16,201 paired decision transitions** from this panel with identical viewer unit states and final original-referee scores. [Comparison](comparison.json) · [Verification](verification.json) · [Manifest](confirmation/manifest.json) · [Full records](confirmation/records.tar.gz).

## What was built

- An in-memory C++ simulator ported from the attributed, pinned original referee. It handles movement, spawning, simultaneous attacks, road additions/removals, shared troop costs, surrounding, triangle capture/reset, scores and termination. Python accesses it through a small C ABI.
- A shared native feature encoder and full-turn decoder that reserves original troops and supports every mechanical command family. Both training and inference use the same feature implementation.
- A **24,833-parameter MLP**, 128 → 128 → 64 → 1, that scores legal candidates. The network selects actions; there is no v6 fallback, copied teacher planner, search or value model.
- PyTorch training, CPU/MPS timing, reproducible dataset reconstruction, native text-weight export, original-arena evaluation and paired analysis tools.

This compact candidate scorer is a smaller first control than the 0.1–0.5M-parameter graph encoder in the initial research proposal. The result measures the complete BC policy/representation/decoder package; no ablation isolates individual features, road support or training alone. [Implementation and commands](../../../docs/rl/IMPLEMENTATION.md) · [Recorded command history](commands.json).

## Simulator and label correctness

Before training/evaluation, the native mechanics matched full states from the original Java Board/TaskManager on **13,984 archived transitions**, including 399 independently checked final game scores, and **4,991 randomized transitions** from 100 populated boards. Tests include ATTACK, both road operations, resource conflicts and capture settlement. There were zero unexplained mismatches. The later confirmation replay adds an independent check on student-visited states; it is not counted as another new tournament.

Teacher data comes from the historical 1,600-game v3/v6 comparison, using the recorded decisions of the unchanged public opponents. Two complete Lacoz-timeout games are excluded. There are **55,782 usable teacher turns** before command-normalization auditing.

Nonadjacent teacher moves are converted to their actual next house; amounts are decoded unit by unit. Triangle choices and moves use a canonical order. Comparing normalized and original joint transitions found **one order-sensitive double-attack turn**. It is recorded and excluded, leaving **55,781 turns**, or **99.9982% observed transition coverage**. This checks equivalence with the recorded opposing plan, not every possible opposing plan. No action family was silently removed. [Label audit](label-audit.json).

The excluded turn was in validation. Both the initial diagnostic fit and the clean rerun are retained; they produced **identical trained weights**. The native/PyTorch export check agrees on all 1,000 held-out choice groups, with maximum absolute logit difference **0.0000153**. A separate 2,000-decision native-policy benchmark produced zero parsing errors. [Export check](export-verification.json) · [Policy benchmark](policy-speed.json).

## Data and training

| Item | Recorded value |
|---|---:|
| Teacher turns after audit | 55,781 |
| Lacoz / khoufou turns | 20,012 / 35,769 |
| Training / validation maps | 158 / 42 |
| Training / validation full turns | 44,090 / 11,691 |
| Training / validation small choice groups | 1,170,666 / 325,958 |
| Candidate feature rows, both splits | 9,901,431 |
| Model parameters | 24,833 |
| Epochs / optimizer updates | 10 / 13,980 |
| Best validation choice accuracy | 62.51% |
| Best validation cross-entropy | 0.9093 |

Splits are by complete map content; neighboring states of a map cannot cross splits. Features use the current observation plus earlier friendly allocations, without the opposing current action or future information. Half of training groups use their teacher identity; half use the equal-mixture conditioning used for evaluation. Loss balances teachers and gives triangle choices weight 2. AdamW uses learning rate 0.001, weight decay 0.0001 and gradient clipping 1. The lowest validation loss selects epoch 10 before any confirmation result is inspected.

Choice accuracy is not a game win rate. One full move involves many choices, and different legal plans can be equally useful. The teacher games are mostly against v3/v6, so student-visited states and strong-teacher interactions are not comprehensively covered.

The dataset arrays are rebuildable local caches with hashes; they are not uploaded. Their original game sources, split/source register, final and diagnostic checkpoints, portable text weights and full tournament records are committed. [Dataset and split register](dataset.json) · [Training history](training/history.json) · [Configuration](training/config.json) · [Portable weights](training/weights.txt) · [Checkpoint](training/checkpoint.pt).

## Actual local resources

| Measurement | Result | Scope |
|---|---:|---|
| Native rules | about **21,700 joint turns/s** | Archived plans; excludes policy, generation, rendering and processes |
| Complete native policy | **1,147 decisions/s** | Features + legality + network + decoding, 2,000 archived observations |
| Final fitting and validation | **117 seconds** | 10 epochs on Metal/MPS |
| Initial diagnostic fitting | 133 seconds | Retained separately; same final weights |
| Peak recorded process RSS | **3.04 GB** | Does not measure total machine/GPU memory |
| Derived feature storage | about 2.5 GB | float16, before small index arrays |
| Confirmation tournament | **541 seconds** | 500 sequential original-referee games |
| External compute spend | **$0** | No rented GPU or purchased compute |

The representative fixed-shape optimizer benchmark measured 472k small choice groups/s on MPS and 295k on CPU, about 1.6×. This excludes data loading and is not a game simulation/rollout rate. MPS was detected and used by a permitted local process outside the restrictive sandbox. The actual environment was CPython 3.14.6, PyTorch 2.15.0 and NumPy 2.5.4.

In the confirmation arena, BC's p95 planning time was **1.19 ms against Lacoz**, **2.75 ms against khoufou** and **3.21 ms against v6**; the maximum was **10.62 ms**. These are internal planning times; the original runner separately enforced whole-response deadlines and reported no timeouts. Coding-subscription consumption is not observable and is not converted into invented token or dollar costs.

## What the games suggest

Against khoufou, BC averaged 43.88 captures and 33.47 executed spawns per game, versus v6's 32.54 captures and 27.21 spawns, despite shorter average games. At turn 15 in the 93 matched pairs where both games were still active, BC had **17.76 troops and 2.62 owned triangles**, versus **13.55 and 1.75** for v6. The trained policy develops and reuses its army more effectively on this opponent panel.

Against Lacoz, the 88 corresponding turn-15 pairs show more BC troops (**12.00 versus 10.09**) but fewer owned triangles (**0.55 versus 1.28**). Faster troop growth alone does not solve control and coordination against Lacoz. These are descriptive survivor-conditioned observations, not causal feature ablations.

The policy actually emitted all five mechanical command families during confirmation, including 353 ATTACK, 98 ADD_PATH and 15 REMOVE_PATH commands. Command counts are distinct from executed events: opponent actions can legitimately cancel planned actions. Detailed per-seat results, economy checkpoints and events are in `comparison.json` and the complete records.

## Decision and next experiment

BC v1 is a successful first learned research baseline: clearly stronger than v6 on these new maps and roughly even with the frozen khoufou. Lacoz remains the principal weakness. The main branch and prepared v6 submission are unchanged; this task does not promote or submit the new bot.

The next proposed experiment is a bounded self-play/PPO stage starting from this BC checkpoint, compared directly with the frozen BC control on new maps. Before scaling, add stochastic full-plan sampling/log probabilities and verify the learner's rollout loop. Targeted teacher relabeling on student-visited states is a separate alternative for the Lacoz/state-distribution gap. More epochs, a larger encoder and search should be isolated experiments rather than simultaneous changes.

The current bot is a native executable plus a text weights file. Single-file contest packaging, live platform limits and actual contest ranking are not established. This one-seed local experiment does not predict the outcome of subsequent RL training.

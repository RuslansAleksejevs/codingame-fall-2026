# Longer PPO training and a stronger opponent pool

The initial v2 controls keep the 24,833-parameter actor, native mechanics, legal-action decoder and whole-turn PPO objective from [PPO v1](PPO.md). It studies additional training, broader maps and stronger opponents. Its [protocol](../../experiments/rl/2026-11-06-ppo-v2/PROTOCOL.md) separates development selection from fresh confirmation.

## Separate experimental controls

`code/rl/train/ppo_long.py` resumes learning from the frozen selected PPO v1 actor, critic and optimizer states. The controlled-decision counter and training seed start a new experiment. With the original 158 maps it is a longer-training control; with the new 2,000-map corpus it is a map-only ablation. It retains the original 50% current/current, 25% BC and 25% recent-history mixture. Native BC/PPO v1 wins are diagnostics; they do not automatically select a checkpoint.

`code/rl/train/ppo_league.py` uses the new corpus and a separate native collector. Its game distribution is:

| Share | Opponent | Learning trajectories |
|---|---|---|
| 50% | Current sampled actor | Both players |
| 25% | Greedy frozen anchor: 90% PPO v1, 10% BC | Current actor only |
| 12.5% | Uniform historical snapshot, half greedy and half sampled | Current actor only |
| 12.5% | Original Lacoz | Current actor only |

Learner seats alternate in balanced blocks. The history holds up to 12 snapshots, refreshed every 250,000 controlled decisions. These are game shares, not exact shares of training decisions: game lengths differ, and self-play contributes both players. `--teacher none` substitutes additional history for the Lacoz category, enabling deterministic collector checks.

The reward stays terminal +1/-1/0 for win/loss/draw. No intermediate economy reward, teacher action labels or opponent future actions enter the PPO update. Fixed anchors and historical opponents are frozen within each rollout. Both players observe the same state before either command is applied.

## Original-opponent training bridge

The separate `code/rl/league/` library constructs the regular game input directly from the native simulator. A Python callback sends it to one persistent teacher process per collector worker. Each game executes the unchanged public Lacoz source in fresh globals; imports are reused, and per-game globals are discarded on termination. Source provenance and SHA256 are checked before starting workers.

Lacoz keeps its original 30 ms search budget. Training processes use health timeouts to detect hangs; those are not competition timing measurements. CPU contention and the opponent's wall-time search can change individual actions between runs. The original serial referee is used for all reported competitive panels while heavy training is stopped.

The bridge validates the complete initial and per-turn observation against original Java `Board.getInput()`, with order-insensitive comparison of undirected roads, triangles and legal connections. Observation list order is canonicalized by the native bridge and can differ from the original Java iteration order; semantic input equality is tested, not byte-for-byte output-policy identity. Full resulting states are replayed through the original Java oracle. `test_league.py` also checks native/PyTorch joint log probabilities and worker-count invariance without the wall-timed teacher. No opponent algorithm is reimplemented or attributed to this repository.

## Maps and checkpoints

`code/rl/data/generate_maps.py` calls the pinned original Java map generator. The null-renderer wrapper accepts only the expected `BoardView` initialization exception, after the original board has generated all map properties. It first regenerates the archived BC maps exactly, then excludes known map content and duplicates. Seed numbers alone are not treated as evidence of novelty.

Both trainers retain actor, critic, Adam states, NumPy/Torch RNG, history, opponent pool, counters, source snapshots and immutable milestone exports. Resume checks reject changed source files or configurations. `--steps` and `--minutes` are cumulative limits for the new experiment, including completed blocks. A recovery checkpoint is written every ten iterations; complete training games are collected before every update.

The resume test compares uninterrupted training with a split run for both deterministic recipes and requires identical actor, critic, optimizer states, opponent pool, sampling state and exported weights. Torch RNG bytes differ because temporary module construction consumes values after restoration; current optimization contains no Torch-random operations, and actual learned tensors are identical. This test does not claim bitwise repetition of a wall-timed Lacoz search.

The original v1 trainer and collector remain available unchanged. Build the separate league library with:

```sh
python3 code/rl/league/build.py
```

The required local environments and original referee are described in [the implementation guide](IMPLEMENTATION.md). Exact campaign commands and measured resources belong to the experiment record.

## Optional road-observation variant

`code/rl/roads/` and `code/rl/train/ppo_roads.py` isolate a representation experiment. The network still has 128 inputs and 24,833 actor parameters. Inputs 13–15, previously constant (0.5, 0.5, 1) for the deployed teacher-mixture style, are reused for three observations:

| Input | ADD_PATH value | REMOVE_PATH value |
|---|---|---|
| 13 | Newly closed empty triangles / 2 | Negative destroyed triangles / 2 |
| 14 | Friendly unit-majority corners in those triangles / 6 | Negative corresponding corner count / 6 |
| 15 | Enemy unit-majority corners in those triangles / 6 | Negative corresponding corner count / 6 |

The three-unit action cost is subtracted before counting corner majorities. These are observations of unit counts, not a guarantee of capture: surrounding and simultaneous enemy moves still matter. Other action kinds have zeros in these slots. No road action is forced or assigned a handcrafted score.

Initialization folds the old constant contributions into the first-layer bias and zeros the new columns, preserving actor and critic outputs to floating-point precision. Adam moments for those columns and the affected first bias are cleared; other optimizer state remains. Historical learner snapshots receive the same conversion. Frozen BC/PPO v1 anchors continue using the original style-2 features. This reparameterization is recorded as part of the intervention.

The variant has a separate C++ namespace/library, so it cannot replace the collectors of a running control. Its standalone bot uses **style 3**. A panel declares `"policy_variants": {"roads1m": "roads"}` for such a model and compiles the road binary separately; ordinary policies continue using the original source and style 2. Model files retain the common matrix format, so the correct feature variant must accompany the weights.

Validation covers original-Java road geometry and full transitions, native/PyTorch probabilities, frozen-anchor action compatibility, exported logits and full stdin/stdout plan parity. Competitive evidence comes from the same original-arena panels as the other candidates, not from these correctness checks.

## Selection and confirmation

`code/rl/eval/panel.py` copies all deployed weights and sources before starting a named-policy panel. It recompiles the frozen opponents and plays the original timed referee serially, on identical maps from both seats. Development maps may be previously inspected; confirmation maps must be unseen. Model weights cannot change during a panel.

`code/rl/eval/analyze.py` reports clean outcomes, errors/timeouts, per-seat results and paired map-clustered intervals. `code/rl/eval/verify_panel.py` checks all expected match keys, source/model hashes, historical and training-map overlap, and native replay outcomes. `verify_java_panel.py` additionally replays every clean game through the original Java oracle and compares the complete native state at every turn, including roads and triangle capture flags. Technical failures remain visible and are not silently counted as strategic wins. Intervals describe map/game uncertainty for the selected trained model; they do not estimate general training-seed variance.

`code/rl/eval/select_ppo_v2.py` applies the campaign's recorded rule to its complete 1,150-game finalist panel after both replay audits. It ranks eligible candidates by clean Lacoz score, then the equally weighted four-opponent score, then lower cumulative training time. Safeguards allow at most a six-point drop against each of khoufou/v6 relative to the simultaneous PPO-v1 control and require at least 60% direct score against PPO v1. Incomplete or technically faulty candidate panels are ineligible. The script refuses to replace an existing selection or select after the confirmation directory exists. It writes the selected checkpoint/weights hashes, feature variant and a fixed 1,800-game confirmation specification before any final map is generated.

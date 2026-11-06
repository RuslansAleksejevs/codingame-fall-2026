# PPO self-play v1 — fresh-map comparison

As of 2026-11-06. PROJECT_REPORTED local results on the M4 MacBook Air. One training seed; no live contest submission. Main remains v6.

## Result

**PPO improved all three fresh-map comparisons:** +33 percentage points against v6, +40 against khoufou and +29 against Lacoz. Every paired 95% map interval is above zero. PPO also won 94/100 directly against BC. Lacoz still won 69/100 against PPO, so it remains the strongest unresolved opponent in this panel.

The actor was actually fine-tuned from frozen BC with terminal-reward PPO and self-play. The following results use the selected trained checkpoint, frozen before the final panel. BC was rerun on the same new maps, with the same decoder and original opponents.

| Opponent | BC W/D/L | PPO W/D/L | Paired score-rate change | 95% map interval |
|---|---:|---:|---:|---:|
| v6 | 65/0/35 | 98/0/2 | +33.0 pp | +20.0 to +47.0 pp |
| lacoz | 2/0/98 | 31/0/69 | +29.0 pp | +17.0 to +41.0 pp |
| khoufou | 55/0/45 | 95/0/5 | +40.0 pp | +28.0 to +52.0 pp |

Direct PPO vs BC: **94/0/6**, score rate 94.0%, map-clustered 95% interval 88.0–99.0%. W/D/L means wins/draws/losses; a draw contributes half a point to score rate.

The panel contains 700 original-referee games on 50 maps, seeds 7001–7050, both seats. Technical outcomes: 0 candidate-error games, 0 opponent-error games; 0 records excluded from native replay due to technical issues. Clean-pair denominators and every excluded key are retained in `comparison.json`.

## Training and selection

The bounded run collected **1,001,849 controlled-player decisions** from **19,776 complete games**, over 309 collection/update iterations. It reached the sample target in **10.87 minutes**, below the 60-minute cap. Native collection supplied 654,083 joint game turns and 19,997,602 categorical choices. Self-play supplies two controlled decisions per joint turn; fixed-opponent games supply one.

The actor has 24,833 parameters, unchanged architecture/features/actions, initialized from BC. A separate 24,833-parameter critic learns only for PPO updates. Fifty percent of games use the current stochastic policy on both sides; 25% use greedy frozen BC; 25% use a recent frozen stochastic actor. The four-model pool refreshes every 100,000 decisions. No original Lacoz/khoufou process runs during learning. Sampling temperature is 0.7; both neural candidates act greedily.

Training reuses 158 BC training maps. Checkpoint selection uses the other 42 BC maps, both seats, against greedy BC. The highest score rate wins, earlier checkpoint on ties. These development results do not replace the fresh comparison above.

| Controlled decisions | Selection W/D/L | Selection score rate | Selected |
|---:|---:|---:|---|
| 102,000 | 61/4/19 | 75.00% |  |
| 251,717 | 68/2/14 | 82.14% |  |
| 500,237 | 76/0/8 | 90.48% |  |
| 752,998 | 78/0/6 | 92.86% | yes |
| 1,001,849 | 77/0/7 | 91.67% |  |

Selected actor SHA256: `8b9f669b3b4047eb75d1ff1df2ea9cc8e61de59629de1c9260f8a954b40ae7e7`. Both the selected checkpoint and final checkpoint are retained; the selected step is **752,998**. Initial BC SHA256: `b97859bc318a0bcbbf9d9b3080da695313fd716018d50f8155902d558291e24e`.

There were 0 KL-triggered actor early stops. Maximum replayed native/PyTorch full-turn log-probability error across training: 0.00006866 (abort threshold 0.003). The last update's critic explained variance was 0.832. These are optimization diagnostics, not evidence of strength against public bots.

## Correctness and comparison controls

CPU and MPS correctness suites passed. Initial sampled-game checks matched the original Java oracle on 258 transitions; the final selected actor matched another 205 full Java transitions in eight sampled games. Exported C++ logits and decisions were checked against the saved tensor model. Final arena records were replayed through the native simulator: **20,957 joint transitions**, **0 mismatches** in checked pre-decision units or terminal scores. All 50 new maps differ by content from 375 previously inspected maps.

The main v6 source, frozen BC, legal decoder and simulation rules were preserved. Lacoz remains `7f1901834d2ffc16532e083edfec8cbdb5941ab6`; khoufou remains `372c1cd6738d456513cb50705b98549eedfdfad8`. The referee remains `b6913124a10de328316ff42906448a18cb948431`, league 3, first turn 1000 ms and later turns 50 ms. Games run serially after training, interleaving candidates on identical seeds. Opponent wall-time search can vary between reruns.

The 28 deployment smoke games use already known seeds 4101–4102 and are excluded from final strength estimates. No checkpoint, reward or hyperparameter was selected using final-panel outcomes. Confidence intervals resample whole maps with both seats, 10,000 replicates; matched pairs exclude either side’s technical failure. One training seed cannot establish consistency across independent training seeds.

## Local resources

| Measurement | Actual |
|---|---:|
| Main training wall time | 652.17 s |
| Native rollout time within training | 326.40 s |
| Optimization/checking time within training | 306.95 s |
| End-to-end controlled decisions/s | 1536 |
| Peak training process RSS | 1.55 GB |
| Final 700-game panel wall time | 11.82 min |
| External compute spend | $0 |

CPU was chosen by a representative complete-loop benchmark: 10,656 decisions in 5.57 s, approximately 1,914/s, versus MPS 10,829 in 15.03 s, approximately 720/s. This small ragged PPO workload favors CPU; the earlier fixed-shape BC optimizer favored MPS. Both pilots restart from BC, and their updates are not carried into the main run. The initial 1,850-decision functional pilot is also preserved. Peak RSS refers to the training process, not total machine or GPU usage. Coding-subscription quota usage is not observable here.

Measured environment: MacBook Air M4, 24 GB unified memory, macOS 26.6.2, CPython 3.14.6, PyTorch 2.15.0, NumPy 2.5.4. Four native rollout workers and four PyTorch CPU threads, used in successive collection/update phases.

## Reproduction and evidence

[Protocol](PROTOCOL.md), [commands](COMMANDS.md), [implementation](../../../docs/rl/PPO.md), `maps.json`, `device-selection.json`, `training/config.json`, all five selection folders, selected/final checkpoints, pilot folders, tests, `comparison.json` and `verification.json` are retained. Complete arena records and training history are packed in `records.tar.gz`; restore them with `python3 code/restore_records.py`. Per-candidate training arrays are transient derived buffers rather than a full trajectory archive.

## Deployment timing

| Policy on the matched three-opponent panel | Decisions | Median | p95 | Maximum |
|---|---:|---:|---:|---:|
| BC | 10,361 | 0.774 ms | 2.984 ms | 6.553 ms |
| PPO | 8,605 | 1.018 ms | 2.951 ms | 45.373 ms |

These are self-recorded complete-plan compute times, excluding input parsing and process startup; they include operating-system scheduling delays. The original runner independently enforces the full response deadline. Different game trajectories affect army size and the number of candidate evaluations.

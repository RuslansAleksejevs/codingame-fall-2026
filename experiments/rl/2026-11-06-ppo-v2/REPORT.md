# PPO v2: larger local training campaign

**Confirmed:** the selected PPO v2 wins **139/200 against Lacoz**, versus **74/200 for PPO v1**, on 100 new maps from both seats. The paired gain is **+32.5 percentage points**, with a map-clustered 95% interval of **+22.5 to +42.5**. Direct PPO v2 versus PPO v1: **155 wins / 45 losses**. All 1,800 final games were clean.

The selected model is **league3m**, after 3,002,173 additional controlled-player decisions. It was frozen before the final maps were opened. The campaign trained four arms for **10,633,778 additional decisions / 218,880 games / 5.997 summed training hours**, entirely on the local MacBook. The model and executable entry point are recorded in [selected-policy.json](../../../code/rl/configs/selected-policy.json).

## Fresh confirmation

Seeds 9001–9100 contain 100 distinct maps with no content overlap against 2,425 previously inspected maps, including the 2,000 new training maps. Each matchup uses both seats, with serial cyclic ordering and the original 1000/50 ms limits. Both policies use the same frozen opponents and matched maps.

| Opponent | PPO v1 W / D / L | PPO v2 W / D / L | Score change | Paired 95% interval |
|---|---:|---:|---:|---:|
| Lacoz | 74 / 0 / 126 | **139 / 0 / 61** | **+32.5 pp** | **+22.5 to +42.5** |
| khoufou | 182 / 0 / 18 | **193 / 0 / 7** | **+5.5 pp** | **+2.0 to +9.5** |
| v6 | 195 / 0 / 5 | 194 / 0 / 6 | -0.5 pp | -3.0 to +1.5 |
| BC | 189 / 2 / 9 | 192 / 0 / 8 | +1.0 pp | -3.5 to +5.0 |

Score counts a draw as half a win. All 200 pairs per opponent are clean; no technical outcomes were excluded. The gain against Lacoz is substantial and also appears against khoufou. The v6 result is essentially unchanged in this sample; the BC interval includes zero. Direct PPO v2–PPO v1 is **77.5% wins** on 200 clean games. These results support the selected model, not a claim that every new recipe or random training seed is superior.

All **49,424 complete states / 47,624 joint transitions** from the final panel matched the original Java referee, including roads and triangle capture flags. The final tournament took **35.07 minutes**. Maximum measured PPO-v2 plan computation was **12.705 ms**; every full response also passed the original arena's limits. See [paired analysis](confirmation-comparison.json), [source/map/native audit](confirmation-verification.json), [complete-state audit](confirmation-java-verification.json) and [confirmation decision](confirmation-decision.json).

The [selection record](selection.json) predates the confirmation manifest; its weights, checkpoint and feature variant were rechecked. Frozen BC, PPO v1 and v6 hashes are unchanged. The primary aspiration (+15 pp or better against Lacoz with a positive lower interval) was exceeded. Main v6 and live submission status remain unchanged.


## Scope

All work runs locally on the MacBook Air M4 with 24 GB RAM. Frozen PPO v1 (selected after 752,998 controlled-player decisions) initializes every production arm. The actor remains a 24,833-parameter MLP; the separate critic is used only during learning. Main v6, BC and PPO v1 remain unchanged. External compute spend is **$0**; subscription quota and electricity cost are not measured.

The [pre-recorded protocol](PROTOCOL.md) reserves 100 new maps for an 1,800-game final comparison. Previously inspected seeds 6001–6025 are development data. Native checks against BC/PPO v1 help detect regressions but do not select the model. The final model is selected using the original timed arena against Lacoz, khoufou, v6 and PPO v1.

## Completed initial training

All counts below are additional to the common frozen PPO v1 initialization. Elapsed times are summed within each run, including resumed blocks. Some runs overlap and share the CPU, so these are not isolated throughput benchmarks or campaign calendar time.

| Arm | Training maps | Opponent recipe | New decisions | Games | Run elapsed |
|---|---:|---|---:|---:|---:|
| Longer control | 158 | Original current/BC/history | 3,002,813 | 63,680 | 74.74 min |
| Map-only | 2,000 | Original current/BC/history | 1,002,950 | 20,800 | 29.64 min |
| League | 2,000 | Current/strong anchors/wider history/Lacoz | 3,002,173 | 60,608 | 132.39 min |
| Road observations | 2,000 | Same league | 1,002,234 | 20,032 | 39.07 min |
| **Total** | | | **8,010,170** | **165,120** | **275.84 min** |

The league uses 50% current self-play games, 25% frozen-anchor games (90% PPO v1 and 10% BC within that category), 12.5% historical models and 12.5% original Lacoz. History holds up to 12 snapshots. Self-play contributes both players' learning trajectories. Rewards remain terminal +1/-1/0, with the original whole-turn PPO loss and optimization settings. Lacoz supplies opposition, not supervised action labels.

The road arm replaces three constant inputs with the immediate triangle effects of adding/removing a road. Initial constant contributions are folded into the first-layer bias; new columns start at zero. Corresponding Adam moments are reset. This is a feature/reparameterization bundle, not a pure feature-only causal ablation. See [implementation details](../../../docs/rl/LEAGUE.md).

Production training parents peaked at up to 1.46 GB RSS individually. That figure excludes teacher child processes and is not combined peak system memory. Both Lacoz-training arms completed without bridge errors. The [resource record](initial-production-summary.json) retains exact counts, times, memory scope and teacher calls.

## Preliminary development evidence

Before the common panel, the 1M longer-control checkpoint won **28/50 against Lacoz and 50/50 against khoufou**. Simultaneously evaluated PPO v1 won **18/50 and 47/50**. These are reused development maps, not the reserved final holdout. All 200 games were clean, and all 5,761 full states / 5,561 transitions matched original Java.

The common panel compared all seven frozen versions on the same maps. All 700 games were clean; all 19,937 full states / 19,237 transitions matched original Java.

| Policy | Lacoz wins / 50 | khoufou wins / 50 |
|---|---:|---:|
| PPO v1 | 16 | 47 |
| Longer control 1M | 26 | 50 |
| Longer control 3M | 32 | 50 |
| Map-only 1M | 27 | 50 |
| League 1M | 23 | 50 |
| **League 3M** | **34** | **50** |
| Road observations 1M | 29 | 50 |

League 3M minus PPO v1 is +36 percentage points against Lacoz on these development maps (paired map-clustered interval +18 to +54). This panel is used for model selection, so it is not independent confirmation of the selected model. Its two-win lead over the longer 3M control does not establish that the league recipe is reliably better. Repeated screens on the same 25 maps are not pooled as independent samples.

The subsequent 350-game safeguard panel was also entirely clean:

| Policy | v6 wins / 50 | Direct PPO v1 wins / 50 |
|---|---:|---:|
| PPO v1 control | 48 | — |
| League 3M | 50 | 42 |
| Longer control 3M | 50 | 39 |
| Road observations 1M | 50 | 39 |

All three leaders passed the pre-recorded regression/direct-play screens. Every one of the safeguard panel's 9,115 full states / 8,765 transitions matched original Java. The [recorded follow-up](followup-training-decision.json) gives the larger remaining block to league continuation and a smaller block to the road variant. All prior leader checkpoints remain available for the final development panel. This continuation phase uses the same training seed; it is not an independent-seed replication.

Road construction remains rare: 12 ADD_PATH commands for league3m and 9 for roads1m across their 50 Lacoz games. Mean captures/spawns increase in stronger models, but these are descriptive game statistics influenced by survival and game length, not a causal explanation or reward-shaping result.

## Completed continuation

The league run stopped at the cumulative time cap after **4,836,947 additional decisions**, **98,432 games** and **190.20 run minutes**. Its planned 5M sample target was not reached; the actual frozen export is `league-a/step-04836947`. The latest parent peaked at 1.45 GB RSS and no teacher errors occurred. Native diagnostics improved from 60/84 to **75/84 against PPO v1**, with **84/84 against BC**; these diagnostics do not select the final candidate.

The saved tensor/text/native export passed **1,000/1,000 argmax comparisons**, covering 6,934 logits with maximum absolute error 3.05e-5. The road continuation stopped at its time cap after **1,791,068 additional decisions**, **35,968 games** and **65.21 cumulative minutes**, below its 2M sample target. Its export passed 11,324 logits (maximum error 1.91e-5), 206 anchor plans and 246 standalone plans. Native diagnostics were 80 wins / 2 draws / 2 losses against BC and 60/84 against PPO v1. All production runs together completed **10,633,778 new decisions / 218,880 games / 5.997 summed training hours**. The subsequent final development panel compared both extended models, all three prior leaders and PPO v1 before any reserved confirmation map was opened.

## Final development selection

The complete final development panel contains 1,150 original-referee games on the same 25 reused maps. All games were clean, and all 31,337 full states / 30,187 transitions matched original Java.

| Policy | Lacoz wins / 50 | khoufou wins / 50 | v6 wins / 50 | Direct PPO v1 wins / 50 |
|---|---:|---:|---:|---:|
| PPO v1 | 17 | 47 | 48 | — |
| **League 3M** | **35** | **50** | **50** | **42** |
| Longer control 3M | 27 | 50 | 50 | 39 |
| Road observations 1M | 27 | 50 | 50 | 39 |
| League extended, 4.837M | 30 | 50 | 50 | 46 |
| Road observations extended, 1.791M | 29 | 50 | 50 | 46 |

All candidates passed the predeclared safeguards. **League 3M** wins the primary Lacoz ranking and is frozen in [selection.json](selection.json), before any confirmation map was generated. It has 3,002,173 additional decisions (plus the common 752,998-step initialization), with 132.39 cumulative training minutes. Its text-weight SHA256 is `dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb`; it uses the original style-2 features. Its checkpoint/export passed 1,000/1,000 argmax checks across 6,934 logits, maximum absolute error 2.29e-5.

More training did not improve every matchup monotonically: both extended models beat PPO v1 more often, but the 3M league checkpoint remains stronger against Lacoz in this selection panel. Native diagnostics against the old network alone would have selected a different checkpoint. This does not establish that any single intervention caused the improvement; earlier repeated Lacoz results also vary because its search is wall timed. The completed fixed final test above compared that frozen winner to PPO v1 on untouched maps.

## Resource accounting and next evidence

Across development, smoke and confirmation panels, **4,256 original-arena games** completed without technical failures, taking **86.73 summed panel minutes**. Production training used 5.997 summed run hours; the measured goal-to-final-tournament wall span was **5.65 hours**, including implementation and early experiments, with some training runs overlapping. Later reporting and repository publication are outside that wall-time boundary. Individual parent RSS reached up to 1.46 GB; teacher children and total system peak are not included. External compute spend is $0; electricity and subscription quota are unmeasured. Exact boundaries and timings are in [resources.json](resources.json).

Longer training with the original recipe already improved the development control. More maps alone did not establish an independent advantage at the 1M checkpoint, and road observations did not produce the selected model. The league produced the best measured checkpoint, but the recipe has not been replicated across independent fine-tuning seeds. All later and unsuccessful variants are preserved. Learning diagnostics retain probability-consistency errors and per-opponent training outcomes; changing, sampled training opponents are not a replacement for the external tournament.

A next experiment should first test another training seed with development opponents that reflect the desired matchups; selecting only against the old PPO would have favored the wrong checkpoint here. Increasing the original-opponent share or adding another strong opponent should be a separate measured change. Those experiments, learned lookahead and contest packaging have not been run as part of this campaign.

## Correctness and provenance

- All 29 local original-referee Java sources match the pinned upstream Git tree by Git blob hash.
- The original map generator reproduced all 200 archived generation maps exactly. The 2,000 new training maps have no content overlap with 425 historical maps.
- League and road collectors pass full-state original-Java checks, native/PyTorch likelihood checks and deterministic worker-count checks without the wall-timed opponent.
- Split/resume tests preserve learned tensors, optimizers, pools, NumPy sampling state and exported weights. Torch RNG bytes differ after temporary module construction; current training has no Torch-random update operations. This is not a claim that wall-timed Lacoz repeats bit-for-bit.
- The trained road model passes 11,324 exported-logit comparisons (maximum absolute error 2.29e-5) and 246 complete standalone/native action-plan comparisons. All 206 frozen-anchor plans also match.
- The training bridge preserves semantic observations but canonicalizes list order; its wall-timed opponent behavior may differ from original-arena behavior. Competitive evidence uses the original serial 1000/50 ms arena.

Exact commands are in [COMMANDS.md](COMMANDS.md). Configurations, checkpoint tensors, immutable text exports, source snapshots, complete optimization histories, sampled training rollouts and every evaluation game record are retained, including pilots and variants that may fail to improve. Training games are summarized per rollout; they are not all stored as full trajectories. No live contest submission or main-branch promotion occurs in this campaign.

The evaluated deployment is a local C++ executable plus a separate text-weight file. Contest-side single-file packaging, permitted libraries and live ranking are outside this experiment and have not been validated here.

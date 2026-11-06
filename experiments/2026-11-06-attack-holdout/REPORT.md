# Fresh-map confirmation: v3 versus v6

Date: 2026-11-06, America/Los_Angeles. Classification: PROJECT_REPORTED.

**v6 passed the frozen promotion rule and is now the main bot.** Against khoufou it won 64/400, versus 29/400 for v3: 16.00% versus 7.25%, a gain of **8.75 percentage points**. The paired map-bootstrap 95% interval is **+5.25 to +12.75 points**. Against Lacoz, both won 1/398 on the shared clean pairs; no gain was observed.

All 1,600 planned games completed. Neither candidate had a command error or timeout. Lacoz timed out twice against v6; these two technical wins are excluded from the strategy comparison. External paid spend: 0. No contest submission was made.

## Design and decision

[plan.json](plan.json) records the criteria and frozen source hashes before either run manifest was created. There was no tuning, early stopping or sample extension. Seeds 4001–4200 were played from both seats against both unchanged public opponents, with v3/v6 interleaved and their order rotated. Only one game ran at a time.

The pinned original referee `b6913124a10de328316ff42906448a18cb948431` ran in league3 with its 1000 ms first-turn and 50 ms subsequent-turn limits. Opponents were Lacoz `7f1901834d2ffc16532e083edfec8cbdb5941ab6` and khoufou `372c1cd6738d456513cb50705b98549eedfdfad8`. The newer khoufou revision discovered during this work was not substituted into the experiment.

All 200 map contents are distinct and differ from the 125 historical maps across 17 manifests. The content check excludes the seed number itself and compares coordinates, edges and initial units. [historical-maps.json](historical-maps.json) freezes the historical inventory; [selection.json](selection.json) records the checks and decision. This checks identical map contents, not graph isomorphism.

| Pre-recorded promotion condition | Result |
|---|---|
| khoufou: positive lower bound of the paired 95% interval | Passed: +5.25 pp |
| Lacoz: no lower observed paired clean score | Passed: unchanged |
| No own command errors/timeouts | Passed: zero in 1,600 games |
| Complete valid schedule and at least 95% shared clean pairs per opponent | Passed: 100% against khoufou, 99.5% against Lacoz |

The Lacoz condition is an observed-score check, not a statistical proof of non-inferiority. The decision uses this fresh sample alone; older reused-map results were not pooled into the promotion test.

## Outcomes

| Opponent | v3 wins / shared clean games | v6 wins / shared clean games | Paired change |
|---|---:|---:|---:|
| khoufou | 29/400 | **64/400** | **+8.75 pp** |
| Lacoz | 1/398 | 1/398 | 0 pp |

There were no draws. Against khoufou, 40 paired outcomes improved and five worsened; the remaining 355 were unchanged. Both seats improved: seat0 went from 15/200 to 34/200, seat1 from 14/200 to 30/200. The interval uses 10,000 paired bootstrap resamples of the 200 maps, preserving both seats together, with RNG seed1729 and draw value0.5.

For Lacoz, v3's individual clean record is 1/400; v6's is 1/398, plus two technical wins. For the paired table, the corresponding v3 games are also excluded. Both ordinary wins occurred on seed4013, seat0. The two timeouts occurred only for Lacoz against v6: seed4008/seat1 and seed4017/seat0. All outcomes and error messages remain in the records; no failed game was rerun or silently discarded. An all-zero observed paired change does not prove zero true effect.

The main bot is stronger against the frozen khoufou but still loses most games, and remains far behind frozen Lacoz. These results do not establish performance against the newer khoufou or the live contest field. Lacoz's wall-clock-limited search can change decisions on replay; the intervals are conditional on the frozen opponents and observed executions.

## What ATTACK changed

The source is the unchanged v6 from the [previous experiment](../2026-11-05-attack/REPORT.md): at most one attack on an adjacent enemy stack of four or more, with six friendly units overall and one on each triangle corner. The planner deducts the three-unit cost and marks the triangle spent before running v3's movement/spawn logic.

| v6 attack audit, all measured games | Against khoufou | Against Lacoz |
|---|---:|---:|
| Games containing an attack | 317/400 | 122/400 |
| Requested / executed attacks | 816 / 816 | 145 / 145 |
| Enemy units actually killed | 3,785 | 609 |

All 961 requested attacks executed; 4,394 casualties agree between viewer records and event summaries. Targets contained 4,437 units at decision time: simultaneous enemy actions can change the stack before resolution, so requested target size is not counted as actual kills.

Against khoufou, spawned units per 100 decisions increased from 68.59 to 71.03, captures from 78.03 to 86.51, and surrounding deaths fell from 32.42 to 23.20. These descriptive statistics accompany the win-rate gain; surrounding/hostile-attack losses exclude the three friendly units consumed by each own attack.

Against Lacoz, attack opportunities were much rarer. Around turn10, the v6 army averaged 9.84 units versus 22.09 for Lacoz in clean games. This describes an early army gap, not a controlled explanation of its cause. More isolated attacks do not address the coordinated planning and economy differences discussed in the [roadmap](../../docs/ROADMAP.md).

## Verification and artifacts

- All 1,600 raw game records were reanalyzed; saved outcomes, events and trajectories matched. Every launcher exited zero and no referee failed.
- 55,901 decision states were checked against the original viewer protocol. Every attack met the observed troop/target thresholds; consumed troops were not moved and the triangle was not also spent on SPAWN.
- Both frozen sources compiled with C++17 `-O2 -Wall -Wextra -Wpedantic` without warnings. The promoted `code/bot.cpp` and prepared `submissions/baseline-v6-attack.cpp` are byte-identical to the tested v6 source; the main executable was rebuilt without warnings. v3 is retained.
- v6 internal planning time: p95 0.751 ms against khoufou and 0.593 ms against Lacoz; maximum 7.642 ms overall. These are in-process measurements, not complete server response times.
- Environment: Apple clang17.0.0, Temurin17.0.21+9, Python3.14.6, NumPy2.5.4, SciPy1.18.1. Python imports were warmed and numerical-library threads capped at one. Exact commands and versions are in the manifests.
- Summed match-process wall time: 33.68 minutes, excluding preparation, analysis and upload.

Frozen v3 SHA256: `0b2d033bfda7282eaa31891f033124d680234e698dde714c21005fe2f9ac518f`.
Frozen/promoted v6 SHA256: `d36adc818e238b49544f1752beaf7388ea22ca4bb75446fcddc173c091e2ccf4`.

[comparison.json](comparison.json), [audit.json](audit.json), [selection.json](selection.json), schedules, manifests, source snapshots and full record archives preserve the evidence. Root CHECKSUMS.json covers exported files; machine-specific paths are normalized. Prepared code is not a submission.

## Reproduce the analysis

From the repository root:

```sh
python3 code/restore_records.py
python3 code/analyze_incremental.py --runs v3=experiments/2026-11-06-attack-holdout/run/v3 v6=experiments/2026-11-06-attack-holdout/run/v6 --pairs v3:v6 --out /tmp/fresh-attack-comparison.json
python3 code/audit_attack.py --runs experiments/2026-11-06-attack-holdout/run/v3 experiments/2026-11-06-attack-holdout/run/v6 --out /tmp/fresh-attack-audit.json
python3 code/analyze_holdout.py --experiment experiments/2026-11-06-attack-holdout --out /tmp/fresh-attack-selection.json
```

The original measured command was:

```sh
python3 code/benchmark_ablation.py --variants v3=code/variants/v3-multispawn.cpp v6=code/variants/v6-attack.cpp --seeds 4001:4200 --map-context fresh --out experiments/2026-11-06-attack-holdout/run
```

For a replay, use a new output directory and `--map-context reused`: these maps are now known. A future confirmation must use a new frozen plan and untouched maps.

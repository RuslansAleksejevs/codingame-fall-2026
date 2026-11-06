# ATTACK added to v3: paired comparison

Date: 2026-11-05, America/Los_Angeles. Classification: PROJECT_REPORTED.

**v6-attack won 29/200 against khoufou, compared with 21/200 for v3. Neither version won against Lacoz.** The observed khoufou increase is +4 percentage points (10.5% to 14.5%), but the paired 95% interval is -0.5 to +8.5 points. This is a promising local signal, not a reliably established improvement.

v6 is retained as an experimental variant. The main `code/bot.cpp` and prepared submission remain v3 until a stronger confirmation is available. All 800 measured games and eight smoke games are preserved, with no errors or timeouts. External paid cost: 0. No contest submission was made.

## One strategy change

`code/variants/v6-attack.cpp` adds one optional ATTACK before the v3 movement/spawn planner:

1. Require at least six friendly units overall, and an owned triangle with at least one unit at each corner.
2. Find the largest enemy stack neighboring any corner, requiring at least four enemy units.
3. Issue at most one attack. Deduct one friendly unit at each corner, clear the target's enemy stack in the planning state, and mark the triangle spent and temporarily uncapturable.
4. Run the existing v3 planner on the resulting state. Never move the consumed units or spend the same triangle on SPAWN.

ATTACK resolves before MOVE and SPAWN in the pinned referee. Four enemy casualties cover three sacrificed troops plus the immediate alternative of one SPAWN; this simple threshold does not price future income or positional value. At least three friendly units remain in the planning state. No road changes, triangle-reset or protection variant was added. Without a selected attack, the original v3 strategy is unchanged.

Mechanics were checked in the pinned `AttackTask.java`, `Triangle.java`, `TaskManager.java` and `Board.java`. Simultaneous enemy attacks can change the actual target size or interfere with a later action; measured execution records, rather than requested commands alone, are used below.

## Same maps, fresh executions

Both variants were frozen before measurement and rerun together. The control source is byte-identical to historical v3 (SHA256 `0b2d033bfda7282eaa31891f033124d680234e698dde714c21005fe2f9ac518f`). Map hashes match the earlier experiments exactly.

| Map set | v3 vs khoufou | v6 vs khoufou | v3 vs Lacoz | v6 vs Lacoz |
|---|---:|---:|---:|---:|
| Seeds1001–1050 | 8/100 | 14/100 | 0/100 | 0/100 |
| Seeds2001–2050 | 13/100 | 15/100 | 0/100 | 0/100 |
| Combined | **21/200** | **29/200** | **0/200** | **0/200** |

Every map was played from both seats against both frozen opponents. Variants were interleaved for each map/seat/opponent, with rotated order and one game at a time. The original referee b6913124a10de328316ff42906448a18cb948431 ran in league3 with 1000/50 ms limits. Lacoz7f190183 and khoufou372c1cd6 sources were unchanged; exact hashes, versions and commands are in each manifest. Python libraries were warmed before each series.

Both map sets had already been examined in earlier work. The second set is called `previous-validation` because it was an unseen validation set for the earlier experiment, **not a new holdout for ATTACK**. Coefficients were not changed after observing these ATTACK runs. Smoke seed42 was separate from measurement.

## Size and uncertainty of the gain

The first set improved by +6 points; the second by +2. Across 200 paired khoufou games, 13 changed from loss to win and five changed from win to loss. The other 182 outcomes were unchanged. There were no draws or technical outcomes.

The 95% interval uses 10,000 paired resamples of the 100 maps, retaining both seats together. It includes zero. The point estimate favors ATTACK, but this sample does not rule out no true gain. Reusing known maps further limits generalization. Lacoz's time-bounded search may vary between executions; no improvement against it was observed. Its all-zero observed interval does not establish zero true win probability.

## What the attacks did

| v6 metric | Against khoufou | Against Lacoz |
|---|---:|---:|
| Games containing an ATTACK | 156/200 | 60/200 |
| Requested / executed attacks | 361 / 361 | 71 / 71 |
| Enemy units killed by ATTACK | 1,658 | 312 |
| Enemy kills per executed attack | 4.59 | 4.39 |
| Mean spawned units, v3 → v6 | 33.66 → 30.91 | 13.03 → 12.79 |
| Mean captures, v3 → v6 | 39.01 → 37.61 | 14.58 → 14.50 |

Attacks remove meaningful stacks, especially against khoufou, but consume troops and triangles that otherwise support expansion. Reinforcement and capture rates did not improve. Against Lacoz the attack opportunities were much rarer and did not change outcomes.

Against khoufou, own surrounding deaths fell from 32.18 to 23.54 per 100 decisions and enemy-ATTACK deaths from 34.22 to 21.79. These categories exclude the troop cost of the bot's own ATTACK; they must not be interpreted as a free reduction in total losses. Wins remain the primary metric.

## Verification

- `code/test_attack.py`: threshold, legal troop availability, largest target, consumed-unit accounting, no triangle reuse and v3 fallback behavior passed.
- All sources compiled with C++17 `-O2 -Wall -Wextra -Wpedantic`, with no warnings.
- 800 measured records were reanalyzed and matched saved outcomes, events and trajectories. All launchers exited zero; no player command errors, timeouts or referee failures occurred.
- 27,974 decision states were checked against viewer-protocol unit counts.
- All 432 issued attacks executed; 1,970 casualties match both viewer serialization and text event summaries. Every attack's observed troop budget, four-unit target threshold and exclusion from SPAWN were checked.
- v6 planning time: p95 0.711 ms against khoufou, 0.608 ms against Lacoz; maximum 1.635 ms overall. These are internal process timings, not complete server response times.
- Summed measured match-process time: 15.98 minutes. Preparation, smoke tests, analysis and upload are excluded.

Sources: `development-comparison.json`, `previous-validation-comparison.json`, `combined-comparison.json`, `audit.json`, schedules/manifests and complete archives. Source SHA256 and archive integrity are retained in manifests and root CHECKSUMS.json. Paths in exported metadata are normalized; historical source/binary hashes still identify the actual run artifacts.

## Reproduce

From the repository root after environment setup, use new output folders:

```sh
python3 code/test_attack.py
python3 code/benchmark_ablation.py --variants v3=code/variants/v3-multispawn.cpp v6=code/variants/v6-attack.cpp --seeds 1001:1050 --map-context reused --out experiments/attack-repeat/development
python3 code/benchmark_ablation.py --variants v3=code/variants/v3-multispawn.cpp v6=code/variants/v6-attack.cpp --seeds 2001:2050 --map-context reused --out experiments/attack-repeat/previous-validation
```

To inspect the preserved runs without playing new games:

```sh
python3 code/restore_records.py
python3 code/analyze_incremental.py --runs v3=experiments/2026-11-05-attack/development/v3 v6=experiments/2026-11-05-attack/development/v6 --pairs v3:v6 --out /tmp/attack-development.json
python3 code/analyze_incremental.py --runs v3=experiments/2026-11-05-attack/previous-validation/v3 v6=experiments/2026-11-05-attack/previous-validation/v6 --pairs v3:v6 --out /tmp/attack-previous-validation.json
python3 experiments/2026-11-05-attack/analyze_combined.py
python3 code/audit_attack.py --runs experiments/2026-11-05-attack/development/v3 experiments/2026-11-05-attack/development/v6 experiments/2026-11-05-attack/previous-validation/v3 experiments/2026-11-05-attack/previous-validation/v6 --out /tmp/attack-audit.json
```

`code/archive_run.py` packages completed runs and normalizes machine-specific paths. All repository documentation, including older reports and research notes, is now in English. Frozen historical bot sources and game measurements were preserved.

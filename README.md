# CodinGame Fall Challenge 2026 — TryAngle Catch

A private working repository for a C++17 bot, a reproducible local arena and experiment results.

I work on this project through **Codex**. **Codex created this repository and makes changes to it**, including code, validation tools and documentation.

[Contest](https://www.codingame.com/contests/fall-challenge-2026) · [Rules](docs/RULES.md) · [Fresh ATTACK confirmation](experiments/2026-11-06-attack-holdout/REPORT.md) · [Development roadmap](docs/ROADMAP.md) · [RL research](docs/rl/README.md)

## RL research branch

The selected local RL bot is **PPO v2, league3m**, a 24,833-parameter network initialized from frozen PPO v1 and trained for 3,002,173 additional controlled-player decisions. The larger campaign compared four training arms: **10.63M additional decisions / 218,880 games / 6.00 summed training hours** on the MacBook CPU, with $0 external compute spend. [Selected policy and run command](code/rl/configs/selected-policy.json) · [Full PPO v2 report](experiments/rl/2026-11-06-ppo-v2/REPORT.md) · [Implementation](docs/rl/LEAGUE.md).

On **100 new maps, both seats**, after freezing the winner:

| Opponent | PPO v1 wins / 200 | PPO v2 wins / 200 |
|---|---:|---:|
| Lacoz | 74 | **139** |
| khoufou | 182 | **193** |
| v6 | 195 | 194 |
| BC | 189 | 192 |

PPO v1 also drew twice against BC. The paired score gain against Lacoz is **+32.5 percentage points**, with a 95% map-clustered interval of **+22.5 to +42.5**. Direct PPO v2–PPO v1: **155/200 wins**. All 1,800 final games were clean; all 49,424 full states / 47,624 transitions matched original Java. v6 performance is essentially unchanged, and the BC difference is inconclusive. This is one fine-tuning seed, with checkpoint selection completed before the final maps were opened.

[BC report](experiments/rl/2026-11-06-bc-v1/REPORT.md) and [PPO v1 report](experiments/rl/2026-11-06-ppo-v1/REPORT.md) retain the earlier controls. The main baseline below remains v6. The RL deployment is currently a local executable plus a weight file; contest-side packaging has not been validated.

## Current baseline

The selected baseline is **v6-attack**, using ATTACK/MOVE/SPAWN/WAIT. Prepared candidate: [baseline-v6-attack.cpp](submissions/baseline-v6-attack.cpp). Its frozen source passed the pre-recorded promotion rule on 200 new maps, both seats, against both opponents: **1,600 games**.

| Opponent | v3 wins / paired clean games | v6 wins / paired clean games |
|---|---:|---:|
| khoufou | 29/400 | **64/400** |
| Lacoz | 1/398 | 1/398 |

The khoufou gain is **+8.75 percentage points**, with a paired 95% interval of **+5.25 to +12.75 points**. No gain was observed against Lacoz. Neither candidate had errors or timeouts. Two Lacoz timeouts produced technical wins for v6; those pairs are excluded from the table and retained in the records. [Full report and decision](experiments/2026-11-06-attack-holdout/REPORT.md).

v6 is stronger against the frozen khoufou but still far behind Lacoz. These are local measurements, not contest rankings. No contest submission has been made from this repository.

## Development history and next direction

[v6](code/variants/v6-attack.cpp) adds one attack on an enemy stack of at least four, accounting for three consumed friendly units and the spent triangle before movement/spawning. v3 and earlier variants remain available for comparison.

- [Incremental experiment](experiments/2026-11-05-incremental/REPORT.md): multiple SPAWN commands improved v2; the isolated reset and protection variants did not improve v3.
- [Initial ATTACK experiment](experiments/2026-11-05-attack/REPORT.md): 800 games on reused maps gave 21/200 versus 29/200 against khoufou, with an interval including zero. Promotion waited for the fresh confirmation above.
- Complete public Lacoz/khoufou sources are already copied unchanged as test opponents. Their whole algorithms have not been adopted as the main bot. The [roadmap](docs/ROADMAP.md) recommends comparing complete bases, including a newly reviewed khoufou revision, before further isolated ports. Those future tournaments have not been run.


## Layout

- `code/bot.cpp`: main bot; `code/variants/`: isolated strategy variants.
- `code/arena/`, `code/*.py`: build, match execution and paired analysis tools.
- `code/rl/`: native simulator, replay dataset, BC/PPO training, C++ policy export and evaluation.
- `code/opponents/`: test opponents with source provenance.
- `experiments/`: reports, summaries, configurations, source snapshots and complete match archives.
- `submissions/`: prepared single-file candidates.
- `sources/`: community research, rule sources and the original referee source archive.
- `docs/`: rules and archive documentation.

## Run

Requirements: Python 3.12+ (measurements used 3.14.6), C++17/clang++, JDK17 and Maven. Lacoz uses pinned NumPy/SciPy packages; use Python 3.14 if those versions are unavailable for another interpreter.

```sh
python3 code/bootstrap.py
python3 -m venv code/arena/.venv-lacoz
code/arena/.venv-lacoz/bin/python -m pip install --only-binary=:all: -r code/arena/requirements-public.txt
# Set JAVA_HOME and, if mvn is not on PATH, TRYANGLE_MAVEN.
python3 code/build_local.py
python3 code/build_public.py
python3 code/benchmark_public.py --source code/bot.cpp --label current --seeds 3001:3005 --out experiments/new-smoke
```

`bootstrap.py` restores the bundled referee sources. Maven may download dependencies during the build. Public-opponent matches run sequentially with the original 1000/50 ms limits. Output directories must be new.

To analyze archived records:

```sh
python3 code/restore_records.py
python3 code/analyze_incremental.py --runs v2=experiments/2026-11-05-incremental/validation/v2 v3=experiments/2026-11-05-incremental/validation/v3 v4=experiments/2026-11-05-incremental/validation/v4 v5=experiments/2026-11-05-incremental/validation/v5 --pairs v2:v3 v3:v4 v3:v5 --out /tmp/validation-comparison.json
```

See [archive contents](docs/ARCHIVE.md). Virtual environments, caches and compiled binaries are excluded from Git. Third-party provenance and licensing limitations are retained; no blanket license is assigned to third-party materials.

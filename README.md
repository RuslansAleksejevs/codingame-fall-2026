# CodinGame Fall Challenge 2026 — TryAngle Catch

A private working repository for a C++17 bot, a reproducible local arena and experiment results.

I work on this project through **Codex**. **Codex created this repository and makes changes to it**, including code, validation tools and documentation.

[Contest](https://www.codingame.com/contests/fall-challenge-2026) · [Rules](docs/RULES.md) · [Latest ATTACK experiment](experiments/2026-11-05-attack/REPORT.md)

## Current baseline

The selected baseline is **v3-multispawn**, using MOVE/SPAWN/WAIT. Prepared candidate: [baseline-v3-multispawn.cpp](submissions/baseline-v3-multispawn.cpp).

Wins against khoufou; each set contains 50 maps played from both seats:

| Variant | Development maps | Separate validation maps |
|---|---:|---:|
| v2 — initial control | 0/100 | 0/100 |
| v3 — multiple SPAWN commands | **8/100** | **13/100** |
| v4 — v3 + triangle reset | 1/100 | 7/100 |
| v5 — v3 + surround protection | 7/100 | 5/100 |

None won against Lacoz under normal game conditions. Technical outcomes caused by timeouts are reported separately. The incremental experiment added 1, 400 matches; 200 control matches were retained from the preceding experiment. These are local measurements, not contest rankings. No contest submission has been made from this repository.

## Latest experiment: ATTACK

[Experimental v6](code/variants/v6-attack.cpp) adds one attack on an enemy stack of at least four, accounting for three consumed friendly units and the spent triangle before movement/spawning.

| Opponent | v3 control | v6 + ATTACK |
|---|---:|---:|
| khoufou | 21/200 | 29/200 |
| Lacoz | 0/200 | 0/200 |

800 new measured games, identical historical maps and both seats, with both versions rerun together. No command errors or timeouts. The observed khoufou gain is +4 percentage points; the paired 95% interval is -0.5 to +8.5 points. **v6 remains experimental; the main bot stays v3.** Both seed sets were previously used, so this is not a fresh holdout. [Full report and reproducible records](experiments/2026-11-05-attack/REPORT.md).

## Layout

- `code/bot.cpp`: main bot; `code/variants/`: isolated strategy variants.
- `code/arena/`, `code/*.py`: build, match execution and paired analysis tools.
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
python3 code/benchmark_public.py --source code/bot.cpp --label current --seeds 3001: 3005 --out experiments/new-smoke
```

`bootstrap.py` restores the bundled referee sources. Maven may download dependencies during the build. Public-opponent matches run sequentially with the original 1000/50 ms limits. Output directories must be new.

To analyze archived records:

```sh
python3 code/restore_records.py
python3 code/analyze_incremental.py --runs v2=experiments/2026-11-05-incremental/validation/v2 v3=experiments/2026-11-05-incremental/validation/v3 v4=experiments/2026-11-05-incremental/validation/v4 v5=experiments/2026-11-05-incremental/validation/v5 --pairs v2:v3 v3:v4 v3:v5 --out /tmp/validation-comparison.json
```

See [archive contents](docs/ARCHIVE.md). Virtual environments, caches and compiled binaries are excluded from Git. Third-party provenance and licensing limitations are retained; no blanket license is assigned to third-party materials.

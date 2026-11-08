# Local setup and inspection

Start with [STATUS](STATUS.md). The default heuristic source is historical; use explicit source/model paths when comparing a learned bot.

## Requirements

- Python 3.12+; recorded runs used 3.14.6.
- C++17/clang++, JDK 17 and Maven.
- A local CPU environment; no hosted GPU or paid inference API is required.

```sh
python3 code/bootstrap.py
python3 -m venv code/arena/.venv-lacoz
code/arena/.venv-lacoz/bin/python -m pip install --only-binary=:all: -r code/arena/requirements-public.txt
python3 code/build_local.py
python3 code/build_public.py
```

Set `JAVA_HOME` or `TRYANGLE_MAVEN` only if needed for the installed tools. Bootstrap/build may download pinned dependencies. Environments and compiled artifacts are not committed.

## Inspect without training or submitting

```sh
python3 code/check_repository.py
python3 code/split_evidence.py verify experiments/rl/2026-11-08-rl5/archive-parts/manifest.json
```

The first command checks tracked-file integrity and documentation links. The second streams the three archive parts and verifies their individual and combined hashes. Neither command contacts CodinGame or changes a bot.

For exact raw-data restoration, see [ARCHIVE](ARCHIVE.md). The RL-v5 archive has repository-relative member paths and must be inspected/restored under those paths; old `records.tar.gz` archives use a different, per-directory layout.

## Run an explicit local comparison

```sh
python3 code/benchmark_public.py --source code/bot.cpp --label historical-v6 --seeds 3001:3005 --out experiments/new-smoke
```

This example tests the **historical v6**, not the current deployed PPO bot. Use a new output directory and inspect an experiment's own protocol before reproducing its learned-policy evaluation. Preserve frozen sources/checkpoints and avoid sharing a timed arena with heavy training.

## Evidence, not automation

Old training commands preserve how an experiment ran. They are not background jobs or a recommended new campaign. No GitHub workflow, scheduler or platform submission is enabled by these setup instructions.
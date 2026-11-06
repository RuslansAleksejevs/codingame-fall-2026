# Public opponents for local evaluation

Only the game source files are copied, separately from the main bot. They are unchanged; Git blob SHA and SHA256 were verified. Each source has an adjacent `PROVENANCE.json` with exact links and hashes.

| Directory | Source | Revision |
|---|---|---|
| lacoz-7f190183 | [Lacoz/cg2026](https://github.com/Lacoz/cg2026) | 7f1901834d2ffc16532e083edfec8cbdb5941ab6, bot.py |
| khoufou-372c1cd6 | [khoufou/Codingame_2026-11_FallChallenge](https://github.com/khoufou/Codingame_2026-11_FallChallenge) | 372c1cd6738d456513cb50705b98549eedfdfad8, Player.java |

These were the two most substantial public solutions found in the research, not verified leaders of the entire contest. No explicit repository license was found. The copies are retained in this private repository for local comparison, not submitted as the project's solution. Imports and I/O paths were reviewed before execution: no network calls, subprocess launches or personal-file reads/writes were found in the bots.

## Environment

- Java: Temurin17.0.21+9; the Java bot is compiled before matches.
- Python3.14.6, NumPy2.5.4, SciPy1.18.1 in `code/arena/.venv-lacoz`. These are local versions, not an exact replica of CodinGame's Python environment.
- OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, VECLIB_MAXIMUM_THREADS=1.
- Original unmodified referee b6913124a10de328316ff42906448a18cb948431, league3, all actions available.
- Original GameManager limits: 1000 ms for the first answer, 50 ms thereafter, verified from core4.1.6 bytecode. Matches run sequentially to reduce load effects.

The first cold Python import after installation exceeded one second and the smoke match timed out at startup. After warming the libraries, import took about 0.30 seconds and a smoke match ended normally. Both are retained under `experiments/2026-11-05-public-bots-smoke/`; this preliminary failure was outside the measured series. `benchmark_public.py` imports libraries before measurement without changing opponent source or game limits.

## Reproduce

From the repository root, with JDK and the original referee built:

```sh
python3 -m venv code/arena/.venv-lacoz
code/arena/.venv-lacoz/bin/python -m pip install --only-binary=:all: -r code/arena/requirements-public.txt
python3 code/build_public.py
python3 code/benchmark_public.py --seeds 1001: 1050 --out experiments/public-repeat
```

Skip environment creation if it already exists. Use a new output directory. Runs preserve source/binary snapshots, commands, versions, errors, all raw records and statistics; binaries are excluded from Git. The default candidate is the frozen baseline-v2 from the first validation, regardless of `code/bot.cpp`. Use `--source path/to/bot.cpp --label name` for another source.

Lacoz's search stops based on elapsed time, so decisions can differ on repeated maps. Opponents are not changed to hide failures; such matches remain in the report as technical outcomes.

# First simple bot: validation result

**40 wins from 40 games** on 20 fresh maps played from both starting seats. No draws or losses. Date: 2026-11-05. Classification: PROJECT_REPORTED. Sources: `summary.json`, `matches.json`, `audit.json` and complete `seed*-seat*.json.gz` records, restored from the adjacent archive.

## Evaluation setup

The project's C++17 v2 bot uses MOVE/SPAWN/WAIT: nearby triangle targets, coordinated movement, exposed-corner guards and active army growth until late game.

The opponent is a C++ adaptation of game author eulerscheZahl's `config/level1/Boss.cs`. C# Random was replaced with mt19937 and debug drawing removed. This is a simple reference opponent, **not an exact copy of the current CodinGame boss**.

The original unmodified TryAngle-Catch referee was used at commit `b6913124a10de328316ff42906448a18cb948431`, league3, with every action available. Both tested bots use only MOVE/SPAWN/WAIT.

Seeds101–120 were not used to choose the v2 change. Each seat won 20/20. These are 20 distinct maps, not 40 independent maps.

## Measurements

| Metric | Result |
|---|---:|
| Wins / draws / losses | 40 / 0 / 0 |
| Validated bot decisions | 3,758 |
| Own command errors | 0 |
| Opponent command errors | 0 |
| Timeouts / engine failures | 0 / 0 |
| Median planning time | 0.303 ms |
| 95th percentile planning time | 0.596 ms |
| Maximum planning time | 2.889 ms |
| Mean captures per game, including recaptures | 57.65 |
| Mean spawned units | 39.675 |

29 games ended early: 16 by domination, 12 because the opponent could no longer score, and one because it lost all units and triangles. The other 11 were score wins after 200 turns. A raw result of -1 means engine elimination, not accumulated game points.

Timing was measured inside the bot on Apple Silicon with two concurrent local games, not on CodinGame's servers. All player and referee messages were audited: only normal game-ending messages, no errors. See `audit.json`.

## Earlier development comparison

| Version | Seeds1–4, both seats | Change |
|---|---:|---|
| v1 | 1/8 wins | Early army cap of 12 |
| v2 | 8/8 wins | Army cap equals the house count before turn 150 |

Only the army growth threshold changed. v2 was frozen before the separate validation above. Development results remain in `2026-11-05-v1-dev` and `2026-11-05-v2-dev`.

## Limits

The bot does not predict enemy moves, attack or alter roads. This opponent also does not test resilience to attacks or road changes. Strong opponents may exploit troop concentrations and weak defenses.

Fall Challenge ranking remains unknown. Before actual submission, verify the contest IDE, protocol, limits and applicable rules. Submission is a separate action. The initial objective was met: legal games, territory capture, reinforcement and scoring. Stronger local opponents or contest-IDE checks are subsequent steps.

## Reproduce

From the repository root, using the frozen v2 source as `code/bot.cpp` for this historical comparison:

```sh
python3 code/build_local.py
python3 code/run_matches.py --seeds 101:120 --out experiments/repeat-v2
```

The current main bot may be newer; do not silently label its results v2. JDK17, Maven and clang++ are required; see `code/README.md`. Versions, commands, SHA256 and parameters are in `manifest.json` and archived `matches.json`. Sources and records are retained; historical binaries are excluded from Git and can be rebuilt. Paid external cost: 0. No contest submission or public release was performed by this experiment.

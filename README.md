# TryAngle Catch — CodinGame Fall Challenge 2026

A private C++17 bot project with a local referee, reinforcement-learning experiments and reproducible evidence.

[Current status](docs/STATUS.md) · [Research results](docs/rl/README.md) · [Run locally](docs/QUICKSTART.md) · [Evidence archive](docs/ARCHIVE.md) · [Contest](https://www.codingame.com/contests/fall-challenge-2026)

## Where things stand

As of **8 November 2026**. The contest deadline recorded from the official API is **9 November, 09:00 UTC**.

| Role | Version | What the evidence says |
|---|---|---|
| Last confirmed deployed bot | **PPO-v3 B2M**, submission `41665776` | The completed 07:10 UTC snapshot was 382/989 overall, in Gold. No live improvement over the preceding league3m snapshot was demonstrated. |
| Preserved local reference | **PPO-v2 league3m** | 139/200 wins against Lacoz on 100 fresh maps; 1,800 clean final games across the panel. |
| Strongest recent research result | **D16 bounded search** | +5.42 percentage points against the external panel, 95% paired interval [+1.25, +9.58], in a 1,120-game independent series. Not a deployable single-file package. |
| Compact student | **RL-v5 Round 2** | Export and timing checks passed, but the 1,680-game strength test failed. Rejected; not submitted. |

**There is no newly validated, deployable replacement.** Local wins are not leaderboard gains. The last live ranking above is a dated snapshot, not the current or final contest rank. Repository integration does not submit, replace or roll back the platform bot.

## Start here

- **Understand the result:** [current status and exact artifact pointers](docs/STATUS.md).
- **Read the latest experiment:** [bounded search and compact-student report](experiments/rl/2026-11-08-rl5/deadline-search/REPORT.md).
- **Review the three earlier approaches:** [exploiters, difficult-start curriculum and search](docs/rl/v4/RESULTS.md).
- **Reproduce or inspect:** [local setup](docs/QUICKSTART.md), [archive reconstruction](docs/ARCHIVE.md), [file checksums](CHECKSUMS.json).
- **Find the submitted source:** [B2M source](experiments/rl/2026-11-07-ppo-v3/handoff-b2m/bot.cpp) and [submission audit](experiments/rl/2026-11-07-ppo-v3/live-submission/REPORT.md).
- **Consider what comes next:** [three last-day options](docs/rl/LAST_DAY_OPTIONS.md) and [research on competitive advantage with AI agents](docs/rl/AI_COMPETITION_EDGE.md). Recommendations only; no new campaign is running.

## Research progression

| Stage | Main outcome | Evidence |
|---|---|---|
| Heuristic v2 → v6 | Multiple spawns and attacks improved the initial baseline. | [Fresh v6 test](experiments/2026-11-06-attack-holdout/REPORT.md) |
| Imitation → PPO-v1 | A small learned policy improved on the imitation baseline. | [PPO-v1](experiments/rl/2026-11-06-ppo-v1/REPORT.md) |
| PPO-v2 league | The selected league3m policy substantially improved the fresh Lacoz comparison. | [PPO-v2](experiments/rl/2026-11-06-ppo-v2/REPORT.md) |
| PPO-v3 | B2M looked stronger locally, but its live ranking snapshot did not establish improvement. The campaign was stopped. | [Live audit](experiments/rl/2026-11-07-ppo-v3/live-submission/REPORT.md) |
| RL-v4: three approaches | No candidate met its predeclared continuation or admission criteria. | [Results](docs/rl/v4/RESULTS.md) |
| RL-v5 | Bounded search passed; the compact student did not retain its advantage. | [Report](experiments/rl/2026-11-08-rl5/deadline-search/REPORT.md) · [Completion](experiments/rl/2026-11-08-rl5/deadline-search/COMPLETION.json) |

Negative results, rejected checkpoints and failed technical checks are retained. Historical reports remain unchanged; this page and [STATUS](docs/STATUS.md) provide the current interpretation.

## Repository map

| Directory | Contents |
|---|---|
| `code/arena/`, `code/rl/sim/` | Original-referee arena, fast simulator and replay verification |
| `code/rl/` | Imitation/PPO training, policy export, evaluation and isolated research |
| `code/variants/`, `code/bot.cpp` | Historical heuristic bots; `code/bot.cpp` is **not** the current submitted B2M |
| `code/opponents/` | Public benchmark opponents with provenance |
| `experiments/` | Protocols, reports, models, manifests and archived raw records |
| `submissions/` | Preserved submission candidates and fallback sources |
| `docs/`, `sources/` | Navigation, implementation notes, primary references and pinned referee source |

The repository stays private. Environments, compiled binaries, credentials and scratch files are excluded. Full raw evidence is archived rather than repeated as thousands of loose files; the latest archive is split into verified GitHub-sized parts. No data was discarded to tidy the project.

I work on this project through **Codex**. **Codex created this repository and makes changes to it**, including code, validation tools and documentation.
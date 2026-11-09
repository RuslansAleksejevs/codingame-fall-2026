# TryAngle Catch — CodinGame Fall Challenge 2026

A private C++17 bot project with a local referee, reinforcement-learning experiments and reproducible evidence.

[Current status](docs/STATUS.md) · [Detailed timeline](docs/EXPERIMENT_TIMELINE.md) · [Research results](docs/rl/README.md) · [Run locally](docs/QUICKSTART.md) · [Evidence archive](docs/ARCHIVE.md) · [Contest](https://www.codingame.com/contests/fall-challenge-2026)

## Where things stand

As of **9 November 2026, 01:50 UTC**. The contest deadline recorded from the official API is **9 November, 09:00 UTC**.

The controlled position-diversity pilot completed800 clean games and failed its
continuation gate: broader data slightly beat narrow data but not unchanged
league3m. Repaired **compact D16 A3 is now submitted once**. Its search passed
the bounded functional checks, but the final ranking is not yet verified:
last saved progress28%, with live refresh temporarily blocked by the execution-
review service. This snapshot does not claim a completed leaderboard result.
[Scope and limits](docs/rl/v7/PLAN.md).

| Role | Version | What the evidence says |
|---|---|---|
| Current submitted bot | **Compact D16 A3**, submission `41672652` | Accepted9Nov01:31UTC, exact source94f0d426… verified. Last saved28%:444/1040,Gold282/428,score12.37; **not final**.18audited logs clean. |
| Immediate previous deployment | **PPO-v2 league3m**, submission `41671805` | Fresh9Nov01:29:34UTC:380/1039,Gold228/428,score14.89,100% ranked. Preserved unchanged. |
| Preserved local reference | **PPO-v2 league3m** | 139/200 wins against Lacoz on 100 fresh maps; 1,800 clean final games across the panel. |
| Strongest recent research result | **D16 bounded search** | +5.42 percentage points against the external panel, 95% paired interval [+1.25, +9.58], in a 1,120-game independent series. Not a deployable single-file package. |
| Compact student | **RL-v5 Round 2** | Export and timing checks passed, but the 1,680-game strength test failed. Rejected; not submitted. |
| Earlier compact search package | **RL-v6 D16, 9-bit** | Fits in94,123UTF16; final stopped656/4200 after one emergency WAIT. No official timeout; deployment rejected, strength inconclusive. Later A3 does not rewrite this failure. |
| New diversity students | **RL-v7 narrow/broad, two seeds** |800 clean fresh-map games: seed-average broad−narrow+1.5625pp [−2.6042,+6.25], broad−base−3.125pp [−7.2917,0]. NO-GO; no final extension or submission. |

**No newly trained, stronger deployable policy was established.** The selected
preserved league3m has now been rechecked live. Rankings above are dated
snapshots, not the final contest result; local wins are not leaderboard gains.

The separately requested leaderboard check is complete: unchanged **league3m**
finished368/1036 versus B2M380/1036 immediately before replacement, score15.11
versus14.59. This small moving-snapshot gain is not a controlled causal estimate.
[Full live report](experiments/rl/2026-11-08-leaderboard-recheck/REPORT.md).
The new [D16 running report](experiments/rl/2026-11-09-d16-live/REPORT.md) keeps
that completed league3m check separate from the currently incomplete A3 ranking.
Repository publication is a separate preservation operation, not a new experiment.

## Start here

- **Understand the result:** [current status and exact artifact pointers](docs/STATUS.md).
- **Follow every stage:** [detailed experiment timeline](docs/EXPERIMENT_TIMELINE.md), including rejected variants, fresh versus reused maps and live submissions.
- **Read the latest experiments:** [D16 A3 delivery](experiments/rl/2026-11-09-rl7/d16/A3_REPORT.md), [running platform audit](experiments/rl/2026-11-09-d16-live/REPORT.md), and [diversity pilot](experiments/rl/2026-11-09-rl7/diversity/REPORT.md).
- **Review the three earlier approaches:** [exploiters, difficult-start curriculum and search](docs/rl/v4/RESULTS.md).
- **Reproduce or inspect:** [local setup](docs/QUICKSTART.md), [archive reconstruction](docs/ARCHIVE.md), [file checksums](CHECKSUMS.json).
- **Find the submitted source:** [D16 A3](experiments/rl/2026-11-09-rl7/d16/package-attempt3/bot.cpp). Previous [league3m](submissions/ppo-v2-league3m.cpp) and [B2M](experiments/rl/2026-11-07-ppo-v3/live-submission/REPORT.md) remain preserved.
- **Follow the new work:** [bounded D16 delivery and diversity pilot](docs/rl/v7/PLAN.md). Earlier [last-day options](docs/rl/LAST_DAY_OPTIONS.md) and [AI competition review](docs/rl/AI_COMPETITION_EDGE.md) remain dated recommendations.
- **Read the new pilot result:** [diversity report](experiments/rl/2026-11-09-rl7/diversity/REPORT.md) and [independent800-game audit](experiments/rl/2026-11-09-rl7/coordinator/pilot-audit.json).

## Research progression

| Stage | Main outcome | Evidence |
|---|---|---|
| Heuristic v2 → v6 | Multiple spawns and attacks improved the initial baseline. | [Fresh v6 test](experiments/2026-11-06-attack-holdout/REPORT.md) |
| Imitation → PPO-v1 | A small learned policy improved on the imitation baseline. | [PPO-v1](experiments/rl/2026-11-06-ppo-v1/REPORT.md) |
| PPO-v2 league | The selected league3m policy substantially improved the fresh Lacoz comparison. | [PPO-v2](experiments/rl/2026-11-06-ppo-v2/REPORT.md) |
| PPO-v3 | B2M looked stronger locally, but its live ranking snapshot did not establish improvement. The campaign was stopped. | [Live audit](experiments/rl/2026-11-07-ppo-v3/live-submission/REPORT.md) |
| RL-v4: three approaches | No candidate met its predeclared continuation or admission criteria. | [Results](docs/rl/v4/RESULTS.md) |
| RL-v5 | Bounded search passed; the compact student did not retain its advantage. | [Report](experiments/rl/2026-11-08-rl5/deadline-search/REPORT.md) · [Completion](experiments/rl/2026-11-08-rl5/deadline-search/COMPLETION.json) |
| RL-v6 | Full D16 was compactly packaged, but one emergency fallback stopped the independent final. | [Report](experiments/rl/2026-11-08-rl6/compact-d16/REPORT.md) · [Completion](experiments/rl/2026-11-08-rl6/compact-d16/COMPLETION.json) |
| Requested live recheck | Unchanged league3m:368/1036 after100% ranking;92 clean battles. No further research. | [Report](experiments/rl/2026-11-08-leaderboard-recheck/REPORT.md) |
| RL-v7 D16 delivery | A1/A2 failures retained; A3 passes contracts,96-game gross guard and3fixed official checks. One submission accepted; final ranking unverified. | [A3](experiments/rl/2026-11-09-rl7/d16/A3_REPORT.md) · [Platform](experiments/rl/2026-11-09-d16-live/REPORT.md) |
| RL-v7 diversity pilot | Four matched students,800clean strength games. Broader data did not improve unchanged league3m; NO-GO. | [Exact tables and report](experiments/rl/2026-11-09-rl7/diversity/REPORT.md) |

Negative results, rejected checkpoints and failed technical checks are retained. Historical reports remain unchanged; this page and [STATUS](docs/STATUS.md) provide the current interpretation.

## Repository map

| Directory | Contents |
|---|---|
| `code/arena/`, `code/rl/sim/` | Original-referee arena, fast simulator and replay verification |
| `code/rl/` | Imitation/PPO training, policy export, evaluation and isolated research |
| `code/variants/`, `code/bot.cpp` | Historical heuristic bots; `code/bot.cpp` is **not** the current submitted D16 |
| `code/opponents/` | Public benchmark opponents with provenance |
| `experiments/` | Protocols, reports, models, manifests and archived raw records |
| `submissions/` | Preserved submission candidates and fallback sources |
| `docs/`, `sources/` | Navigation, implementation notes, primary references and pinned referee source |

The repository stays private. Environments, compiled binaries, credentials and scratch files are excluded. Full raw evidence is archived rather than repeated as thousands of loose files; the latest archive is split into verified GitHub-sized parts. No data was discarded to tidy the project.

I work on this project through **Codex**. **Codex created this repository and makes changes to it**, including code, validation tools and documentation.
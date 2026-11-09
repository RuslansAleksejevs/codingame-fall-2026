# TryAngle Catch — CodinGame Fall Challenge 2026

A private C++17 bot project with a local referee, reinforcement-learning experiments and reproducible evidence.

[Current status](docs/STATUS.md) · [Bot portfolio](docs/BOT_PORTFOLIO.md) · [Delivery rules](docs/CONTEST_DELIVERY.md) · [Detailed timeline](docs/EXPERIMENT_TIMELINE.md) · [Run locally](docs/QUICKSTART.md) · [Evidence archive](docs/ARCHIVE.md)

## Where things stand

Final choice9November06:15UTC: **D16 A3 selected; final replacement awaits a new
official login and has NOT yet been sent**. league3m remains the last verified
active entry. GitHub freshly confirmed PRIVATE; completed evaluation evidence
is included in this checked repository refresh. [Final-delivery status](experiments/rl/2026-11-09-final-delivery/REPORT.md).

Authenticated leaderboard checked **9 November 2026, 05:59 UTC**. Official contest
deadline: **9 November, 09:00 UTC**; this is not the final contest standings.

**D16 A3 evaluation is complete:371/1042,Gold207/422,score15.77**,100%,
`in_progress=false`. All98snapshot logs are audited:55wins/43losses, no official
technical errors or emergency WAIT. A separate parser correction verifies all
3209telemetry records without changing the bot or old evidence.
**Fresh league3m41673756 completed433/1042,Gold269/422,score13.37**;93logs49W44L,
zero own errors,one opponent timeout. **D16 A3 is now the explicitly selected
final candidate; actual active bot remains league3m pending delivery.**
[Completed comparison](experiments/rl/2026-11-09-final-choice/REPORT.md).

The controlled position-diversity pilot completed800 clean games but did not
improve unchanged league3m. All four students remain rejected. No new training,
source change or student submission was made during this assessment.
The earlier status-reporting mistake and its
[dated correction](experiments/rl/2026-11-09-d16-live/ERRATUM_2026-11-09.md) remain preserved.

| Role | Version | What the evidence says |
|---|---|---|
| Current submitted control | **PPO-v2 league3m**, submission `41673756` | Completed433/1042,Gold269/422,13.37;93logs49W44L,0ownerrors/1opponenttimeout. Remains active, not the recommended final choice. |
| Immediately previous deployment | **Compact D16 A3**, submission `41672652` | Full audit371/1042,Gold207/422,15.77;98logs55W43L,zero official errors. Separate immediately-before read370/1042. |
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
The [D16 report](experiments/rl/2026-11-09-d16-live/REPORT.md) now closes its full
98-game audit. The later [final-choice assessment](experiments/rl/2026-11-09-final-choice/REPORT.md)
is separate; its evidence and navigation updates are included in this private refresh.
Repository publication is a separate preservation operation, not a new experiment.

## Start here

- **Understand the result:** [current status and exact artifact pointers](docs/STATUS.md).
- **Follow every stage:** [detailed experiment timeline](docs/EXPERIMENT_TIMELINE.md), including rejected variants, fresh versus reused maps and live submissions.
- **Read the latest experiments:** [D16 A3 delivery](experiments/rl/2026-11-09-rl7/d16/A3_REPORT.md), [platform ranking and audit coverage](experiments/rl/2026-11-09-d16-live/REPORT.md), and [diversity pilot](experiments/rl/2026-11-09-rl7/diversity/REPORT.md).
- **Prepare the final entry:** [one active bot, deadline, deliverables and rules caveats](docs/CONTEST_DELIVERY.md).
- **Review the three earlier approaches:** [exploiters, difficult-start curriculum and search](docs/rl/v4/RESULTS.md).
- **Reproduce or inspect:** [local setup](docs/QUICKSTART.md), [archive reconstruction](docs/ARCHIVE.md), [file checksums](CHECKSUMS.json).
- **Find the submitted source:** current [league3m](submissions/ppo-v2-league3m.cpp); preceding [D16 A3](experiments/rl/2026-11-09-rl7/d16/package-attempt3/bot.cpp) and [B2M](experiments/rl/2026-11-07-ppo-v3/live-submission/REPORT.md) remain preserved.
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
| RL-v7 D16 delivery | A1/A2 failures retained; A3 passes bounded checks. One submission, full-audit rank371/1042;98logs55W43L,zero official errors. | [A3](experiments/rl/2026-11-09-rl7/d16/A3_REPORT.md) · [Platform](experiments/rl/2026-11-09-d16-live/REPORT.md) |
| Final-choice control | league3m41673756 completed433/1042,13.37,93fully audited logs. Recommend preserved D16; no automatic final switch. | [Comparison](experiments/rl/2026-11-09-final-choice/REPORT.md) |
| RL-v7 diversity pilot | Four matched students,800clean strength games. Broader data did not improve unchanged league3m; NO-GO. | [Exact tables and report](experiments/rl/2026-11-09-rl7/diversity/REPORT.md) |

Negative results, rejected checkpoints and failed technical checks are retained. Historical reports remain unchanged; this page and [STATUS](docs/STATUS.md) provide the current interpretation.

## Repository map

| Directory | Contents |
|---|---|
| `code/arena/`, `code/rl/sim/` | Original-referee arena, fast simulator and replay verification |
| `code/rl/` | Imitation/PPO training, policy export, evaluation and isolated research |
| `code/variants/`, `code/bot.cpp` | Historical heuristic bots; `code/bot.cpp` is **not** the current submitted source |
| `code/opponents/` | Public benchmark opponents with provenance |
| `experiments/` | Protocols, reports, models, manifests and archived raw records |
| `submissions/` | Preserved submission candidates and fallback sources |
| `docs/`, `sources/` | Navigation, implementation notes, primary references and pinned referee source |

The repository stays private. Environments, compiled binaries, credentials and scratch files are excluded. Full raw evidence is archived rather than repeated as thousands of loose files; the latest archive is split into verified GitHub-sized parts. No data was discarded to tidy the project.647untracked suffix copies were moved, without deletion, to a local ignored recovery directory; see [workspace preservation](docs/WORKSPACE_HYGIENE.md).

I work on this project through **Codex**. **Codex created this repository and makes changes to it**, including code, validation tools and documentation.
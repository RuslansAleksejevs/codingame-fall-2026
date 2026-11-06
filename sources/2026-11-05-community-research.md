# TryAngle Catch / Fall Challenge 2026: discussions and public solutions

as_of: 2026-11-05. Historical research note, preceding the public-opponent benchmark.

**Finding:** CodinGame has a Kaggle-like discussion channel through its forum, Feedback & Strategies threads and post-mortems. For this game, the richest material found was two recent participant repositories containing code and experiment logs. No large current strategy discussion was found on the forum.

SOURCE_VERIFIED means the cited primary source was read; upstream rankings and wins remain author-reported. PROJECT_REPORTED identifies local analysis. HYPOTHESIS identifies proposed experiments. Public bots had not yet been run at this research stage, so their reported results were not independent replications.

## Discussion channels

| Source | Observed contents | Relevance |
|---|---|---|
| [Spring2026 Feedback & Strategies](https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241) | Algorithms, failures, tests, simple heuristics, search and learning | Demonstrates solution sharing for another game |
| [Winter2026 Feedbacks and Strategies](https://forum.codingame.com/t/winter-challenge-2026-feedbacks-and-strategies/208044) | Beam search, MCTS, opponent models, learning and parameter tuning | General experience, not a ready TryAngle strategy |
| [TryAngle Catch thread](https://forum.codingame.com/t/community-puzzle-tryangle-catch/189038) | Five public posts, 2021–2022: ending with one unit and an unanswered request for ideas | Little strategy detail |
| [AI Rules](https://forum.codingame.com/t/fall-challenge-2026-ai-rules/208706) | Two posts on November 2: a question about AI and a participant's affirmative answer | Not a substitute for the full official rules |
| [League/statement mismatch](https://forum.codingame.com/t/fall-challenge-2026-no-wood-league-and-missing-input/208705) | Two posts on November 2–3 about league names/commands differing from IDE behavior | Do not infer action availability solely from league names |
| [Games not running](https://forum.codingame.com/t/fall-challenge-2026-games-not-running/208708) | Four posts on November 3, including a paraphrase of a team response in Discord | Evidence of Discord discussion, not service status on November 5 |
| [Official Discord invite](https://discord.com/invite/qAKXEEv) | Link verified through the official contest menu | Discord channels/history were not read |

Each linked source was read; SOURCE_VERIFIED, 2026-11-05. Short threads were retrieved through public Discourse JSON because search indexing was weak. Exact forum search for “fall challenge 2026” returned the three current threads above. This is a dated search result, not proof that no other publications exist.

Code sharing exists but differs from an open notebook catalog. The Spring2026 game author asks for approaches without large code dumps because the game remains on the permanent arena. A [historical TwoSteps answer dated2017-02-09](https://forum.codingame.com/t/cg-stance-regarding-code-sharing-alts/2564/24) says publishing code is not prohibited. Neither an old reply nor one thread's request establishes the complete Fall2026 rules.

## Main public bot repositories

### Lacoz/cg2026

[Repository](https://github.com/Lacoz/cg2026), examined commit `7f1901834d2ffc16532e083edfec8cbdb5941ab6`. Created November 3; latest observed push November 5.

The [Python bot](https://github.com/Lacoz/cg2026/blob/7f1901834d2ffc16532e083edfec8cbdb5941ab6/bot.py) considers individual units and improves a joint movement plan through local search. Shared corners are counted once; assignments can minimize total distance. It coordinates clearing spent triangles, estimates surrounding/attack threats, issues multiple SPAWN commands and sometimes delays spawning to preserve a critical shared corner. These observations come from code, not README alone (SOURCE_VERIFIED).

The [README](https://github.com/Lacoz/cg2026/blob/7f1901834d2ffc16532e083edfec8cbdb5941ab6/README.md) records specific losses, variant comparisons and failed ideas. A key lesson is that stronger self-play performance need not improve results against real opponents. The log discusses army growth, vulnerable stacks and faulty threat estimates. Its results were not independently reproduced at this stage.

The latest [ranking.csv](https://github.com/Lacoz/cg2026/blob/7f1901834d2ffc16532e083edfec8cbdb5941ab6/ranking.csv) entry was2026-11-05 10:10 UTC: Gold 252/356, overall 252/788. This is an author's saved record, not a live leaderboard check. The README title still said Silver despite a later Gold section.

**Caution:** README combines several historical versions. Its earlier claim that SPAWN requires troops at every corner is false for the checked original referee. Current source and authoritative mechanics are more reliable than treating the whole diary as current instructions.

### khoufou/Codingame_2026-11_FallChallenge

[Repository](https://github.com/khoufou/Codingame_2026-11_FallChallenge), commit `372c1cd6738d456513cb50705b98549eedfdfad8`. Created November 4; latest observed push November 5.

[Player.java](https://github.com/khoufou/Codingame_2026-11_FallChallenge/blob/372c1cd6738d456513cb50705b98549eedfdfad8/Player.java) has explicit stages: profitable attacks, spending doomed triangles, surrounding, capture, clearing spent triangles, free-troop movement and reinforcement. Targets prioritize arrival time. Already assigned troops on shared corners reduce other targets' demand. Relative army strength changes expansion priority. Normal growth is capped at six SPAWN commands per turn, with exceptions for immediate gains (SOURCE_VERIFIED).

The [arena README](https://github.com/khoufou/Codingame_2026-11_FallChallenge/blob/372c1cd6738d456513cb50705b98549eedfdfad8/tools/arena/README.md) includes older bots, Java boss translations and test tables. It reports roughly73–77% against its own boss3 across different300-game sets. The author explicitly notes that the custom engine was not checked game-by-game against the original and boss randomness differs from C#. These are upstream local claims, not replicated results or verified contest positions.

The same log reports regressions from early unconditional aggression and some road-addition variants. A reasonable hypothesis is to test economy and allocation first, and road changes separately rather than assuming they help.

## Referees and tooling

| Repository | Verified contents | Potential use |
|---|---|---|
| [eulerscheZahl/TryAngle-Catch](https://github.com/eulerscheZahl/TryAngle-Catch/tree/b6913124a10de328316ff42906448a18cb948431) | Original referee, statement, C# bosses | Existing local reference; stronger bosses than adapted level1 |
| [adamadair/TryAngle-Catch-Brutal](https://github.com/adamadair/TryAngle-Catch-Brutal/tree/04dd154e604888ef85e5db4f466de60fef9a1605) | Original-engine fork with CLI, standalone JAR, random Go bot and testing notes | Ready local-match wrapper |
| [adamadair/cgarena](https://github.com/adamadair/cgarena) | Go arena, seat swaps, reproducible maps, logs, error/loss separation and win intervals | Possible replacement launcher for larger experiments |
| [mlomb/battle](https://github.com/mlomb/battle/tree/1d379275aac436249c62d9b9c5ed12b51fae50d8) | Build/tournament tools, reference JAR, C++ TryAngle port and referee comparison | Possible faster large-scale evaluation |

SOURCE_VERIFIED for README, trees and key sources. New tools were not installed or run in this research.

adamadair documents a seed-argument mismatch: its fork expects `-seed`, while cg-brutaltester sends `-d seed=...`. In that combination, seat-swapped matches may not share a map. This is a specific reported integration issue, not a claim about every BrutalTester setup. LocalMatch sets seeds directly with `setSeed`, so it does not use that argument path.

The [mlomb C++ referee](https://github.com/mlomb/battle/blob/1d379275aac436249c62d9b9c5ed12b51fae50d8/crates/battle/assets/cg-cpp/cg-2026-fall-tryangle-catch.cpp) claims to preserve Java map generation and some quirks. The project's table marks it validated, but equivalence was not checked here. It depends on shared project libraries, not a standalone file.

## Excluded findings

- [waimanwong/FallChallenge2026](https://github.com/waimanwong/FallChallenge2026), tree6566161ff6d0da0c21124c9f23268a9aed2b929e: only .gitignore, no bot.
- [Pingwi85/Fall_challenge_2026](https://github.com/Pingwi85/Fall_challenge_2026): search reported size0; no substantial solution established.
- [Riduidel/codingame](https://github.com/Riduidel/codingame/tree/a77a2461f0416c266e31a9c33e5becd45d44cd7d/multiplayer/fall-challenge-2026): input models and Java scaffold, with move-selection logic commented out in the examined Playfield.
- [Zweer/codingame](https://github.com/Zweer/codingame/tree/3d955ea0fb3ecbdb5d95de0c4016acce5c761c52/src/06-multi/tryangle-catch): only a statement README in the game directory despite a completion mark in the global list.
- [abhijeet1999/TryAngle-Catch](https://github.com/abhijeet1999/TryAngle-Catch): HEAD matched original b691312; no new strategy found.

## Cross-check against original mechanics

SOURCE_VERIFIED: [SpawnTask.java](https://github.com/eulerscheZahl/TryAngle-Catch/blob/b6913124a10de328316ff42906448a18cb948431/src/main/java/engine/task/SpawnTask.java), [Triangle.java](https://github.com/eulerscheZahl/TryAngle-Catch/blob/b6913124a10de328316ff42906448a18cb948431/src/main/java/engine/Triangle.java), [level3 Boss.cs](https://github.com/eulerscheZahl/TryAngle-Catch/blob/b6913124a10de328316ff42906448a18cb948431/config/level3/Boss.cs).

1. SPAWN uses `canUse(player, 0)`: no troops are required at the corners. Ownership and an unspent triangle are required; attacks/roads have a different cost.
2. Multiple SPAWN commands are legal. The single-SPAWN limit belonged to the early baseline.
3. Reuse requires all corners to become free of friendly units or an intervening enemy capture. Cycle length depends on the map and actions; it is not universally exactly three turns.
4. The original senior boss evaluates joint movement plans with up to 10,000 random modifications, multiple SPAWN, ATTACK and ADD_PATH. It is substantially more complex than the adapted level1 opponent.

The initial opponent's exact source is `config/level1/Boss.cs`. The historical filename `wood1_port.cpp` does not establish the current league name; khoufou calls original level1 Wood2. “Adapted level1” is the precise comparison label. This naming correction does not change the40/40 result or its records.

## Testable hypotheses at this research stage

| Priority | Baseline limitation | Experiment |
|---|---|---|
| 0 | All40 wins came against one weak opponent | Add original level2/3 and the public Java bot; retain original Java referee as control |
| 1 | At most one SPAWN; army cap equals house count | Multiple reinforcements according to resources, targets and enemy army |
| 2 | meCanCapture=0 targets ignored; no coordinated clearing | Clear all spent-triangle corners and return later |
| 3 | Separate targets reserve separate troops | Share sufficient troops across neighboring target corners |
| 4 | Mostly stationary enemy assumptions, no ATTACK | Evaluate one-step final positions, vulnerable stacks and surrounding threats |

Test one feature at a time on matched maps and both seats, then use new validation maps. Alongside wins, measure captures/spawns per turn, triangle reuse and causes of death. Deeper search and road changes can follow if measurements justify them.

## Scope limitations

Methods: web search, direct forum search, GitHub name/code search, tree/README/key-function inspection and original-referee cross-checks. Query/version records remain in the local project research archive; they were not included in this repository export.

Searchable public repositories do not establish exhaustive coverage. Private repositories and Discord history were not inspected. GitHub metadata did not identify a license for the two main bot repositories; public readability does not itself establish unrestricted republication rights.

At this research stage the baseline and prepared candidate were unchanged. No new matches, submissions, participant messages or paid computations had been performed.

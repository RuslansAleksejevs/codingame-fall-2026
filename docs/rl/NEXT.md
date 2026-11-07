# RL after the first Gold deployment

As of **2026-11-07**. Status: **research and replay diagnosis only**. No new policy was trained, evaluated in new games or submitted. Proposed gains and budgets below are hypotheses, not measured improvements.

The strongest next experiment is **search-generated training targets for complete plans**, with emphasis on early development. A separate **league of deliberate exploiters** is the best compatible follow-up. A graph policy with coordinated objectives has a higher implementation cost and should follow evidence from those smaller experiments.

## Evidence that changes the priorities

[Replay diagnosis](../../experiments/rl/2026-11-07-next-directions/REPORT.md) reconstructs all 92 archived Gold games: 52 wins and 40 losses. Final scores agree in all games; 2,714 own pre-action army/income observations agree. These are existing platform games, not a fresh benchmark.

| Observation | Won games | Lost games |
|---|---:|---:|
| Behind in army after 5 completed turns | 22/52 | 32/40 |
| Behind in army after 10 completed turns | 17/52 | 38/40 |
| Median army gap after 10 turns | +1 | -7 |
| Median game length | 28.5 turns | 28 turns |

All 92 games were still running at the 10-turn observation. Later comparisons have survivor bias. Early economic disadvantage is a strong diagnostic association, not proof that spawning or the opening alone caused defeat. Poor captures, wasteful movement and early enemy tactics can all produce that pattern.

Enemy road commands occur in only **two of the 40 losses**; one opponent used both adding and removing. This weakens the case for making road tactics the first intervention. It does not establish that roads are strategically unimportant. The previous road-feature arm also failed to win selection. There were no own platform technical failures in this final Gold panel.

Code inspection gives three separate hypotheses:

- `models/policy.hpp` constructs a turn in fixed triangle order, then numeric house order, one unit at a time. Pending unit reservations already provide some coordination, but exploring a coordinated capture/reset can require several individually unattractive choices.
- The actor receives local summaries and handcrafted distance/capture features, not a learned encoding of the complete graph. The training critic pools node statistics; it does not preserve the full arrangement of their connections.
- The league contains self-play, related historical policies, old BC/PPO anchors and 12.5% Lacoz games. It has no separately trained exploiters or adaptive payoff matrix. Strong local results against that pool do not establish broad Gold strength.

The complete-turn PPO objective is mathematically valid. Its product of conditional probabilities may make updates sensitive to plan length, but that is **not an established bug**. Among the final 100 updates through league3m, median clip fraction was 0.24237, explained variance 0.81707 and final rollout KL 0.00731; none of the first 947 updates triggered the KL early-stop rule. These aggregate diagnostics do not identify a broken optimizer or measure out-of-distribution value quality.

## 1. Search teacher, compact student

**Plain version:** spend extra time finding better combinations during training, then teach the fast competition bot those combinations.

[Expert Iteration](https://arxiv.org/abs/1705.08439) alternates planning and learning from the planner. [Sampled MuZero](https://proceedings.mlr.press/v139/hubert21a.html) provides a framework for policy improvement over sampled subsets of a large action space. [Gumbel planning](https://openreview.net/pdf?id=bERaNdoegnO) specifically studies improvement with small simulation budgets. Their reported results are from other domains; none guarantees an improvement in this contest.

The proposed adaptation uses the **existing exact simulator**, rather than learning game mechanics:

1. Keep the current greedy plan and sample 8–16 distinct legal full-turn alternatives. Add diversity by regenerating suffixes or changing a coherent capture/defence objective, rather than independently shaking every unit. Deduplicate plans by resulting orders, accounting for command-order semantics.
2. Test each plan against 4–8 opponent plans drawn before seeing the chosen friendly plan. Both players act from the same state. Evaluate a small simultaneous-action payoff matrix; start with expected value against a frozen diverse mixture, then compare a regularized robust mixture as its own ablation. Ordinary alternating-move minimax would give the opponent information it does not have.
3. Use short joint rollouts and a separately validated outcome-value model. Initially check value ordering against longer rollouts. The existing critic is a useful initialization, not a trusted search oracle. A cached opponent first plan is valid; its future actions must be recomputed after every changed state.
4. Train the student on a soft distribution over improved complete plans, decomposed into the same legal conditional choices. Mix in current-policy examples and a small anchoring loss to reduce catastrophic drift. Generate new examples from the evolving student to reduce imitation distribution shift.
5. Concentrate a development subset on turns 0–10, but retain normal full-game positions and terminal win/loss as the outcome criterion. More troops alone is not the objective.

The expensive teacher runs **offline**. The first deployed student can keep the existing 24,833-parameter actor and decoder, avoiding additional inference cost. A small runtime search is a later, separate option. Current real-game maximum plan time was 18.926 ms in paired executed turns; platform timing varies, so this does not authorize multiplying inference work blindly under the 50 ms limit.

**Go/no-go:** the teacher must beat the unchanged actor on fresh development maps before a large dataset is generated. Then the distilled student must retain the gain. If better plans cannot be represented by the existing decoder, measure that gap before enlarging the actor.

**Estimated local budget:** a 30–60 minute throughput/value-quality pilot; 4–12 hours of search-data generation and training for the first substantive run. Implementation and competitive evaluation are additional. Profile actual plan generation, not just raw simulator steps: neural inference and candidate construction can dominate.

## 2. Train opponents specifically to expose weaknesses

**Plain version:** build two sparring bots whose job is to beat the champion, then train the champion against the weaknesses they discover.

The current historical pool is not this procedure. [PSRO](https://arxiv.org/abs/1711.00832) trains responses to mixtures of policies and uses empirical game results to choose mixtures. [AlphaStar's league](https://deepmind.google/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/) supplies a large-scale example of deliberately diverse adversaries. Only the training principle transfers; AlphaStar's compute budget does not.

Freeze league3m. Train two independently seeded exploiters, one initialized from an earlier policy to reduce shared blind spots. First target the champion, then a mixture containing it and public opponents. Their reward is winning, not a handcrafted preference for attacks or roads. Admit only exploiters with a reproducible advantage on unseen development maps. Maintain a small 6–8-policy payoff table; retain public anchors and a floor on sampling probabilities so old weaknesses are not forgotten.

Train a new champion on that mixture. Test against held-out policies, both public opponents and the old champion. Beating one exploiter does not prove overall progress. Closed-source Gold players cannot be recreated from a few replays; learned imitators would be approximations and must be labeled that way.

**Estimated local budget:** 6–12 hours for two small exploiters and a champion continuation, plus evaluation. The measured reference is 132.39 minutes for 3.002M decisions in the previous league recipe; changing episode lengths, mixtures and simultaneous CPU workloads changes throughput.

## 3. Curriculum from the beginnings of lost games

**Plain version:** repeatedly practise the difficult situations before a collapse, instead of replaying long already-lost endings.

This is an adaptation of reset-based exploration and start-state curricula, not a literal implementation of [Go-Explore](https://arxiv.org/abs/2004.12919) or [reverse curriculum learning](https://arxiv.org/abs/1707.05300). Use those ideas to construct a small training curriculum with the exact simulator.

Start with positions from turns 2–8 of diagnosed losses and comparable fresh self-play positions. Restore the **complete state**, including turn, scores, triangle capture flags and topology. A map reconstructed from unit positions alone is insufficient. Continue against live policy opponents, not a fixed replay of their future commands, because changed positions invalidate those commands.

Mix at most 10–20% curriculum starts with ordinary games initially. Keep only positions with evidence that recovery is possible; move starts earlier if all policies always lose. Include successful positions and diverse map content to avoid teaching one narrow defensive style. The 92 Gold games become development material permanently; final evaluation must use new complete games from their real starting states.

**Estimated local budget:** 2–6 hours for a controlled continuation after state restoration is implemented and checked. This is a relatively small intervention, but recovery skills may not improve opening decisions. Test it separately from the search teacher and league changes.

## 4. Graph policy and coordinated objectives

**Plain version:** let the network understand how the houses form triangles, and choose a group objective before assigning individual troops.

[Graph networks](https://arxiv.org/abs/1806.01261) provide an appropriate structural model. The proposed contest architecture has house nodes, road edges and triangle factor nodes, with shared message-passing weights and a global summary. Encode the graph once per real turn; update lightweight resource features while constructing the plan.

First replace only the representation, preserving primitive actions and the PPO recipe. If that improves results, separately add objectives such as capture a specific triangle, empty its corners to reset it, or defend a vulnerable group. The assignment stage still respects troop and triangle budgets, and primitive actions remain available. This is a proposed architecture, not a demonstrated improvement or a claim that the current policy has no coordination.

The deployed source is already **80,247 UTF-16 units** with 24,833 float32 actor parameters. A casually proposed 100k–500k-parameter exported network does not fit the existing 100k-character packaging budget. Use a compact weight-tied graph actor, or validate quantization/distillation; a larger training-only critic has no submission-size cost. Benchmark inference and memory before a long run.

**Estimated budget:** 1–2 days of implementation/validation, then 8–24 hours of local training for an informative first comparison. Highest engineering risk among the four. It should not be treated as the default last-minute contest change.

## Cheap control and a more experimental reserve

**Average nearby checkpoints.** Before a large training campaign, compare the current policy with averages of compatible, nearby checkpoints from the same training trajectory. [SWA](https://arxiv.org/abs/1803.05407) motivates weight averaging, but its original results are supervised learning. The [third-place Summer Challenge 2026 report](https://github.com/Pduhard/back-track-king-postmortem) also reports useful checkpoint averaging, distillation and two-turn search. These are author-reported results in another game. Our sparse milestone exports are not automatically suitable neighbours; inspect the checkpoint history or save denser snapshots in a short continuation. Do not average independently permuted networks or different feature styles. Constructing an average is cheap; an adequate match panel is the main cost. No gain has been measured here.

**Credit for partial plans.** Treat construction of a turn as an internal decision process, with a critic for each legal prefix. Internal choices use discount 1; real time advances only when the full turn is committed. [COMA](https://arxiv.org/abs/1705.08926) motivates counterfactual credit, but our centralized autoregressive policy is not COMA's independent multi-agent setting. Changing an early action requires regenerating the dependent suffix; holding it fixed can violate resources and bias comparisons. First measure clipping and advantage variance by plan length. This is a reserve experiment, not an asserted fix for PPO.

## Proposed order and acceptance criteria

1. Cheap averaging control where compatible snapshots exist; no deployment by assumption.
2. Search-teacher pilot, then teacher-versus-actor and student-versus-actor panels.
3. Exploiter league as a separate branch of the experiment, then combine only confirmed improvements.
4. Curriculum and graph architecture according to the remaining failure evidence and time.

For each intervention, compare on identical **new maps from both seats** against frozen league3m, Lacoz and khoufou; retain v6/BC regression checks. Prefer 100 development maps, followed by a frozen 200-map confirmation for the selected finalist, subject to measured arena throughput. Report per-opponent paired, map-clustered intervals, not just a pooled win rate. Predeclare the acceptance rule: positive paired gain against the old champion, no material public-opponent regression, and no own technical failures. Verify deployment compatibility before any separately authorized submission. Two training seeds for finalists would distinguish algorithmic benefit from a lucky run if time permits.

All proposed compute is local to the measured M4 Air with 24 GB RAM. The hour ranges are planning estimates, not measured runtimes or promises. Start serially, measure sustained throughput and memory, and keep training stopped during timed arena tests. This research/replay work used no paid compute; subscription usage was not measured.

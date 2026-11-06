# RL research branch

As of **2026-11-06**. Status: **native simulator, BC and bounded PPO self-play implemented and trained locally**. See the [BC experiment](../../experiments/rl/2026-11-06-bc-v1/REPORT.md), [PPO experiment](../../experiments/rl/2026-11-06-ppo-v1/REPORT.md), [BC guide](IMPLEMENTATION.md) and [PPO guide](PPO.md). Learned search and Q-learning remain future stages.

The recommended first route is **imitation of strong opponents, followed by small-scale PPO self-play**. A learned value function can then support short lookahead. A separate **BTR-inspired Q-learning experiment over complete turn plans** is the most interesting alternative.

The measured machine is an **Apple M4 MacBook Air, 24 GB unified memory, 10 CPU cores and 10 GPU cores**. BC v1 uses a smaller **24,833-parameter** candidate-scoring MLP as the initial control. BC runs locally on Metal/MPS; the measured PPO workload is faster on CPU. External compute spend is zero. The earlier 100,000–500,000-parameter graph encoder remains a proposal.

- [Research and primary sources](RESEARCH.md): actual competition winners, relevant counterexamples, public implementations and transfer limits.
- [Implementation and evaluation plan](PLAN.md): stages, directory layout, acceptance gates and isolated comparisons.
- [Resources](RESOURCES.md): original conditional estimates and a link to the measured BC run, plus the coding-model workflow.
- [Source register](../../sources/2026-11-06-rl-research.json): evidence classes, access notes and repository revisions.

`rl/research` starts at main commit `601a00eea536e305d9b77ea44d813228eb7d148d`. The selected main-branch bot remains **v6-attack**. BC and PPO are separate research candidates; neither has been submitted to the live contest. Each checkpoint is frozen before evaluation against Lacoz, khoufou and v6 under the original referee.

All recommendations are hypotheses for TryAngle Catch. Results reported by other authors are not local replications or predictions of a contest rank.

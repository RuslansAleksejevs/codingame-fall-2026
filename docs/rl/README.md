# RL research branch

As of **2026-11-06**. Status: **native simulator and first behavior-cloning policy implemented and trained locally**. See the [measured experiment](../../experiments/rl/2026-11-06-bc-v1/REPORT.md) and [reproduction guide](IMPLEMENTATION.md). PPO, value learning and search remain future stages.

The recommended first route is **imitation of strong opponents, followed by small-scale PPO self-play**. A learned value function can then support short lookahead. A separate **BTR-inspired Q-learning experiment over complete turn plans** is the most interesting alternative.

The measured machine is an **Apple M4 MacBook Air, 24 GB unified memory, 10 CPU cores and 10 GPU cores**. BC v1 uses a smaller **24,833-parameter** candidate-scoring MLP as the initial control. Training runs locally on Metal/MPS; external compute spend is zero. The earlier 100,000–500,000-parameter graph encoder remains a proposal.

- [Research and primary sources](RESEARCH.md): actual competition winners, relevant counterexamples, public implementations and transfer limits.
- [Implementation and evaluation plan](PLAN.md): stages, directory layout, acceptance gates and isolated comparisons.
- [Resources](RESOURCES.md): original conditional estimates and a link to the measured BC run, plus the coding-model workflow.
- [Source register](../../sources/2026-11-06-rl-research.json): evidence classes, access notes and repository revisions.

`rl/research` starts at main commit `601a00eea536e305d9b77ea44d813228eb7d148d`. The selected main-branch bot remains **v6-attack**. BC is a separately tested research candidate; it has not been submitted to the live contest. Its checkpoint is frozen before evaluation against Lacoz, khoufou and v6 under the original referee.

All recommendations are hypotheses for TryAngle Catch. Results reported by other authors are not local replications or predictions of a contest rank.

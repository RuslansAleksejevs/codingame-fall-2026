# RL research branch

As of **2026-11-06**. Status: **research and implementation plan only**. No learning algorithm has been implemented or trained in this branch.

The recommended first route is **imitation of strong opponents, followed by small-scale PPO self-play**. A learned value function can then support short lookahead. A separate **BTR-inspired Q-learning experiment over complete turn plans** is the most interesting alternative.

The target machine is an **Apple M4 MacBook Air, 24 GB unified memory, 10 CPU cores and 10 GPU cores**. Training is local; no rented GPU is assumed. Proposed model size starts around 100,000–500,000 parameters, subject to measured training and deployment speed.

- [Research and primary sources](RESEARCH.md): actual competition winners, relevant counterexamples, public implementations and transfer limits.
- [Implementation and evaluation plan](PLAN.md): stages, directory layout, acceptance gates and isolated comparisons.
- [Resources](RESOURCES.md): conditional laptop runtimes, memory limits and coding-model workflow.
- [Source register](../../sources/2026-11-06-rl-research.json): evidence classes, access notes and repository revisions.

`rl/research` starts at main commit `601a00eea536e305d9b77ea44d813228eb7d148d`. The selected game bot remains the tested **v6-attack**. Its source, prepared submission and all historical results are unchanged. An RL checkpoint becomes a candidate only after independent games against the frozen Lacoz and khoufou, plus v6, under the original referee.

All recommendations are hypotheses for TryAngle Catch. Results reported by other authors are not local replications or predictions of a contest rank.

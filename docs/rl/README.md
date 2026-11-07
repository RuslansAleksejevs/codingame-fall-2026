# RL research branch

As of **2026-11-06**. Status: **native simulator, BC, PPO self-play and a larger league-training campaign are implemented and evaluated locally**. The selected [PPO v2 policy](../../code/rl/configs/selected-policy.json) won **139/200 against Lacoz versus 74/200 for PPO v1** on 100 new maps; direct PPO v2–PPO v1 was **155/200**. All 1,800 final games were clean. [Complete results and paired intervals](../../experiments/rl/2026-11-06-ppo-v2/REPORT.md). PPO v2 is now deployed: **340/937 overall in Gold**, ranking completed at 2026-11-07 08:01 UTC. [Live report](../../experiments/rl/2026-11-06-live-ppo-v2/REPORT.md). Learned search and Q-learning remain future stages.

The initial imitation-to-PPO route is implemented. The [post-Gold diagnosis and next experiments](NEXT.md) now prioritize **search-generated complete-plan targets and compact-policy distillation**, followed by an independently tested **exploiter league**. Reset curricula, a compact graph policy and checkpoint averaging are additional proposals. No follow-up training has been run yet. A separate **BTR-inspired Q-learning experiment over complete turn plans** remains an alternative from the original research.

The measured machine is an **Apple M4 MacBook Air, 24 GB unified memory, 10 CPU cores and 10 GPU cores**. BC v1 uses a smaller **24,833-parameter** candidate-scoring MLP as the initial control. BC runs locally on Metal/MPS; the measured PPO workload is faster on CPU. External compute spend is zero. The earlier 100,000–500,000-parameter graph encoder proposal requires compression or distillation to meet the measured single-file packaging constraint; it is not a ready deployment design.

- [Larger local PPO campaign](../../experiments/rl/2026-11-06-ppo-v2/REPORT.md): longer controls, broader maps, original-opponent league, road observations and fresh confirmation.
- [League and continuation implementation](LEAGUE.md): exact mixtures, warm starts, checkpoints, replay checks and limitations.
- [Research and primary sources](RESEARCH.md): actual competition winners, relevant counterexamples, public implementations and transfer limits.
- [Implementation and evaluation plan](PLAN.md): stages, directory layout, acceptance gates and isolated comparisons.
- [Resources](RESOURCES.md): measured BC/PPO v1/PPO v2 costs, original conditional estimates and the coding-model workflow.
- [Source register](../../sources/2026-11-06-rl-research.json): evidence classes, access notes and repository revisions.

`rl/research` starts at main commit `601a00eea536e305d9b77ea44d813228eb7d148d`. The selected main-branch bot remains **v6-attack**. BC remains a local control; selected PPO v2 is packaged and submitted to the live contest. See [deployment](DEPLOYMENT.md) and the [live report](../../experiments/rl/2026-11-06-live-ppo-v2/REPORT.md). Each checkpoint is frozen before evaluation against Lacoz, khoufou and v6 under the original referee.

All recommendations are hypotheses for TryAngle Catch. Results reported by other authors are not local replications or predictions of a contest rank.

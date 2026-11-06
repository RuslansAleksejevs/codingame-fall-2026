# Reinforcement learning for TryAngle Catch

As of **2026-11-06**. Primary-source review; no RL experiment was run here. Recommendations and transfer assessments are **MODEL_INFERENCE**. The source register records **SOURCE_VERIFIED** access to author reports; this verifies what an author reports, not an independent reproduction of their measurements.

## Recommendation

Start with **behavior cloning (BC), then PPO with a small opponent pool**. BC means learning to imitate useful decisions already made by strong bots. PPO then improves the policy through games and their outcomes. Keep the BC checkpoint as a control so that an imitation gain cannot be mislabeled as an RL gain.

Next, reuse the policy/value network for **short simultaneous-move search**. This is a promising route to better decisions per millisecond without increasing the network dramatically. In parallel as a research option, consider **distributional Q-learning over complete plans**, inspired by BTR. These routes share the simulator, data, action validation and evaluation tools; they do not require three separate infrastructure projects.

This recommendation balances the available laptop with the game's action space. It does not establish PPO as universally better than Q-learning, IMPALA or search.

## Closest competition evidence

The placement and method columns describe published results. Hardware and training totals are author-reported unless explicitly marked unknown. Different papers count steps differently; these totals are not a normalized speed comparison.

| Competition / result | Published method and scale | Relevance and limitation |
|---|---|---|
| **CodinGame Summer 2026, Indrill, 1st** | Q-learning close to BTR, a KataGo-style network, engineered route features; no search during play. Full training cost not disclosed in the reviewed post. | Very relevant simultaneous construction/economy game. Its bounded placement budget is easier to structure than our variable army. [Author post](https://forum.codingame.com/t/summer-challenge-2026-feedback-strategies/208574). |
| **Same contest, Pduhard, 3rd** | PPO, C++ simulation, 512 parallel games, historical opponents, checkpoint averaging and a small two-turn search. About 50,000 iterations; wall time/hardware not specified. Search beat the same network without search in 83.9% of the reported comparison. | Strong precedent for a compact learned planner. That percentage is a mirror ablation, not a gain against every competitor. [Postmortem](https://github.com/Pduhard/back-track-king-postmortem). |
| **Same contest, RamzaBeoulve, 4th** | Approximately 165k-parameter graph network; BC from a heuristic, then PPO and simultaneous-game search. | Particularly close to the proposed small graph policy. Source reports that self-play search improvements could fail against other strategies. [Author post](https://forum.codingame.com/t/summer-challenge-2026-feedback-strategies/208574). |
| **CodinGame Fall 2023, reCurse, 1st** | PPO; 156k parameters; native multithreaded C++ simulation. Reported about 300k training steps/s on a 32-core Ryzen plus RTX 3080. | Demonstrates small networks winning CodinGame; compact deployment does not imply small training cost. Different game and training units. [Postmortem](https://gist.github.com/reCurs3/7d4eb5b952790e3009337f61c3341074), [official ranking](https://www.codingame.com/contests/fall-challenge-2023/leaderboard). |
| **Lux AI Season 1, Toad Brigade, 1st** | IMPALA-derived training with UPGO/TD-lambda losses, teacher-policy KL and early reward shaping. Final network around 20M parameters. | Joint army decisions and long-term economy are relevant; distributed training is more infrastructure than the first laptop prototype needs. [Winning implementation and report](https://github.com/IsaiahPressman/Kaggle_Lux_AI_2021). |
| **Lux AI Season 3, Flat Neurons, 1st** | IMPALA/V-trace, old opponents and teacher stabilization. Final model: about 1.5B environment steps in 3–4 days; over 20B steps across experiments. Exact hardware not given in the reviewed README. | Important correction to a simplistic “PPO won everything” narrative. Final rewards still included a score component alongside match results. [Author repository](https://github.com/tonykozlovsky/lux-ai3-pub). |
| **Lux AI Season 3, Frog Parade, 2nd** | PPO, legal masks, teacher KL; native Rust environment. Reported full training throughput: 2,800 steps/s for 420k parameters, 430 for 10M, on a desktop with RTX 3090/2070 Super. | Model and learner cost can dominate even with a fast simulator. [Author report](https://www.kaggle.com/competitions/lux-ai-season-3/writeups/frog-parade-frog-parade-s-solution). |
| **Lux AI Season 3, aDg4b, 3rd** | Imitation learning from leading agents, two UNets; no RL fine-tuning in the reported solution. | A strong argument for measuring BC first. This is an IL result, not an RL victory. [Author report](https://www.kaggle.com/competitions/lux-ai-season-3/writeups/adg4b-imitation-learning-3rd-place-solution). |
| **Hungry Geese, HandyRL, 1st** | Distributed off-policy policy-gradient learning combined with simultaneous-game MCTS. Reported 16M self-play games over three weeks, then 3M games against diverse opponents over four days. | Demonstrates why homogeneous self-play can learn fragile conventions. Four movement choices per goose are much simpler than an army's joint commands. [DeNA technical report](https://engineering.dena.com/blog/2021/12/distributed-reinforcement-learning-with-handyrl/). |
| **Orbit Wars 2026, IsaiahP, 1st** | PPO, native Rust environment, structured entity actions; 200M-parameter model, 15B self-play steps, about 2,400 B200 GPU-hours. | Strong recent evidence for scale and action engineering. The compute recipe is outside this project. [Winning report](https://www.kaggle.com/competitions/orbit-wars/writeups/1st-place-solution-scaling-reinforcement-learnin), [code](https://github.com/IsaiahPressman/kaggle-orbit-wars). |
| **Orbit Wars, flg, 6th** | 2.5M-parameter entity/edge-attention model, native C++ simulation, league training and search; reported 800–2,000 training steps/s. Two-player search helped, while four-player search could hurt leaderboard performance. | Opponent-model error can erase a local search gain. [Author report](https://www.kaggle.com/competitions/orbit-wars/writeups/6th-rl-league-search-with-a-custom-edge-atte). |
| **Orbit Wars, linrock, 80th** | All training/evaluation on an M-series MacBook. 337k parameters; BC on about 303k positions took under an hour, PPO about three days. Reported 80–160 training samples/s even after C++ simulation and MPS work. | The closest hardware precedent. Most reported strength came from BC. It is not a winning result or a benchmark of this MacBook/game. [Author report](https://www.kaggle.com/competitions/orbit-wars/discussion/733686). |

Another useful recent result is **Average Joe for Generals.io**, a public human ladder result rather than a Kaggle/CodinGame contest. The October 2026 paper revision reports first place in ten consecutive weekly standings after seven days on four H200 GPUs (672 GPU-hours for the final run). It uses sparse-reward self-play policy gradients, parameter averaging and sample filtering. This shows that historical-opponent leagues and imitation are useful options, not universal prerequisites. Its JAX simulator's frame rate is not the full learner's training speed. [Paper, v2](https://arxiv.org/html/2606.23348v2), [training code](https://github.com/strakam/AverageJoe).

## Three practical routes

### A. BC → PPO → optional short search: recommended first

**Plain meaning:** learn good habits from strong bots, then improve by playing, then briefly check promising moves before choosing one.

Use a small shared graph/entity encoder for houses, road edges, triangle membership and global economy. An actor selects commands; a value head estimates expected game outcome. A single player controls the whole army: a shared policy with coordinated decoding is a natural starting point. Giving each unit an independent learner is not required merely because there are many units.

Build a resource-aware action decoder: later commands see the units and triangle resources already committed earlier in the same plan. First support an explicitly restricted action set if necessary, but label it and measure the ceiling. The full target includes road changes; a simulator omitting them is unsuitable against Lacoz. Strict legality masks are different from suppressing moves that merely look bad to a heuristic. [Masking analysis](https://arxiv.org/abs/2006.14171).

PPO is a comparatively simple, well-tested policy-gradient baseline. Its fresh-data loop is easy to audit, but can consume many games. Start with a BC control and bounded training; use teacher KL gently and ablate/relax it if the learner cannot depart from the teacher. Track the full plan's log probability, not unrelated per-unit objectives that silently change the training problem. [PPO paper](https://arxiv.org/abs/1707.06347).

**Risk:** cloning a strong bot imperfectly can lose its coordination; pure self-play can improve against itself while worsening against Lacoz. Neither training loss nor teacher-action accuracy establishes playing strength.

### B. Learned value + short search / Expert Iteration

**Plain meaning:** generate several coherent turn plans, simulate their consequences, and train a network to judge the resulting positions. Later the network can learn from the search's improved choices.

Use 8–32 diverse legal plans as a starting design range, not a promised runtime. Keep the tested v6 plan, coordinated expansion, reset, attack and road alternatives represented. Search one or two turns using the exact simulator and a small value network. The number of evaluated plans must follow measured CPU cost and the platform deadline.

Choose opponent plans from the same pre-turn observation, without revealing the selected current friendly action. Score a small payoff matrix or sample from a fixed opponent distribution. A worst-case response is an explicit conservative approximation, not the rules of the game. Preserve diversity when estimates are uncertain.

Expert Iteration alternates better search decisions and a network that generalizes them; the original paper tested Hex. That supplies a design principle, not evidence that an unmodified alternating-game AlphaZero tree will work here. Search-only, learned-value-only and the combined system need separate comparisons. [Expert Iteration](https://arxiv.org/abs/1705.08439).

**Risk:** candidate generation caps the attainable strategy; bad opponent assumptions produce confidently wrong lookahead. Search-generated labels cost more than ordinary replay labels. This route becomes particularly attractive if PPO throughput is poor but a small value model and exact search are cheap.

### C. BTR-inspired distributional Q-learning over complete plans

**Plain meaning:** remember previous games and repeatedly learn which of the available plans tends to lead to a better result.

BTR combines Rainbow components with an IMPALA-style CNN architecture, adaptive pooling, spectral normalization, implicit-quantile values, Munchausen targets and vectorized environments. “IMPALA architecture” here refers to the network; it is not the distributed IMPALA training algorithm. Its published Atari runtime uses a high-end NVIDIA desktop, not Apple Silicon. [ICML paper](https://proceedings.mlr.press/v267/clark25a.html), [full method and hardware](https://arxiv.org/html/2411.03820).

For this game, encode a variable set of complete legal plans and predict a return distribution for each. Do not enumerate every combination of army commands as one giant DQN output layer. Start with an auditable simpler Q-learning control, then add quantile targets/replay prioritization only when they improve a fixed-budget comparison. A graph encoder and plan scorer would be an adaptation, not a reproduction of published BTR.

**Benefit to test:** replay may reuse scarce simulated experience more effectively than PPO. **Costs:** additional updates and replay storage may erase the wall-time advantage; changing opponents make old data stale. Freeze opponent mixtures within stages, record opponent versions, and cap replay age. Ordinary DQN over a changing adversary is not guaranteed to converge to a robust strategy.

## What to postpone

- **Large models trained from scratch:** a higher ceiling in some recent winners, but billions of steps and 10M–200M weights are not a sensible first target here.
- **Full distributed IMPALA:** credible winning evidence, but worker/learner lag and off-policy correction introduce machinery before laptop throughput has been established.
- **MuZero / Dreamer world models:** they learn dynamics or latent rollouts. Here the referee supplies exact rules; first make exact simulation cheap. Revisit learned dynamics only if profiling shows a specific benefit. This is a project fit judgment, not a claim that these algorithms are weak. [MuZero](https://arxiv.org/abs/1911.08265), [DreamerV3](https://arxiv.org/abs/2301.04104).
- **GRPO because it is popular for LLMs:** a tiny shared critic is inexpensive; grouped game rollouts can be expensive. No reviewed winning system establishes it as the best first choice here.
- **Blindly copying Atari hyperparameters or a champion's CUDA stack:** action spaces, rewards, runtimes and hardware differ. Reuse tested concepts and appropriately licensed components, then measure the adaptation.

## Game-specific issues that decide whether any route works

1. **Simultaneous actions.** Observed state does not reveal the opponent's current commands. The simulator accepts both plans, then resolves the referee's phases. No search or feature computation may give one policy privileged access to the other's chosen current action.
2. **Delayed economy.** Spending a triangle can buy troops or combat now and lose income later. Emptying and recapturing shared corners creates multi-turn coordination. Rewarding each spawn/capture directly invites useless cycles.
3. **Reward objective.** Use game win/draw/loss as the primary target. If progress needs shaping, test a bounded potential difference `gamma * Phi(next_state) - Phi(state)`, with terminal potential zero and consistent discounting. Keep time-dependent potentials explicit; measure shaped and unshaped variants separately. The classic invariance result is for a fixed MDP and is not a blanket convergence guarantee in changing self-play. [Reward-shaping paper](https://ai.stanford.edu/~ang/papers/shaping-icml99.pdf).
4. **Dynamic graph.** Road edits affect reachability, triangles and future legal actions. Cache static geometry separately from changing graph features and invalidate correctly.
5. **Training/deployment agreement.** The same command reservations and features must exist in the native submission. A float32 model working in Python is not yet a bot that fits contest source size and CPU time.
6. **Evidence of improvement.** Keep frozen external opponents and unused maps. Mirror win rates, increasing shaped reward and a favorable checkpoint are insufficient. Preserve failures and independent training seeds.

## Public material worth reusing

Current default-branch revisions and license observations are frozen in the source register. None of these libraries was installed or executed during this research.

| Source | Useful material | Portability / reuse note |
|---|---|---|
| [VIPTankz/BTR](https://github.com/VIPTankz/BTR) | Public training code, network and prioritized replay | MIT reported by GitHub; Atari/CUDA-oriented defaults, not a ready-made graph-game learner. |
| [IsaiahPressman/kaggle-orbit-wars](https://github.com/IsaiahPressman/kaggle-orbit-wars) | Winning PPO system, Rust engine, structured actions, checkpoints and export | MIT reported; large CUDA/DDP/compile-oriented setup requires reduction for Mac. |
| [IsaiahPressman/Kaggle_Lux_AI_2021](https://github.com/IsaiahPressman/Kaggle_Lux_AI_2021) | Winning distributed learner and detailed design | MIT reported; useful joint-action/teacher-loss reference. |
| [tonykozlovsky/lux-ai3-pub](https://github.com/tonykozlovsky/lux-ai3-pub) | Winner's report, model/training material and final versions | MIT reported; preserve dependency-specific notices. |
| [DeNA/HandyRL](https://github.com/DeNA/HandyRL) | Small distributed game-RL framework | License file contains permissive MIT-style terms and an additional component notice; retain both. |
| [strakam/AverageJoe](https://github.com/strakam/AverageJoe) | Recent self-play, averaging and JAX implementation | No repository license detected in the checked metadata; study/reference first, verify reuse terms before importing code. |
| [Pduhard/back-track-king-postmortem](https://github.com/Pduhard/back-track-king-postmortem) | Particularly relevant architecture, validation and search account | A postmortem, not a full runnable training package; no license detected. |

The already frozen Lacoz/khoufou sources remain valuable opponents and potential teachers. Their precise current behavior must be reproduced before creating labels; a new upstream revision is a separate opponent. The repository's existing provenance and reuse limitations still apply. A policy imitating them is not a verified copy of their algorithms and is not automatically stronger than either teacher.

## Research limits

Several Kaggle writeup pages returned no readable body when opened directly. Their indexed primary-author text was available through search; those entries are marked accordingly in the register. GitHub and forum accounts were read directly where available. Public Discord content, private training logs and unavailable source packages were not reviewed. No cross-game rank, speed or win-rate claim above has been replicated locally.

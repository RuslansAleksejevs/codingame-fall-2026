# RL implementation and evaluation plan

As of **2026-11-06**. Research branch: `rl/research`. **The native simulator and BC-only milestone are implemented**; see the [measured report](../../experiments/rl/2026-11-06-bc-v1/REPORT.md) and [implementation guide](IMPLEMENTATION.md). The baseline is still v6. PPO, value learning, search and their comparisons below are future work. Unexecuted thresholds and budgets remain proposals.

## First deliverable

A small learned bot that runs in the original arena, plus a report comparing **v6, BC alone, BC + PPO, and BC + PPO + search** against the same frozen opponents. The first milestone is a reliable measurement of whether learning helps, not a promised contest rank.

Recommended sequence: simulator/representation → BC → bounded PPO → optional search. If PPO is too slow, retain the common infrastructure and test learned value/search or plan-level Q-learning. Do not start all alternatives at once.

## Repository layout

The directories below define the staged layout. Simulator/data/BC/native export/evaluation now contain implementations; PPO, a value head, search and single-file submission packaging remain unimplemented.

| Location | Purpose |
|---|---|
| `docs/rl/` | Research, architecture, decisions expressed technically, resource plan |
| `code/rl/sim/` | Native turn simulator, batches and bindings |
| `code/rl/data/` | Replay reconstruction, teacher labels and split manifests |
| `code/rl/models/` | Observation encoder, actor/value or plan scorer |
| `code/rl/train/` | BC, then PPO; a separate Q-learning entry point only if pursued |
| `code/rl/eval/` | Frozen opponent panels, checkpoint selection and paired analysis |
| `code/rl/export/` | Native inference, quantization/packing and feature agreement |
| `code/rl/configs/` | Small explicit configurations with seed and budget |
| `experiments/rl/<date>-<hypothesis>/` | Manifest, metrics, report, config and checkpoint hashes |
| `submissions/rl-<version>.cpp` | Tested single-file candidates, prepared separately from submission |
| `sources/` | Source links, licenses, exact third-party revisions |

Large rollout buffers, caches and intermediate checkpoints stay ignored. Preserve winning/diagnostic checkpoints in a deliberate local artifact location with hashes and a documented restore path; do not claim they are archived on GitHub if only their hashes are committed. Retain compact aggregate metrics and selected full games instead of millions of viewer frames.

## Stage 0 — establish a trustworthy training loop

1. Read the pinned referee and define an exact state/action contract. Port turn resolution to C++ in memory, reusing the existing C++ toolchain. Keep map generation from the referee initially; training maps can be generated once and cached with hashes.
2. Differential-test saved and randomized states against the Java referee. Cover simultaneous attacks, triangle spending, shared-corner troop reservations, moves, spawns, surrounding, recapture eligibility, road additions/removals, terminal ordering and scores. Compare complete state transitions, not only final winners. Require zero unexplained mismatches before generating training targets.
3. Expose batched reset/step/observe without launching processes or rendering every turn. Batch only legal full plans; store both plans and the pre-state for any divergence.
4. Benchmark simulation-only, feature encoding, policy inference and **end-to-end training** separately. Count joint game turns, controlled-player decisions and optimizer updates separately. Try modest parallelism (for example 16/64/128 games) and CPU versus MPS on the same representative workload.
5. Smoke-test random weights and the export path early. Verify actual contest IDE memory, libraries, source-size and whole-response time before committing to a larger architecture. The original local arena's 1000/50 ms limits are not a complete platform specification.

Gate: deterministic replay agreement, valid actions, a small network exported successfully, and a sustained throughput/memory report. If less than 100 controlled-player samples/s is achieved, profile before committing to a multi-million-step run. This is a planning threshold, not a correctness requirement.

## Stage 1 — imitate strong behavior

The repository contains 4,064 archived games across previous work. The latest comparison contains 55,901 checked candidate decision states. These numbers do **not** establish how many valid teacher labels can be reconstructed.

Audit one complete game from each opponent first: recover the teacher-visible observation/history, commanded action, legality and subsequent state. Viewer state, referee internals and an opponent's later action must not leak into the input. Time-limited teacher search may not reproduce the same command when called again; preserve the actual recorded command.

Do not silently remove ATTACK or road commands from teacher targets. If the initial decoder supports fewer commands, report full-plan coverage and every rejected label. Fit the value head to recorded outcomes separately from action imitation, and check held-out calibration before using it to guide search.

Start with a compact encoder, approximately 0.1–0.5M parameters. Use house/road/triangle relations and global features for turn, income, score and army sizes. A global pooling path can provide economy context without a deep network. Candidate-plan scoring is an alternative when sequential command decoding proves too costly; measure candidate coverage of teacher plans.

Construct a small dataset first, then target roughly 50k–300k verified teacher decisions if available. Split by **whole map/game**, not neighboring turns. Separate teacher identity/style or use a clearly specified mixture. Include useful losing states and recovery positions; a winners-only dataset can hide failure recovery. Prefer saved labels to calling a 30 ms teacher on every training step.

Measure command validity, held-out imitation loss, whole-plan coverage and actual win rates against both teachers and v6. Treat disagreement on equally good plans separately from illegal or incoherent actions. Add targeted teacher relabeling on student-visited states only if distribution shift is observed; it is an extra compute stage.

Gate: BC bot plays legal complete games and has a reproducible strength report. Preserve the BC-only checkpoint even if later RL is worse. Poor imitation is a reason to inspect representation, data and decoder, not immediately increase training time.

## Stage 2 — bounded PPO self-play

Use the BC weights, a shared actor/value encoder, GAE and clipped PPO as the initial control. Declare the full turn plan as the learning action; sequential command decisions share the turn advantage, with the joint log probability computed consistently. A restricted action set must be explicit in each manifest.

Begin with terminal win/loss rewards and correct draw handling. If learning stalls, test potential-based shaping as a separate ablation. Never count higher shaped reward as success. Keep recapture loops and delaying an inevitable loss among diagnostic cases.

Train against a mixture of the current policy, recent frozen checkpoints and cheap anchor policies. Avoid executing expensive public search bots throughout every rollout; use verified fast implementations or distilled anchors, while keeping the original public bots for external evaluation. Record the opponent mixture and each checkpoint hash. Teacher KL and parameter averaging are subsequent isolated stabilizers if the control drifts or fluctuates.

Initial budgets: legality smoke → 100k samples → 1M samples. Consider 5M–10M only after throughput and evaluation justify it. Set a wall-time cap as well as a sample cap. Save optimizer, RNG, scheduler, opponent pool and counters so resuming does not silently change the experiment. Avoid unbounded hyperparameter sweeps.

Gate: compare BC + PPO with BC at matched evaluations. If training score rises but the fixed-opponent panel does not improve, stop scaling and inspect policy collapse, illegal masking, reward mismatch or simulator bugs. A null or negative result is a completed experiment and must be retained.

## Stage 3 — learned search, or the Q-learning alternative

For search, freeze the learned network and compare search disabled/enabled. Generate diverse full plans, evaluate plausible simultaneous opponent plans and use the value head beyond one or two exact transitions. Do not grant the opponent observation of the selected current friendly plan. Profile feature generation and total response time; retain a ready legal fallback.

Only after the search itself helps, consider generating search targets and distilling them back into a policy (Expert Iteration). Keep a control using the same extra games without search labels to separate more-data gains from better-target gains.

For Q-learning, share the simulator and plan generator. Start with a fixed opponent distribution and a bounded replay buffer. Store candidate-set version, selected plan and opponent version. Compare simple Q-learning against the BTR-inspired additions at equal wall time and include a same-plan-set PPO control when affordable. Otherwise an action-space improvement could be mistaken for an algorithm improvement.

## Evaluation and promotion

Use separate map sets for training, checkpoint selection and final confirmation. Every previously inspected map, including seeds 4001–4200, is now development data. Check map-content hashes as well as seeds to avoid duplicate layouts. Reserve new confirmation maps before looking at results.

- Freeze source/checkpoint, decoder, opponent revisions, rules and decision criteria before confirmation.
- Development panel: for example 50 maps × both seats × Lacoz/khoufou/v6 = 300 games per candidate. This is a screening estimate, not final evidence.
- Confirmation proposal: 200 new maps × both seats × the same three opponents. For candidate versus control, that is 2,400 games. Run original-referee timed games sequentially when needed to avoid CPU-contention timeouts.
- Primary report: wins/draws/losses per opponent, matched clean-game differences and map-clustered intervals. Also report every own error, opponent error and timeout; keep technical outcomes separate and never erase failed games.
- Conservative promotion proposal: positive lower 95% bound for the equally weighted panel gain; no opponent's lower bound below -2 percentage points; no own invalid action or timeout. Pre-register before opening the holdout. A change targeted specifically at Lacoz may instead use a declared Lacoz-first rule with safeguards for the rest.
- A final selected checkpoint is different from a claim that an algorithm reliably improves play. For the latter, repeat promising training with at least three independent seeds, reporting all seeds; a game bootstrap does not measure training randomness.

Run BC/PPO/search comparisons one step at a time. Do not repeatedly tune on confirmation maps, cherry-pick a lucky checkpoint or add games only because a confidence interval nearly passes. If the laptop budget only permits a small panel or one training seed, label the result preliminary.

## Run manifest

Record source/referee/opponent/checkpoint hashes; observation/action schema; data/map split hashes; model size; precision/device; library/compiler versions; all RNG seeds; reward and opponent mixture; sample/turn/update counts; wall-clock breakdown; peak process memory; failures; evaluation schedule; commands and resume history. External compute cost is zero for the proposed local runs; subscription usage remains separate and is recorded only when observable.

## Calendar fit

The organizer's published window ends **2026-11-09 10:00 CET**, equivalent to **2026-11-09 01:00 America/Los_Angeles**; rechecked 2026-11-06. A complete RL implementation, validation and competitive training run is not promised before that deadline. The first useful target is simulator parity plus a small BC/throughput report; a longer research continuation is a separate scheduling decision. [Organizer announcement](https://bsky.app/profile/codingame.bsky.social/post/3mxyfcrrg6c2e).

# Reinforcement learning: results and evidence

As of **8 November 2026**. Research code and evidence are integrated into the main project; the branch name does not identify which bot is deployed. See [current status](../STATUS.md) for that distinction.

## Current conclusions

- **Reference policy:** PPO-v2 league3m, 24,833 parameters. Its independent 100-map test produced 139/200 wins against Lacoz, versus 74/200 for PPO-v1; paired gain +32.5pp, 95% interval [+22.5, +42.5].
- **Last confirmed submission:** PPO-v3 B2M, submission41665776. The dated live snapshot did not demonstrate improvement; there was no automatic rollback.
- **Useful offline teacher:** D16 search, +5.42pp external-panel gain in 1,120 fresh games, with no technical errors. Its multi-network implementation is not a valid unchanged-rule single-file package.
- **Rejected compact student:** the 1,680-game independent test did not preserve the teacher's advantage. Export correctness is not playing strength.
- **No experiment remains active.** New work requires a new decision; historical plans and command files are not an instruction to restart training.

## Completed stages

| Stage | Report | Implementation / supporting material |
|---|---|---|
| Behavior cloning | [BC-v1](../../experiments/rl/2026-11-06-bc-v1/REPORT.md) | [Initial research](RESEARCH.md) |
| Initial self-play | [PPO-v1](../../experiments/rl/2026-11-06-ppo-v1/REPORT.md) | [Training code](../../code/rl/train/) |
| Larger league campaign | [PPO-v2](../../experiments/rl/2026-11-06-ppo-v2/REPORT.md) | [League implementation](LEAGUE.md) · [Selected policy](../../code/rl/configs/selected-policy.json) |
| Original deployment | [League3m live report](../../experiments/rl/2026-11-06-live-ppo-v2/REPORT.md) | [Deployment guide](DEPLOYMENT.md) |
| Diverse PPO continuation | [B2M live report](../../experiments/rl/2026-11-07-ppo-v3/live-submission/REPORT.md) | [Post-v3 diagnosis](POST_V3.md) |
| Exploiters / curriculum / search | [RL-v4 results](v4/RESULTS.md) | [Verified snapshot](../../experiments/rl/2026-11-08-rl4/SNAPSHOT.json) |
| Deadline-bounded search and distillation | [RL-v5 report](../../experiments/rl/2026-11-08-rl5/deadline-search/REPORT.md) | [Implementation](v5/DEADLINE_SEARCH.md) · [Independent audits](../../experiments/rl/2026-11-08-rl5/coordinator/) |

## Evaluation discipline

Candidates are compared on matched maps and both seats. Technical losses are retained; clean-paired results are reported separately. Whole-map confidence intervals do not measure variation across training seeds or guarantee live leaderboard gains. The latest teacher/student confirmation sets were fixed before evaluation, with no post-result sample extension.

The global reserved partitions 40001–40100 and 65001–65040 remain unopened. Older development maps and training-bank diagnostics must not be relabelled as independent tests.

## Reproduction and historical planning

The current [last-day recommendations](LAST_DAY_OPTIONS.md) prioritize delivering the measured search advantage. The [AI competition evidence review](AI_COMPETITION_EDGE.md) separates research findings, winner accounts and inference. Neither document starts a new experiment.

Use the experiment-specific protocol, command manifests, model identities and reports. Frozen research sources contain their original budget/cutoff guards; reading an old command is not authorization to rerun it. The measured environment was an Apple M4 MacBook Air with24GB memory; PPO used CPU because that workload was faster than MPS. External compute spend was zero.

[Quick start](../QUICKSTART.md) · [Evidence restoration](../ARCHIVE.md) · [Resource measurements](RESOURCES.md)

[PLAN](PLAN.md), [NEXT](NEXT.md) and the [original research](RESEARCH.md) are historical proposals. Consult current reports before interpreting any item as unimplemented or pending.
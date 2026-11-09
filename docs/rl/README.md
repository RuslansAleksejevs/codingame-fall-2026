# Reinforcement learning: results and evidence

As of **9 November 2026,01:50UTC**. The branch name does not identify the deployed bot. See [current status](../STATUS.md).

[Detailed experiment timeline](../EXPERIMENT_TIMELINE.md) covers the heuristic,
learning and platform stages, including failures and corrections, through the
closed v7 pilot and the dated, incomplete D16 ranking check.

## Current conclusions

- **Reference policy:** PPO-v2 league3m, 24,833 parameters. Its independent 100-map test produced 139/200 wins against Lacoz, versus 74/200 for PPO-v1; paired gain +32.5pp, 95% interval [+22.5, +42.5].
- **Current submission:** D16 A3 `94f0d426…`,41672652, accepted9Nov01:31UTC. Last saved28%,444/1040,score12.37; **final ranking unverified**, live refresh temporarily blocked. Immediate beforeleague3m:380/1039,Gold228/428,14.89. [Running report](../../experiments/rl/2026-11-09-d16-live/REPORT.md).
- **Useful offline teacher:** D16 search, +5.42pp external-panel gain in 1,120 fresh games, with no technical errors. Its multi-network implementation is not a valid unchanged-rule single-file package.
- **Rejected compact student:** the 1,680-game independent test did not preserve the teacher's advantage. Export correctness is not playing strength.
- **Rejected compact D16:** RL-v6 fits in94,123UTF16 units, but its final stopped at656/4200 after one emergency WAIT before baseline generation. No official timeout in that game; strength inconclusive.
- **New diversity pilot: NO-GO.** Four new students, matched800updates each;800 clean fresh-map games. Seed-average broad−narrow+1.5625pp [−2.6042,+6.25], but broad−base−3.125pp [−7.2917,0]. No final extension or submission. [Report](../../experiments/rl/2026-11-09-rl7/diversity/REPORT.md).
- **D16 A3 delivery completed:** complete-ensemble shallow-first fallback passes contracts,96fresh gross-guard games and3fixed official checks. Local46/48 versus41/48,95%CIgain[0,27.0833]pp is not strong confirmation. Official102outputs/17paired/1nonself changed move shows sparse functional search. A1/A2 failures remain. [A3 report](../../experiments/rl/2026-11-09-rl7/d16/A3_REPORT.md).

The separately requested **leaderboard recheck** is complete. League3m's final
snapshot improved12 places and0.52score points over the fresh precedingB2M
snapshot; this is not a paired causal comparison. The new v7 request is separate.
[Live report](../../experiments/rl/2026-11-08-leaderboard-recheck/REPORT.md).

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
| Compact multi-network search | [RL-v6 report](../../experiments/rl/2026-11-08-rl6/compact-d16/REPORT.md) | [Protocol](../../experiments/rl/2026-11-08-rl6/compact-d16/PROTOCOL.md) · [Stop audit](../../experiments/rl/2026-11-08-rl6/compact-d16/coordinator/final-stop-audit-attempt2.json) |
| Requested league3m recheck | [New live report](../../experiments/rl/2026-11-08-leaderboard-recheck/REPORT.md) | [Complete92-game audit](../../experiments/rl/2026-11-08-leaderboard-recheck/audit-final.json) |
| Matched position-diversity pilot | [RL-v7 report](../../experiments/rl/2026-11-09-rl7/diversity/REPORT.md) | [Frozen decision](../../experiments/rl/2026-11-09-rl7/diversity/gamedev-decision.json) · [Independent audit](../../experiments/rl/2026-11-09-rl7/coordinator/pilot-audit.json) |
| Useful-baseline and shallow-first D16 delivery | [A3 report](../../experiments/rl/2026-11-09-rl7/d16/A3_REPORT.md) | [Independent96-game audit](../../experiments/rl/2026-11-09-rl7/coordinator/d16-a3-audit.json) · [Incomplete live check](../../experiments/rl/2026-11-09-d16-live/REPORT.md) |

## Evaluation discipline

Candidates are compared on matched maps and both seats. Technical losses are retained; clean-paired results are reported separately. Whole-map confidence intervals do not measure variation across training seeds or guarantee live leaderboard gains. The latest teacher/student confirmation sets were fixed before evaluation, with no post-result sample extension.

RL-v6 opened40001–40020:16maps played,15 complete;40017–40020 generated only.
The remaining40021–40100 and65001–65040 are unopened. Older development maps,
training-bank diagnostics and exact repeats must not be relabelled as independent tests.

## Reproduction and historical planning

The current [last-day recommendations](LAST_DAY_OPTIONS.md) prioritize delivering the measured search advantage. The [AI competition evidence review](AI_COMPETITION_EDGE.md) separates research findings, winner accounts and inference. Neither document starts a new experiment.

Use the experiment-specific protocol, command manifests, model identities and reports. Frozen research sources contain their original budget/cutoff guards; reading an old command is not authorization to rerun it. The measured environment was an Apple M4 MacBook Air with24GB memory; PPO used CPU because that workload was faster than MPS. External compute spend was zero.

[Quick start](../QUICKSTART.md) · [Evidence restoration](../ARCHIVE.md) · [Resource measurements](RESOURCES.md)

[PLAN](PLAN.md), [NEXT](NEXT.md) and the [original research](RESEARCH.md) are historical proposals. Consult current reports before interpreting any item as unimplemented or pending.
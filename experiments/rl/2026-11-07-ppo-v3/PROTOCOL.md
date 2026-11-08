# PPO-v3 frozen execution protocol

Frozen before any production PPO-v3 training or development outcomes, 2026-11-07.
Local CPU only; external compute spend $0. No submission, commit/push or publication.

## Base and objective

Start both independent continuations from PPO-v2 league3m (3,002,173 additional
decisions). Keep its checkpoint, weights and deployed fallback untouched. Retain
the 24,833-parameter standard/style2 actor, optimizer states, terminal +1/0/-1
reward, gamma .995 and existing PPO math. No army/spawn shaping.

Production outputs `seed-a` and `seed-b` use seeds 202611074 and 202611075.
Pilot updates never initialize production. Start with one 2M-decision block per
seed, each capped at 120 training minutes, run sequentially. Checkpoints every
250k decisions and recovery snapshots every ten updates. Block limits are
cumulative on resume; source hashes must match. Run evaluation between blocks,
never concurrently with heavy training. Continuation is conditional on broad
development results, at most 8M decisions / 8 CPU training hours per seed.

## Diverse prioritized pool

35% of games use current/current self-play. Remaining 65% samples frozen
league3m, long-control3m, league4.837m, two recent versions, and unchanged Lacoz.
Each eligible opponent receives 6--25% of games; remaining mass is proportional
to `(0.2 + 1 - score_ema)^1.5`, EMA decay .99 per observed game. Historical
opponents play greedily, learners sample at the inherited temperature .7.
Recent slots alternate replacement every 250k decisions and reset their EMA.
Log actual labels, probability vectors and outcomes for every rollout.

Both khoufou versions, v6 and BC remain **evaluation-only**. The new khoufou is
070bc128, distinct from legacy 372c1cd6; its unchanged source and provenance
are saved separately. No external source is copied into the submitted policy.

## Evaluation and selection

Smoke: known 6001--6002 maps, four opponents; excluded from strength claims.
Rebuild a union of canonical/legacy content hashes from previous map manifests
and saved platform game options. Development uses 30001--30040, both seats.
Its first 12 maps form a cheap screening subset, not a new independent test.
Final confirmation is reserved at 40001--40100 and **not generated or played
until a single finalist is frozen**. Rebuild exclusions immediately beforehand,
including all v3 development maps. Abort on a content collision; seed novelty
alone does not establish a holdout.

Primary panel: Lacoz, new khoufou, old khoufou, direct league3m. Safeguards:
v6 and BC. Preserve per-opponent game wins/draws/losses, errors/timeouts,
original referee records, source/weight hashes and paired map-cluster intervals.
Technical wins never count as strategic improvement; paired clean games determine
strength comparisons, with all technical outcomes retained separately.

At each block screen raw checkpoints near .5M, 1M, 1.5M and the actual block end,
plus one average of the last three compatible snapshots from that trajectory.
Do not average across independent seeds or feature variants. Advance at most
two candidates per seed to the full 40-map development panel. Select by equal
mean score on Lacoz/new khoufou/old khoufou/direct league3m, subject to zero own
errors and no >5 percentage-point loss versus base on a safeguard. Break ties
within one point in favor of the earlier/simpler raw network. Do not claim the
adaptive development winner is an unbiased effect estimate.

Final confirmation: candidate and frozen league3m each face Lacoz, both khoufou
versions, v6 and BC; add direct candidate--league3m (2,200 games on 100 maps).
Predeclared promotion evidence: direct score >=55% with map-clustered 95% lower
bound >50%; equal-weight external score gain >=3 points; no opponent point-score
drop >5 points; zero own command errors/timeouts. Report intervals individually.
If criteria fail or uncertainty remains, retain league3m; never label a weaker
or inconclusive candidate an established improvement. No final-set tuning.

## Bounded search and final window

Search pilot gets at most four hours of engineering/testing wall time. Include
the greedy complete plan; evaluate simultaneous joint actions against multiple
enemy models chosen before revealing our action. Recompute both policies at
future states. Continue only with broad opponent gains and measured cost;
no search-generated training dataset before that evidence. No new GNN/BTR/MuZero.

Saved official deadline 2026-11-09T09:00:00Z (fresh OAuth GET pending).
Hard research cutoff **2026-11-09T02:00:00Z**, retaining seven hours for final
confirmation, export/packaging and platform tests. Trainer enforces the cutoff.
Platform checks do not overwrite IDE code or the deployed bot. A separate
explicit authorization would be required for any competitive submission.

Status and logs are checked during execution; durable continuation messages
are scheduled for active processes. No new LLM chats or paid resources.
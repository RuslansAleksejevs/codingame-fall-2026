# Distillation pilot

Completed9November2026: **NO-GO at the prospective800-game development gate**.
No student promoted, no independent final opened, no extra training. This was a
NEW bounded experiment using unchanged league3m initialization/24,833-parameter
decoder and the original unquantized D16 teacher, not a resumed old campaign.

[Prospective protocol](../../../experiments/rl/2026-11-09-rl7/diversity/PROTOCOL.md)
defines exact maps, promise screen, conditional independent final and stop rules.
Counts/map/phase coverage change together; no single-factor causal claim.
No PPO campaign, platform action or submission is part of this pilot.

[Final report](../../../experiments/rl/2026-11-09-rl7/diversity/REPORT.md) and
[frozen full-game decision](../../../experiments/rl/2026-11-09-rl7/diversity/gamedev-decision.json):
800/800fresh original-referee games,16canonical-novel maps,both seats,all four
students plus untouched base against Lacoz/new+old Khoufou/league3m/B2M. All clean,
all Java replaysPASS; all/common-clean analyses identical. Paired whole-map95%CIs:

|External difference|Seed1 pp[CI]|Seed2 pp[CI]|Mean pp[CI]|
|---|---:|---:|---:|
|Broad−narrow|+2.08[−3.13,+7.29]|+1.04[−4.17,+6.25]|+1.56[−2.60,+6.25]|
|Broad−base|−2.08[−6.25,+2.08]|−4.17[−9.38,0]|−3.13[−7.29,0]|

Designated broad1 lost direct league3m12W/20L; broad2 10W/22L. The fixed promise
criterion failed. This is uncertain improvement over narrow data, not established
strength above base or proof that diversity cannot help. Both Khoufou versions
were beaten32/32 by every arm, limiting pilot sensitivity. Final73401–73440 and
unused training73065–73128 remain closed; no seed selection or final retry.

Actual data:2,011broad unique roots/63maps versus205narrow/12maps;509labeldev roots/
16maps. Same2training seeds,800updates/25,600root-group exposures per model,matched
objective/hyperparameters. Count/map/phase and changed-target frequency vary
together. Original opponent-timeout STOP is preserved; authorized pre-training
A1 excluded map73017/both seats without replacement/replay, an explicit technical
selection confound. Teacher adapter unchanged. Exact float32 exports and old-
record command parity allPASS after a preserved compiler failure; no retraining.

Total960new games (160collection+800strength),0own errors/1collection-opponent
timeout;4new retained checkpoints/3,200updates. All raw/labels/checkpoints/failures
retained.12closed shared leases/21.236570heavy minutes,spend0; protected/frozen
hashesPASS, own processes and timers closed. See
[closeout audit](../../../experiments/rl/2026-11-09-rl7/diversity/closeout-audit.json)
for exact paths/hashes/counts and the report for versions/commands/uncertainty.

Recommendation: keep untouched league3m; deploy none of these students. If a later
experiment is explicitly authorized, use a NEW same-sized student initialized
from league3m with better-audited D16 targets and an objective/retention test.
Lower CE here reduced base agreement and did not preserve full-game strength.
Do not continue rejected Round2/current students or automatically enlarge the
architecture; capacity/objective explanations remain follow-up hypotheses.
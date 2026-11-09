# Existing bot portfolio — 9 November 2026

Final choice06:15UTC: D16 A3 selected for the final entry. Replacement is awaiting
new login, not yet submitted; league3m remains the last verified active source.
[Delivery status](../experiments/rl/2026-11-09-final-delivery/REPORT.md).

Updated9November06:00UTC. No new training; one separately requested unchanged
league3m control completed ranking05:59 and full audit06:00. Local results
are PROJECT_REPORTED; platform snapshots are SOURCE_VERIFIED. Different dated
ratings are moving, unpaired comparisons, not causal rankings of algorithms.

| Candidate | Independent/local evidence | Platform evidence | Current use |
|---|---|---|---|
| PPO-v2 league3m |1800clean independent games;139/200 against Lacoz |Fresh41673756:433/1042,Gold269/422,13.37;93audited49W44L,0ownerrors/1opponenttimeout. Historical8Nov23:25:368/1036,15.11,92clean52W40L |Current active control; reliable fallback/reference, not the new recommendation |
| PPO-v3 B2M |+4.25pp on adaptive development, not an independent final |Completed8Nov07:10:382/989,12.90;95clean logs41W/54L. Later pre-league3m snapshot380/1036,14.59 |Reserve; no established live advantage |
| Original FP32 D16 teacher |1120independent games;external+5.4167pp,95%CI[1.25,9.5833];76/80 direct league3m |Original uncompressed package not deployable under source limit |Useful teacher/research ceiling, not the current A3's measured effect |
| Compact D16 A3 |96fresh gross-guard games;46/48 versus41/48 base;gainCI[0,27.0833]pp. Technical delivery passed |Authenticated full audit9Nov05:37:371/1042,Gold207/422,15.77,100%;98logs55W43L,0official errors;3209complete telemetry/0emergency |Preserved finalist41672652, temporarily replaced by requested league3m control; no causal superiority claim |
| v5 compact student |1680independent games,30/80 direct league3m;external−2.9167pp |Not submitted |Rejected |
| v7 four diversity students |800fresh games;meanbroad−base−3.125pp,CI[−7.2917,0];broad−narrow+1.5625pp,CI[−2.6042,6.25] |Not submitted |All rejected; do not resume their weights automatically |

Heuristics, BC and PPO-v1 are historical controls. The three v4 directions
(exploiters, difficult-start curriculum, early search) failed their declared
criteria. RL-v6 compact D16 stopped656/4200 after an emergency fallback; A1's
later final stopped359/1200 after a control timeout. These incomplete negative
results remain unchanged by A3's later delivery.

## Decision implications — MODEL_INFERENCE

The realistic final choice is league3m or D16 A3. D16's full-audit snapshot is
9places and0.88score points above its original league3m before-snapshot, with a
changing field. This is descriptive evidence, not a controlled estimate. The
private98-log audit is now complete. Fresh unchanged league3m finished433/1042,
13.37 with93fully audited logs. **Recommend D16 A3**: its full-audit snapshot is
62places/+2.40score above this control, with no own errors in either snapshot.
This is a practical choice, not statistically established causal superiority.
league3m remains active; no automatic final restoration occurred.
[Completed comparison](../experiments/rl/2026-11-09-final-choice/REPORT.md).

If further work is separately selected, first measure useful completed D16
comparisons under the same timing limit and investigate redundant feature work.
For learning, start a NEW student from unchanged league3m only after checking
the usefulness of changed D16 targets and retention of base decisions. The pilot
does not justify simply adding more updates to the rejected recipe.

[Live D16 evidence](../experiments/rl/2026-11-09-d16-live/REPORT.md) ·
[League3m full audit](../experiments/rl/2026-11-08-leaderboard-recheck/REPORT.md) ·
[B2M full audit](../experiments/rl/2026-11-07-ppo-v3/live-submission/REPORT.md) ·
[Detailed timeline](EXPERIMENT_TIMELINE.md) · [Delivery rules](CONTEST_DELIVERY.md).
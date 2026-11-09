# Existing bot portfolio — 9 November 2026

Final delivery06:42UTC: **D16 A3 selected, accepted and current41673944**.
Exact source94f0d426; the preceding league3m control remains preserved in history.
[Final delivery, ranking and audit](../experiments/rl/2026-11-09-final-delivery/REPORT.md).

Updated9November06:00UTC. No new training; one separately requested unchanged
league3m control completed ranking05:59 and full audit06:00. Local results
are PROJECT_REPORTED; platform snapshots are SOURCE_VERIFIED. Different dated
ratings are moving, unpaired comparisons, not causal rankings of algorithms.

| Candidate | Independent/local evidence | Platform evidence | Current use |
|---|---|---|---|
| PPO-v2 league3m |1800clean independent games;139/200 against Lacoz |Fresh41673756:433/1042,Gold269/422,13.37;93audited49W44L,0ownerrors/1opponenttimeout. Historical8Nov23:25:368/1036,15.11,92clean52W40L |Previous control; preserved reference, no longer active |
| PPO-v3 B2M |+4.25pp on adaptive development, not an independent final |Completed8Nov07:10:382/989,12.90;95clean logs41W/54L. Later pre-league3m snapshot380/1036,14.59 |Reserve; no established live advantage |
| Original FP32 D16 teacher |1120independent games;external+5.4167pp,95%CI[1.25,9.5833];76/80 direct league3m |Original uncompressed package not deployable under source limit |Useful teacher/research ceiling, not the current A3's measured effect |
| Compact D16 A3 |96fresh gross-guard games;46/48 versus41/48 base;gainCI[0,27.0833]pp. Technical delivery passed |Earlier41672652:371/1042,15.77,98logs55W43L. Final41673944:100%,345progress/346leaderboard out of1043,16.84,90logs51W39L/0ownerrors; [full result and caveats](../experiments/rl/2026-11-09-final-delivery/REPORT.md) |Explicitly selected, active and fully audited final entry; no causal superiority claim |
| v5 compact student |1680independent games,30/80 direct league3m;external−2.9167pp |Not submitted |Rejected |
| v7 four diversity students |800fresh games;meanbroad−base−3.125pp,CI[−7.2917,0];broad−narrow+1.5625pp,CI[−2.6042,6.25] |Not submitted |All rejected; do not resume their weights automatically |

Heuristics, BC and PPO-v1 are historical controls. The three v4 directions
(exploiters, difficult-start curriculum, early search) failed their declared
criteria. RL-v6 compact D16 stopped656/4200 after an emergency fallback; A1's
later final stopped359/1200 after a control timeout. These incomplete negative
results remain unchanged by A3's later delivery.

## Decision implications — MODEL_INFERENCE

The evaluated finalists were league3m and D16 A3; D16 is now explicitly selected.
D16's original full-audit snapshot is
9places and0.88score points above its original league3m before-snapshot, with a
changing field. This is descriptive evidence, not a controlled estimate. The
private98-log audit is now complete. Fresh unchanged league3m finished433/1042,
13.37 with93fully audited logs. **Recommend D16 A3**: its full-audit snapshot is
62places/+2.40score above this control, with no own errors in either snapshot.
This is a practical choice, not statistically established causal superiority.
No automatic final restoration occurred at the comparison's close. The later
explicitly authorized D16 final replacement41673944 is now current.
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
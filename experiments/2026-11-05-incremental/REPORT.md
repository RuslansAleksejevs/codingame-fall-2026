# Sequential evaluation of three improvements

as_of: 2026-11-05, America/Los_Angeles. Measurement classification: PROJECT_REPORTED.

Completed: **v3, multiple SPAWN commands per turn, was selected**. On fresh validation maps it won13/100 against khoufou versus 0/100 for the original baseline. Triangle reset and surrounding protection did not add further gains. No variant won a normal game against Lacoz.

There were 1,400 new matches plus200 retained control matches. Paid external cost: 0.

## Variants

| Version | Base | Change |
|---|---|---|
| v2 | Frozen preceding baseline | Control: one SPAWN per turn |
| v3 | v2 | Multiple SPAWN commands, retaining the army cap and one-triangle income reserve |
| v4 | v3 | Clear all corners of one spent triangle, then recapture when legal |
| v5 | v3 | Assess surrounding risk at final positions and make up to six movement corrections |

v4 performed worse on development maps, so v5 branches from v3. Comparing v5 with v4 would confound two changes. Sources are retained in `code/variants/` and per-run snapshots, frozen before each run. Opponents were unchanged. New variant coefficients were not tuned on that variant's measured series.

## Development maps

Seeds1001–1050, both seats: 100 games per opponent per variant. v2 uses the preceding archived control series; v3/v4/v5 added600 matches.

| Version | Wins vs khoufou | Clean wins vs Lacoz | Technical wins vs Lacoz |
|---|---:|---:|---:|
| v2 | 0/100 | 0/100 | 0 |
| v3 | 8/100 | 0/81 | 19 |
| v4 | 1/100 | 0/99 | 1 |
| v5 | 7/100 | 0/98 | 1 |

v5 also had one own timeout against Lacoz: 98 ordinary games, one opponent timeout and one own timeout. Every outcome is retained. Technical wins count in the engine but do not establish improved strategy.

Against khoufou, v3 spawned31.93 units per game versus 18.38 for v2. v4 reduced this to 15.98; captures fell from 36.34 to 18.81. These measurements describe this implementation. The hypothesis is that prematurely clearing corners disrupts expansion, not that triangle reuse is inherently unhelpful.

## Separate validation

Before execution, seeds 2001–2050, four frozen sources and the protocol were recorded in `plan.json`. The series ran50 new maps ×2 seats ×2 opponents ×4 versions =800 games. Variants were interleaved per map, with order rotated across seats and opponents to reduce timing effects. Sources stayed fixed throughout.

| Version | Wins vs khoufou | Clean wins vs Lacoz | Technical wins vs Lacoz |
|---|---:|---:|---:|
| v2 | 0/100 | 0/99 | 1 |
| v3 | 13/100 | 0/100 | 0 |
| v4 | 7/100 | 0/100 | 0 |
| v5 | 5/100 | 0/100 | 0 |

No own errors or timeouts occurred in the separate validation. One Lacoz timeout gave v2 a technical win, reported separately. Sources: `validation-comparison.json`, `validation/completion.json`.

## Measured contribution

1. **Retain multiple SPAWN.** The khoufou gain repeated: +8 percentage points in development and +13 in validation. Validation reinforcements increased from 19.25 to 35.39 per game; captures from 23.99 to 41.67. The descriptive paired95% interval for the validation win-rate change was +5 to +22 points. Across both sets: 21/200 versus 0/200, +10.5 points, interval +5.5 to +16.
2. **Do not include this triangle-reset implementation.** It won fewer games than v3 in both sets: 1 versus 8, and 7 versus 13. Validation reinforcements fell to 22.00 and captures to 25.86. The next implementation would need more selective clearing timing rather than persistent clearing.
3. **Do not include this protection implementation.** Validation surrounding losses against khoufou fell from 35.02 to 14.33 units per100 own decisions, but ATTACK losses rose from 34.08 to 51.33. Wins fell from 13 to 5. Combined difference from v3: -4.5 points, descriptive interval -10.5 to +1. Reducing one type of loss did not improve overall play.

These findings concern the tested implementations, not every possible reset/protection algorithm. The gap to Lacoz remains large.

## Saved result and audit

At completion, `code/bot.cpp` and the local binary were set to validated v3. Candidate: `submissions/baseline-v3-multispawn.cpp`; the old v2 candidate was retained. Source/binary hashes matched the validation snapshot. Selected source SHA256: `0b2d033bfda7282eaa31891f033124d680234e698dde714c21005fe2f9ac518f`.

`audit.json` confirms 1,400 complete new records, 44,513 checked decision states, source identity across development/validation, and exit0 for every launcher. No compiler warnings occurred. The new runs contain22 opponent timeouts and one own timeout, v5 development seed 1044/seat1 against Lacoz. Selected v3 had no own errors in its400 games. Failures were retained rather than replaced by successful reruns.

Summed match-process time was about 38.81 minutes, excluding preparation and analysis. No contest submissions, public releases or paid computations were performed by this experiment.

## Method and limits

- Original unmodified referee b6913124a10de328316ff42906448a18cb948431, league3, 1000/50 ms limits. Games ran sequentially.
- Unchanged Lacoz7f1901834d2ffc16532e083edfec8cbdb5941ab6 and khoufou372c1cd6738d456513cb50705b98549eedfdfad8. Per-run manifests retain provenance, hashes and environment versions.
- Java17.0.21+9, Python3.14.6, NumPy2.5.4, SciPy1.18.1. Python libraries were warmed before the series. These are local results, not server rankings.
- Viewer-protocol army totals were checked against bot stderr before every recorded decision. All results, error logs, commands, source snapshots and complete records are retained. Binaries are excluded from Git.
- Primary metric: game wins. Duration, units and captures explain outcomes but do not replace them. Secondary metrics use error-free games, with denominators in JSON.
- Comparisons pair identical map, seat and opponent. Both seats of a map are dependent, so intervals resample entire map clusters10,000 times. Intervals are descriptive. An all-zero interval from zero observed wins does not prove zero true win probability.
- Lacoz technical outcomes and shared clean pairs are reported separately. Clean filtering may introduce selection bias. Lacoz's time-bounded search can produce different decisions on repeated maps. Conclusions are conditional on these sources and runs.

## Reproduce

Single series: `python3 code/benchmark_public.py --source file.cpp --label version --seeds 1001:1050 --out new_directory`. Without `--source`, frozen v2 is used.

Original validation command from the repository root:

```sh
python3 code/benchmark_ablation.py --variants v2=experiments/2026-11-05-baseline-v2-validation/bot.cpp v3=code/variants/v3-multispawn.cpp v4=code/variants/v4-reset.cpp v5=code/variants/v5-protection.cpp --seeds 2001:2050 --out experiments/2026-11-05-incremental/validation
```

For replay use a new directory and `--map-context reused`; those seeds are no longer unseen. Analyze with `code/analyze_incremental.py --pairs v2:v3 v3:v4 v3:v5`; the historical script is also retained here. Supporting files: dev-comparison.json, validation-comparison.json, combined-comparison.json, audit.json, plan.json and run snapshots. Paid cost: 0.

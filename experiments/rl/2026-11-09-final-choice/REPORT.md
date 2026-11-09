# Final-choice leaderboard assessment

9 November2026,06:00UTC. **COMPLETE. Recommendation: D16 A3**, based on the
completed current snapshots and clean own execution. One fresh unchanged
league3m control41673756 completed ranking at05:59 and its full audit at06:00.
**league3m remains active.** No final restoration or switch was performed; the
recommendation is not a selected final submission. The authenticated process
exited normally and its pending control was cancelled after both results.
Official responses are SOURCE_VERIFIED; saved-log analyses PROJECT_REPORTED;
candidate selection/recommendations MODEL_INFERENCE. This report is local only.

| Candidate / snapshot | Overall | Gold | Score | Full-log evidence |
|---|---:|---:|---:|---|
| D16 A3 /41672652, full audit05:37 |371/1042|207/422|15.77|98/98 complete:55W43L,zero official technical errors/warnings;3209complete telemetry records after additive parser correction|
| Same D16, immediately before replacement05:39 |370/1042|206/422|15.77|Separate moving snapshot; no new D16 source or submission|
| league3m /41673756, new control05:59 |433/1042|269/422|13.37|93/93complete:49W44L;0own errors/warnings,1opponent timeout;clean-only48W44L|
| league3m /41671805, earlier8Nov23:25 |368/1036|221/428|15.11|Historical92clean logs,52W40L; not a new execution|
| B2M /41665776, earlier8Nov07:10 |382/989|243/392|12.90|Historical95clean logs,41W54L; not selected for another submission|

## D16 audit closed

Exact accepted source94f0d426… matches the frozen A3 package. The authenticated
history preserves all earlier submissions and confirms the single original A3
POST; it was not resubmitted.98done/0pending battles, no further page, all full
logs saved. Coverage is this frozen snapshot, not later passive matches.

The frozen line-based auditor reported five malformed telemetry lines because
complete JSON objects were concatenated with subsequent stderr fragments
without newline separators. The additive parser decodes exact JSON boundaries,
checks every contiguous turn identity and preserves all formerly parsed records.
Five synthetic parser checks passed. No bot source, old auditor, game or old
receipt changed. Both the original flagged receipt and the correction remain.

All3209outputs have complete mandatory baselines and no emergency records.
143nonbaseline actions, allD1;940paired-comparison turns;3418completeD1 and247D2
evaluations. Only17turns reach a complete D2 comparison, none chooses a different
action through D2. Internal wall maximum22.097ms/CPU22.026ms;2ordinary turns>20ms,
but no official timeout. The original uncompressed teacher's local advantage
must not be attributed directly to this much shallower platform execution.

Evidence: [complete D16 audit](../2026-11-09-d16-live/audit-final.json),
[additive telemetry audit](d16-telemetry-supplement.json),
[final progress](../2026-11-09-d16-live/progress-final.json),
[final leaderboard](../2026-11-09-d16-live/leaderboard-final.json),
[full battle list](../2026-11-09-d16-live/battles-final.json).

## Why one fresh league3m control

league3m is the best independently validated ready PPO policy and the principal
remaining finalist. Its prior completed recheck is over six hours old. The new
control uses exactly199c6a2d…:186203UTF8bytes/80247UTF16units, no edits or training.
Its saved Gold compilation/test and92clean ranked games establish reused
compatibility, not a newly executed technical game. Fresh challenge remains
Gold/C++/1000–50ms; exact current source/history/quotas were checked before POST.
The accepted readback matches and history adds exactly one ID, preserving six.

B2M has no established independent/live improvement and rejected students have
negative strength evidence. Neither is included in a mass rating sweep.
[Prospective request](league3m/submission-request.json),
[accepted response](league3m/submission-response.json),
[readback](league3m/accepted-source.json), [execution ledger](COMMANDS.md).

The new read-only candidate auditor reproduces all92old league3m games and
the saved52W40L/zero-error result exactly; no match was replayed.
[Regression receipt](auditor-regression-league3m.json).

## Completed control and recommendation

The final accepted source still hashes to199c6a2d… and is current. All seven
history IDs are preserved, exactly one new ID added. Progress and independent
leaderboard agree:433/1042,Gold269/422,13.37,100%/notinprogress. All93snapshot
battles are done and fully downloaded, no pending or further page.49W44L;
3514own outputs,0own errors/warnings or global failures. GoldenGlove's timeout
in918937207 is the sole opponent error: keep that win in gross results, omit it
from the clean-only48W44L. Max internal planning11.101ms is not total charged CPU.
[Full audit](league3m/audit-final.json), [progress](league3m/progress-final.json),
[leaderboard](league3m/leaderboard-final.json),
[final source](league3m/accepted-source-final.json),
[history](league3m/submissions-final.json), [battle list](league3m/battles-final.json).

MODEL_INFERENCE: choose D16 A3 from the ready finalists. Its full-audit snapshot
is62places and2.40score points above the fresh league3m control; its immediately
before-replacement snapshot differs by63places at the same15.77score. Both own
executions are clean in their complete saved snapshots. This supports a practical
choice, **not** a paired causal estimate, statistically proven superiority or a
promise of final placement. The packaged A3 does not inherit the original FP32
teacher's entire independent strength estimate.

The active entry is still league3m41673756/source199c6a2d. To use the recommended
D16 at the deadline, explicitly choose that final replacement, then verify its
new acceptance/ranking. No automatic restoration was made. B2M was not rerun;
its older completed evidence remains historical. No new learning is justified
by this assessment; the diversity pilot and rejected students stay closed.

## Interpretation and delivery boundary

Sequential leaderboard results use different maps/opponents and a moving field;
neither rank differences nor raw win rates prove a causal strength difference.
D16's audited371/1042 is top35.6%, approximately64.4th percentile by players below.
Fresh league3m433/1042 is top41.6%, approximately58.4th percentile.
No result here is the final contest standings.

Fresh authenticated deadline:9November09:00UTC. There is one active final bot,
not several simultaneous entries; a new POST replaces it. No extra mandatory
paper/video/public repository was found. The published general-vs-specific
AI-rule inconsistency remains explicitly disclosed in
[delivery rules](../../../docs/CONTEST_DELIVERY.md).

No new training, paid compute, IDE overwrite, bot edits or Git commit/push.
Published main and rl/research were both verified at e5cd7b4 during the preceding
completed repository task; this assessment's newer evidence is local.
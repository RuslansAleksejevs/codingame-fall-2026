# Compact D16: one accepted submission, final ranking not yet verified

Corrected **9 November2026,02:36UTC**, from saved files, not a new live query.
A3 was submitted exactly once as
**41672652** at01:31:03.050UTC. The accepted source matches the frozen package.
The last saved progress response is63%, not a completed ranking. The first
GET-batch attempt failed review availability, but its exact retry succeeded.
The later summary claiming two failures was incorrect. Exit-only cleanup02:30
returned unread responses and closed the client without new HTTP requests.
No additional submission, rollback, source change or stored credential.
[Full erratum](ERRATUM_2026-11-09.md).

This is a dated incomplete report, not a final leaderboard result. Saved official
responses are SOURCE_VERIFIED; local analyses are PROJECT_REPORTED. The official
deadline was freshly confirmed before submission as2026-11-09T09:00:00Z.

## Exact source and before/after snapshots

[Standalone A3 source](../2026-11-09-rl7/d16/package-attempt3/bot.cpp):
SHA256 `94f0d426de787f7ed29a0ce87fa03fd3e0bae2ebb27c7d76548f4624f67ab4f8`,
95,540 UTF-16 units /220,400 UTF-8 bytes. Four exact9-bit networks; mandatory
greedy plan, complete three-model depth1 comparisons, then original depth2 when
time remains. Same16ms cooperative budget and20,000forward cap. This is an
explicit timed-policy change, not a claim of identical A2 timed behavior.

| Snapshot | Source / submission | Overall | Gold | Score | Completion |
|---|---|---:|---:|---:|---|
| Immediate before,9Nov01:29:34UTC | league3m `199c6a2d…` /41671805 |380/1039|228/428|14.89|100%, `in_progress=false`|
| Last saved D16 response, not final | A3 `94f0d426…` /41672652 |374/1040|220/429|15.47|63%, `in_progress=true`|
| Earlier league3m recheck,8Nov23:25UTC | same league3m /41671805 |368/1036|221/428|15.11|100%,92clean audited games|

The first row is the appropriate immediate baseline, not the older368snapshot.
Even completed sequential rankings would be moving, unpaired comparisons.
The partial D16 rank must not be interpreted as its final strength or percentile.

Evidence: [fresh before](progress-before-submit.json), [last saved progress](progress-004.json),
[submission request](submission-request.json), [accepted response](submission-response.json),
[source readback](accepted-source.json), [history after](submissions-after.json).
History retains all five earlier IDs and adds exactly one new ID. Test requests
did not overwrite the IDE. No further POST is authorized by this running report.

## Why A3 was admitted for this exploratory ranking

| Stage | Actual sample | Result / limitation |
|---|---|---|
| A1 useful-baseline repair |1156old-state roots,78technical/development games; frozen final stopped359/1200|One **control league3m** timeout;119candidate games clean. Full final gate failed. No relabeling as a successful final.|
| A1 official delivery |5technical games;104D16outputs|Clean official execution but zero completed search; baseline wall reached71.446ms.|
| A2 guardedGCCO3-only delivery |3valid fixed tests,104D16outputs|14completed depth2 evaluations, zero nonbaseline choices. Working-search gate failed. One extra wrong-map request and its correction are separately retained.|
| A3 contracts |1156unlimited depth2 parity roots,1156independent shallow oracles,328forced baselines,542interruption cases|Passed; actual delayed-input cases return useful baseline. One failed oracle-harness compile retained; bot source unchanged by its correction.|
| A3 fresh gross guard |96games /8new maps /3public opponents /both seats /candidate+control|All clean. A3 46/48 versus league3m41/48; paired gain+10.4167pp,95%CI[0,27.0833]. Small gross guard, **not proof of strength**.|
| A3 official fixed tests10/11/12 |102own outputs,17complete paired comparisons|One nonself nonbaseline choice, all clean, no emergency. No complete depth2 comparison; local search capacity did not fully transfer.|

[Prospective A3 amendment](AMENDMENT_A3.md),
[full local A3 report](../2026-11-09-rl7/d16/A3_REPORT.md),
[independent96-game audit](../2026-11-09-rl7/coordinator/d16-a3-audit.json),
[official A3 audit](tests-audit-a3-final.json),
[command and error ledger](COMMANDS.md).

## Incomplete battle-log audit

[audit-002.json](audit-002.json), generated01:42:19UTC, covers the **previous
20%-progress snapshot**, not all completed games visible in progress004/battles004:

| Measurement | Audited value |
|---|---:|
| Completed logs audited / missing in that snapshot |18/18 /0|
| Wins / draws / losses |10/0/8|
| Own errors / warnings / opponent error games / global failure games |0/0/0/0|
| Own outputs / emergency records |543/0|
| Complete same-tier paired-comparison turns |167|
| Completed depth2 evaluations / shallow evaluations |42/589|
| Nonbaseline choices |28, all depth1|
| Maximum internal through-flush wall / processCPU |22.097ms /22.026ms|
| Non-first turns exceeding20ms internal wall |2|

There are26saved full logs, already present in the previous publication;
battles004 lists57completed/1pending, with31completed-snapshot logs missing.
The table above remains the earlier18-game audit, not a new26-game audit. No final audit,
final source readback or final leaderboard/progress agreement is claimed.
Counts above come from the saved audit, not from interim narrative summaries.

Cooperative16ms is not a hard response-time guarantee. In game918861381,
seat1/turn18, the maximum measured atomic interval was7.538665ms, baseline
1.695861ms, parse0.050373ms and through-flush22.097ms. The interval's underlying
cause is UNKNOWN. Official errors were zero. Internal processCPU excludes
startup/pre-first-token/final stderr and is not official charged CPU.

## Remaining bounded work

The prior extra-retry permission question was unnecessary and is obsolete;
withdrawal was requested. OAuth is closed and no scheduled controls remain.
A later resumed authenticated GET-only check would obtain missing completed logs,
wait for100% and
`in_progress=false`, save final source/history/progress/leaderboard/battles,
and run `audit_ranking.py --snapshot final --require-complete` to a new receipt.
Never duplicate the already successful POST. No new authenticated session is
started by this correction. No training, A4, extra technical games or rollback.

The separate repository-publication request may preserve this honest running
snapshot now. It does not imply a completed ranking or any additional platform
authority. All old failures and original local evidence remain retained.
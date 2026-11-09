# Compact D16: public ranking complete, full battle audit pending

Updated **9 November2026**, with a fresh public leaderboard read at04:58UTC:
**365/1042 overall, Gold, score15.81,100%,notinprogress**. Public agent6866403
matches the accepted A3's saved logs. A3 was submitted exactly once as41672652
at01:31:03.050UTC; no source change, new submission or rollback followed.
[Public evidence](final-review/public-ranking.json).

All26available full logs have now been audited:15W/11L,802own outputs,
0official errors/warnings/emergencies. **This is not a complete final battle
audit**: additional logs and fresh authenticated source/history remain missing.
The new login flow expired without approval and was closed; no token was stored.
Public ranking completion is not the eventual final contest result.
Official responses are SOURCE_VERIFIED; analyses are PROJECT_REPORTED.
Deadline09November09:00UTC was reconfirmed in the official public FAQ.
[Rules/deliverables](../../../docs/CONTEST_DELIVERY.md).

The earlier two-failed-GET narrative was wrong: the exact first retry succeeded.
Its [dated erratum](ERRATUM_2026-11-09.md) and all raw records remain unchanged.

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
| Public website9Nov04:58UTC | A3 agent6866403, prior accepted41672652 |365/1042|Gold; website localRank201|15.81|100%, `inProgress=false`;full-log audit pending|
| Earlier saved private response004 | A3 `94f0d426…` /41672652 |374/1040|220/429|15.47|63%, `in_progress=true`,historical|
| Earlier league3m recheck,8Nov23:25UTC | same league3m /41671805 |368/1036|221/428|15.11|100%,92clean audited games|

The first row is the appropriate immediate baseline, not the older368snapshot.
Even completed sequential rankings would be moving, unpaired comparisons.
The completed public snapshot is15places/+0.92score above the immediate
before-snapshot, with a changing field; no causal superiority is established.
It corresponds to approximately top35.0% (65.0%below), not a final-contest percentile.
The server row update time04:26:37.705UTC differs from the04:58retrieval time.
Website localRank/divisionAgentsCount are not silently mapped to API league fields.

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

## Current available-log audit and its missing coverage

[audit-saved004.json](final-review/audit-saved004.json), generated04:57:10UTC,
reanalyses all26existing logs without new games or downloads:15W/11L,0own/
opponent/global errors or own warnings,802outputs,0emergencies,274complete
paired-comparison turns,65completedD2 evaluations and920shallow evaluations.
There are44nonbaseline selections, allD1. Maximum internal wall22.097ms,
processCPU22.026ms,2ordinaryturns above20ms. No official timeout observed.

The old saved battle-list004 contains57done/1pending and lacks31completed logs;
its outcomes36W/21L are list-only, not57fully audited games. The later completed
ranking's entire battle list has not been read. Public completion cannot certify
these missing logs or all later games as clean.

### Earlier18-game audit, retained for its own historical snapshot

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

The table above remains the earlier18-game audit. The separate new26-game audit
is described above; neither is a complete final audit. No fresh authenticated
source/history/progress readback is claimed.
Counts above come from the saved audit, not from interim narrative summaries.

Cooperative16ms is not a hard response-time guarantee. In game918861381,
seat1/turn18, the maximum measured atomic interval was7.538665ms, baseline
1.695861ms, parse0.050373ms and through-flush22.097ms. The interval's underlying
cause is UNKNOWN. Official errors were zero. Internal processCPU excludes
startup/pre-first-token/final stderr and is not official charged CPU.

## Remaining bounded work

The old extra-retry question is obsolete. The newly requested04:46login flow
expired without approval; the client exited normally and withdrawal of its
obsolete question was requested. UI removal was not confirmed. No active OAuth
or future scheduled control is retained.
Public ranking is complete, but a new authenticated GET-only session is still
needed for final source/history/progress/battles and all missing logs, followed
by `audit_ranking.py --snapshot final --require-complete` to a new receipt.
Never duplicate the already successful POST. No training, A4, extra technical
games or rollback. The private repository refresh preserves this exact partial
audit status rather than claiming full closure.
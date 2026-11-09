# Compact D16: completed ranking and full snapshot audit

Updated **9 November2026,05:38UTC**. Fresh authenticated final progress and
leaderboard agree: **371/1042 overall, Gold207/422,score15.77,100%,notinprogress**.
Source94f0d426 matches the frozen A3; all six history IDs are preserved, with
exactly one original A3 submission41672652 at01:31:03.050UTC.

**All98completed battles in the final snapshot are audited:55W/43L, zero
official technical errors/warnings.** All3209outputs have complete mandatory
baselines and no emergencies. A supplemental parser recovered five complete
JSON telemetry objects joined to subsequent stderr fragments without newlines;
the original flagged audit and all raw bytes are preserved. This is a parser
correction, not a bot repair or game replay. Coverage is the saved snapshot,
not future passive games or the eventual final contest result.

At05:39 a separately authorized fresh league3m control replaced D16; see the
[current comparison](../2026-11-09-final-choice/REPORT.md). D16 was not resubmitted.
Official responses are SOURCE_VERIFIED; analyses are PROJECT_REPORTED.
Deadline09November09:00UTC was reconfirmed by the authenticated challenge read.
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
| Authenticated full-audit snapshot,9Nov05:37UTC | A3 `94f0d426…` /41672652 |371/1042|207/422|15.77|100%, `in_progress=false`;98/98logs audited|
| Immediately before new league3m control,9Nov05:39UTC | Same A3 /41672652 |370/1042|206/422|15.77|Separate moving snapshot; source unchanged|
| Public website9Nov04:58UTC | A3 agent6866403, prior accepted41672652 |365/1042|Gold; website localRank201|15.81|100%, `inProgress=false`;full-log audit pending|
| Earlier saved private response004 | A3 `94f0d426…` /41672652 |374/1040|220/429|15.47|63%, `in_progress=true`,historical|
| Earlier league3m recheck,8Nov23:25UTC | same league3m /41671805 |368/1036|221/428|15.11|100%,92clean audited games|

The first row is the appropriate immediate deployment baseline, not the older368
snapshot. The05:37full-audit rank is9places/+0.88score above it, with a changing
field; no causal superiority is established. It corresponds to top35.6%
(approximately64.4th percentile by players below), not final-contest standing.
The earlier public365snapshot is retained as dated history, not today's final
private rank.
The server row update time04:26:37.705UTC differs from the04:58retrieval time.
Website localRank/divisionAgentsCount are not silently mapped to API league fields.

Evidence: [fresh before](progress-before-submit.json), [last saved progress](progress-004.json),
[submission request](submission-request.json), [accepted response](submission-response.json),
[source readback](accepted-source.json), [history after](submissions-after.json).
History retains all five earlier IDs and adds exactly one new ID. Test requests
did not overwrite the IDE. The later league3m control has its own new scope;
this report does not itself authorize any further POST.

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

## Complete authenticated snapshot audit

[Full audit](audit-final.json) verifies all98battle identities/outcomes, exact
accepted source, preserved history,100%/notinprogress and matching independent
leaderboard.55W43L, own/opponent/global errors and own warnings0. No pending
games or further battle pages; all98logs saved. Earlier snapshots remain intact.

The original line-based telemetry parser flagged five concatenated records.
[Supplemental audit](../2026-11-09-final-choice/d16-telemetry-supplement.json)
decodes exact JSON boundaries and verifies all3209contiguous turns. It preserves
every formerly parsed record, checks original post-flush marker coverage and
reuses the frozen safety/tier checks on normalized in-memory boundaries. Five
synthetic parser checks passed; no source/raw/old-auditor edit occurred.

| Measurement | Full snapshot |
|---|---:|
| Outputs / complete telemetry / emergency records |3209/3209/0|
| Nonbaseline choices |143, allD1|
| Same-tier paired-comparison turns |940|
| Complete shallow / depth2 evaluations |3418/247|
| Turns choosing through a completeD2comparison |17;0nonbaseline|
| Maximum internal through-flush wall / processCPU |22.097ms/22.026ms|
| Non-first turns>20ms internal wall |2;0official timeouts|

The earlier3204record/3415D1/246D2counts in the frozen audit are superseded only
for telemetry by this additive correction. Outcomes, official errors,143changed
actions and940paired turns are unchanged.

## Earlier26-log audit and its then-missing coverage

[audit-saved004.json](final-review/audit-saved004.json), generated04:57:10UTC,
reanalyses all26existing logs without new games or downloads:15W/11L,0own/
opponent/global errors or own warnings,802outputs,0emergencies,274complete
paired-comparison turns,65completedD2 evaluations and920shallow evaluations.
There are44nonbaseline selections, allD1. Maximum internal wall22.097ms,
processCPU22.026ms,2ordinaryturns above20ms. No official timeout observed.

The old saved battle-list004 contained57done/1pending and lacked31completed
logs at that time; its36W/21L were list-only then. The later98-log audit above
closes this coverage gap without relabeling the earlier26-log audit.

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

The table above remains the earlier18-game audit. Neither it nor the historical
26-game audit is the later complete98-game audit. Fresh authenticated readback
is claimed only in the dated completed section above.
Counts above come from the saved audit, not from interim narrative summaries.

Cooperative16ms is not a hard response-time guarantee. In game918861381,
seat1/turn18, the maximum measured atomic interval was7.538665ms, baseline
1.695861ms, parse0.050373ms and through-flush22.097ms. The interval's underlying
cause is UNKNOWN. Official errors were zero. Internal processCPU excludes
startup/pre-first-token/final stderr and is not official charged CPU.

## Closure and separate current assessment

The expired04:46login and obsolete retry question remain historical. A newly
confirmed session completed this audit05:37–05:38. No A4/training/extra technical
game or repeated D16POST occurred. The same current assessment then made one
separately requested league3m control submission; its result and session cleanup
belong to the [final-choice report](../2026-11-09-final-choice/REPORT.md).
New final-log evidence and this update are local, not yet a new Git publication.
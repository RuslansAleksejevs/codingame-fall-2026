# RL-v7: bounded D16 delivery and diversity pilot

## Current closure status — 9 November2026,06:00UTC

Both research lanes are closed. Diversity remains NO-GO. D16 A3 full authenticated
audit is complete:371/1042,Gold207/422,15.77;98logs55W43L,zero official errors,
3209complete telemetry records/zero emergency. A separately requested unchanged
league3m control41673756 completed433/1042/13.37 with93audited logs,zero own
errors/one opponent timeout. No new training or bot source. Recommend D16, but
league3m remains active; no automatic final restoration. OAuth/control closed.
[Completed comparison](../../../experiments/rl/2026-11-09-final-choice/REPORT.md) ·
[D16 report](../../../experiments/rl/2026-11-09-d16-live/REPORT.md) ·
[Final-entry rules](../../CONTEST_DELIVERY.md).

## Original finite plan and dated updates

Started9 November2026,00:00UTC. This is new authorized work, not a reopened
v4/v5/v6 experiment. Old failures, protocols, gates and archives stay unchanged.
No stronger deployable policy or completed D16 ranked result has been established.
Correction02:36UTC: diversity completed with NO-GO. Repaired D16A3 passed its
bounded delivery checks and was submitted once. Saved ranking63%, not final;
the first GET retry succeeded despite the later erroneous status summary.
OAuth is now closed; no new live check or experiment is started. Old protocols
and negative decisions remain unchanged.

| Lane | Question | Controlled scope | Output |
|---|---|---|---|
| D16 | Can compact search retain a useful completed baseline even after delayed input, and run reliably on the real platform? | Start from preserved9-bit D16; isolate baseline/budget repair; forced-delay/budget contracts, short dev, one frozen fresh comparison | Exact standalone source, technical evidence, local strength with uncertainty, then one authorized exploratory ranking submission |
| Diversity | Does broader position coverage transfer the teacher's advantage into the compact policy? | OriginalFP32D16 teacher; unchangedleague3m initialization/24,833 parameters; matched optimizer/update budgets for narrow versus broad datasets; two fixed training seeds if feasible | Real full-game broad–narrow and broad–baseline comparisons; go/no-go for subsequent scaling, not an automatic large campaign |

Broad-versus-narrow combines data quantity, map coverage and game-phase coverage;
it is not claimed to isolate all three effects. Teacher agreement and cross-entropy
are diagnostic, not a substitute for new full-game results. Rejected v5Round2 is
preserved, not the initialization for this new pilot. A future small student from
league3m is the provisional training recommendation, conditional on actual gains.

## Scope and coordination

Separate code/docs/evidence directories are owned by each lane. One coordinator
owns platform OAuth/API/submission and shared status/navigation. The subsequent
repository-refresh request separately authorizes a checked ordinary commit/push
to the existing private repository. No paid compute, IDE overwrite, mass
submission sweep or automatic rollback.
The research pilot itself is not authorized to replace the deployed bot.

New heavy-work caps:90min D16,120min diversity,15min coordination;25min maximum
lease. [The new wrapper](../../../code/rl/v7/compute_slot.py) shares the original
global lock but records a separate new-phase ledger. The old budgets are not reset.
All training, generation and timed arenas are serial. Local research stops by
**9November06:00UTC**, leaving three hours before the last verified09:00deadline.
Normal exit, timeout, mutual exclusion and incomplete-lease accounting tests passed.

Allocated seeds: D16dev72001–72012/final72101–72140; diversitytrain73001–73128
(initial proposed64),labeldev73201–73216,gamedev73301–73316,final73401–73440.
Canonical-content novelty is still required. No final maps before the respective
source/protocol freeze. Old40021–40100/65001–65040 reserves remain unopened.

## Reference and submission semantics

Preserved reference remains [league3m41671805](../../../experiments/rl/2026-11-08-leaderboard-recheck/REPORT.md):
8November23:25UTC368/1036 overall,Gold221/428,score15.11,52W/40L in92clean games.
Fresh9November01:29:34UTC league3m reference:380/1039,Gold228/428,score14.89.
It was then replaced by the one acceptedA3 submission41672652. Earlier A2source`d36aba4d…`
valid tests06/07/09 yield104safe baseline outputs,14complete evaluations and
zero nonbaseline selections. Test08's coordinator map-transcription mistake and
single correction are preserved; actual9technical games,8valid fixed checks.
[Platform ledger](../../../experiments/rl/2026-11-09-d16-live/COMMANDS.md).
Sequential live snapshots are not a paired causal estimate of strength.

The official [API reference](https://www.codingame.com/api/v1/docs/api), freshly
read9November00:03UTC, states that submitting replaces the user's current entry;
history retains prior versions. There is **one active ranked bot per participant
in this challenge**, with repeated versions subject to rate limits. Last actual
limits were5/5min,20/30min,40/hour,100/5hours; refresh before a new submission.
These are request quotas, not independent slots or a rule for final reranking.

Status: diversity scientific pilot COMPLETE/NO-GO; D16 delivery complete and
ranking audit incomplete, not a final live strength result.
Pilot800/800games are clean, but average broad−base is−3.125pp and designated
broad1 direct league3m is12/32. Final73401–73440 stays unopened; no additional
training or student deployment follows. [Report](../../../experiments/rl/2026-11-09-rl7/diversity/REPORT.md)
and [independent raw/statistical audit](../../../experiments/rl/2026-11-09-rl7/coordinator/pilot-audit.json).

Update01:17UTC: after the read-only diagnosis, one coordinated
[A3 repair](../../../experiments/rl/2026-11-09-d16-live/AMENDMENT_A3.md) is being
implemented: complete three-model depth1 comparisons first, then originaldepth2,
same weights/16ms/20k. This is a timed-policy change; A2's failed gate remains.
Exact unlimited-depth2/forced-stop contracts, one frozen96-game fresh guard on
72005–72012 and exactly three fixed official technical tests precede the one
authorized exploratory ranking. This paragraph records the01:17 prospective
plan, not a command to repeat those completed checks.

Updated02:36UTC from preserved evidence: A3source94f0d426…/95540UTF16 passed all fixed contracts,
96clean fresh gross-guard games (46/48 versus41/48;gainCI[0,27.0833]pp) and
exactly3official checks (102outputs/17paired/1nonselfdepth1change). One POST
accepted41672652 at01:31:03UTC; accepted-source/history verified. Last saved
progress00463%,374/1040/score15.47; final remainsUNKNOWN. Only the first GET-batch
attempt failed review availability; the exact retry succeeded. The later summary
was wrong. Exit-only cleanup02:30 closed OAuth without new HTTP requests.
26logs are saved,31completed-snapshot logs missing; no final audit claimed.
[Current platform report](../../../experiments/rl/2026-11-09-d16-live/REPORT.md) ·
[Dated correction](../../../experiments/rl/2026-11-09-d16-live/ERRATUM_2026-11-09.md).
No A4, further training/tests, automatic rollback or duplicate POST.
# Current project status

Final-delivery update9November06:42UTC: **D16 A3 accepted and current41673944**.
One explicitly authorized final replacement; downloaded source94f0d426 exact,
history retains all seven earlier entries. No new weights/source/training.
GitHub PRIVATE/main/research526ffee was verified after the preceding publication.
[Final-delivery result and audit](../experiments/rl/2026-11-09-final-delivery/REPORT.md).

Final audit07:08UTC complete: **100%/notinprogress,345progress versus346leaderboard
out of1043,Gold180/421,score16.84**. All90logs51W39L,zero own errors/warnings/
emergency. All2976outputs verified. Three opponent-warning losses, one also a
command-error game, remain in gross results. Separate live ordinal ranks differ
by one; exact rank equality is not asserted. OAuth closed after the full audit.

Earlier9November06:00UTC: full D16 and fresh unchanged league3m assessments
completed and recommended D16 A3. The explicit final choice was subsequently delivered above.
Scientific results are PROJECT_REPORTED; deployment facts come from saved official
responses. The repository is private.

**Diversity pilot completed, NO-GO:**800 clean fresh-map games; broader data did
not improve on unchanged league3m. **D16 A3's original41672652 is fully audited:**
source94f0d426… exact,371/1042,Gold207/422,score15.77,100%complete;98logs55W43L,
zero official errors. league3m41673756 was the explicitly requested fresh control;
it is now replaced by the chosen final D16, not an automatic rollback. A3 passed its bounded checks;
A1/A2 failed gates and the dated earlier reporting correction remain preserved.
[Finite scope and resource plan](rl/v7/PLAN.md). Old failures remain unchanged.

[Detailed experiment timeline](EXPERIMENT_TIMELINE.md) separates training,
repeated checks, fresh-map confirmation and platform ranking. Repository
publication preserves evidence; it does not establish a new experimental result.

## Deployed is not the same as selected locally

| Role | Exact artifact | Status |
|---|---|---|
| Current selected final entry | [D16 A3 source](../experiments/rl/2026-11-09-rl7/d16/package-attempt3/bot.cpp), submission `41673944` |100%/false,345–346/1043,16.84;90audited51W39L,0ownerrors; [full result and caveats](../experiments/rl/2026-11-09-final-delivery/REPORT.md) |
| Previous control, fully ranked/audited | [PPO-v2 league3m](../submissions/ppo-v2-league3m.cpp), submission `41673756` |433/1042,Gold269/422,13.37;93logs49W44L,0ownerrors/1opponenttimeout. Exact199c6a2d; preserved, no longer current |
| Earlier D16 evaluation | D16 A3, submission `41672652` | Full audit371/1042,Gold207/422,15.77,98logs55W43L,zero official errors; separate immediately-before read370/1042 |
| Preserved local reference | [Selected league3m policy](../code/rl/configs/selected-policy.json) | Best independently confirmed PPO-v2 checkpoint, not `final.pt` |
| Preserved league3m package | [ppo-v2-league3m.cpp](../submissions/ppo-v2-league3m.cpp) | Preserved byte-for-byte; the earlier recheck completed before the new D16 request |
| Strong recent offline teacher | [D16 report](../experiments/rl/2026-11-08-rl5/deadline-search/REPORT.md) | Independent local gate passed; no deployable unchanged-rule package |
| Compact student | [Round 2 package](../experiments/rl/2026-11-08-rl5/deadline-search/student/package/bot.cpp) | Technically valid export, strength gate failed; rejected |
| Compact D16 | [RL-v6 report](../experiments/rl/2026-11-08-rl6/compact-d16/REPORT.md) | Size/technical/dev passed; frozen final stopped at656/4200. Deployment rejected; not submitted |
| Historical heuristic | [code/bot.cpp](../code/bot.cpp) | v6-era baseline, not the latest submitted source |

The B2M source SHA256 is `b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214`.
The protected league3m checkpoint is `step-03002173/checkpoint.pt`, SHA256 `9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663`.

## Latest live evidence

The explicitly chosen final source was accepted once as41673944 at06:42:44.501UTC.
Immediate league3m before-snapshot:430/1043,Gold265/421,13.56,100%/notinprogress;
this does not replace its earlier full-audit433/1042snapshot. Source/current flag,
history and fresh Gold rules/deadline were checked. See the
[final-delivery report](../experiments/rl/2026-11-09-final-delivery/REPORT.md)
for this new entry's own ranking/log audit, separate from both evaluations below.

Fresh authenticated D16 progress/leaderboard agree at05:37:371/1042,Gold207/422,
15.77,100%/notinprogress. All98final-snapshot logs are audited:55W43L,zero own,
opponent or global technical errors/warnings. Exactsource/history verified.
[Full audit](../experiments/rl/2026-11-09-d16-live/audit-final.json).

Five complete JSON records were joined to later stderr fragments without
newlines. An additive parser correction preserves old raw/receipts and verifies
all3209outputs/complete baselines,0emergency,143D1changed moves,940paired turns,
3418D1/247D2evaluations. Internal wall maximum22.097ms/2ordinary>20ms is not
official charged CPU; zero official timeouts observed.
[Telemetry supplement](../experiments/rl/2026-11-09-final-choice/d16-telemetry-supplement.json).

The fresh league3m control completed05:59:433/1042,Gold269/422,13.37,100%/false.
All93logs audited49W44L,0own errors/warnings/global failures,1opponent timeout;
clean-only48W44L,3514outputs. Exact final source/history/leaderboard agree.
MODEL_INFERENCE: recommend D16, whose full-audit snapshot is62places/+2.40score
above the control. Moving unpaired results do not prove causal superiority.
At that comparison's completion league3m remained active and its OAuth/control
closed; no automatic switch occurred. The subsequent explicit final choice was
submitted separately above. [Completed comparison](../experiments/rl/2026-11-09-final-choice/REPORT.md).
That assessment evidence was published in the private526ffeerefresh.

### Earlier saved snapshots and reporting correction

The one D16 A3 POST was accepted01:31:03.050UTC as41672652; exact source/history
checks passed. Fresh league3m immediately before it was380/1039,Gold228/428,
score14.89,100% complete. Saved A3progress004 is63%,374/1040,score15.47.
It and its additional logs were already present in the previous publication.
The first GET-batch attempt could not pass unavailable review; its exact retry
succeeded. A later status-summary error overlooked that result. Exit-only cleanup
at02:30 returned the remaining unread responses and closed the OAuth process.
No new HTTP request, authentication, submission or rollback occurred in cleanup.
[Dated erratum and file identities](../experiments/rl/2026-11-09-d16-live/ERRATUM_2026-11-09.md).

At the02:36correction there were26saved full logs and only18had been audited.
The04:57offline audit covered all26then-available logs. The05:37full audit above
subsequently closed the missing-log/source/history gap. Neither old snapshot is
silently rewritten as the final98-game audit.

The saved audit002 covers18completed games in the previous20%-snapshot:
10W/8L,0official errors/warnings/emergencies,543outputs,167paired comparison
turns and28nonbaseline choices, all depth1. Two non-first internal wall times
exceed20ms; maximum22.097ms is not an official timeout/chargedCPU measurement.
[Running report and exact caveats](../experiments/rl/2026-11-09-d16-live/REPORT.md).

At8 November23:25UTC, league3m41671805 is **368/1036 overall**, Gold221/428,
score15.11,100% ranked and `in_progress=false`. All92 final-snapshot logs were
audited:52wins/40losses,0 own warnings/errors/timeouts,0 opponent/global failures.
Fresh B2M immediately before replacement was380/1036,Gold232/428,score14.59.
The observed change is12 overall places and0.52score points higher, not a
controlled paired effect or evidence of a large improvement. The contest continues.

[Completed league3m response archive and audit](../experiments/rl/2026-11-08-leaderboard-recheck/REPORT.md).
The older B2M07:10UTC result382/989,score12.90,41W/54L in95 clean games is
[historical evidence](../experiments/rl/2026-11-07-ppo-v3/live-submission/REPORT.md),
not the before-snapshot for today's new comparison.

The earlier requested live check selected unchanged league3m, source
`199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1`.
The one submission41671805 was accepted at23:04:07UTC; exact initial/final
source readback passed, as did one technical boss test (clean loss). Submission
history has exactly one newID and retains all prior entries. That earlier OAuth
session/control closed. The separately authorized D16 session above is distinct.
[Scope and selection](../experiments/rl/2026-11-08-leaderboard-recheck/REQUEST.md).

## Completed research

The new RL-v7 diversity pilot trained four new students, each800updates from
unchanged league3m. Narrow205roots/12maps versus broad2011roots/63maps combines
quantity, map and phase coverage; it does not isolate one factor. Full800clean
games on16new maps: two-seed average broad−narrow+1.5625pp [−2.6042,+6.25], but
broad−base−3.125pp [−7.2917,0]. Designated broad1 beat league3m12/32 (37.5%).
Several prospective promise conditions failed; final73401–73440 stays unopened,
no further optimization or student submission. This rejects scaling this tested
recipe, not the general value of diverse data.
[Report](../experiments/rl/2026-11-09-rl7/diversity/REPORT.md) ·
[Independent raw/paired-statistics audit](../experiments/rl/2026-11-09-rl7/coordinator/pilot-audit.json).

The three RL-v4 approaches—deliberate exploiters, difficult-start curriculum and initial search—failed their declared continuation/admission criteria. The separate RL-v5 follow-up tested a bounded search teacher and then, conditionally, one compact distillation pilot.

- Teacher: 1,120 games on 40 fresh maps; external gain +5.4167pp, 95% paired interval [+1.25, +9.5833]; no technical errors.
- Student: 1,680 games on 40 other fresh maps; external gain −2.9167pp, 95% interval [−8.75, +2.0833]; 30/80 direct wins against league3m. Student-minus-teacher −9.1667pp, [−15.4167, −3.75]. Rejected.
- All 2,918 new RL-v5 arena games, both student checkpoints, protocols, original failures and independent audits are retained.

No new deployable improvement was established. Limited data, model capacity and objective mismatch are possible explanations for distillation failure, **not identified causes**.

The separate RL-v6 phase packed all four unique D16 networks into94,123UTF16
units at9bits, source `22ccbbe3…`. Its504-game development passed admission.
The frozen4,200-game final stopped after656 games because one input-read wall
interval17.77ms consumed the16ms internal budget before a baseline was ready;
the program emitted emergency WAIT. That game was an engine-valid win, not an
official timeout. The input-delay cause is UNKNOWN. Partial paired intervals
include zero; strength is INCONCLUSIVE and the zero-emergency gate rejected
deployment. All1,166 new games and the negative result are preserved, with
independent raw/CI/archive audits. No policy training or platform call occurred
in that phase. [Full report](../experiments/rl/2026-11-08-rl6/compact-d16/REPORT.md).

## Deadline and boundaries

Official deadline: **2026-11-09T09:00:00Z**, confirmed before the D16 POST and
again in the current public contest FAQ. [Final delivery checklist and rules
caveats](CONTEST_DELIVERY.md) · [Candidate portfolio](BOT_PORTFOLIO.md).
The new finite v7 phase has a06UTC local research cutoff; older02UTC guards remain
historical and unchanged. Both v7 experimental lanes are now closed; publication
and the already-requested ranking audit do not start more research.

No new paid compute, contest submission, rollback or IDE overwrite is implied
by preserving repository changes. No further bot version or automatic rollback
is selected. Final maps40001–40020 have been opened,
16 played and15 completed;40017–40020 were generated only. **40021–40100 and
65001–65040 remain unopened.** All prior research processes and continuations
were closed. New D16final72121–72140 and diversityfinal73401–73440 remain unopened.
CHECKSUMS describes the tracked publication snapshot; original/export archive
ledgers distinguish portable copies from untouched historical source bytes.
# Current project status

Updated 8 November 2026. Scientific results are PROJECT_REPORTED; deployment facts are sourced from the saved official API responses. The repository is private.

## Deployed is not the same as selected locally

| Role | Exact artifact | Status |
|---|---|---|
| Last confirmed deployed | [PPO-v3 B2M](../experiments/rl/2026-11-07-ppo-v3/handoff-b2m/bot.cpp), submission `41665776` | Submitted 8 November; no subsequent replacement or rollback in this work |
| Preserved local reference | [Selected league3m policy](../code/rl/configs/selected-policy.json) | Best independently confirmed PPO-v2 checkpoint, not `final.pt` |
| Published fallback source | [ppo-v2-league3m.cpp](../submissions/ppo-v2-league3m.cpp) | Preserved byte-for-byte; not automatically restored on the platform |
| Strong recent offline teacher | [D16 report](../experiments/rl/2026-11-08-rl5/deadline-search/REPORT.md) | Independent local gate passed; no deployable unchanged-rule package |
| Compact student | [Round 2 package](../experiments/rl/2026-11-08-rl5/deadline-search/student/package/bot.cpp) | Technically valid export, strength gate failed; rejected |
| Historical heuristic | [code/bot.cpp](../code/bot.cpp) | v6-era baseline, not the latest submitted source |

The B2M source SHA256 is `b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214`.
The protected league3m checkpoint is `step-03002173/checkpoint.pt`, SHA256 `9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663`.

## Latest live evidence

At 8 November 07:10 UTC the completed B2M ranking snapshot was **382/989 overall**, Gold 243/392, score 12.90. Its 95 recorded battles were 41 wins / 54 losses, with no technical errors. Immediately before replacement, league3m was 356/987 with score 13.51. These moving snapshots are not a controlled paired experiment, and they do not prove a particular algorithm caused the difference. They also do not establish a live improvement.

[Official-response archive and audit](../experiments/rl/2026-11-07-ppo-v3/live-submission/REPORT.md). No fresh ranking query or platform mutation accompanies repository maintenance.

## Completed research

The three RL-v4 approaches—deliberate exploiters, difficult-start curriculum and initial search—failed their declared continuation/admission criteria. The separate RL-v5 follow-up tested a bounded search teacher and then, conditionally, one compact distillation pilot.

- Teacher: 1,120 games on 40 fresh maps; external gain +5.4167pp, 95% paired interval [+1.25, +9.5833]; no technical errors.
- Student: 1,680 games on 40 other fresh maps; external gain −2.9167pp, 95% interval [−8.75, +2.0833]; 30/80 direct wins against league3m. Student-minus-teacher −9.1667pp, [−15.4167, −3.75]. Rejected.
- All 2,918 new RL-v5 arena games, both student checkpoints, protocols, original failures and independent audits are retained.

No new deployable improvement was established. Limited data, model capacity and objective mismatch are possible explanations for distillation failure, **not identified causes**.

## Deadline and boundaries

Saved official deadline: **2026-11-09T09:00:00Z**. The earlier campaign research cutoff was 02:00 UTC, preserving 7 hours for final checks. Refresh the official status before any new platform action.

No new paid compute, contest submission, rollback or IDE overwrite is implied by merging repository branches. Global final partitions 40001–40100 and 65001–65040 remain unopened. All prior research processes and continuations were closed.
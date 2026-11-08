# B2M submitted and ranked: no live improvement

Verified2026-11-08T07:11:47Z. The complete-ranking snapshot was captured at
07:10:08UTC. Submission41665776 is active,100% ranked, `in_progress=false`.
All95 completed battle logs were downloaded and audited:41 wins,0 draws,
54 losses, no own warnings/errors/timeouts, no opponent technical failures and
no global failures. No battle log is missing and the snapshot has no pending
games. See [complete audit](audit-final.json).

## Result

| Metric | Previous league3m before replacement | B2M after ranking |
|---|---:|---:|
| Submission | 41657621 | 41665776 |
| Overall rank | 356/987 | 382/989 |
| Gold rank | 217/391 | 243/392 |
| Score | 13.51 | 12.90 |

Sources: [before](progress-before.json), [after](progress-009.json).
B2M finished26 positions lower and0.61 score points lower in these snapshots.
The field and opponents changed, so this is not a paired causal estimate or
proof of statistically significant regression. It nevertheless provides no
live evidence for promoting B2M over the preserved league3m baseline. Earlier
four paired platform replays were also2/4 for B2M versus3/4 for league3m; those
few games were explicitly not an independent strength test.

Conclusion: runtime compatibility is good, but the development-panel gain did
not translate into a better observed leaderboard result. Recommendation: prefer
the preserved league3m fallback if choosing a conservative deployed version.
**No rollback was performed. B2M remains active until a separate decision.**
No additional training, candidate search or background monitoring was started.

## Exact submission and preservation

The authorized single POST returned201; its response is preserved in
[submission-response.json](submission-response.json). The accepted source
download matches [the exact B2M package](../handoff-b2m/bot.cpp), SHA256
`b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214`.
This is seedB step2,000,416, not an unevaluated later recovery checkpoint.
The package contains24,833 float32 parameters and needs no external weights.
The official submission time is approximately2026-11-08T06:51:33Z; API
fractional timestamps vary slightly between GETs, so identities and exact source
hashes, rather than full metadata byte equality, establish preservation.

[Final submission history](submissions-final.json) shows exactly one added
submission, current41665776, and preserves all previous IDs. Local fallback
`submissions/ppo-v2-league3m.cpp` still has SHA256
`199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1`.
The selected-policy manifest remains the independently-tested old baseline;
the active experimental deployment is recorded here, not silently promoted in
the local selection configuration.

## Technical audit and reproducibility

The95 recorded battles contain3,584 own turn outputs. Maximum reported internal
planning time is11,291microseconds. This is **not total platform CPU time**;
the stronger observed runtime fact is that all95 games had no timeout or other
reported technical failure. Each raw battle ID and own agent6862440 matches its
submission battle-list record, and outcomes agree between list and full log.
The final page contains95 games with no pagination cursor.

```sh
python3 code/platform/analyze_v3_submission.py --require-complete --out experiments/rl/2026-11-07-ppo-v3/live-submission/audit-final.json
```

The audit includes raw-log and analyzer hashes, the accepted source hash,
per-game outcomes/timing/errors, complete snapshot coverage and submission
history checks. Four synthetic cases passed: own timeout, opponent crash,
normal defeat and invalid command. Regression checks retained the ten earlier
platform-test outcomes. Final assertions passed for ranking completion,
95/95 logs,41/54 outcomes, zero technical events and one new submission only.

## Boundaries and completion

The exact contest deadline was reverified before submission:
2026-11-09T09:00:00Z (01:00PST). This is an ongoing-contest snapshot, not the
final contest result. Submission does not overwrite the IDE draft; no IDE
overwrite request was sent. Old source and checkpoints remain preserved.

The authenticated API client236 exited cleanly after the audit; credentials
existed only in process memory. No pending scheduled messages remain. Research
was not resumed, the reserved independent final100 maps were not opened, and
the cancelled2,200-game final was not retroactively claimed complete. No paid
resource, Git commit/push or repository publication was performed. New code,
logs and conclusions remain local in the original checkout.

## Follow-up diagnosis, 2026-11-08

The saved commands of these same95 games were reconstructed without new play or
training. All final scores and3,543 own army/income observations matched. In52/54
losses versus17/41 wins, the bot was behind in army after ten turns; all95 games
were still running at that point. This is an association, not proof of the cause
or a justification for army-size reward shaping. See [diagnosis summary](diagnosis-summary.json)
and the [new RL proposals](../../../../docs/rl/POST_V3.md).
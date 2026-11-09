# Selected final D16 entry and repository publication

Completed9November2026,07:08UTC: **D16 A3 final submission41673944 accepted,
current,100% ranked and fully audited**. One POST returned201 at06:42:44.501UTC;
initial/final downloaded source and current flag match exactly. Final history has
all seven earlier entries plus this one, with no further submission or rollback.

The completed snapshot is **345/1043 by progress;346/1043 by the subsequent
leaderboard read,Gold,score16.84**, league180/421. Both endpoints report100%,
the same agent6867113/score/league/total; progress has in_progress=false. The
earlier paired reads were345 versus344. Exact ordinal-rank equality is therefore
**not claimed**; all responses are preserved. This is approximately the top33.1%
(about67th percentile), not final contest standings or a fixed rank guarantee.

All **90/90 completed final-snapshot logs** are saved and audited: **51wins,
39losses, zero own errors/warnings/global failures**. No missing, pending or
further battle-list page. One opponent command-error game and three opponent
warning games are disclosed separately below. [Full audit](audit-final.json) ·
[Completion record](COMPLETION.json).

The selected unchanged A3 source SHA256 is
`94f0d426de787f7ed29a0ce87fa03fd3e0bae2ebb27c7d76548f4624f67ab4f8`;
the local hash was freshly verified. Its completed snapshot371/1042/15.77 and
98clean own-execution logs compare with fresh league3m433/1042/13.37 and93logs
without own errors. Different maps/opponents and a changing field make this a
practical final choice, not proof of causal superiority.
[Completed comparison](../2026-11-09-final-choice/REPORT.md).

## Dated comparison and limitations

| Entry / snapshot | Overall rank / score | Audit scope |
|---|---|---|
| Original D16 A3 evaluation,05:37UTC |371/1042 /15.77 |98logs,55W43L,zero official technical events |
| Fresh league3m control,05:59UTC |433/1042 /13.37 |93logs,49W44L,zero own errors;one opponent timeout |
| league3m immediately before final replacement,06:41UTC |430/1043 /13.56 |Fresh state/source/history read, not a new full game audit |
| Final selected D16 A3,07:05–07:06UTC |345progress /346leaderboard out of1043 /16.84 |90logs,51W39L,zero own errors;opponent events retained |

Against the immediate before-snapshot the final D16 is84–85places and3.28score
points higher. Maps/opponents, time and rating state differ: this is not a paired
causal improvement estimate. The same source was selected before this run; no
new candidate was chosen from intermediate results or retrained afterwards.

## Technical audit

All2976outputs have exact parsed telemetry, completed baseline and zero emergency
WAIT. There are3113complete depth1 and202complete depth2 evaluations,859paired
comparison turns,19complete depth2-comparison turns.128nonbaseline choices:
126depth1 and2depth2. Maximum internal through-flush wall19.8011ms, CPU19.472ms;
zero non-first turns above20ms. These internal measurements exclude part of the
platform's whole-turn accounting and are not an absolute real-time guarantee.

Opponent nonofare6849488 in918951945 issued invalid ATTACK tasks; the log contains
the summarized error "3 more errors of that type" and warnings. It is retained
as our loss, not described as a timeout or our failure. Opponent warnings also
occur in918954142 and918951810, both losses. Gross51W39L is the main result;
excluding error games only gives51W38L, excluding all opponent-warning games
gives51W36L. Own errors/warnings are zero in every one of the90games.

The original generic auditor requires exact rank equality across separate live
reads. The additive [final auditor](audit_final.py) instead preserves and explicitly
flags the observed one-place discrepancy while independently requiring100%, no
pending/missing logs, exact final source/current/history, all game/seat/outcome
identities and matching score/league/total/agent. Its broad equality flag is false;
the separate source/history/battle identity and completion checks pass. No raw
field was normalized to force agreement. No additional polls searched for a more
favorable rank, and no scientific gate or old audit was changed.

## Repository

The06:28refresh completed: **PRIVATE**, defaultmain, local/remote main and
rl/research526ffee59226ca1f3900eadbd92a444570cc001b. It preserved both completed
candidate assessments, with4410tracked files/4409checksums/136entrylinks passing.
The new publication payload contains this completed report, all90new logs,
raw state/source/history/leaderboard records, additive auditors and current
English navigation. It uses a checked ordinary private commit/non-force push;
the exact post-push remote commit verification is reported at handoff, separately
from the commit containing this report. Old evidence and source files are unchanged.
657unrelated untracked suffix copies were observed; they are preserved and
excluded from publication. No old model, archive or rejected result is removed.

## Participant actions and closure

Login, exact final submission,100%ranking and the full saved-snapshot audit are
done. OAuth exited cleanly after the audit; credentials were never stored.
No further participant action is currently required. Finite publication controls
are cleared at handoff; no new research or post-deadline monitoring is started.
Fresh06:41challenge/limits/Gold rules agreed with the official FAQ deadline
9November09:00UTC. No extra mandatory paper/video/
publicGitHub upload was found; see [delivery rules](../../../docs/CONTEST_DELIVERY.md)
for exact sources and disclosed rules uncertainty. After accepted delivery,
do not replace the final bot with an older candidate or unsent IDE buffer.

Environment for this evidence audit: Python3.14.6, Git2.49.0. No new training,
local arena replay, paid compute/API purchase or source change. External compute
spend0; subscription usage/electricity are unmeasured. Historical negative gates
and the old98-game D16/93-game league3m assessments remain separate and unchanged.

[Authorized finite scope](REQUEST.md) · [Commands and corrections](COMMANDS.md).
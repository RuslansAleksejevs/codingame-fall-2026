# Requested timeline and one leaderboard check

Authorization: USER_CONFIRMED, 8 November 2026, new task in the original checkout.
Prepare an English, evidence-linked experiment timeline, select a sensible ready
trained bot, run it on the contest leaderboard and return a short result. Stop
after that result for the next decision.

This authorizes one selected competitive submission if necessary. It does not
authorize new training, architecture changes, a candidate sweep, automatic
rollback, IDE overwrite, paid resources, Git commit/push or another campaign.
The prior research phases remain closed. Existing sources and evidence stay intact.

## Selection before new platform results

As of 2026-11-08T22:42:36Z. Classification: MODEL_INFERENCE from the historical
reports; the artifact hashes below were checked again locally.

Selected: unchanged PPO-v2 league3m, full Gold action profile, standalone C++17.

| Artifact | SHA256 |
|---|---|
| `submissions/ppo-v2-league3m.cpp` | `199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1` |
| `league-a/step-03002173/checkpoint.pt` | `9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663` |
| `league-a/step-03002173/weights.txt` | `dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb` |
| Preserved B2M source | `b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214` |

League3m has a frozen independent 100-map, 1,800-clean-game confirmation and a
previously verified platform package. B2M has development gains but no completed
independent final; its earlier live snapshot did not demonstrate improvement.
Those snapshots are unpaired, historical observations, not causal proof that
league3m is stronger today. The original D16 teacher is not packaged; the v5
student and v6 compact D16 failed their respective acceptance criteria.

Sources: [PPO-v2](../2026-11-06-ppo-v2/REPORT.md),
[original package/live report](../2026-11-06-live-ppo-v2/REPORT.md),
[B2M live report](../2026-11-07-ppo-v3/live-submission/REPORT.md),
[v5](../2026-11-08-rl5/deadline-search/REPORT.md),
[v6](../2026-11-08-rl6/compact-d16/REPORT.md).

## Execution safeguards

Use the existing task-scoped OAuth client with read/play/submit. Credentials stay
only in process memory; never archive tokens, device credentials or login codes.
Before mutation: refresh official challenge, limits, submission history/progress
and accepted source. Verify deadline, source size, C++ and full-action compatibility.
If the selected source is already active, inspect it without a duplicate submit.
An unknown POST response requires a GET reconciliation before any further action.
After acceptance: exact source readback, complete ranking and complete saved
battle-snapshot audit. No change of candidate after observing the result.

The new timeline and evidence are local. GitHub is not updated by this task.
External compute spend: 0. No local strength experiment is planned here.
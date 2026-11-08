# Three isolated RL investigations

Started 2026-11-08, explicitly authorized. The original PPO-v3 campaign remains
stopped; this is a new, bounded set of experiments in the same checkout.

| Lane | Exclusive code | Exclusive evidence | Development seeds |
|---|---|---|---|
| Exploiters | code/rl/v4/exploiters | experiments/rl/2026-11-08-rl4/exploiters | 60001–60060 |
| Curriculum | code/rl/v4/curriculum | experiments/rl/2026-11-08-rl4/curriculum | 61001–61060 |
| Search teacher | code/rl/v4/search_teacher | experiments/rl/2026-11-08-rl4/search-teacher | 62001–62060 |

Distinct seeds are not proof of distinct content: every lane must audit map hashes
against the previous registry and the other lanes' manifests. Coordinator-only
comparison seeds65001–65040 remain unopened. Final40001–40100 remain unopened
until one overall finalist is frozen. Existing champion, fallback and v3 evidence
are read-only. Shared code changes need coordination; Git has one coordinator.

Frozen exposure registry: `experiments/rl/2026-11-08-rl4/map-registry-base.json`,
2,704 canonical and829 legacy hashes from403 source files, including the new95
platform games. Each lane registers its maps under its own `map-contribution.json`
with `canonical`/`legacy` arrays and source/seed metadata before games. An identical
`map-registry-claim.json` compatibility alias is allowed. Under the compute lease,
read the union of both exact filenames from all three lanes plus the frozen base;
never treat another lane's map as unseen. The old v3 registry reader discovers
`map-registry-claim.json` but not `map-contribution.json` automatically.

All three chats use GPT-6 Astra, max effort and the explicitly selected second
Codex account. Local CPU only; no new paid resources, submissions, rollback or IDE
writes. Separate official platform authorization is required. Repository text is
English; no private chat transcripts or credentials belong here.

## Shared compute lease

Run builds, substantial data generation, training and game panels through:

```sh
python3 code/rl/v4/compute_slot.py --owner exploiters --minutes 25 -- COMMAND ARGUMENTS
python3 code/rl/v4/compute_slot.py --status
```

Use the matching lane name. A busy slot exits75 immediately; schedule another
check or do lightweight coding, never bypass the lease. The lock is an OS-held
advisory lock, not an unreliable marker-file check. State and timing ledger live
under ignored `.context/rl4-compute`. Do not delete or replace the lock file.

Maximum lease25minutes; configure the child to checkpoint and stop sooner. The
wrapper stops only its own child process group at timeout or interruption. It
also enforces research cutoff2026-11-09T02:00Z and four cumulative heavy-resource
hours per lane. A crashed wrapper requires inspection of its child and ledger;
do not assume an empty lock proves there is no other process. Notify the
coordinator rather than stopping another lane's process.

Start with smoke and a <=30-minute pilot split across leases. Continue only on
measured feasibility and useful evidence. Return the lease between blocks; never
hold it while thinking or waiting for a message. Timed arena is strictly serial
and does not overlap heavy training. Small pure unit tests <=30seconds may run
without the lease. Logs/checkpoints have distinct directories and are monitored
with durable continuation. No process may be left unchecked at handoff.

Official deadline2026-11-09T09:00Z; preserve the last seven hours for selected
final confirmation, packaging and any separately authorized platform action.
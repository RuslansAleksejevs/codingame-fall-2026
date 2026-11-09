# League3m leaderboard recheck: complete, small snapshot gain

**PPO-v2 league3m, submission41671805, is fully ranked:368/1036 overall,
Gold221/428, score15.11.** The final saved API/leaderboard snapshot is from
8 November2026, approximately23:25UTC; the full audit completed at23:27:02UTC.
Ranking is100%, `in_progress=false`, with no promotion pending.

All **92 completed battle logs** were downloaded and checked: **52 wins,
0 draws,40 losses**. No own warnings, invalid commands, crashes or timeouts;
no opponent technical failures or global failures. No pending game, missing
log or unconsumed pagination cursor exists in this frozen snapshot.

Official deployment facts are SOURCE_VERIFIED from the saved API responses;
the log aggregation is PROJECT_REPORTED. Interpretation below is MODEL_INFERENCE.

## Before and after this one selected submission

| Metric | B2M immediately before replacement | League3m after complete ranking |
|---|---:|---:|
| Submission | 41665776 | 41671805 |
| Overall rank | 380/1036 | **368/1036** |
| Gold rank | 232/428 | **221/428** |
| Score | 14.59 | **15.11** |
| Ranking complete | Yes | Yes |

Sources: [before](progress-before.json), [after](progress-final.json),
[public leaderboard response](leaderboard-final.json), [complete audit](audit-final.json).

The final snapshot is12 overall places and0.52 score points higher. This is a
small observed improvement, not a breakthrough or a controlled estimate of
algorithm strength: opponents and the live field change, and the games are not
paired. The first100% read was369th; seconds later both final progress and the
leaderboard showed368th with the same score. Both reads are retained. This is
an ongoing-contest snapshot, not the final result at the9November09:00UTC deadline.

## Choice and exact identity

The unchanged league3m package was chosen **before** new results, for its
independent100-map/1,800-clean-game confirmation and prior working platform
deployment. B2M had development gains but no completed independent final; the
original D16 teacher was not packaged, and the v5 student/v6 compact candidate
failed their respective gates. See [selection and authorization](REQUEST.md).
This was one newly authorized choice, not an automatic rollback of an earlier task.

Source: [ppo-v2-league3m.cpp](../../../submissions/ppo-v2-league3m.cpp).
SHA256:`199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1`.
80,247UTF16 units /186,203UTF8 bytes,24,833 exact float32 parameters.
No architecture, weights, strategy or source change was made.

Fresh challenge/limits reads confirmed registered/ongoing/Gold, full actions,
C++,1000ms first turn and50ms later turns, and the deadline. The fresh reference
did not publish a numeric source-size cap; actual acceptance and compilation of
this exact package were verified instead. One technical test918805589 lost
cleanly toGoldBoss: compatibility evidence, not an independent strength test.
All IDE overwrite/show flags were false.

The single [submission POST](submission-request.json) returned
[201/41671805](submission-response.json), at approximately23:04:07UTC.
[Initial](accepted-source.json) and [final](accepted-source-final.json) readbacks
match the exact selected source. [Final history](submissions-final.json)
contains exactly one new submission and all four previous IDs; league3m remains
the current bot. API fractional submission timestamps drift slightly between
reads, so identities and source hashes are compared, not full JSON byte equality.

## Audit, runtime and preserved evidence

```sh
python3 experiments/rl/2026-11-08-leaderboard-recheck/audit.py --snapshot final --require-complete --out experiments/rl/2026-11-08-leaderboard-recheck/audit-final.json
```

The command above is the executed receipt; it refuses an existing output path.
For another offline inspection, choose a new output filename. No game is replayed.

The audit checks all92 game identities, own/opponent agent identities, battle-list
versus log outcomes, complete coverage, exact source, one-new-submission history
and agreement with the100%-ranked leaderboard entry. It reuses the preserved
platform-log parser without modifying that older code. Every game's raw SHA and
outcome are included. Own agent6865954;3,373 own turn outputs; maximum internal
`plan_us`16,693µs. This is **not total platform CPU time**; zero recorded platform
timeouts is the relevant observed reliability result.

Intermediate progress/battle snapshots and their audits remain separate;
they are not additional independent samples. [Commands](COMMANDS.md) retain
the initial expired OAuth, sandbox limitations, successful reviewed checks and
the technical test. Codes/tokens were not archived; credentials existed only in
process memory. The authenticated client exited cleanly after the final reads,
and no pending scheduled checks remain.

## Timeline, publication and stopping point

[The detailed timeline](../../../docs/EXPERIMENT_TIMELINE.md) now covers all
significant stages, including failures, corrections, fresh/reused maps and this
separate live result. README/STATUS/RL navigation are consistent with it.

All new material is **local only**. No commit, push, remote change, repacking or
deletion of historical evidence was performed. Last verified published integration:
`531c593`, throughv5. The root CHECKSUMS manifest still belongs to that published
tracked snapshot; the new local documentation audit supplies current hashes.
The publication-oriented staged-tree checker is not claimed to pass for these
intentionally untracked additions. RL-v6 remains local and preserved.

No new training, local strength tournament, paid resource, IDE overwrite,
second submission, automatic rollback or next campaign was run. External
compute spend0; subscription quota/electricity unmeasured. Both requested
deliverables are complete; further action awaits a new decision.
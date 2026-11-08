# RL-v5 deadline-bounded complete-plan search: pre-result protocol

Recorded 2026-11-08, before any new compilation, diagnostic or match.
Authorization: USER_CONFIRMED bounded independent experiment. Design/gates:
MODEL_INFERENCE. Measurements will be PROJECT_REPORTED, never platform results
unless obtained from the official read/play API.

## Scope and preservation

One isolated implementation, no old PPO-v3 or RL-v4 continuation. Reuse frozen
interfaces and exact simulator read-only. No shared-source edits, Git mutations,
ranking submission, rollback, IDE writes, paid resources or additional agents.
All portable records use English and repository-relative paths. The active B2M
submission is untouched. Global maps40001-40100 and65001-65040 remain closed.

All compilation, timing, games, replay and archive work uses the existing
`code/rl/v4/compute_slot.py --owner search-teacher --minutes 25 -- ...` lease,
with its existing state and four-hour cumulative owner cap. Initial owner usage
1379.5969817093574s. This phase adds at most10800s, including failures/archives.
Research stop2026-11-09T02:00:00Z; saved official deadline09:00Z (refresh before
any platform stage). Zero external spend. No lease held for network/user waits.

Protected SHA256 identities:

- league3m checkpoint:9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663
- league3m weights:dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb
- packaged league3m:199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1
- packaged B2M:b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214

## A. Technical design and finite diagnostics

Declare ONE design, D16; no strength-driven budget/architecture sweep. Preserve
the old depth2/four-proposal/.15,.35,.7/three-response/.5mean+.5minimum/.02margin/
.995gamma decision rule when unlimited. Timed D16 stops optional work16ms after
the first score token has been read (input preceding that instant is explicitly
unmeasured). Poll before/after feature computation, each neural inference,
decoder construction, candidate list generation, cloning and exact simulation.
Also cap at20000 choice evaluations. Keep an immutable completed greedy plan;
never replace it with an incompletely scored candidate. WAIT exists immediately
as an emergency legal plan if baseline generation itself cannot finish. Record
that separately; it is not a successful greedy plan. One output line per turn,
semicolon-separated commands, flush before diagnostics. Never emit early
replacement outputs or relax the referee1000/50ms limits.

This is conservative cooperative stopping, NOT a hard real-time guarantee on
a preemptive host. Bounded native operations and OS scheduling remain atomic.
Measure parsing after the first token, baseline, response/proposal/future-policy
decoding, features, forwards, cloning, simulation, value, serialization/flush,
total through flush, and post-flush instrumentation. Include raw failed turns,
not only accepted-turn row statistics. Timing overlap of nested counters is
explicit; do not add overlapping components.

Known failures62041/v6/seat0/turn24,62044/Lacoz/seat0/turn24 and
62046/Lacoz/seat0/turn3 are disclosed regression fixtures, NEVER fresh evidence.
Bounded diagnostics: replay each saved prefix, compare old/unlimited-new and
timed-new on both perspectives, repeat each failed root10times for component
profiles; six original-referee regression games (each map/opponent both seats).
Synthetic exhausted-deadline checks must return WAIT or the saved baseline,
never a partially evaluated alternative. Validate absolute ordering, full
input consumption, settled hidden state, root immutability, legal commands,
native/standalone unlimited parity and exact Java/native saved trajectories.

Development allocation70001-70020 is reserved before generation; use exactly
70001-70004 for a48-game technical smoke (search/control x Lacoz/new/old khoufou
x both seats). Do not select by its winrates. D16 is selected solely if contracts
pass, own/control errors=0, emergency baseline fallbacks=0 and measured
through-flush maximum<40ms on diagnostic/smoke turns. Otherwise stop and report;
no alternative configuration is automatically authorized by this protocol.

## B. Fresh independent confirmation

Reserve70101-70140 before generation. Audit canonical nodes/units/edges and
legacy property hashes against ALL exposed manifests, archived platform maps,
v4 branch contributions/claims and local dev claims. Record sources/hashes.
On any overlap stop and report; do not silently substitute maps. Confirmation
generation happens only after the candidate/analyzer freeze. The remaining
development allocation is not a power-extension reserve.

Freeze source/config/models/analyzer and exact ordered schedule. Forty maps,
both seats, search and unchanged greedy control against Lacoz7f190183,
newkhoufou070bc128, oldkhoufou372c1cd6, v6, BC, directleague3m and separate B2M:
1120 games. Comparable search/control executable, identical input/output path,
control uses unchanged greedy actor without optional search. Direct league3m
and B2M use the preserved packaged sources. Four10-map chunks are scheduling
only, <=25min leases. Alternate search/control order by map/opponent/seat and
rotate opponent order; serial matches, no concurrent training/timing.

No intermediate strength analysis, candidate changes, sample additions or
threshold changes. A frozen technical gate failure stops the series promptly;
report the incomplete predeclared sample as rejected, not a smaller valid test.

Teacher gate (ALL mandatory):

- Equal-weight external point gain>=5pp over Lacoz/new/old khoufou and whole-map
  paired bootstrap95% lower bound>0.
- Direct league3m score>=55%, whole-map95% lower bound>50%.
- No opponent point regression>5pp (including v6, BC, separate B2M).
- ZERO own/control technical errors, no missing/discordant implementation data.
- At least36/40 complete clean paired maps for every opponent and external
  composite; exact Java/native replay of every complete clean trajectory.

Report both all-games (own technical failures count as losses; opponent errors
retained and identified, not described as strategic wins) and clean whole-map
paired results. Require the point/CI/direct/regression gates on BOTH estimates,
so excluding technical outcomes cannot manufacture admission. Bootstrap10000,
seed20261108, whole maps with both seats; also report per-opponent, per-seat,
W/D/L, confidence intervals, technical records and coverage. No pooling v4.

## C. Conditional candidate / student

Only a PASSED teacher gate permits a bounded distillation protocol and pilot.
Five-network search is not source-size-compliant. Legal unchanged-rule packaging
must be proven before any platform readiness claim. Fewer networks or another
decision rule is a new candidate requiring separate fresh full-game evidence.
At most10 fixed paired official read/play tests, only after technical packaging
and fresh official rules/API-limit checks; request interactive authorization
coordination then, with submit disabled and all IDE flags false.

For distillation, first specify disjoint maps, bounded data/updates/checkpoints,
fixed selection and exact autoregressive choice-trace supervision. Existing
labels() sorts destinations and is NOT accepted as exact style2 supervision.
No labels, training, student export or submission on failed/inconclusive teacher.

## Decision and delivery

Maintain STATUS.json, dated HISTORY.md, commands, actual lease durations, source
hashes, failed attempts and raw records. Final REPORT/decision/inventory state
COMPLETE, REJECTED or BLOCKED, with unrun stages explicit. Root organizational
records are updated by the coordinator, not concurrently by this experiment.
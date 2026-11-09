# RL-v6: compact direct D16 deployment

Declared 8 November 2026 before implementation, new games or precision selection.
Classification: USER_CONFIRMED objective; MODEL_INFERENCE design and gates;
subsequent actual measurements must be PROJECT_REPORTED.

## One objective and immutable reference

Deliver the useful D16 search as a single legal source, retaining its advantage.
This is a new experiment, not a revision of any closed v3/v4/v5 gate. The user
authorized implementation/training and, if necessary, testing on the real ranking.
That does not authorize paid resources, unrelated approaches or automatic rollback.
The coordinator alone handles OAuth/read-play/submission; implementation agents
must never call the platform or mutate Git.

Base repository: main531c59385ec7370ed6f44c4ab923c2144de71221. Preserve the
four protected artifacts and all frozen v5 sources/weights/binaries. Parent owns
this protocol and organizational records. Implementation is restricted to
code/rl/v6/compact_d16, docs/rl/v6 and this new output directory; parent audits
have their own coordinator subdirectory. Never overwrite prior output attempts.

## Fixed representation and selection before strength outcomes

Four unique weight sets from v5 freeze3a8a3604: league3m actor, frozen critic,
control-long3M response and league4.837M response. Actor is also response0.
Preserve all three response models; do not silently remove a network.

Use symmetric per-output-row quantization of matrix weights. For a declared bit
width b, qmax=2^(b-1)-1; float32 scale=max(abs(row))/qmax (zero row: scale1),
round-to-nearest-even and clamp q to [-qmax,qmax]. Biases and row scales remain
float32. Decode q*scale with explicitly checked float32 rounding at startup,
then run the unchanged float inference. Do not quantize observations/activations.
Store shared actor weights once. No external files, API, temporary weight files
or runtime downloads may be required by the submitted source.

Generate candidate packages at b=12,11,10,9,8 using the SAME deterministic code
extraction/codec. Choose the highest precision whose fully assembled source is
<=98,000 UTF16 units, compiles and passes exact decoder contracts. This is a
static technical selection, not five game candidates. Do not consult game wins
or old final performance to choose bit width. Record all sizes and reasons.
If no width fits, stop this declared pilot; do not switch to simplified search.

In the generated amalgamation only, remove unused training/C-ABI/old-main paths
and replace file-loading constructors with in-memory loading. Preserve source
span hashes/assertions. Never edit the frozen dependencies in place. Search
remains depth2,4 proposals,3 responses, temperatures .15/.35/.7, mean/minimum
aggregation .5/.5, margin .02, gamma .995, D16 cooperative16ms from first score
token and20,000-forward cap. Both seats, absolute-state reconstruction, output
flush and complete-plan fallback semantics remain intact.

No PPO, distillation or QAT training is part of this initial fixed candidate.
Training is authorized in general but is not a reason to train without a measured
need. A failed independent test must not trigger post-hoc retraining on its maps.

## Stage A: technical contracts and disclosed regression games

1. Check source/weight/protected SHA identities, existing environment and serial
   compute lease. Record actual compiler/Python/NumPy versions and commands.
2. Compare original float32 D16 with the new full-precision in-memory shim on
   previously exposed saved trajectories: bitwise weights and unlimited plans.
3. Compare quantized-text reference with the actual packed/dequantized standalone
   program: every weight bit, finite logits, unlimited plans and deterministic
   forward-cap behavior. Original-float versus quantized differences are measured,
   not required to be identical. Timed command equality is not an export contract.
4. Use at least100 saved games/both seats for stream/decoder coverage; verify
   hidden state, legal masks, root immutability, complete-baseline and nonbaseline
   partial-stop cases, exactly one output line. Do not claim game strength here.
5. Play the six disclosed regression fixtures62041/62044/62046,both seats.
   Verify complete Java/native state/score trajectories using the strict normal
   terminal-tail handling already audited in v5. Retain original failures.
6. Source<=98,000UTF16; no external dependencies in the package; startup and
   full original1000/50ms referee limits, zero own/control/teacher errors,
   no emergency WAIT, complete timing coverage. Internal through-flush<40ms
   is an additional diagnostic margin, not a platform CPU guarantee.

Numerical/codec/packaging bugs can be corrected before Stage B, with attempts
preserved. Such corrections cannot change the fixed search strategy or choose
precision based on wins. Technical failure blocks fresh strength games.

## Stage B: one fixed development comparison

Before opening maps, freeze package/source/model/analyzer identities. Generate
71001–71012 with canonical-content and legacy hash novelty checks against all
earlier training/dev/final/platform/branch-map claims INCLUDING v5 maps.
Any overlap stops; do not silently replace maps after seeing results.

Candidate, unchanged league3m control and original D16 each play Lacoz7f190183,
newkhoufou070bc128, oldkhoufou372c1cd6, v6, BC, league3m and B2M, both seats:
3×7×12×2=504 original-referee games. Serial alternating order, no interim
strength decisions. Complete raw logs, manifests, timing and Java replay.

Proceed only if technical checks pass, all-games external candidate-control
point gain>0, directleague3m score>50%, candidate-originalD16 external point
>=-5pp, no per-opponent point regression worse than-10pp, and clean paired
coverage>=90%. This is development/admission, not final proof. Failure ends
this fixed pilot without sample extension, bit-width sweep or retraining.

## Stage C: one independent final, selected before reserved maps

Only after Stage B admission, freeze the sole finalist/package, complete
analyzer, exact schedule, dependencies and gates BEFORE generating/opening
40001–40100. No tuning on these maps. The separate65001–65040 reserve stays closed.
Novelty includes all exposed v5 and current v6 development content, not seed IDs.

100maps×2seats×7opponents×3candidates(candidate/control/originalD16)=4200games.
Run fixed serial ten-map blocks (420games each); no interim win-based tuning.
Original1000/50ms referee limits, technical losses retained. A genuine own
candidate/control/teacher error rejects deployment; remaining fixed evidence
may be stopped for safety and must be described as incomplete, never repaired
by replaying a failed game. Opponent errors do not prove strategic wins.

Analyze all-games and clean-paired results separately. For clean comparison,
drop the full affected candidate/control/teacher×seat opponent-map cluster;
require>=95%complete clean maps for every opponent and composite. Bootstrap
10,000 resamples, seed20261109, unit=whole map including both seats.

Final deployment gate, declared for this new delivery experiment:
- Complete fixed schedule and exact raw/identity/Java replay coverage.
- Zero candidate/control/teacher technical errors, invalid outputs or emergencies.
- Equal-weight external(Lacoz,newkh,oldkh) candidate-control gain>=3pp and95%lower>0.
- Candidate directleague3m AND directB2M score>=55%, each95%lower>50%.
- No per-opponent candidate-control point regression worse than-5pp.
- Candidate-originalD16 external point>=-2pp and95%lower>-5pp.
- The strength/retention tests must pass on both all-games and clean estimates.

The3pp threshold is a prospective meaningful-improvement criterion for this
new delivery experiment, not a change to the earlier5pp teacher/student gates.
Report originalD16/control outcomes and all CIs even if they are disappointing.
Related khoufou variants and saturated opponents limit generalization claims.
Parent independently reparses raw results, recomputes whole-map intervals and
checks source/freeze/replay inclusion/exclusion coverage before deployment.

## Stage D: official validation and conditional ranking

Only a passed, audited, source-size-valid package reaches the platform. Obtain
official OAuth via the existing memory-only client when the package is ready;
never persist tokens or ask for passwords. Refresh challenge/rules/deadline,
limits, current submission and source identity. Preserve accepted B2M source.
At most10 focused read/play games initially, including timing and meaningful
opponents/both seats where supported. No IDE write. Platform errors block submit.

The user's new conditional real-leaderboard authorization permits one submission
of the validated exact source if needed. Record accepted source SHA, submission
ID, before/after snapshots; await100%/not-in-progress and audit available battle
logs. Moving rank snapshots are not a controlled paired causal estimate. Never
repeat an ambiguous POST before checking state. No automatic rollback or series
of new candidates. A new authorization is needed for a materially different action.

## Resource and stopping rules

Same GPT-6 Astra/max/codex_second; original local M4/24GB, no paid resources.
Existing compute_slot ownersearch-teacher, initial4569.00871229358seconds, old
4-hour cumulative cap unchanged. New phase heavy<=150minutes; each lease<=25min.
No competing timed panels or heavy training. Parent's independent audit uses
the separate existing coordinator lease, not to evade the implementation cap.

Soft size/technical feasibility deadline21:45UTC8Nov. Hard research cutoff
02:00UTC9Nov, official submission deadline09:00UTC; preserve the final7hours.
Do not spend the budget just because it remains. If the gate/cutoff blocks
success, preserve evidence, close owned processes and report the honest result.
Coordinator schedules durable progress checks while jobs are active; material
milestones/blockers only to Chief of Staff. Root STATE/HISTORY/index/check and
final report are coordinator-owned. No commit/push is implied by this new task.
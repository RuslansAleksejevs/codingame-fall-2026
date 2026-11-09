# Distillation pilot

Final status,2026-11-09: **NO-GO at the prospective game-development gate**.
All800fresh strength games completed without technical errors. Broader data
slightly improved the narrow-control point estimate, but did not retain base
strength. No candidate is recommended for promotion or further updates. The
independent final73401–73440 was never generated/opened. This was a NEW finite
authorized experiment, not continuation of rejected v5 Round2. No platform
action/submission. Measurements are PROJECT_REPORTED; interpretations below are
MODEL_INFERENCE. Last compute finished2026-11-09T01:08:30.689Z.

## Full-game outcome

[gamedev-decision.json](gamedev-decision.json), SHA
`ef9b0e819c53b86f2e120aa91152caaa7789ffd81f4efb9e26b6cc9c0910db8a`,
binds all800raw results and four Java verification records. All16maps73301–73316
passed canonical-content novelty audits; each arm played both seats against all
five fixed opponents. All/common-clean analyses are identical:0own errors,
0opponent errors,0invalid games. Java replay passed23,766states/22,966transitions.

External means Lacoz/new Khoufou/old Khoufou,96games per arm. Each direct column
contains32games. Entries are win score%[95%CI]; no draws occurred. CIs use10,000
paired WHOLE-MAP bootstrap samples, preserving both seats/all opponents/all arms,
seed20261109. They are not independent-game binomial intervals.

|Arm|External score%[CI]|Lacoz W–L|Direct league3m%[CI]|Direct B2M%[CI]|
|---|---:|---:|---:|---:|
|Untouched base|93.75[87.50,100]|26–6|50.00[50.00,50.00]|40.63[21.88,59.38]|
|narrow1|89.58[82.29,95.83]|22–10|40.63[25.00,56.25]|53.13[31.25,71.88]|
|broad1|91.67[85.42,96.88]|24–8|37.50[18.75,56.25]|59.38[37.50,81.25]|
|narrow2|88.54[80.21,95.83]|21–11|46.88[28.13,65.63]|46.88[25.00,68.75]|
|broad2|89.58[82.29,95.83]|22–10|31.25[15.63,50.00]|37.50[15.63,59.38]|

Every arm was32W/0L against EACH Khoufou version. That ceiling limits this small
panel's sensitivity; empirical100%/degenerate bootstrap intervals do not prove
perfect population performance. Full per-opponent/seat WDL and CIs are in JSON.

|External paired difference, percentage points|Seed1[95%CI]|Seed2[95%CI]|Two-seed mean[95%CI]|
|---|---:|---:|---:|
|Broad−narrow|+2.08[−3.13,+7.29]|+1.04[−4.17,+6.25]|+1.56[−2.60,+6.25]|
|Broad−base|−2.08[−6.25,+2.08]|−4.17[−9.38,0]|−3.13[−7.29,0]|

The mean CI is conditional on these TWO trained seeds, not a training-seed
population uncertainty estimate. Narrow−base is−4.17pp[−9.38,0] for seed1 and
−5.21pp[−11.46,0] for seed2. Upper numerical epsilon in the mean broad−base
interval is rounded to0, not presented as strictly negative evidence.

The fixed promise gate fails because mean broad−base and designated seed1
broad−base are negative; seed1 direct league3m is12W/20L=37.5%<50%; its per-opponent
base deltas are−6.25pp against Lacoz and−12.5pp against league3m, beyond the−5pp
guardrail. No independent confirmation, seed switching, extra updates or retry.
NO-GO is a continuation/promotion decision, not proof that diversity is useless.

## Design

See [PROTOCOL.md](PROTOCOL.md), SHA
`b5f6638e3219069592091c9b100ce00966ecd14d0d2f78a3edcca32e84f80f00`.
Broad64maps/phase-spanning positions versus narrow12maps/early positions, matched
800optimizer updates from unchanged league3m, two paired seeds. Count, map and
phase coverage change together; they are not individually isolated. Same
objective/architecture/optimizer and no asymmetric on-policy round. Seed1 is
designated before outcomes, not selected for performance.

Exact subsets/code/dependencies frozen00:10:49.540504UTC in
[data-freeze.json](data-freeze.json), before any collection game. The original
64-map broad cap became63retained maps under the explicit pre-training A1 below.
Final73401–73440 remains closed after the failed800-game promise gate.

## Historical technical evidence and original stop

Original FP32 D16 is unchanged:16ms/20,000forwards/four proposals/three responses,
all frozen weights and original executable. No required teacher-adapter change.
Seven disclosed contract roots /170groups include3nonbaseline decisions; actual
generator traces, legal masks, exact prefix features/root immutability and
counterfactual Java steps passed. [contracts.json](contracts.json),1.968694heavy
seconds. This is old-state technical evidence, not fresh strength.

First32train maps73001–73032 content novelty passed against2,950canonical and
1,075legacy hashes; no collision. All64collection games completed. One opponent
Lacoz timeout occurred on73017/seat0; own errors0. Its raw scores10:-1,12own
outputs/11opponent outputs and `$1: timeout` establish a technical outcome, not
a clean game win. No opponent stderr identifies the underlying timeout cause.
All63clean trajectories match original Java:1,862states/1,799transitions. The
failed game remains preserved and is explicitly excluded from replay parity.

The prospective protocol required stopping on opponent collection errors too.
Accordingly collection stopped before any training labels or optimization:
**training roots0, optimizer updates0, trained students0, strength games0**.
The seven old contract roots are not a training dataset. No game was replaced,
retried or silently filtered. This is an inconclusive technical stop, not a
negative test of broader distillation. At that stop, remaining training maps and
all labeldev/game-dev/final maps were unopened.

Evidence: [train1-verification.json](train1-verification.json),
[execution failure](execution/collection1-end.json). Data-freeze SHA
`a9f1a788cc7b205708ade8f8a13102ed699773c34e0d88e4ba2dca5e9ab62f4e`;
raw match rows SHA`ceb1ae6d4423c46af8b7eaf6fd90334ef52e17393c160238d51c72b4860543da`;
failed raw SHA`cbc89c8555b63d6c9cb6d94fa98ba5fe09827c4349c7d96ea0455dc957e20808`.
The collection lease ended00:12:18.917UTC,90.242515s; total completed heavy time
92.211210s. The slot was explicitly released to D16; the collection control timer
was cancelled. No diversity child job remains scheduled by its finite driver.

## Explicit prospective A1 continuation

The coordinator authorized [AMENDMENT_A1.md](AMENDMENT_A1.md) before labels or
optimization: exclude BOTH seats of any opponent-only failed collection map,
symmetrically across arms, without replay/replacement/additional seeds.73017 is
excluded. Coverage floors58/64broad,11/12narrow,15/16labeldev,>826unique broad
roots; other scientific gates and budgets unchanged. This conditions the target
population on technical cleanliness and may introduce selection bias.

A1 SHA`d78b30ba8e047610d79c119921453328a034ba3e4a443f8d2e90a8c3a362678a`;
new effective [data-freeze-a1.json](data-freeze-a1.json) SHA
`828dae9154f3ea7dff2e9bd11b44df8115fea067e927ab951022fab6e689d62a`.
Original protocol/datafreeze/failed raw/command remain exact. Original versions
of four amended code files are content-verified in `pre-a1-sources.tar`.
Six original and three A1 synthetic tests passed. The running A1 stage labels
only the62retained already-played train1games, then plays the originally planned
remaining32train maps. The64previous games are not rerun. Existing trainer config
retains the original `data_freeze_sha256`; its effective runtime identity guard
now additionally checks the explicitly linked A1 freeze.

Training collection completed00:20:53.958UTC:128planned games on64maps, one
opponent-only failed map removed from both seats, leaving126retained games on63
maps. Both blocks' clean trajectories match Java:127clean games including the
retained-but-not-labelled other seat of73017,3,692states/3,565transitions.
No game was replayed. Exact labelling consumed3,541teacher observation calls on
126retained streams, with0emergencies/trace/Java failures. The union includes
2,072labelled roots; arms share144targets rather than rerunning their teacher.

|Training arm|Unique roots|Maps|Changed targets|Relative early/middle/late|Maximum zero-based turn|
|---|---:|---:|---:|---:|---:|
|Narrow|205|12|44|85/73/47|27|
|Broad|2,011|63|293|753/639/619|87|

These are actual state identities, not repeated optimization exposures. Narrow
can also contain relatively late states in short games; broad expands absolute
turn coverage as well. Label-development, optimization and strength checks are
still pending at this section's00:29UTC update.

At00:31UTC, labeldev completed32clean games/16maps,1,020states/988transitions,
509unique roots/56changed/10,546groups. Total collection160games,159clean Java
replays (4,712states/4,553transitions),158retained teacher streams/4,529calls and
2,581counterfactual target checks. All amended coverage floors pass. Exact banks:
narrow4,403groups/30,862candidate rows; broad44,386/307,145; labeldev10,546/71,726.

Both seed1 models completed800updates from untouched league3m. Narrow1 exact
float32 text/native parity passed10,546/10,546groups, max logit error3.052e-5.
Its first reference compile in the historical command verifier failed before
any command-parity or strength test. See [BUILD_RECOVERY.md](BUILD_RECOVERY.md):
the original nested compiler stderr was not exposed, so an SDK-cache cause is
not claimed as directly proved for this failure. Failed command/empty build
directory preserved. No trained model is rerun; seed2 and same-source reviewed
compiler/export recovery are the next implementation steps.

## Matched training and verified export

By00:38:04UTC all four NEW models completed exactly800AdamW updates/25,600
root-group exposures each, from the same original checkpoint. No model was
retrained, resumed from rejected Round2 or selected by label/game results.

|Arm|Actual optimizer seconds|Distinct sampled roots / groups|Sampled candidate rows|Labeldev CE (diagnostic only)|
|---|---:|---:|---:|---:|
|narrow1|1.204821|205 /4,017|181,850|0.313275|
|broad1|2.043340|2,011 /15,406|181,967|0.308572|
|narrow2|0.845720|205 /4,029|181,055|0.311716|
|broad2|0.966291|2,011 /15,420|183,053|0.308176|

These optimizer times exclude Python/data loading, evaluation, generation,
verification and compilation. Matched budget means equal updates and choice-
group exposures, not exactly equal FLOPs or wall time. Exact feature-matrix
uniqueness:4,403narrow/44,386broad/10,546dev groups; no exact repeated feature
matrix has conflicting target indices in these banks. This narrow byte-identity
test does not establish sufficient model capacity or absence of near-aliasing.

The same-source reviewed compiler/export block passed in27.469314heavy seconds.
The first failure remains; original cause was not directly captured. All four
native/PyTorch checks passed10,546/10,546argmax; each package recovers all24,833
float32 values exactly and matches1,152commands on20old records/both seats.
All sources80,252UTF16units. This is technical compatibility, not game strength.
All four sources/checkpoints and the untouched base were frozen before game-dev:
[candidate-freeze.json](candidate-freeze.json), SHA
`015a8acc66524e346c6cc0f4282e742cc1c62db9f690408de8c6893bac355d54`.

Panel provenance note: the reused v5 runner retains a static legacy `baseline`
prose field about a same executable. For THIS pilot, its explicit `commands`,
per-game agent specification and source/binary hashes are authoritative: base is
the preserved league3m standalone package, and each student its own standalone
package. They share the decoder, NOT an identical executable. No v5 search-
control wrapper is used for collection or student strength games.

## Interpretation and boundaries

The old v5 student failed1,680fresh games (external−2.9167pp, retention−9.1667pp);
it is not a promising initialization and is not reused. Original D16's previous
1,120game+5.4167pp result motivates the teacher, but is not pooled into this pilot.
CE/agreement/export diagnostics cannot establish game strength. Early/middle/late
means relative to each game's actual trajectory length, not an absolute long-game
guarantee. Only two training seeds and a small fixed panel limit power.

Additional diagnostic: labeldev base CE0.358645/group agreement98.625%; narrow1
CE0.313275/agreement90.982%, broad1 0.308572/92.547%, narrow2 0.311716/91.627%,
broad2 0.308176/91.959%. Lower CE did not preserve argmax agreement or full-game
strength. This motivates an objective/retention audit, not a demonstrated model-
capacity conclusion. Dataset size/map/phase mix and changed-target frequency
(44/205narrow versus293/2,011broad) vary together, with the SAME loss weights and
optimization budget. A1's whole-map technical exclusion is a separate selection
confound; the teacher adapter itself never changed.

Recommendation (MODEL_INFERENCE): keep untouched league3m as the student baseline;
promote NONE of these four checkpoints. If separately authorized later, train a
NEW small24,833-parameter student from unchanged league3m only after checking the
usefulness of D16's changed labels and retention of original decisions. Better
audited D16 targets plus a tightly controlled objective/retention experiment are
more justified than simply repeating more updates. Do not continue rejected
Round2 or this pilot's rejected students. Capacity/objective changes remain
follow-up hypotheses, not authority for a new architecture/PPO campaign.

## Retained evidence and closure

[closeout-audit.json](closeout-audit.json), SHA
`c3e93f37d974ddaccb01eadd279f8ddcaf03b55b72b6fc8c5ce88765a9b8de6b`,
contains exact paths/hashes for all four checkpoints, weights, packed sources,
executables and exposure arrays; bank counts/hashes; all stage counts and protected
reference hashes. Audit PASS:82effective data-freeze identities,54candidate-freeze
identities,68teacher identities and808decision bindings unchanged. Model configs
match the retained bank hashes and original initialization. The final reserve and
unused train73065–73128 were not opened; old reserves were not used.

The coordinator independently verified all800raw scores/errors/maps/schedule,
54frozen identities,808bindings and all whole-map statistics/bootstrap/gates:
[independent receipt](happy-file://agents/rade46b18ac74a5003f254d/repositories/codingame-fall-2026/experiments/rl/2026-11-09-rl7/coordinator/pilot-audit.json).
That audit checked the Java replay receipts; it did not run the replays again.

Actual total:960NEW original-referee games on96novel maps=160collection+800strength;
959clean,0own errors and1collection-opponent timeout. All960full raw records and960
portable records remain. Java replay totals959clean games/28,478states/27,519
transitions.158teacher streams/4,529calls,2,581counterfactual target checks;
4new retained checkpoints,3,200optimizer updates/102,400root-group exposures.
No rerun of collection games or trained model. All labels/failures/logs remain.

Total12closed diversity leases:1,274.194223seconds=21.236570heavy minutes of120;
maximum actual lease248.666680seconds. External spend0. CPU2threads for training;
Python3.14.6,NumPy2.5.4,Torch2.15.0,Apple clang17.0.0,Temurin17.0.21; exact versions
in [environment.json](environment.json). No new environment installed.

The wrapper terminated each owned process group and reported no unclosed leases.
Post-exit scoped `pgrep` could not read processes inside the sandbox (exit3); the
same reviewed read-only query returned exit1/no matching diversity processes.
Product timer listing returned NO pending messages; all owned controls cancelled.
No background job or timer remains. Root STATE/HISTORY/index/check belong to the
coordinator; this chat did not modify them.

No Git mutation/push, architecture change, paid compute, OAuth/API/IDE/submission,
new chat or old-ledger change. Shared v7 owner cap120heavymin,<=25min per lease,
hard9Nov06UTC cutoff; first D16 lease honored and blocks yielded explicitly.
[COMMANDS.md](COMMANDS.md) and `execution/` retain commands/durations/failures.
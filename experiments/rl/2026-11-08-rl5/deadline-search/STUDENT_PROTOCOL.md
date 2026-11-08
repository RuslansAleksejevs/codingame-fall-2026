# Conditional compact-student pilot: pre-result protocol

Recorded2026-11-08 after the independent D16 teacher passed, before trace-data
generation or student training. Teacher evidence remains frozen and separate:
40maps/1120games, external+5.416666667pp,95%CI[1.25,9.583333333], zero technical
errors. No old PPO campaign is resumed. LocalCPU only; existing search-teacher
lease/phase10800s/owner14400s and research cutoff remain binding.

## Practical packaging assessment

The teacher loads five networks (four distinct parameter sets because one
response is the actor). The existing exact15-bit-symbol encoding needs52978
UTF-16 symbols per24833-parameter network before code. Four distinct sets alone
exceed100000 units. This is a limitation of the existing verified lossless
packaging method, not a mathematical impossibility claim about all compressors.
Do not quantize, remove response models or promote a changed search rule.
No technically valid direct-search package exists; no OAuth/API work yet.

## Contracts before any training dataset

Use the frozen D16 executable, actor, critic and response files for teacher
decisions. Reconstruct full observation streams from complete saved trajectories,
including initial map/absolute seat and every prior observation; do not reset
the turn counter at selected states. Labels use the actually returned action
and selected proposal index from its raw stderr. Timed decisions can differ
between runs; no claim of time-independent selection or platform timing.

Regenerate the pure deterministic proposal generator from the exact state,
absolute player and state_seed, recording EACH actual legal choice, its complete
style2 feature matrix, available set and preceding choices. Baseline then
temperatures.15/.35/.7 and exact deduplication order are unchanged. This is
generator trace capture, not parsing/sorting MOVE strings. Inductive contract:
identical decoder initialization -> identical candidate list/features -> same
float inference/RNG draw -> identical choice/prefix. Time checks can abort an
unfinished proposal but cannot alter a completed selected proposal's choices.

Required before dataset collection: selected index/action equality with frozen
D16; trace replay renders the exact complete command; fresh feature recomputation
is bit-equal at every prefix; choices are in legal masks; one-hot target mass=1;
features remain exactfloat32/128 dimensions/style2 with no Python rewriting;
root immutability; exact originalJava/native one-step counterfactual transition
from saved prefixes, both absolute sides. Use the three disclosed failed roots
and the three previously identified changed-plan roots as a finite contract set.
Any contract discrepancy blocks collection/training; no large label dump first.

## Fixed data and optimization

Reserve disjoint seed ranges BEFORE generation, audit content against all prior
exposure and claims, stop on overlap without replacement:

- Training70201-70212; reused only within this pilot's declared two rounds.
- Label development70301-70308; never a training target.
- Independent full-game confirmation70401-70440; generated after student freeze.
- Global40001-40100 and65001-65040 remain closed.

Collection uses the unchanged original referee/50ms limits, both seats. One
opponent per map, cyclically Lacoz/newkhoufou/oldkhoufou/B2M. Round1:24 complete
league3m-anchor games on the12train maps. Development:16 anchor games on8devmaps.
Round2:24 complete games of the Round1 student on the SAME12training maps.
No collection-game winrate is a selection criterion. Preserve all games and
verify complete Java/native trajectories. Any own technical error stops pilot.

For the controlled player label only zero-based turns0,3,6,9,12,15,18,21,24,27
that occur in the complete record. Thus<=240anchor train roots,<=240current-
student train roots and<=160dev roots, <=640 target roots total. Keep every
selected root, including unchanged-baseline decisions; do not select by outcome.
An emergency teacher fallback, missing log or unrepresentable trace blocks the
pilot rather than silently filtering difficult data. Bound each root at400
groups/12000candidate rows and total at3000000candidate rows; exceeding a cap is
a blocker, not permission to truncate a target. Retain actual counts and all
teacher inference calls, including unlabelled prefix observations.

Existing128-128-64-1 actor,24833parameters, initialized from preserved league3m.
One training seed20261108, CPU2threads. Two rounds, exactly400 AdamW updates each,
learning rate3e-5, weight_decay1e-5, gradient clip0.5. Fresh optimizer each round;
round2 starts from Round1 weights. No other seed/architecture/learning-rate sweep.
Batch32roots, then uniformly one legal choice group from each root. Root sampling
weight3 for a changed teacher plan,1 otherwise. Loss=hard-label cross entropy
+0.2*KL(anchor categorical distribution || student distribution) on the SAME
teacher-prefix features, with illegal padded choices masked. No feature-style
rewriting, PPO, value training, reward tuning or action-string label builder.

Round1 uses anchor roots. Round2 samples anchor/current-policy banks50/50,
then the declared changed-root weights within each bank. At most400updates/round
and600seconds/round; hitting the wall cap before completion rejects the pilot.
Save exactly two final checkpoints/exports plus untouched initial baseline.
Select Round1 or Round2 by lower mean per-root/per-group dev teacher cross-entropy;
earlier round wins a tie within1e-6. No full-game development checkpoint selection.

## Export and independent full-game comparison

Package the one selected existing-architecture policy with the existing exact
float32 single-file exporter into a NEW child of this experiment. Verify every
float32 bit, all commands on100 already exposed teacher-confirmation records,
both seats, and C++/PyTorch logits/argmax on dev groups. Source<100000UTF-16units,
no external weight files, fullGold action profile. Package is experimental,
not yet a recommended replacement. No old source/checkpoint is overwritten.

Freeze student source/weights/config/analyzer before70401-70440. Exactly1680
games: student package, unchanged greedy control and frozen D16 teacher, each
against Lacoz/new/oldkhoufou/v6/BC/league3m/B2M on40maps/both seats. Alternate
serial execution; four10-map chunks,<=25min leases. No interim strength selection,
sample extension or retraining. Stop promptly on any own/control/teacher technical
error or implementation/export discrepancy.

Student admission requires on BOTH all-games and clean complete-map estimates:
external gain>=5pp with95%whole-map-bootstrap lower>0; directleague3m>=55% and
lower>50%; no per-opponent point regression>5pp; zero own/control/teacher errors;
>=36/40clean complete maps per opponent/composite; all complete saved trajectories
exactnative/Java. Also require external student-minus-teacher point>=-2pp and
95%lower>-5pp on the SAME fresh maps. Bootstrap10000,seed20261108. Report every
candidate/opponent/seat W/D/L, CIs, coverage and technical exclusions. Do not pool
the original teacher confirmation or call label accuracy a stronger bot.

If failed/inconclusive, close honestly without another student seed or dataset.
If passed and packaged timing is clean, report readiness to the coordinator,
refresh official rules/API limits and arrange<=10 fixed paired read/play tests
with preserved league3m; submit/IDE writes remain disabled. No ranking mutation.
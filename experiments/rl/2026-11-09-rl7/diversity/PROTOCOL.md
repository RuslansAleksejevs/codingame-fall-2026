# Distillation pilot: prospective controlled comparison

Recorded 2026-11-09 before collection, optimization or fresh games. This is new
authorized work, not a resumed PPO/v5/v6 campaign. Historical failures and gates
remain unchanged. Local original-referee evidence is PROJECT_REPORTED.

## Question and fixed arms

Does broader map/state/phase coverage improve actual compact-policy full games
over repeatedly optimizing a narrow collection at the same optimization budget?
This changes **count, map coverage and phase coverage together**, not an isolated
single factor. The same four fixed collection opponents appear in both arms.
Both start NEW from unchanged league3m, not rejected v5 Round2. Actor remains
128-128-64-1 / 24,833 parameters and the same legal autoregressive decoder/style2.
Untouched league3m is a third full-game control.

## Frozen subsets and collection

- Broad training: 73001–73064, 64 maps, 128 complete league3m games, both seats.
  Opponents cycle Lacoz7f190183/new khoufou070bc128/old372c1cd6/B2M by map index.
  In each complete controlled-player trajectory of T joint decisions, retain
  unique turns floor(i*(T-1)/15), i=0..15. No outcome or teacher-change filtering.
- Narrow: first 12 of the SAME collection maps, both seats; eligible zero-based
  turns 0,3,6,9,12,15,18,21,24,27. Collect the union of broad/narrow targets once;
  overlapping targets have exactly the same timed teacher call and trace.
- Label development: 73201–73216, 32 complete league3m games with the same cyclic
  opponents, broad phase rule. Never train on these targets.
- Game development: 73301–73316, all four trained students plus league3m, each
  against Lacoz/new khoufou/old khoufou/league3m/B2M, both seats: 800 games.
- Conditional independent final: 73401–73440, designated seed1 broad/narrow plus
  untouched league3m, same five opponents/both seats: 1,200 games. Generate only
  after game-development promise passes and one exact candidate freeze.

Unused train73065–73128 is NOT an automatic extension. Other old reserves,
including40021–40100 and65001–65040, stay closed. Every generated map is audited
by canonical nodes/units/edges and legacy content hashes against prior exposure,
including later platform records and all available branch claims. A collision
stops the pilot without replacement. Old-map contracts are not fresh strength.

Broad must have >826 unique (map,state,absolute-seat) roots across64 maps to be a
meaningful coverage pilot; otherwise report insufficient coverage without adding
maps. Report unique maps/states/roots/groups, changed and unchanged roots, seat,
opponent, absolute turn and normalized early/middle/late coverage, plus repeated
optimization exposures. Quantile selection covers late relative-to-termination
positions; it does not ensure many absolute turn100+ positions.

## Exact original FP32 teacher and contracts

Use the original frozen v5 D16 executable and all unquantized weight files,
freeze3a8a3604. Exactly four proposals/depth2/three responses,16ms from first
score token and20,000 forward cap, temperatures.15/.35/.7, margin.02,
aggregation.5mean+.5min, gamma.995. No teacher adapter/search change is planned.
Read every prior observation in order in one process per game; one teacher call
per joint-decision observation, including unlabelled prefix turns. Keep complete
stdout/stderr and all failures. No repeat to select a preferred timed target.
An emergency on ANY teacher call, missing output, own collection error, invalid
trace or Java discrepancy stops before training. Opponent collection errors also
stop rather than filtering games. Timing variability is an explicit limitation.

Reuse the actual v5 generator trace: selected proposal index and exact command,
bit-identical per-prefix float32 features, legal choice masks, one-hot targets,
root immutability. Never derive labels by parsing/sorting action strings. Before
data, run a small disclosed-state contract set on both seats. Verify every
complete collection trajectory and every retained target's counterfactual joint
step against original Java. Cap400groups/12,000rows per root and4,000,000rows total
per bank; stop on cap, no truncation. Save raw trajectories, teacher logs, target
metadata and exact NPZ arrays. No changed-only filtering or feature rewriting.

## Matched finite optimization

Two paired seeds,20261109 (seed1, prospectively designated final) and20261110
(seed2, replication diagnostic). Each broad/narrow model starts from the SAME
unchanged league3m actor/checkpoint with a fresh AdamW optimizer. Exactly800
updates, CPU2threads, batch32 roots then one uniformly sampled legal choice group
per root; root weight3 if teacher changed baseline, otherwise1. lr3e-5,
weight_decay1e-5, clip.5, hard categorical CE +.2 KL(anchor||student) on the same
prefix features and padded legal mask. This reproduces the v5 objective equally
in both arms, without a current-policy round or asymmetric objective changes.
Maximum600s optimization per model; incomplete updates reject the comparison.
Save all four final checkpoints, weights, exposure indices and update histories.
No intermediate checkpoint, seed, learning-rate, architecture or outcome-based
selection; no extra updates after rejection. Label CE/agreement is diagnostic.

Verify text/checkpoint float32 bits, native logits/argmax, exact packed weights
and complete commands on20 exposed old records/both seats for EACH student.
Conservative source target<98,000 UTF16. No platform acceptance is claimed.

## Full-game endpoints and prospective decisions

Use original referee1000ms first/50ms later. Serial, alternate arms/order by map,
opponent and seat; no training concurrent with arena. Five arms on game-dev;
three predesignated seed1 arms on final. Fresh games and all technical failures
are retained; own/control failure stops further games, not a permitted retry.
Report all-game and common-clean-whole-map results separately, every arm,
opponent and seat W/D/L and score (draw=.5). CIs:10,000 paired bootstrap samples,
seed20261109, resample whole maps preserving both seats/opponents/arms/training
seeds. The external endpoint averages the three public opponents equally;
league3m/B2M are separately reported direct endpoints. Related khoufou versions
are not independent opponent families. Seed-average CI still does NOT establish
population-level training-seed robustness from only two seeds.

Game-dev is a modest promise screen, not proof. Require on BOTH all/clean sets:
zero own/control errors, >=14/16 common-clean maps; mean-across-seeds external
broad-minus-narrow >0 and broad-minus-base >=0; each seed's broad-minus-base >=-5pp;
designated seed1 external broad-minus-narrow >0 and broad-minus-base >=0;
seed1 directleague3m >=50%; no seed1 broad-minus-base per-opponent regression>5pp.
No CI-significance demand on this small screen. If any fail, NO-GO for this pilot;
leave all final maps closed. Do not rescue with a better seed or additional data.

If promise passes, freeze exact seed1 packages/config/analyzer/schedule before
opening40 final maps. Strong GO requires complete1,200 games, >=36common-clean
maps, zero own/control errors, and on BOTH all/clean estimates: external broad
minus narrow >=3pp with95%lower>0; broad minus base >=3pp with95%lower>0;
directleague3m >=55% and95%lower>50%; no per-opponent regression vsbase>5pp.
Failure/inconclusive is valid; report points and uncertainty, not a forced win.
There is no additional teacher panel: old FP32 teacher evidence is context,
not fresh retention evidence on these maps.

## Resources and closure

All substantial jobs run through new v7 wrapper owner diversity, <=120 heavy
minutes total, <=25min per lease, serial host, hard stop9Nov06:00UTC. D16 receives
first short lease; yield between blocks. External spend0. Use bounded durable
control for running jobs; cancel owned pending controls at closure. No OAuth/API,
submission, IDE write, Git mutation/push, paid compute, new chat or architecture.
Only code/rl/v7/diversity, docs/rl/v7/DIVERSITY.md and this experiment may be edited.
Coordinator alone owns organizational records. Final handoff includes exact
paths/hashes, actual counts/uncertainty, failures, compute and process/timer state.
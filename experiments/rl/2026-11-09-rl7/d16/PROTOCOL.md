# D16: mandatory baseline repair and one exploratory live test

Declared 2026-11-09 before compilation or new games. USER_CONFIRMED scope;
MODEL_INFERENCE design. New finite authorization, not a reopened v5/v6 gate.

## Fixed change

Start from the exact v6 b9 source, SHA256
22ccbbe3fedd8cdb7bae8c232b62269ee5b7cde838b23afb4405692b92e5a5c9.
Keep all four unique networks, 9-bit row representation, inference, simulator,
depth2/four proposals/three response models, temperatures .15/.35/.7,
.5 mean + .5 minimum, .02 margin and .995 gamma. No learning or precision sweep.

The greedy baseline must finish before optional cooperative stopping is enabled.
Both time and forward caps apply to optional work, counting the baseline's real
elapsed time/forwards. The original clock still starts after the first score
token; it is never reset after input or baseline. Optional limit remains 16ms,
forward cap 20000. A completed baseline can be a legitimate WAIT; explicit
baseline-complete telemetry and equality to the uncapped greedy plan distinguish
that from an emergency. Keep emergency accounting. Record input, restore,
baseline, optional work, flush and through-flush time without adding overlapping
counters. This is a bounded-work baseline, not a hard real-time OS guarantee.

## Short technical/development stage

Use existing tested machinery read-only. Compile production, diagnostic and
native contract variants; exact decoded weights must equal the old b9 bytes.
Compare unlimited commands on 20 disclosed saved games, both seats and full
streams. Include the v6 emergency record and the three v4 failure fixtures.
Test immutable roots, restored hidden state, legal commands, completed partial
search selections and forced cap1 / already-expired / tiny wall budgets.
Inject real delayed input on the original emergency prefix (20ms and 30ms),
retaining actual input/output/stderr. Require completed exact greedy baseline,
no emergency, optional stop and honest elapsed time including injected delay.

Six original-referee regression games on62041/62044/62046, both seats, are old-map
technical evidence only. New development: exactly72001–72004, three external
opponents, candidate/control/teacher, both seats =72 games. Remaining72005–12
stay unused, not a reserve for strength-driven tuning. Development is technical,
not a winrate selection. No candidate sweep. Any source repair is documented
before freeze; no repairs after independent maps are opened.

Technical admission: source <=98000 UTF16; exact representation/command contracts;
zero own/control/teacher engine errors or emergencies; baseline complete on every
candidate output; exact original Java/native replay of eligible full games;
complete timing coverage and candidate internal through-flush <40ms. Full referee
limits remain1000ms/50ms. Timing on this host is not platform acceptance.

Send exact source/SHA/UTF16 and manifest to coordinator immediately after technical
readiness, before long final. Fixed minimal official request: one full GoldBoss
test, then two archived own timeout fixtures with candidate and unchanged
league3m on identical game parameters (five tests total), all IDE overwrite flags
false. If fixtures unavailable, coordinator may use two existing live archived
games, both absolute seats where supported; record exact selection before tests.
No platform or OAuth actions in this lane.

## One independent finite final

Freeze source, config, binaries, evaluation code and exact schedule before map
generation. Use all40maps72101–72140: candidate, unchanged league3m control and
original FP32 D16 versus Lacoz7f190183, newkh070bc128, oldkh372c1cd6, league3m and
B2M, both seats =1200 original-referee games. Four ten-map serial blocks, rotating
opponent/candidate/seat order. No interim strength selection or sample extension.
Audit canonical board content plus legacy hashes against prior registries and
all later exposed map/live evidence. Overlap stops without substituting a map.
40021–40100 and65001–65040 remain closed. No pooling old or development results.

Retain every raw technical outcome. Own technical failures count as losses;
opponent failures remain flagged. Clean comparison drops the entire six-row
candidate/control/teacher x seat opponent/map cluster. External composite uses
the intersection across all three external opponents. Report all-games and clean
W/D/L, per-seat/per-opponent results, external gain, teacher retention, direct
league3m/B2M scores. Whole-map paired bootstrap10000, seed20261109, both seats kept
together. At least36/40 clean complete maps required for interpretable comparison.

Technical failure stops unsafe submission. Independent strength can be inconclusive
and still support the explicitly authorized single exploratory ranking, provided
technical readiness and official tests pass. Prospective exploratory sanity:
external candidate-control point >=-5pp, candidate-teacher point >=-10pp,
directleague3m >=50%, directB2M >=40%, no external per-opponent regression <-15pp,
on both all and clean views. Failure is a blocker for coordinator review, not a
post-hoc replacement search. Strong local evidence is separately described only
if external95% lower>0 and directleague3m/B2M95% lower>50%; exploratory admission
must never be called the historical v6 strength gate passing.

## Resources and closure

All substantial jobs use code/rl/v7/compute_slot.py --owner d16, <=25min per lease,
<=5400s total new heavy time, shared original global lock. Release between blocks;
no training concurrent with timed arena. Hard cutoff2026-11-09T06:00Z, official
deadline09:00Z. No paid compute, Git mutation/push, IDE overwrite, automatic
rollback, new chat/subagent/worktree or root organizational edits. Coordinator
owns platform and root records. Save commands, versions, durations, raw data,
failures and final hashes. Product scheduling bounds long-job control; cancel
owned pending timers at closure. No historical report or protected artifact edited.
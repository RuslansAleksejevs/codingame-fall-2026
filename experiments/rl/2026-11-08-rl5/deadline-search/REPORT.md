# Deadline-safe lookahead and conditional compact-policy pilot

Research outcome as of2026-11-08T12:02Z: **COMPLETE; teacher PASSED; compact
student REJECTED; no deployable improvement established; platform not run**.
Evidence classification is PROJECT_REPORTED unless explicitly stated otherwise.
All results below are local original-referee measurements, not CodinGame platform
or leaderboard results. Original B2M and league3m artifacts remain untouched.

## Technical outcome

One declared design, D16, implements cooperative deadline-bounded search in an
isolated adapter. It retains an immutable complete greedy plan, checks the budget
around individual expensive operations and only accepts a completely evaluated
joint plan. Optional work stops16ms after the first score token;20000forwards
is an additional deterministic bound. The existing depth2/four proposals/three
response models/.5mean+.5minimum/.02margin/.995gamma rule is unchanged when
unlimited. An immediately available WAIT is a separately counted emergency
fallback, not a successful greedy plan. One protocol-legal output line is flushed
per observation. Original referee1000ms first turn/50ms subsequent limits were
not weakened. Search still loads five network instances/four unique weight sets.

This is not a hard real-time guarantee: preemption, atomic operation latency,
input time before the first score token and referee/platform accounting are not
bounded by the internal timer. Instrumentation separates parsing, state restore,
baseline/proposal/response/future decoding, features/forwards, simulation/clone,
value, output flush and post-flush diagnostics. Nested counters overlap and must
not be summed. Full stderr, including failed historical turns, is retained.

Disclosed historical failure maps62041/62044/62046 are regression fixtures, not
fresh strength evidence. The old internal75.244/34.676/32.577ms observations
remain evidence; the complete causes of the referee timeouts remain UNKNOWN.
Sixty additional original30ms-budget calls did not reproduce those timeouts.
Current non-reproduction does not identify scheduler/arena blame.

Contracts passed:102unlimited old/new/standalone commands,54forced-stop prefix
contracts including5nonbaseline completed selections, hidden state restoration,
absolute player ordering, legal masks/root immutability, and108unchanged-control
streams/2518commands. Six regression games and48technical development games
have zero own/opponent errors. Their complete saved trajectories match original
Java:215/1098states and209/1050transitions respectively. The first replay verifier
incorrectly rejected the original referee's normal terminal unpaired survivor
output. Its failed command/log is preserved; a narrow terminal-score/done/normal-
ending check was fixed before freeze and both sets rechecked, without rerunning
or replacing games. No development winrate selected D16.

## Independent teacher confirmation: PASSED

Frozen40maps70101-70140,1120games, both seats,7opponents, serial alternating
search/control. Canonical board content and legacy map hashes were checked
against prior exposed manifests/platform archives/branch claims before playing;
all40maps are unique and unexposed. Global40001-40100/65001-65040 stayed closed.
No interim strength selection, sample extension, pooling with v4 or threshold
change. Freeze SHA:
`3a8a360441013efe735d7f2f3d27e4bdd11e66b84b83323938991bf36987f532`.

External equal-weight Lacoz/new/old khoufou gain is **+5.416667pp**, whole-map
paired bootstrap95%CI **[+1.25,+9.583333]pp**. Directleague3m score is76/80=95%,
95%CI[90,98.75]. Own/control/opponent technical errors:0/0/0; clean coverage40/40
for every opponent and composite. Therefore all-games and clean-paired estimates
coincide. All predeclared teacher criteria pass, including no opponent regression.
The coordinator independently reproduced raw counts and bootstrap intervals.

|Opponent|D16 W-D-L|Control W-D-L|Paired gain pp|Map95%CI pp|
|---|---:|---:|---:|---:|
|Lacoz7f190183|64-0-16|54-0-26|12.50|[1.25,23.75]|
|newkhoufou070bc128|80-0-0|77-0-3|3.75|[0,10]|
|oldkhoufou372c1cd6|80-0-0|80-0-0|0|[0,0]|
|v6|80-0-0|80-0-0|0|[0,0]|
|BC|79-0-1|78-0-2|1.25|[0,3.75]|
|league3m|76-0-4|40-0-40|45.00|[40,48.75]|
|B2M separate benchmark|59-0-21|21-0-59|47.50|[36.25,58.75]|

All per-seat counts, score CIs, exclusions and paired estimates are in
`decision.json`. Bootstrap10000, seed20261108, unit=whole map/both seats. Related
khoufou versions are not independent algorithm families; several opponents are
saturated, so generalization beyond this panel is unproven.

All1120complete trajectories match Java/native:30884states/29764transitions.
Raw timing coverage30712/30712outputs, no missing turns. D16 itself:
14675turns,2162changed plans,4804budget stops,0emergencies. Through-flush timing
p50=12.5999ms,p95=16.0464ms,p99=16.0842ms,max=19.4728ms; maximum post-flush
instrumentation0.087958ms. These are defined internal measurements, not the
entire referee-charged turn. Original referee games have zero technical losses.
See `confirmation-timing.json`, `final-audit.json`, full raw records and freezes.

## Conditional compact student

The teacher is useful locally but not an unchanged-rule deployable package.
The existing verified lossless15-bit-symbol packing requires52978UTF16symbols
per network before code; four unique networks exceed100000units. This is not
a claim that every possible compression scheme is impossible. No response
network was silently removed, quantized or promoted as the same teacher.

`STUDENT_PROTOCOL.md` was written before data/training. Exact generator trace
contracts passed before collection:9disclosed roots/192groups/1173feature rows,
actual selected commands, per-prefix float32 bits, legal masks and exact
counterfactual Java/native transitions. Old labels() string sorting is not used.
Collector/trainer/config/trace-library hashes were frozen before collecting data.

Fixed data:12training maps70201-70212,8dev maps70301-70308, each content-audited;
current-state collection reuses only declared train maps.24anchor+16dev+24current
full games, zero technical errors, complete replay verified. Actual targets:
202anchor+133dev+211current=546roots,13047choice groups,87976float32candidate rows,
92changed roots,1723teacher calls;546counterfactual transitions verified. Every
declared eligible turn is retained, including unchanged baseline targets.

One24833parameter128-128-64-1 actor initialized from unchanged league3m;
CPU2threads, seed20261108, exactly400AdamW updates twice. Round2 uses50/50anchor/
current banks; changed-root weight3, hardCE+.2anchorKL on identical prefix
features, lr3e-5, decay1e-5, clip.5. No architecture/seed/hyperparameter sweep.
Dev mean root/group CE0.316817194447→0.313241164663 selects Round2 by the fixed
rule; collection wins were not consulted. Both checkpoints/exports are retained.

Selected weights SHA:
`dd97f3f6329fa41b75e96bda7a73bd9e264b1db05c14d060a25210912ae755f9`.
Single-file source SHA:
`5502b574b459560722b77e4c21335ad2a0afd41ac9e816e262a7f83196774ccc`.
Source80252UTF16units, no external weights, fullGold action profile. Float32
packing is exact;3798/3798devgroup argmax agrees, maximum native/PyTorch logit
error0.000030517578125.100exposed records/both seats/200streams/5616commands agree
between reference, compact package and collection wrapper. This proves export
contracts, not strength or platform timing.

Student freeze SHA:
`15c74bc0ee784dfa2533a776f047687e9ba8851cd1edde6be0542eff6b00de80`.
Eight analyzer gate tests passed before the independent series. Fixed1680games
on40fresh70401-70440maps compare student/control/frozen teacher against the same
7opponents/both seats. The student must independently satisfy the original
meaningful gain/direct/regression/zero-error gates AND retain teacher external
performance:student-minus-teacher point>=-2pp and95%lower>-5pp. No interim
strength selection or additional training was allowed.

## Independent student result: REJECTED

All1680/1680games on40new70401-70440maps completed. Own/control/teacher/opponent
technical errors0; every opponent/composite has40/40complete clean maps. All
46076Java/native states/44396transitions match. Raw score/error/count/content/
ordered-schedule audit agrees with frozen analysis and all source identities.
All-games and clean-paired results are identical, with no exclusions.

Student-minus-control external gain is **-2.916667pp**, map95%CI
**[-8.75,+2.083333]pp**: no confirmed gain and the required+5pp threshold fails.
Directleague3m score30/80=**37.5%**,95%CI[25,50], fails both direct-score criteria.
Student-minus-teacher external performance is **-9.166667pp**,95%CI
**[-15.416667,-3.75]pp**: the teacher advantage was not retained. The direct
league3m opponent also has a-12.5pp regression versus control, beyond the5pp
guard. This rejects the frozen student on both all-games and clean estimates.

|Opponent|Student W-D-L|Control W-D-L|D16 W-D-L|Student-control pp|Map95%CI pp|
|---|---:|---:|---:|---:|---:|
|Lacoz7f190183|49-0-31|52-0-28|65-0-15|-3.75|[-15,7.5]|
|newkhoufou070bc128|76-0-4|78-0-2|80-0-0|-2.50|[-7.5,0]|
|oldkhoufou372c1cd6|78-0-2|80-0-0|80-0-0|-2.50|[-7.5,0]|
|v6|78-0-2|80-0-0|80-0-0|-2.50|[-7.5,0]|
|BC|78-1-1|79-0-1|80-0-0|-0.625|[-5.625,3.75]|
|league3m|30-0-50|40-0-40|72-0-8|-12.50|[-25,0]|
|B2M separate benchmark|31-0-49|35-0-45|60-0-20|-5.00|[-18.75,8.75]|

Full per-seat/per-opponent W/D/L, score/gain/retention CIs and all observed rows
are in `student/decision.json`; raw identities/order/timing coverage are in
`student/raw-audit.json`. No old teacher evidence is pooled into these estimates.
The coordinator independently reparsed all1680original raw records and repeated
every candidate/opponent/seat/external/direct/retention bootstrap interval; all
agree. It checked existing replay identities/coverage, without rerunning Java.
Audit source:`../coordinator/student-audit.json`, as_of2026-11-08T12:01:59Z,
SHA`f25d863289e89451bd77ca95ac69b2191ccd68202c85273abe762930e6e53b24`.
That independently owned audit is referenced, not copied into this archive.
The additional saved-label audit regenerated all546targets exactly from original
records and checked all1723teacher prefix calls, with zero emergencies even on
unlabelled turns. This does not identify whether limited data, architecture or
the objective caused the strength loss; it only rules out the tested trace/export
contract failures and measures this fixed pilot's failure to transfer advantage.

Timing logs cover all45776outputs:15538student plan measurements,15897control
and14341teacher detailed measurements, missing0. Student internal plan_us
p50=.409ms,p95=1.089ms,p99=1.57263ms,max=4.537ms; these exclude parsing/output/
startup and are not full-wall or platform timing. D16 through-flush max16.3935ms
on this second series,4941budget stops/2013changed plans/0emergencies. Full games
passed original50ms limits, but no platform transfer/timing claim follows.

The measured practical bottleneck is now **strength transfer to the compact
policy**, not its verified source size or these local time limits. The useful
multi-network teacher remains offline. No new labels, training seeds, sample
extension, changed search rule or platform tests follow this rejection. The
experimental package and both checkpoints are retained as rejected evidence;
they are not a recommended replacement or a prepared ranking submission.

## Boundaries and evidence

No platform/read-play tests, OAuth, ranking submission, rollback, IDE writes,
Git mutation, publication, additional chat/agent, paid compute or external spend.
Preserved baseline/checkpoint/source hashes are checked at every heavy stage.
All heavy work uses the original exclusive search-teacher lease, max25min each;
phase10800s and existing cumulative14400s caps are unchanged. Exact commands,
versions, source identities, raw games, failures and actual durations are kept
in manifests/logs/HISTORY. Before final evidence archiving, phase heavy usage is
3167.001874s (52.783365min) of10800s; cumulative owner4546.598856s of14400s.
Final archive overhead, complete per-lease durations and remaining budget are
recorded in `lease-ledger-final.json` and `COMPLETION.json`. In total2918local
original-referee games ran:6regression+48technical dev+1120teacher confirmation+
64student collection+1680student confirmation. No new game remains scheduled.
Root organizational records remain coordinator-owned. Nothing here changes the
closed v3/v4 gates or the active B2M submission.
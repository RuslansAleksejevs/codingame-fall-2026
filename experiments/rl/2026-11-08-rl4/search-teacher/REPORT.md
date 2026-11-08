# Search teacher: rejected after the complete fixed confirmation

As of2026-11-08T09:16Z. PROJECT_REPORTED from preserved branch evidence.
The unchanged teacher failed the predeclared strength gate: external gain
4.8246pp is below5pp, and three own timeouts violate the zero-error requirement.
No teacher dataset, student or deployable candidate was produced.
This is a new bounded cycle; the stopped PPO-v3 campaign is not resumed.

All40 confirmation maps/960games completed once. External paired95%CI is
[0.4386,10.0877]pp on38 complete common maps; direct score versus league3m
is97.5%,95%CI[93.75,100] on40 maps. Positive external evidence and a strong
direct matchup do not override either failed criterion. No thresholds were
rounded, relaxed or changed. No extra maps, retests or student training follow.

Decision: [teacher-decision.json](teacher-decision.json), SHA256
`6e1744b784d4fb72e479ea26fc2b68073b76dd3c6d1081a5ff8082b0cc99184c`.

## Pre-result commitment

[Protocol](PROTOCOL.md) fixes existing search2: unchanged league3m actor,
four complete proposals (greedy always included), two-turn simultaneous
rollouts against three frozen responses, mean/min critic aggregation,
.02 margin and30ms budget in timed games. The earlier28-map search result
remains not confirmed; no observations are pooled with the present sample.
No labels/student training until the strict new40-map confirmation gate passes.

The actor SHA256 is `dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb`;
critic `91fd5a290dd4a015fade1abdfe8840e1b580b4480c50102b4f7a3fb14f1f6680`.
The original checkpoint and fallback hashes are checked at every stage.
Build/source hashes and commands are saved, with repository-relative paths.

## Completed pilot

The first sandbox invocation ended before compilation: the compiler could not
create temporary files. Its failure log/manifest remain preserved, with only
personal path prefixes redacted. Reviewed execution of the same bounded CPU
wrapper succeeded. Apple Clang17.0.0, arm64 Darwin25.6.0. No shared source or
binary was replaced. Ten pure gate tests passed, including strict CI boundaries,
regression guards, map identities, coverage, duplicates and reserved seeds.

Six fresh maps62001–62006 were checked by content against2,704 prior canonical
and829 legacy identities plus all existing lane claims. Hash-only claims were
published before the first rollout. No reserved final map was opened.

[Diagnostic](diagnostic/summary.json):36 roots from normal full-game starts,
both player seats and turns0/5/10;219 complete counterfactual continuations;
1,095 exact native/Java snapshots. Roots are immutable, greedy is included,
root enemy actions are committed independently, and both policies recompute
later actions in altered states. No invalid command. Repeated diagnostics are
deterministic and depth2 scores/selection match the existing native teacher.

| Diagnostic horizon | Pairwise agreement with long rollout | Changed roots | Better / worse roots | Mean value delta vs greedy |
|---|---:|---:|---:|---:|
|1|30/54 (55.6%)|8|6 /2|+0.04263|
|2, frozen teacher|33/54 (61.1%)|8|5 /3|+0.00379|
|4, diagnosis only|31/54 (57.4%)|7|7 /0|+0.04634|
|8, diagnosis only|44/54 (81.5%)|10|10 /0|+0.05585|

Values use .995-discounted terminal ±1/0 under greedy continuation and .5mean+
.5minimum across the same three response models. Non-tied pair comparisons
are correlated within roots/maps; these proportions are not independent
binomial confidence estimates. Full deterministic continuation is a proxy,
not optimal value or evidence against independent external opponents. Depth2
critic ranking is not reliable enough to assume every selected plan improves.
The diagnostic depths do **not** replace the frozen teacher after inspection.

[Undiscounted outcome audit](diagnostic/raw-outcome-summary.json) separates
win/loss changes from faster/slower wins. For frozen depth2, the eight changed
roots have two improved/two worsened/four equal robust terminal outcomes;
mean delta is numerically zero, six-map95%CI[-0.1111,+0.1111] in signed-value
units. Pairwise outcome-only agreement15/22 (68.2%). Thus the tiny positive
discounted mean is not demonstrated outcome improvement. Depth8 has three
improved/zero worsened robust outcomes but includes one worse individual
response-model outcome; it remains a post-inspection diagnostic, not a new
selected teacher. All such small-sample intervals are local and correlated.

Timed smoke: four wins against Lacoz/new khoufou, both seats on one diagnostic
map, zero own/opponent errors. All93 joint transitions and97 full states match
original Java.97 emitted search decisions include seven changes; zero budget
stops, maximum internal planning28.594ms. This is not total platform CPU or a
statistical strength estimate. See [pilot audit](pilot-audit.json).

Actual heavy usage:0.187s failed launch +22.888s successful pilot. External
spend0. Shared CPU released after the pilot. There is no active process here.

## Completed frozen external screen

All192 games on12 maps62007–62018 completed, zero technical errors. Full-state
replay:5,350 transitions/5,542 native/Java states exact. Before the panel,
372/372 standalone/native commands agreed on fresh smoke records from both
absolute player perspectives. No code/configuration adjustment was selected.

| Opponent | Greedy wins/draws/losses | Search2 wins/draws/losses | Paired gain, pp | Map95%CI, pp |
|---|---:|---:|---:|---:|
|Lacoz|16/0/8|19/0/5|+12.50|[0,33.33]|
|New khoufou|23/0/1|24/0/0|+4.17|[0,12.50]|
|Old khoufou|24/0/0|24/0/0|0|[0,0]|
|Direct league3m|11/2/11|24/0/0|+50|[50,50]|

Equal-weight external gain5.5556pp,95%CI[0,12.5]. The preliminary screen gate
passes, **not the teacher strength gate**. All-win/identical-score bootstrap
intervals are degenerate empirical estimates, not certainty about population
strength. The two khoufou versions are related opponents, not independent
algorithmic families. Direct search superiority alone is insufficient.

The timed teacher emitted2,463 decisions;393 changed the greedy plan and46
hit the30ms search budget. Maximum internal plan35.552ms, no timeout/invalid
plan in the actual referee. This measures the timed program, unlike the
unlimited native diagnosis. See [screen decision](screen-decision.json) and
[audit](screen-audit.json). Candidate configuration/source/weight identity:
[candidate.json](candidate.json), SHA256
`d58fa093312b3df60712ceeef032741c94f8bb4ebb967db21c3bb9051c20c81e`.
Screen CPU lease271.267s. Total branch heavy usage294.343s (4.91minutes), spend0.

## Technical rejection before the final fixed chunk

Confirm1/2 each completed240 clean games. Confirm3 completed all240 games but
exited1 after verification because search2 timed out on62041/v6/seat0,
62044/Lacoz/seat0 and62046/Lacoz/seat0. The greedy control also has one separate
opponent timeout62039/league3m/seat1. All records remain preserved.236 clean
games replay exactly against Java:6,127 transitions and6,363 states. A clean-
subset Java pass does not mean the full panel passed its technical criterion.

[Immutable rejection](technical-rejection.json), SHA256
`e1e39277d82f88ae6092f2d0187d4c30c1c7313a4d891ce943c688cc83f62c0d`,
was recorded09:07:08Z, before confirm4 started09:08:39Z. It fixes teacher
strength FALSE and labels/student0 regardless of final win confidence intervals.
The final original10maps62049–62058 complete the fixed40-map descriptive series;
there are no reruns, replacements, new parameters or expanded samples.

### Timing erratum from the raw failed records

The initial inspection used `matches.jsonl::own_plan_us`, which records accepted
turns. It omitted late stderr from timed-out turns; this does not mean that no
failed-turn internal timing was recorded. The raw saved games contain:

| Search failure | Raw frame / reported turn | Late internal planning | Output at that frame | Search budget stopped |
|---|---:|---:|---|---|
|62041 vs v6, seat0|93 /24|75.244ms|none|yes|
|62044 vs Lacoz, seat0|91 /24|34.676ms|none|yes|
|62046 vs Lacoz, seat0|9 /3|32.577ms|none|no|

The first internal duration alone exceeds50ms. The other failures cannot be
explained by these internal measurements: they exclude some input/output and
do not measure the full referee deadline interval. Host fault is UNKNOWN.
The source checks its30ms budget between expensive operations, not continuously;
it does not enforce a hard50ms end-to-end deadline. No repair or timing retest
is performed. The separate control-opponent late log is9.248ms, also not a
causal explanation. Earlier records are retained; this is an additive correction.

## Full40-map paired results and technical records

Each row below keeps both seats for both candidates on a map only when all
four games are clean. W/D/L counts are per candidate, not pooled independent
trials. The paired bootstrap resamples whole maps10,000times, seed20261106.

| Opponent | Complete maps | Greedy W/D/L | Search2 W/D/L | Paired gain, pp | Paired95%CI, pp |
|---|---:|---:|---:|---:|---:|
|Lacoz|38|53/0/23|60/0/16|+9.2105|[-2.6316,22.3684]|
|New khoufou|40|77/0/3|80/0/0|+3.7500|[0,10.0000]|
|Old khoufou|40|78/0/2|79/0/1|+1.2500|[0,3.7500]|
|league3m|39|39/0/39|76/0/2|+47.4359|[43.5897,50.0000]|
|v6|39|78/0/0|78/0/0|0|[0,0]|
|BC|40|80/0/0|80/0/0|0|[0,0]|

The external composite uses the same38 maps complete for all three external
opponents, so it is not the mean of the differently filtered table rows:
**+4.824561pp,95%CI[0.438596,10.087719]pp**. That is below the fixed5pp minimum.
Direct search-versus-league3m uses all40 maps/80 clean search games,78wins,
2losses:97.5%,95%CI[93.75,100]. Its sample is different from the39-map paired
comparison, where one control-opponent timeout excludes the complete pair.

Coverage passes (at least38 paired maps per opponent/composite), the lower
external CI is positive, the direct criterion passes and no regression guard
fails. The gain minimum and zero-own-error criterion both fail. Teacher gate
is FALSE. This remains development evidence for the overall multi-branch
selection, not an opened global final. Degenerate empirical intervals do not
establish perfect population play; khoufou versions are related opponents.

All960 records are retained, including technical outcomes:

| Opponent | All80 greedy W/D/L | All80 search W/D/L | Technical outcome retained |
|---|---:|---:|---|
|Lacoz|56/0/24|62/0/18|Two search timeout losses|
|New khoufou|77/0/3|80/0/0|None|
|Old khoufou|78/0/2|79/0/1|None|
|league3m|41/0/39|78/0/2|One control win from opponent timeout|
|v6|80/0/0|79/0/1|One search timeout loss|
|BC|80/0/0|80/0/0|None|

There are956 clean raw games; the full-map paired comparison retains944 game
records (472 candidate/control game pairs). The other12 clean records belong
to affected opponent-map clusters and are excluded symmetrically with the four
technical records. The all-record table is descriptive, not the clean strength
estimate; an opponent timeout is never recast as a strategic win.
[technical-errors.json](technical-errors.json) preserves all four raw-file
hashes, frames, turns, relevant stderr, referee summaries and extraction command.
It also preserves the original confirm3 stage exit1. All other chunks exited0.

## Technical checks, limits and resources

Across smoke/screen/confirmation:1,156 timed games on53 distinct timed maps,
1,152 clean;29,698 native/Java joint transitions and30,850 full states match.
The separate ranking diagnostic contributes1,095 exact snapshots on six maps.
No state mismatch or invalid/parse command was found; the three own timeouts
remain genuine technical failures. Thirteen pure tests pass (ten frozen-gate
checks and three raw-late-log ownership/retention checks).

All timed raw search logs contain14,479 decisions,2,341 changed plans and149
budget stops. Accepted-turn internal maximum is41.460ms; raw failed-turn
maximum is75.244ms. Never substitute the accepted-turn maximum for the complete
timing record. No end-to-end platform50ms compliance is established. The372/372
standalone/native parity check is unlimited-time same-input equivalence, not
timed strategy equivalence. The five-network teacher is not a compact single-
file submission. No student export or packaging claim is made.

[teacher-audit.json](teacher-audit.json) SHA256
`fda82389952c93b2cf1d184b2959ca608aa5829a0c8cc46b61d4daacc2530197`;
[technical-errors.json](technical-errors.json) SHA256
`e4a46f68bb0817b122c5f041acb96c841dd84507ef24a2ba43e12b38e35fe39d`.

All58 development map contents were claimed and checked against the prior
registry plus both other lanes before games. Seeds40001–40100 and65001–65040
were not read, generated or played. Technical reserve62059–62060 is unused.
Model/source hashes remained fixed; source/checkpoint/fallback verification is
in the audit. No old campaign, selected policy, shared build or Git state was
modified by this branch.

Completed heavy leases before archival total1,375.063091seconds (22.918minutes),
including the failed initial launch, all builds/maps/games/Java checks and the
0.879400second closing analysis. Archive time is separately recorded in the
final completion inventory. External spend0; no framework/environment install.
Apple M4/24GiB, Darwin25.6.0/arm64, Python3.14.6, Apple Clang17.0.0;
installed package metadata is recorded in [environment.json](environment.json).
At09:16Z,16h44m remain before the research stop02:00Z and23h44m before the
official09:00Z deadline on2026-11-09. Remaining research budget is intentionally
unused because the gate failed, not an invitation to restart this branch.

## Reproduction and integration handoff

Commands ran from the repository root, always using the shared exclusive lease.
Each exact child command, wall time, return code and source hash is retained in
the corresponding `*-command.json`/log; finite-stage lease records are also
bound in the technical error report. Representative completed invocations:

```sh
python3 code/rl/v4/compute_slot.py --owner search-teacher --minutes 15 -- code/arena/.venv-rl/bin/python -B code/rl/v4/search_teacher/run_stage.py pilot --build-attempt 2
python3 code/rl/v4/compute_slot.py --owner search-teacher --minutes 15 -- code/arena/.venv-rl/bin/python -B code/rl/v4/search_teacher/run_stage.py screen
python3 code/rl/v4/compute_slot.py --owner search-teacher --minutes 15 -- code/arena/.venv-rl/bin/python -B code/rl/v4/search_teacher/run_stage.py confirm1
python3 code/rl/v4/compute_slot.py --owner search-teacher --minutes 15 -- code/arena/.venv-rl/bin/python -B code/rl/v4/search_teacher/run_stage.py confirm2
python3 code/rl/v4/compute_slot.py --owner search-teacher --minutes 15 -- code/arena/.venv-rl/bin/python -B code/rl/v4/search_teacher/run_stage.py confirm3
python3 code/rl/v4/compute_slot.py --owner search-teacher --minutes 15 -- code/arena/.venv-rl/bin/python -B code/rl/v4/search_teacher/run_stage.py confirm4
python3 code/rl/v4/compute_slot.py --owner search-teacher --minutes 2 -- code/arena/.venv-rl/bin/python -B code/rl/v4/search_teacher/close_report.py
```

These are records, not permission to rerun completed experiments. Evidence
writers refuse overwrite. Shared frozen dependencies are the original repo
files named and hashed by each manifest; the archive is not a new environment.

The final archive target is `evidence.tar.gz`; `evidence-manifest.json` records
its checksum and verified roundtrip for every entry. Raw originals remain on
disk. All per-game launch specs are included as normalized archive copies with
originalSHA→archivedSHA mappings; project/home prefixes become placeholders.
Only build/cache binaries and other archive files are omitted. The completion
inventory binds this frozen report, archive and actual final lease cost.

Integrate only the isolated code/docs and rejected research evidence. Do not
select this teacher, generate labels, train a student, replace B2M/league3m,
or submit anything from this lane. Keep the active platform entry and frozen
fallback unchanged; overall selection/platform actions remain separate. No
active research process or pending continuation is required after archival.
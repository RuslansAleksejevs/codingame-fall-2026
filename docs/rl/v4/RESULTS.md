# Three bounded RL investigations: no deployable replacement

As of2026-11-08. PROJECT_REPORTED measurements; all three predeclared continuation
or teacher gates failed. No global finalist was nominated, no student was trained
and no contest submission or rollback was performed. The existing B2M
submission41665776 remains active. This is not a conclusion that these approaches
cannot work in general.

The experiments reused the same local CPU checkout with an exclusive compute
lease. Each approach had an isolated code/evidence directory. Shared league3m
checkpoint/weights and published fallback identities were preserved. External
compute spend was$0. The original stopped PPO-v3 campaign was not resumed.

## Results and decisions

| Approach | Main measured result | Predeclared decision |
|---|---|---|
| Deliberately trained exploiters | Frozen early A:21/40 wins against league3m on20 new admission maps; map95%CI32.5–70%, seat scores65%/40%. Against held-out B2M15/40. | Failed score>=60%, CI lower>50% and both-seat>50% admission. No champion response. |
| Early-state curriculum | On12 new maps/264 full games, external gain over matched ordinary-start training+6.944pp, map95%CI[−1.389,+16.667]. Direct11W/11L/2D=50%. | Required direct score strictly>50%; failed. No additional training, expanded development or post-hoc promotion of the control. |
| Complete-plan search teacher | Full40-map/960-game series: external clean-paired gain+4.825pp, map95%CI[+0.439,+10.088],38 complete composite maps. Direct78/80 versus league3m. Three own timeouts. | Failed required external gain>=5pp and zero-own-error gate. No labels or student training, regardless of positive clean-paired CI. |

Intervals cluster both seats by map. They describe map variation for these exact
trained policies, not training-seed robustness or live leaderboard strength.
Technical failures are retained separately; the positive search interval is
conditional on clean paired map clusters and does not excuse the timeouts.

## Exploiters

Two initializations and one permitted A extension used1,204,216 production
decisions/38,336 training games. B and the longer A continuation were rejected;
the early A301610 checkpoint was frozen before admission maps60021–60040 opened.
Its development27/40 result did not reproduce as an admissible advantage on the
fresh20 maps. The repeat280-game panel was byte-exact but adds no independent
observations. All1,200 panel executions, including those repeats, were clean:
40,068 Java states/38,868 transitions matched; smoke16games is separate.

[Final report](../../../experiments/rl/2026-11-08-rl4/exploiters/REPORT.md)
and [admission decision](../../../experiments/rl/2026-11-08-rl4/exploiters/admission-decision.json).
The rejected candidate and all alternative checkpoints remain retained, not
selected for deployment. The public-anchor response panel and50ms packaging
test were not run because the response prerequisite failed.

## Curriculum

Full settled state restoration, including hidden ownership/capture fields and
remaining units, was checked against original Java. Stateful Lacoz received
ordinary starts in both arms; restored starts were sampled within stateless
neural matchups. The bank remained48 fixed recoverability-screened positions.

Ordinary control used100,020 decisions/3,049 complete episodes/48 updates;
curriculum used100,013/3,157/50. Actual restored exposure was469 episodes
(14.856%) and12,209 decisions(12.207%). This is matched nominal decision budget
and training configuration, not identical update or episode counts.

Paired curriculum minus control on the three external opponents:

| Opponent | Gain, pp | Paired map95%CI, pp |
|---|---:|---:|
| Lacoz | 0 | −20.833 to+16.667 |
| Old khoufou | −4.167 | −12.5 to0 |
| B2M | +25 | +12.5 to+37.5 |

Against the unchanged league3m reference directly, curriculum won10/24, not a
confirmed general improvement. All264 full games were clean;8,568 states and
8,304 transitions matched Java. Clean coverage was24/24 per opponent, exceeding
the declared22/24 minimum. A floor-versus-ceiling implementation discrepancy
therefore did not affect the rejection; both original and strict decisions
remain saved. The explicit analysis SHA record was made after launch, a timing
limitation retained in the branch report.

A separate frozen training-bank diagnostic produced55/96 curriculum wins,
59/96 control wins and57/96 league3m wins;7,988 Java states matched. These288
continuations reuse selected training states/anchors and are not independent
strength evidence or a reason to reopen the failed development gate.

An intermediate textual status contained incorrect numbers. The saved dataset
was unchanged. All11 result groups, paired gains and bootstrap intervals were
recomputed from264 raw rows; the corrected audit is authoritative. The
coordinator separately checked the raw outcome counts and artifact hashes.

[Report](../../../experiments/rl/2026-11-08-rl4/curriculum/REPORT.md),
[analysis](../../../experiments/rl/2026-11-08-rl4/curriculum/screen/analysis.json),
[raw-data audit](../../../experiments/rl/2026-11-08-rl4/curriculum/final-data-audit.json).

## Search teacher

One frozen search2 candidate was tested. Preliminary12-map screening passed;
the fixed confirmation then completed all40 maps62019–62058,960 games against
six opponents, with no interim candidate selection. After three own timeouts
in chunk3, technical rejection was recorded before opening chunk4. The last
chunk completed the original descriptive series; it could not restore eligibility.

The clean paired Lacoz comparison is60/76 search wins versus53/76 greedy wins
(+9.211pp, CI[−2.632,+22.368]); new khoufou80/80 versus77/80 and old khoufou79/80
versus78/80. v6/BC clean paired gains were0. All technical outcomes remain in
the report: three search timeouts and one opponent timeout. Clean replay covers
956 games/25,211 Java states/24,255 transitions with no state mismatch.

Raw stderr records a failed planning turn taking75.244ms, above the50ms limit.
The other failed search turns logged34.676ms and32.577ms internally; internal
planning does not cover the entire referee deadline. Their complete timing
causes remain unknown. Coarse budget polling between expensive operations is
not a hard deadline guarantee. No repair, repeated failed map or host-fault
excuse was introduced into this frozen experiment.

[Report](../../../experiments/rl/2026-11-08-rl4/search-teacher/REPORT.md),
[full teacher decision](../../../experiments/rl/2026-11-08-rl4/search-teacher/teacher-decision.json),
[technical error records](../../../experiments/rl/2026-11-08-rl4/search-teacher/technical-errors.json).

## Boundaries and next decision

Global comparison65001–65040 and final40001–40100 remain unopened. No replacement
was packaged or sent to the platform. Training-bank diagnostics, clean-subset
advantages and adaptive screens are not substituted for a selected independent
final test. Reports, checkpoints, failed attempts and full raw archives are
retained; path normalization affects archive copies only, with dual SHA ledgers.

The most concrete future hypothesis is a new deadline-safe search design,
followed by a separately frozen fresh evaluation; it is a proposal, not a repair
or run executed here. More training of these rejected recipes is not automatic.

## Preserved snapshot

The [snapshot manifest](../../../experiments/rl/2026-11-08-rl4/SNAPSHOT.json)
binds four archives,5,875 members and42,870,372 compressed bytes. All5,575
Git-ignored scientific files are covered, with no original SHA mismatch;
78 build/cache files are excluded. Personal paths were normalized in2,625
archive copies only. No original was deleted or rewritten.

The final scan inspected selected files, checkpoint metadata and every archive
member; it detected no secret literals/auth fields, personal host paths or
executable binaries. All four protected baseline/deployed-source hashes match.
These checks establish snapshot integrity, not playing strength.
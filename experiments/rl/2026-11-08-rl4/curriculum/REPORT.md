# Curriculum pilot — candidate rejected

Research results frozen as of 2026-11-08T09:14:18Z.
Classification: **PROJECT_REPORTED** local experiments.
**The prespecified full-start development gate failed. No expansion, retraining,
promotion or submission.** The candidate's paired pooled gain over ordinary
continuation is +6.94 percentage points (95% map-bootstrap CI -1.39 to +16.67),
but its direct score is exactly 50%, not the required strictly greater than 50%.
This small experiment does not establish a general curriculum advantage.
The old league3m checkpoint and active B2M deployment remain unchanged.

## Full-start development results

Twelve newly content-audited maps (61001–61012), both seats, 11 policy pairings:
264 original-referee games, all clean. Score is win=1, draw=0.5, loss=0.
Paired gains compare each arm on the same map, seat and opponent. Intervals use
10,000 resamples of whole maps, retaining both seats and all opponent pairings,
fixed bootstrap seed20261106. They measure map uncertainty for one training
seed, not training-seed variance or an independent final test.

| External opponent | Curriculum W/L/D | Ordinary control W/L/D | league3m W/L/D | Curriculum minus control, pp (95% paired CI) | Curriculum minus league3m, pp (95% paired CI) |
|---|---:|---:|---:|---:|---:|
| Lacoz | 19/5/0 | 19/5/0 | 15/9/0 | 0.00 (-20.83, +16.67) | +16.67 (0.00, +37.50) |
| Old khoufou | 23/1/0 | 24/0/0 | 24/0/0 | -4.17 (-12.50, 0.00) | -4.17 (-12.50, 0.00) |
| B2M | 13/11/0 | 7/17/0 | 11/13/0 | +25.00 (+12.50, +37.50) | +8.33 (-25.00, +41.67) |
| Pooled external | 55/17/0 | 50/22/0 | 50/22/0 | +6.94 (-1.39, +16.67) | +6.94 (-8.33, +20.83) |

| Direct matchup | W/L/D | Score | 95% map-bootstrap CI |
|---|---:|---:|---:|
| Curriculum versus ordinary control | 11/11/2 | 50.00% | 29.17–70.83% |
| Curriculum versus frozen league3m | 10/14/0 | 41.67% | 20.83–62.50% |

The positive B2M result is opponent-specific; it is not proof of general playing
strength. Do not select the control post hoc either. The gate's pooled point
gain, per-opponent regression floor, coverage and technical conditions passed;
the direct-score condition failed. Candidate weights are retained as rejected.
No seeds61013–61060 or reserved global-final maps were opened by this branch.

Evidence: [unchanged analysis](screen/analysis.json), [raw matches](screen/matches.jsonl),
[strict decision](screen-strict-decision.json), [final data/hash audit](final-data-audit.json).
The final audit recomputed all eleven W/L/D groups, rates, per-opponent and pooled
paired gains and bootstrap intervals directly from raw matches, and verified
source, DLL, checkpoint and policy hashes. All matched the saved evidence.

### Interim-summary erratum

An interim summary after context compaction incorrectly stated pooled0pp,
direct11W13L versus control and18W6L versus league3m. It also misstated the Java
state counts, screen duration and certain runtime hashes. That summary is
withdrawn. The tables above and machine audit are authoritative: direct11/11/2
and10/14/0; Java8,568states/8,304transitions; screen lease285.674seconds ending
2026-11-08T08:53:41Z. No raw evidence or selection criterion was changed to make
this correction, and the decision remains rejection.

## Protocol and implementation

The pre-result protocol is [CURRICULUM.md](../../../../docs/rl/v4/CURRICULUM.md).
The isolated adapter imports the unchanged simulator, decoder, value features
and PPO update. It restores complete, settled, nonterminal states, not a map made
from current units. Remaining units, triangle initial owners, both capture flags,
absolute turn, scores, geometry/topology and surrounding-pass flag are retained.
The action queue is empty at the chosen boundary. No extra settle/income pass is
performed on restoration. Both future policies act anew on the current state.

Before training, inspection identified that Lacoz is stateful (turn, original
homes, previous observation and opponent priors). Its 12.5% of matchups therefore
start normally in both arms. Restored starts are sampled with probability
0.15/0.875 among the stateless neural matchups, targeting 15% of all episodes.
This correctness amendment preceded any strength result; no reward or gate was
changed. Actor/critic/optimizer initialization, opponents, map/seat schedule and
nominal 100k-decision/12-minute budget match between the two arms. A final batch
ends only at a complete-episode boundary; any overshoot is at most one episode.

## Completed checks

| Check | Actual result |
|---|---:|
| Archived full-game native/Java parity | 95 games, 3,638 states, 3,543 transitions |
| Direct native restoration | 475 boundaries, zero mismatches |
| Direct original-Java restoration | 475 boundaries, zero mismatches |
| Live recoverability screen with two learners/two anchors | 384 continuations |
| Direct and sequential Java checks of those changed continuations | 18,268 states, zero mismatches |
| Stochastic training/teacher contract games | 10 games, 406 Java states, zero mismatches |
| Recomputed full-plan old log-probability | maximum absolute error 0.0000457764 |
| Neural-opponent rollout reproducibility | one/four workers agree |
| Split/resume | actor, critic, optimizers, RNG, steps, episode counts and exported weights agree |
| Actual training samples, both arms | 8 games / 268 Java states per arm, zero mismatches |
| Full-start screen native replay | 264 games / 8,304 transitions, zero mismatches |
| Full-start screen original-Java parity | 264 games / 8,568 states, zero mismatches |
| New map content | 12 unique, zero canonical/legacy overlap with frozen registry and neighboring claims |
| Screen errors | own0, opponent0, invalid0, no excluded games |

Evidence: [restoration](restoration.json), [bank verification](bank-verification.json),
[training contracts](contracts/summary.json), [successful smoke](smoke-execution-attempt1.json).
The 48-state bank contains 20 historical losses, 12 historical wins and 16 fresh
training-map self-play controls, on 48 different original map contents. Chosen
turns 2/4/6/8/10 have counts 6/6/7/6/23. Four of the first 24 prespecified losses
had no recovery win under the declared four-policy screen even at turn 2 and
were excluded. These screen outcomes are not independent evidence of strength.
All 95 archival map contents are already present in the shared exclusion
registry; no branch/global final map was opened.

Bank SHA256:
`2604762ff2c317d33ede69e4371b4bd0c6a74ae46543aa5726102b8a87ad7fc0`.

## Errors retained, not hidden

The first sandboxed compiler invocation could not create its xcrun temporary
file. The reviewed, bounded local build succeeded. Its failed log is retained.
The first comparator then incorrectly fabricated a Java parse-error count of
zero. Original Java does not expose that counter. All physical fields matched;
the corrected comparator keeps native counters separately and compares every
actual physical/hidden field exactly. Archived game918428620 has a native
counter20 for opponent seat0 after turn21; the controlled bot is seat1. This is
not a platform-reported technical failure. Its commands and original mismatch
are retained. Every eligible early boundary and newly generated plan is clean.

The `legacy_hash` field in the archive extraction uses compact property JSON and
is not the shared registry's legacy encoding; it is not used for novelty checks.
Canonical original-map hashes and the frozen shared registry establish archival
coverage. New development claims use both exact shared encodings.

Large raw preflight evidence is also preserved in
[preflight-evidence.tar.gz](preflight-evidence.tar.gz), with every uncompressed
SHA256 verified in [preflight-archive.json](preflight-archive.json). Compression
reduced 167,498,374 bytes to 4,387,514 bytes without deleting original files.

## Matched training and identities

Control100k finished with 100,020 training decisions / 3,049 complete episodes /
48 updates in233.85 seconds. Actual opponent episodes: current1517, league3m767,
olderPPO382, Lacoz383. An additional23 fully collected episodes (748 decisions)
were not used for the final update; no partial episode received a fake terminal.
The overshoot is20 decisions. Teacher384 collected games / 13,435 calls, errors[].
Export1000/1000 argmax agreement, maximum logit error2.29e-5. Sources remained
unchanged. Weights SHA256:
`21c6da38b91e236ffa29a6663af4a2a97d9a83efbbf3c7d6541b9ac277165762`.
Evidence: [control summary](pilot-control/summary.json),
[export check](pilot-control/export-verification.json). Six pure/synthetic tests
passed (four state-contract tests, two
matched-schedule/complete-episode-trimming tests).

Treatment completed under the same frozen source/DLL/initialization guard:

| Budget / dose | Ordinary control | 15% curriculum |
|---|---:|---:|
| Training decisions | 100,020 | 100,013 |
| Used complete episodes | 3,049 | 3,157 |
| PPO updates | 48 | 50 |
| Training seconds | 233.85 | 233.32 |
| Restored episodes | 0 | 469 (14.86%) |
| Restored decisions | 0 | 12,209 (12.21%) |
| Final decision overshoot | 20 | 13 |
| Collected, unused complete-episode decisions | 748 | 1,373 |

The budgets are matched nominally and differ by seven actual decisions; episode
and update counts are not equal. Treatment source categories: loss155/win160/
fresh154. Actual opponent episodes: current1579/league3m788/olderPPO394/Lacoz396.
Teacher400 collected games / 13,844 calls, errors[]. Both exports agree in all
1000 groups, maximum logit error2.29e-5. Shared source-manifest SHA256:
`05157018f183bb484dbc61e314bc7a55f0d6f94bf896b63765f0f891114d14c5`.
Treatment weights SHA256:
`7689e7cc277d26d76af80edd8ab95829786397e872fd53a43af1707667a8636f`.
Evidence: [treatment summary](pilot-curriculum/summary.json),
[export check](pilot-curriculum/export-verification.json).

Additional correctness coverage before treatment: three actual archived
post-road states (turns47/34/22),82 direct/sequential Java state checks,zero
mismatches. These late states were not added to the bank. The separate test
process did not advance the training RNG. See
[changed-topology restoration](changed-topology-restoration.json).

The shared training-source manifest hashes match between arms, as does the
isolated rollout DLL:
`85f1b2b32a144e692066b37d5a676ff9a37b18aecba3ab2233dc90781d1b6a44`.
Treatment checkpoint:
`dfe5710585695cd5c33dc98b11cf144c4b51235dab4c973181f54c541142c96d`.
Control checkpoint:
`ec7fe5b20fd6bbe87048b8d1c0b36d384c55a54f843feceb4c52bc20fa803a84`.
The immutable B2M evaluation weights are
`0369bcdddb1ba2e3378c23621871f650c4d0552f4364793bdaae5f524077be61`.
The frozen league3m actor/critic checkpoint, exported weights and fallback C++
hashes all remain equal to the supplied originals; see the strict decision.

### Analysis freeze limitation and coverage correction

The analysis code was loaded by the evaluation process before games. The
explicit [SHA freeze](screen-analysis-freeze.json) was written at08:49:21Z,
after process launch but before any game-outcome inspection. This is not a
pre-launch SHA record. Those source hashes stayed unchanged through final audit.
Before inspecting outcomes, a floor bug was noticed: the loaded analyzer used
`int(0.9 * 24) = 21` instead of the declared at-least90%, which requires22.
The running code and original boolean were left intact; a separate strict
decision enforced22. All three comparisons had24 clean pairs, so both decisions
are false and this bug did not determine the outcome.

### Recovery diagnostic

The [frozen diagnostic plan](recovery-plan.json) covers every unchanged bank
state against two live anchors, for each of the three frozen policies:288games.
This uses training data selected for recoverability against those same anchors.
It is not independent testing and cannot reopen the failed full-start gate.
The diagnostic completed at09:14:18Z in22.278seconds (22.465seconds lease).
All7,988 direct-restored/sequential Java states matched; no state mismatch.

| Policy | Training-bank recovery W/L/D | Win rate |
|---|---:|---:|
| Curriculum | 55/41/0 | 57.29% |
| Ordinary control | 59/37/0 | 61.46% |
| Frozen league3m | 57/39/0 | 59.38% |

There is no observed diagnostic advantage here either. Do not treat these rates
as general strength, construct independent-test claims from them or select a
policy from this table. See [raw diagnostic](recovery-diagnostic.json). The
pre-game plan SHA was
`07113019e78dbc8aced2c1d584d346dd83363cfd4cc107633b3fa73721ca945e`;
all twelve code/binary/state/policy/audit guards passed before the first game.

## Limitations and decision

- Only one training seed202611081 and12 development maps were used. No claim
  about all curricula, larger budgets or general tournament strength follows.
- Training sample budgets match to seven decisions, not episode/update counts:
  48 versus50 updates and3,049 versus3,157 used episodes. This limits precise
  causal attribution to state selection alone.
- Restored episodes are14.86% but restored decisions12.21%. Lacoz never receives
  a false restored history. Only settled boundaries and stateless live opponents
  are supported; arbitrary mid-resolution or stateful-policy restoration is not.
- The archival95games and all recoverability screens are development/training
  data. Army deficits correlate with loss; no causal army claim or army shaping
  was used. No historical future enemy commands are reused after intervention.
- Bootstrap intervals use twelve empirical map clusters. Degenerate24/24 win
  intervals do not prove100% population win probability; no multiple-comparison
  adjustment or training-seed replication is claimed.

Integration decision: **do not promote either pilot policy or replace the active
submission.** Preserve the isolated restoration implementation, rejected
checkpoints and negative evidence for review. The coordinator may archive these
exact owned files, update project state and select among other authorized
branches. Further curriculum training or new development maps are not a next
step of this closed pilot.

## Reproduction and boundaries

From the repository root, with the original virtual environments and pinned
referee classes available:

```sh
python3 -B code/rl/v4/curriculum/test_state.py
code/arena/.venv-rl/bin/python -B code/rl/v4/curriculum/test_sampling.py
python3 code/rl/v4/compute_slot.py --owner curriculum --minutes 5 -- code/arena/.venv-rl/bin/python -B code/rl/v4/curriculum/run_stage.py smoke
python3 code/rl/v4/compute_slot.py --owner curriculum --minutes 15 -- code/arena/.venv-rl/bin/python -B code/rl/v4/curriculum/run_train.py control
python3 code/rl/v4/compute_slot.py --owner curriculum --minutes 15 -- code/arena/.venv-rl/bin/python -B code/rl/v4/curriculum/run_train.py curriculum
python3 code/rl/v4/compute_slot.py --owner curriculum --minutes 20 -- code/arena/.venv-rl/bin/python -B code/rl/v4/curriculum/evaluate.py screen
code/arena/.venv-rl/bin/python -B code/rl/v4/curriculum/strict_decision.py
code/arena/.venv-rl/bin/python -B code/rl/v4/curriculum/final_audit.py
python3 code/rl/v4/compute_slot.py --owner curriculum --minutes 2 -- code/arena/.venv-rl/bin/python -B code/rl/v4/curriculum/recovery.py
```

These are the recorded execution commands, not permission to rerun them into
nonempty directories. Commands creating evidence require fresh designated
outputs; assertions protect existing runs. All the commands above completed.
Every heavy command used the shared exclusive lease. Sources, versions, exact
commands, weights and costs are saved
per run. No external compute spending ($0), platform/API games, submissions,
OAuth, Git operations or changes to shared training sources were performed.

Recorded training runtime: Python3.14.6, PyTorch2.15.0, NumPy2.5.4, CPU,
four Torch threads/four rollout workers. Panel compiler: Apple clang17.0.0
(clang-1700.6.4.2), arm64; Java Temurin17.0.21+9. Panel runs one game at a time
with50ms normal/1000ms first-turn limits. Exact versions and referee/source
hashes are in [final-data-audit.json](final-data-audit.json) and the panel manifest.
Shared-lease wall time through the final diagnostic, including failed attempts,
was854.854seconds (14.25minutes). No experimental process remains active.
No allocation of the full four-hour allowance was required.

Final packaging uses `pack_evidence.py` in its own bounded one-minute lease,
after this research report is frozen. It covers every ignored raw
`.json.gz/.jsonl/.log/-spec.json` in this lane, including contract histories.
Build/cache files are excluded. Private prefixes are normalized only in archive
copies; originals stay byte-for-byte unchanged, with original/stored SHA256
recorded per member. The three large preflight extracts are already preserved
by their separate verified archive. Final packaging is complete only when
[pilot-evidence-archive.json](pilot-evidence-archive.json) records a successful
roundtrip and [completion.json](completion.json) records successful checks and
the full portable-file inventory. These ledgers give the archive SHA and total
lease cost including packaging; no research result changes during packaging.

The final pure checks include six unit tests and `python3 contest.py check`.
A manual attempt to run the sampling tests with system Python lacked NumPy;
the prescribed RL virtual environment passed both tests without a code change.
That was an environment invocation issue, not an algorithm failure. Exact
closure outputs are retained in `completion.json`. Root state/index/history
updates are serialized by the coordinator, not this lane.

Hard research cutoff: 2026-11-09T02:00:00Z. Reserved 40001–40100 and65001–65040
remain unopened. At09:14Z roughly16hours46minutes remain to that cutoff.
Coordinator alone selects the cross-branch finalist.
# PPO-v3 execution report — stopped with an experimental candidate

As of2026-11-08T07:11:47Z. Results below are PROJECT_REPORTED from the linked
local records. **Research was stopped on explicit request. The original full
objective was not completed: the independent final-holdout was not run.**
The persistent goal was cleared, not marked complete; all scheduled checks were
cancelled. No automatic resume is authorized. See [stop record](user-stop.json).

A separately authorized [official platform series](platform/REPORT.md) has now
completed10 games with zero errors/timeouts/warnings. B2M won2/4 paired replays
versus3/4 for league3m and lost to the Gold boss. Technical compatibility passed;
strength gain is not demonstrated by these few games. No submission was made
during that test-only stage.

The subsequently authorized [B2M leaderboard submission](live-submission/REPORT.md)
is complete:41665776,382/989Gold after100% ranking, versus356/987 immediately
before replacement. Score12.90 versus13.51. All95 battle logs are clean,41 wins/
54 losses. No live improvement was shown. B2M remains active; restoring the
preserved league3m baseline is a recommendation, not an executed rollback.

The development winner B2,000,416 is available as a single C++17 file:
[handoff-b2m/bot.cpp](handoff-b2m/bot.cpp). Compilation, all24,833 embedded float32
values and4,978/4,978 commands from100 archived games passed. No external weight
file is required. Source size80,252UTF-16 units; SHA256
`b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214`.
This is a locally and platform-smoke-checked experimental candidate, not an
independently promoted bot. The old fallback source and submission history
remain preserved; B2M is now the separately authorized active deployment.

## Scope and preservation

Two independent continuations start from the unchanged PPO-v2 league3m actor:
checkpoint SHA256 `9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663`,
weights `dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb`.
Historical submission41657621 and `submissions/ppo-v2-league3m.cpp` remain
unchanged as fallback records; current deployment is41665776 as noted above.
The24,833-parameter standard/style2 actor, terminal-only win/draw/loss reward,
PPO math and inherited optimizer states are retained. No army/spawn shaping.
See [frozen protocol](PROTOCOL.md), [readiness and smoke evidence](READINESS.md),
and [live control log](CONTROL.md). Starting Git commit4baecdf3; no commit/push.

Runtime is GPT-6 Astra/codex_second. Compute is the existing local arm64 Mac CPU,
four torch threads/four rollout workers. Python3.14.6, torch2.15.0, NumPy2.5.4,
SciPy1.18.1, Apple Clang17.0.0, JDK17.0.21+9. Each run preserves versions,
configuration, commands, source hashes and intermediate checkpoints. External
compute spend is0; no rented GPU, paid API or repository publication. One
competitive B2M submission was separately authorized and completed afterward.

## Implemented and checked

35% current/current games plus a difficulty-prioritized diverse pool: league3m,
long-control3m, extended league, two recent versions, and unchanged Lacoz.
Eligible opponents receive6–25% each; hard games receive more mass. Both khoufou
versions, v6 and BC stay evaluation-only. New khoufou070bc128 has separate
unchanged source/provenance, never replacing the old372c1cd6 silently.

Production smoke and original-referee checks passed. Exact split/resume matched
actor, critic, optimizers, RNGs, opponent pool and export. The initial failed
logging-path test and corrected repeat are both retained. Pilot22,254 decisions
is not used to initialize either production run. Details: [READINESS](READINESS.md).

The initial map-content registry covers2,561 canonical/686 legacy hashes from
218 archived sources. Baseline400 games on40 new development maps were clean:
Lacoz59/80 wins, newkh71/80, oldkh72/80, v6 74/80, BC73wins/2draws/5losses.
All10,637 transitions/11,037 full states matched original Java. These maps are
now development data; seed novelty alone is not treated as an independent test.

## Training and adaptive selection

Each seed starts from the exact same preserved base, not from the other seed.
Checkpoints are saved every250k decisions; evaluation runs separately and serially.
Numbers count new controlled-player decisions after the original league3m base.

| Seed/block | New decisions | New games | Training minutes | Status |
|---|---:|---:|---:|---|
| A202611074, first | 2,001,950 | 45,312 | 55.47 | Complete |
| B202611075, first | 2,000,416 | 45,376 | 58.03 | Complete |
| A, second | 2,002,588 | 46,208 | 54.46 | Complete |
| B, second | 1,609,778 | 37,184 | 50.58 | Stopped; saved recovery point |

B recovery is readable/finite at3,610,194 cumulative decisions, iteration1290.
Two later diagnostic history rows remain preserved but are beyond that checkpoint.
Its `summary.json`/`final.pt` still describe the last completed first block;
`user-stop.json` records the interrupted second block. No result directory was
deleted. Own driver/trainer processes were verified absent after stopping.

Training sources remain frozen. First-block summaries/snapshots are retained;
latest mutable files are additionally backed up before second-block resume in
`continuation-block2/before-a` and `before-b`, with hashes. Completed blocks have
zero local-Lacoz teacher errors. Cumulative time caps add at most120 new training
minutes per block; the overall ceilings remain8M/8hours per seed.

The first840-game screen for each seed selected A1.002M/A1.502M and B2M/B1.502M;
both first averages were weaker. All1,680 games were clean and43,129 transitions/
44,809 full states matched Java. These12-map screens are adaptive selection only.

### First full40-map panel

[Ranking](full-dev-block1-ranking.json):2,320 games, zero own technical errors.
Two Lacoz technical outcomes for other candidates are excluded from paired
comparisons, not counted as strategic wins. All60,994 transitions/63,312 full
states in2,318 clean games matched Java. B2,000,416 leads under the predeclared
primary mean and one-point earlier/simpler tie rule.

| Matchup | B2M wins/80 | Simultaneous base score/80 | Paired gain, pp |
|---|---:|---:|---:|
| Lacoz | 60 | 58 | +2.50 |
| New khoufou | 77 | 71 | +7.50 |
| Old khoufou | 76 | 72 | +5.00 |
| v6 | 76 | 74 | +2.50 |
| BC | 77 | 74 | +3.75 |
| Direct versus base | 57 | — | — |

Base BC score includes draws. Equal-weight external gain is4.25pp; individual
paired map-cluster95% intervals still include zero. A1,501,957 has3.50pp mean
external gain, with Lacoz-3.75pp and positive gains on the other four opponents.
This is an adaptive development winner, **not independent promotion evidence**.

Broad point gains justified one more bounded block on each seed. The prior
full-panel champion is retained alongside at most one new admissible screen
leader per seed. See [continuation decision](CONTINUATION.md). Synthetic budget,
checkpoint-selection, retention, tie and failed-incumbent checks passed.

The second A984-game screen is complete: zero technical errors,24,502 transitions/
25,486 states exact. A1.502M still leads; challengerA3,000,798 advances with it.
The second average fails the BC safeguard (22/24 versus24/24base, -8.33pp), despite
a higher primary point estimate. Final A4M also fails that safeguard. No new A
improvement has been demonstrated. The three averaged snapshots were3,750,930/
4,001,815/4,004,538; the last two are close because of final-rollout overshoot.
All six A exports passed1,000/1,000argmax comparisons. B second-block screen and
the second full40-map panel were not started before the stop request.

## Bounded search: closed, not confirmed

The pilot stayed within00:00–04:00UTC8Nov and closed02:40UTC. Joint-action plans
were tested against multiple preselected enemy response models, recomputing
future policies. A standalone absolute-player-order bug was repaired before
external evaluation; failed records remain, and post-repair parity was1,986/
1,986 complete plans. The native search library itself was unchanged.

External evaluation:288 screening games, then448 confirmation games on28 other
development maps, with no parameter change. All736 games were clean;21,009
transitions/21,745 states matched Java. The selected two-turn search gained
7.1429pp in equal-weight external score; map-cluster95%CI[0,15.4762]. The strict
lower-bound>0 teacher gate failed. [Decision](search/decision.json):not_confirmed.
No teacher dataset/training starts, no post-result threshold change or new maps
to chase significance. This is inconclusive, not proof that search has no effect.
The multi-network prototype also is not a deployable source-size-compliant bot.

## Final stage not executed before the stop request

The original protocol requires one candidate frozen after research decisions, before generating or
playing any40001–40100 map. [Final safeguards](FINAL_GATES.md) require a rebuilt
content-exclusion registry, both actual single-source packages, exactly2,200
games, native/Java verification and paired map-cluster confidence intervals.
Promotion requires direct score≥55% with lower95% bound>50%, external mean
gain≥3pp, no opponent drop>5pp, zero own technical failure, and adequate clean
coverage. Otherwise retain league3m; no final-set tuning or alternate finalist.

Final tooling is prepared but has not run. Eleven synthetic final-gate tests
passed. Old-base packaging smoke verified all24,833 float32 values and890/890
saved-game commands; source80,252UTF-16 units is below100,000. A build-only
packaged harness smoke played zero games. These are tool checks, not new PPO
strength or official-platform timing evidence.

Read/play OAuth subsequently succeeded for the separately authorized10-game
platform series linked above. Fresh official GET confirms the deadline
2026-11-09T09:00Z. The token remained only in memory and the client exited after
testing. The old source and submission41657621 were verified unchanged during
those tests; all IDE overwrite flags remained false. Subsequent explicit
authorization and submit scope enabled the one B2M submission reported above.
API client236 has now exited; no further submission, rollback or research is
authorized.

## Executed driver commands

Run from the original checkout. Existing output directories are deliberately
not reusable; these commands document the actual launch, not instructions to
overwrite/re-run the preserved experiment.

```sh
caffeinate -s code/arena/.venv-rl/bin/python code/rl/v3/campaign.py --arms a b
caffeinate -s code/arena/.venv-rl/bin/python code/rl/search/run_external.py
caffeinate -s code/arena/.venv-rl/bin/python code/rl/v3/full_development.py --block 1
caffeinate -s code/arena/.venv-rl/bin/python code/rl/v3/continue_blocks.py --block 2
```

Exact per-stage commands, timing, errors and isolated output paths are recorded
in `campaign-events.jsonl` and `continuation-block2-events.jsonl`. Frozen panel
snapshots preserve sources/weights and complete original-referee game records.
Long processes were checked using durable15–20minute continuation messages.
There are no remaining scheduled checks or active experiment processes.
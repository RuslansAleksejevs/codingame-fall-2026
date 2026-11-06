# Public bots versus baseline-v2

The baseline lost **all 200 games**: 100 against khoufou and 100 against Lacoz, with no draws. The measured series had no command errors, timeouts or referee failures.

Date: 2026-11-05, America/Los_Angeles. Classification: PROJECT_REPORTED. Sources: `summary.json`, archived `matches.jsonl`, `audit.json` and 200 complete game records. These are actual local matches, not contest rankings.

## Frozen opponents

These were the two most substantial public solutions found in the research; their standing among all contest entrants was not established.

| Bot | Source | Commit |
|---|---|---|
| [khoufou](https://github.com/khoufou/Codingame_2026-11_FallChallenge/blob/372c1cd6738d456513cb50705b98549eedfdfad8/Player.java) | Player.java | 372c1cd6738d456513cb50705b98549eedfdfad8 |
| [Lacoz](https://github.com/Lacoz/cg2026/blob/7f1901834d2ffc16532e083edfec8cbdb5941ab6/bot.py) | bot.py | 7f1901834d2ffc16532e083edfec8cbdb5941ab6 |

Sources under `code/opponents/public/` and the experiment's `snapshots/` are unchanged. Git blob SHA was checked against GitHub; SHA256 and provenance are in PROVENANCE.json and manifest.json. Executable I/O paths were reviewed before running. No explicit license was found. Copies are used for local comparison in a private repository, not submitted as the project's solution.

The baseline and `submissions/baseline-v2.cpp` were unchanged. Source SHA256: `3045b35c774824d724340cb9f42be2fc156cd2c1dced476941f1d8d30e98df39`.

## Method

- Seeds1001–1050, both seats, both opponents: 50 × 2 × 2 = 200 games. Map identity across seats/opponents was checked. There are 50 distinct maps, not 200 independent maps.
- Frozen baseline-v2 binary from the preceding validation. These maps were not used to tune its strategy.
- Original unmodified referee b6913124a10de328316ff42906448a18cb948431, league3, all actions available.
- GameManager limits: 1000 ms first answer, 50 ms thereafter, verified from core4.1.6 bytecode. Sequential matches; summed match-process time about 3.93 minutes.
- Temurin17.0.21+9; Python3.14.6, NumPy2.5.4, SciPy1.18.1 in an isolated environment. BLAS/OMP use one thread. This is not an exact copy of CodinGame's servers.
- A preliminary cold Python import exceeded the first-turn limit and was retained separately in `experiments/2026-11-05-public-bots-smoke/`. Warm import took about 0.30 seconds and the next smoke game ended normally. The measured series then retained every one of its 200 outcomes; neither opponent code nor time limits were changed.

## Results

| Metric | Against khoufou | Against Lacoz |
|---|---:|---:|
| Wins / draws / losses | 0 / 0 / 100 | 0 / 0 / 100 |
| Wins from first / second seat | 0/50 / 0/50 | 0/50 / 0/50 |
| Median own decisions before defeat | 36 | 25 |
| Decision-count range | 22–62 | 14–47 |
| Spawned units per game, own / opponent | 18.38 / 43.43 | 11.64 / 73.58 |
| Captures per game, own / opponent | 22.82 / 67.90 | 13.72 / 87.09 |
| Army at start of turn 10, own / opponent | 8.77 / 12.12 | 8.70 / 20.96 |
| Own surrounding deaths per game | 12.14 | 10.47 |
| Own ATTACK deaths per game | 6.83 | 3.60 |
| Command errors / timeouts | 0 / 0 | 0 / 0 |

Capture counts include recaptures. Reinforcements and losses count successful referee events, not requested commands. Decision counts start at one. All games reached turn 10, so that army comparison does not select only long games.

Against khoufou, 68 losses ended by enemy domination, 20 by inability to score and 12 by losing all units/triangles. Against Lacoz, 57 ended by inability to score and 43 by complete loss of units/triangles. All losses were early. Final score -1 represents elimination; its mean is not used as a strength measure.

Own planning time: median0.375 ms, p95 0.598 ms, maximum8.388 ms. These are internal process timings, not full server response times. No evidence of computation speed limiting this result was found.

## Interpretation

**Measured:** khoufou spawned 2.36 times as many units and Lacoz 6.32 times as many. By turn 10, Lacoz averaged about 21 units versus 9. Of 3,304 counted own deaths, 2,261 were caused by surrounding (**68.4%**); ATTACK accounted for 31.6%. Own surrounds killed only 87 enemy units across the series.

**Source observations:** baseline-v2 issues at most one SPAWN per turn and does not coordinate clearing spent triangles for reuse. Both opponents reinforce multiple times and clear spent triangles. khoufou also plans attacks and surrounds; Lacoz uses time-bounded search and road changes. Lacoz successfully added502 and removed102 roads in these matches.

**Hypothesis:** army growth and triangle reuse are leading improvement candidates, followed by surrounding prevention. A larger army supports expansion and denies enemy control. These observations alone do not isolate any feature's causal contribution or prove one change would close the gap.

The earlier40/40 result only established superiority over an adapted weak level1 opponent. Lacoz defeated this baseline faster, but the two public opponents were not played against one another and no overall ranking is claimed.

## Audit and limitations

`audit.json` confirms 200 valid results and 6,303 decision states: viewer-protocol army counts match bot stderr. Units before declared defeat balance against initial units, spawns and losses. Every launcher exited0.

On khoufou seed 1012/seat0 and seed 1034/seat1, the original referee executes one additional attack in a terminal frame after announcing defeat. Four displayed units are removed without appearing in the text event summary. Loss statistics therefore refer to events before declared game end; outcomes are unaffected and complete records are retained.

Fixed maps do not guarantee identical Lacoz decisions because its search is time-bounded. Conclusions apply to these versions and local runs. Live ranking, opponents' current positions and exact contest-IDE alignment were not measured.

## Follow-up hypotheses

1. Allow multiple useful SPAWN commands and measure the isolated effect.
2. Clear and recapture spent triangles; coordinate shared target corners.
3. Estimate surrounding risk before movement.

Compare each change with baseline-v2 and both opponents. Seeds1001–1050 become development maps; improved candidates need a separate new validation set. Deep search is not necessary to test these simple hypotheses.

## Reproduce and records

Environment setup: `code/opponents/public/README.md`. Original command:

```sh
python3 code/build_public.py
python3 code/benchmark_public.py --seeds 1001:1050 --out experiments/2026-11-05-public-bots-v2
```

Use a new output directory when repeating. manifest.json contains versions, commands and provenance; matches.jsonl contains outcomes, actions and trajectories; summary.json aggregates results; audit.json records checks. Snapshots preserve sources; specs, logs and JSON.gz records are in `records.tar.gz`. Executable binaries are excluded from Git.

Paid external cost: 0. This experiment made no contest submissions, public releases or messages to participants.

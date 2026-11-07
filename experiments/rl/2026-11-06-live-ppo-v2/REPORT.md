# PPO v2 live deployment

**Submitted and ranked: 340th of 937 overall, Gold league**, at
**2026-11-07T08:01:22.885820Z** (00:01 PST). Ranking is 100% complete.
The active submission is **41657621**, PPO v2 league3m with the full action set.
TrueSkill score: **13.29**; within Gold: **340/486**.

The final snapshot contains **52 wins, 0 draws and 40 losses in 92 completed Gold games**.
Every log was inspected: **zero own command warnings, crashes or timeouts**.
This is a current contest rank, not the final result when the contest ends.
[Public leaderboard](https://www.codingame.com/contests/fall-challenge-2026/leaderboard/global)
· [Machine-readable result](result.json).

## Exact policy and packaging

The actor is the previously selected **PPO v2 league3m**, with 24,833 float32 parameters,
feature style 2 and dimensions 128 → 128 → 64 → 1. Its text weight SHA256 remains
`dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb`.
No retraining or quantization was performed.

`code/rl/export/package.py` embeds the exact IEEE-754 bits using 15-bit Unicode symbols.
The generated C++17 source needs no external files or libraries. The current full and
Silver profiles each contain **80,247 UTF-16 units / 186,203 UTF-8 bytes**. Unicode inside
the weight literal is opaque binary data; repository documentation remains English.

The full profile preserves all trained actions. The Silver profile masks road actions,
which the platform does not yet permit there, before choosing the highest-scoring candidate.
Both use the same network. `package.json` and `package-silver.json` identify exact sources.
Accepted submission sources are retained as compressed API responses and checked by SHA256.

## Local verification

All 24,833 embedded values match the original C++ text loader bit for bit.
On 100 archived games from both seats, **5,070 complete plans** of the full profile match
the original bot. Another **5,070 Silver plans** match the original scalar network with the
same legal-action mask. The Silver outputs contain no road commands.

The vectorized loop preserves per-neuron summation order. With contraction disabled,
10,000 random forward results match bit for bit. Under default Apple Clang contraction,
loop layouts differ slightly: maximum absolute error 0.000244141 and normalized error
4.11242e-5. The tested complete plans still match. This does not guarantee identical
floating-point arithmetic or decisions on every possible state/compiler.
See `package-verification.json` for inputs/output hashes, compiler and local timings.

## Platform findings and timing fix

The live Bronze statement contains a misleading template sentence saying all rules are
unlocked in Bronze. Actual Bronze accepts MOVE/SPAWN; two ATTACK commands were rejected
without aborting the initial self-play test. The refreshed Silver statement explicitly
adds ATTACK and still omits roads. The Silver profile implements that actual action set.
Initial and refreshed statements and the input stub are archived.

The initial package won both smoke tests against the Bronze boss and B4LBU. It then
completed its 60 Bronze ranking games with **58 wins and two losses**, both caused by
own timeouts against Captainseb. It finished first in Bronze and entered Silver at
**2026-11-07T07:24:38.074Z**. That initial source and its failures are preserved.

To fix the timeout, `inference.hpp` transposes each dense layer so independent output
neurons can be processed by SIMD. Weights, features, neuron summation order and tie-breaking
remain unchanged. This is a deployment speed improvement, not another training run.

| Identical platform replay | Initial maximum plan time | Optimized maximum | Ratio |
|---|---:|---:|---:|
| Ranked-timeout map | 64.797 ms | 13.842 ms | 4.68× |
| Self-play map | 55.258 ms | 8.725 ms | 6.33× |

Both complete output sequences match, including both self-play seats. Timings are measured
wall time inside the bot, not a direct measurement of the platform's timeout clock; machines
and scheduling vary. The unoptimized timeout-map replay happened to finish despite its
large measured time. The two original ranked losses show the actual deployment failure.

The optimized Silver profile also won a test against Lord Bossington, with maximum measured
plan time **6.661 ms**, no warnings and no timeout. One boss test is a functional check,
not an estimate of its general win probability. Test logs and their exact source versions
are mapped in `source-manifest-tests.json`; paired timings are in `inference-speedup.json`.

## League progression

The initial submission was **41657474** (unoptimized full-rule source). It passed Bronze,
then played a partial Silver series before replacement. Submission **41657553** used the
optimized Silver profile. At the promotion snapshot, its battle list contained **54 wins
and 7 losses in 61 finished games**; the arena continues to add games, so this is an observed
snapshot rather than a fixed 60-game independent tournament. All 61 logs were inspected:
**zero own command warnings, crashes or timeouts**.

Gold was entered at **2026-11-07T07:38:54.101Z**. Its statement unlocks ADD_PATH/REMOVE_PATH
and says higher leagues add no further rules. The full-rule source was tested against
DomiKo (then first overall) and ViktorCs (around 200th): both were game losses, without
technical failures; maximum measured plan times were 1.244 and 2.522 ms respectively.
The full source was submitted as **41657621**, SHA256
`199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1`.
The API readback matches the generated source exactly.

Gold is the highest open league at this snapshot; the next league is scheduled for
2026-11-07T09:00:00Z. No future monitoring or scheduled task was created.

## Evidence and reproduction

- `COMMANDS.md` and `docs/rl/DEPLOYMENT.md` describe packaging, verification and API use.
- `progress-*.json`, leaderboard snapshots and battle lists record observed ranking states.
- `games/` contains the inspected full ranked-game logs as deterministic `.json.gz` files; `test-*.json` contains full tests.
- `platform-verification.json` separates command warnings from crash/timeout evidence.
- `package-initial.py`, `package-initial.json`, `package-verification-initial.json` and
  `submission-source.json.gz` retain the original deployment. `fast-unmasked-source.cpp.gz`
  retains the intermediate optimized source used for paired timing tests.

All timestamps in API records are UTC. The experiment directory uses the local start date,
2026-11-06 in America/Los_Angeles. Public ranks are snapshots of an ongoing contest,
which ends **2026-11-09T09:00:00Z**; they are not the final contest result.

Official sources: [contest](https://www.codingame.com/contests/fall-challenge-2026),
[API skill](https://www.codingame.com/api/v1/docs/skill),
[API reference](https://www.codingame.com/api/v1/docs/api),
[promotion rules](https://www.codingame.com/api/v1/docs/leagues).
Live observations are **SOURCE_VERIFIED**; local verification/timing are **PROJECT_REPORTED**.
OAuth credentials remained only in the task process's memory and are absent from artifacts.
The authenticated process was closed after the final reads.
All preparation ran on the MacBook; **$0 external compute spend**. Subscription quota and
electricity were not measured. Main/v6 and all training weights remain unchanged.

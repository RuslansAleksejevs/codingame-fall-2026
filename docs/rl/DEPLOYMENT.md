# PPO v2 single-file deployment

The selected `league3m` actor is packaged in `submissions/ppo-v2-league3m.cpp`
(full rules) and `submissions/ppo-v2-league3m-silver.cpp` (Silver).
The Silver profile excludes ADD_PATH and REMOVE_PATH candidates before scoring,
matching the current league rules. It still supports ATTACK. Both contain the same weights.
It uses standard C++17 and requires no weight file, Python, PyTorch or network access.
The network, features and action decoder are unchanged from the selected local policy.
The deployment uses a transposed weight layout to vectorize independent output neurons;
the mathematical accumulation order within each neuron is preserved.

The active Gold submission is the full profile, **41657621**, ranked **340/937 overall**
at 2026-11-07 08:01 UTC. Silver is retained as a tested intermediate profile.

## Build and verify

```sh
python3 code/rl/export/package.py
python3 code/rl/export/package.py --league silver
clang++ -std=c++17 -O3 submissions/ppo-v2-league3m.cpp -o code/build/ppo2-submission
# Requires the local native simulator libraries and the RL Python environment:
code/arena/.venv-rl/bin/python code/rl/export/verify_package.py
python3 code/platform/analyze_live.py
```

The packager verifies the selected weight hash, converts the original numbers to float32,
and stores the bits in 15-bit Unicode symbols. The generated Unicode is opaque model data,
not natural-language documentation. All symbols are BMP characters with three UTF-8 bytes.
The source has 80,247 UTF-16 units and 186,203 UTF-8 bytes. The live report identifies each exact source accepted by the platform.
There is no quantization. The verifier compares all 24,833 values against the original C++
text loader and compares complete plans on 100 archived games from both seats.

GCC optimization is enabled in the generated source. The compiler still determines
floating-point execution details. With contraction disabled, 10,000 random forward values
match bit for bit. Default Clang contraction produces small numerical differences between
loop layouts (maximum normalized error 4.12e-5), while all 5,070 replay plans still match.
Two paired live tests also produce identical complete command sequences. These checks do
not prove bitwise identical arithmetic on every compiler and CPU.

## Platform operations

The official [CodinGame API skill](https://www.codingame.com/api/v1/docs/skill),
[API reference](https://www.codingame.com/api/v1/docs/api) and
[league guide](https://www.codingame.com/api/v1/docs/leagues) describe the workflow.
Use `/challenges/fall-challenge-2026`, not the permanent TryAngle Catch puzzle.

`code/platform/codingame_session.py` accepts one JSON command per line. It uses an OAuth
device authorization with `challenge:read challenge:play challenge:submit` and keeps
credentials in process memory only. Do not commit credentials or print them in logs.
An `auth_start` command returns the approval URL; after approval, `auth_poll` completes
the connection. `exit` drops the in-memory credential. A later process needs authorization again.

Request commands accept `path`, optional `method` and `body`, optional `code_file`
(loaded into the request body), and an optional `save` path under `experiments/`.
The optional `keys` list limits console output without truncating the saved response.
The client is restricted to this contest's endpoints, its tests and game logs.
It does not modify IDE drafts or settings.

Test with `POST /challenges/fall-challenge-2026/test-games?wait=30&format=json`,
language `C++`, the generated source, and a boss or permitted opponent.
Inspect complete logs, including warnings: a finished game is not proof that every command
was accepted. Bronze rejected two ATTACK commands in the self-play test without aborting it.
That initial full-rule version could reserve resources internally for unavailable actions.
Silver permits attacks but not roads, so the Silver profile masks road candidates.
Its 5,070 replay plans are checked against the original scalar network with the same mask.
The full-rule profile is separately checked against the unchanged original policy.
The live report records promotion and later rules.

Submission is a separate `POST /challenges/fall-challenge-2026/submissions` action.
Verify the returned submission's source hash. Poll progress at sensible intervals until
`percentage` is 100 and `in_progress` is false. Follow eligible promotions: new league rules
can stop the old submission and require another submission of compatible code.
Refresh the statement after every promotion, and distinguish global rank from league rank.

See [live evidence and results](../../experiments/rl/2026-11-06-live-ppo-v2/REPORT.md).

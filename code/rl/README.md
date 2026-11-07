# Local learning code

The branch implements behavior cloning and PPO self-play fine-tuning. The [BC guide](../../docs/rl/IMPLEMENTATION.md) describes exact state/action semantics and teacher coverage; the [PPO guide](../../docs/rl/PPO.md) describes whole-turn likelihoods, the critic, opponent pool and reproduction. Separate [BC](../../experiments/rl/2026-11-06-bc-v1/REPORT.md) and [PPO v1](../../experiments/rl/2026-11-06-ppo-v1/REPORT.md) reports retain both controls and actual results. The [larger PPO campaign](../../experiments/rl/2026-11-06-ppo-v2/REPORT.md) adds longer-training controls, an original-opponent league and an isolated road-observation experiment; [implementation details](../../docs/rl/LEAGUE.md) describe their exact differences.

| Directory | Entry points |
|---|---|
| `sim/` | C++ rules, C ABI, Python wrapper, original-Java differential oracle, archive and randomized parity checks |
| `data/` | Reconstruct archived decisions, audit teacher plans, split whole maps and generate novel maps with the original Java generator |
| `models/` | Shared 128-feature encoder, resource-aware decoder and native MLP |
| `train/` | PyTorch BC/PPO, native self-play collection, CPU/MPS benchmark, bounded runs and checkpoint selection |
| `league/` | Separate native collector, frozen anchors, wider history, original Lacoz bridge and Java observation checks |
| `roads/` | Separate feature variant, warm-start conversion, collector and style-3 standalone bot |
| `export/` | Original protocol C++ bot; tensor/text/native prediction agreement |
| `eval/` | Complete-policy speed, frozen original-arena tournament, map-clustered paired analysis |
| `configs/` | Exact measured dependencies and the selected local RL policy manifest |

After `python3 code/rl/build.py`, run a trained bot with:

```sh
code/build/bc-bot experiments/rl/2026-11-06-bc-v1/training/weights.txt 2
```

It reads the regular CodinGame protocol on stdin and writes one command plan per line. Style 2 is the tested equal teacher mixture. Styles 0/1 exist as teacher-conditioning inputs but are not separate validated candidates.

The simulator's terminal flag must be checked before advancing another turn. A joint step receives both plans selected from the same pre-state. Native simulation covers legal game mechanics; the original Java arena supplies process timeouts and authoritative match results. Compiled binaries, environments and derived feature arrays are ignored local caches.

PPO uses the same bot executable and actor format; replace the weight path with `experiments/rl/2026-11-06-ppo-v1/training/weights.txt`. The training-only critic is not part of deployment.

The isolated continuation entry points are `train/ppo_long.py`, `train/ppo_league.py` and `train/ppo_roads.py`. Each saves complete resumable training state and immutable milestone exports; the original v1 trainer remains unchanged. Exact run commands and bounds are recorded in [the campaign command log](../../experiments/rl/2026-11-06-ppo-v2/COMMANDS.md).

Road-model weights require `roads/bot.cpp` with style **3**. They share the matrix-file format with standard weights but use different inputs, so the feature variant must accompany the file. Named-policy panels declare this explicitly in `policy_variants`. `eval/panel.py` runs the original timed arena; `verify_panel.py` audits frozen artifacts/map novelty and native outcomes, while `verify_java_panel.py` compares every full state against original Java.

The current selected research model is recorded in [`configs/selected-policy.json`](configs/selected-policy.json), including weights/checkpoint hashes and the confirmation report. Build and run it with:

```sh
python3 code/rl/build.py
code/build/bc-bot experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt 2
```

The executable retains the historical `bc-bot` name; the supplied weights determine whether it runs BC, PPO v1 or PPO v2. These weights use ordinary style 2, not the optional road variant. This is the local stdin/stdout deployment, not a validated single-file contest submission.

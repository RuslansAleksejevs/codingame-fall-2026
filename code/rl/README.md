# Local learning code

The branch implements behavior cloning and PPO self-play fine-tuning. The [BC guide](../../docs/rl/IMPLEMENTATION.md) describes exact state/action semantics and teacher coverage; the [PPO guide](../../docs/rl/PPO.md) describes whole-turn likelihoods, the critic, opponent pool and reproduction. Separate [BC](../../experiments/rl/2026-11-06-bc-v1/REPORT.md) and [PPO](../../experiments/rl/2026-11-06-ppo-v1/REPORT.md) reports retain both controls and actual results.

| Directory | Entry points |
|---|---|
| `sim/` | C++ rules, C ABI, Python wrapper, original-Java differential oracle, archive and randomized parity checks |
| `data/` | Reconstruct archived decisions, audit canonical teacher plans, build whole-map training/validation splits |
| `models/` | Shared 128-feature encoder, resource-aware decoder and native MLP |
| `train/` | PyTorch BC/PPO, native self-play collection, CPU/MPS benchmark, bounded runs and checkpoint selection |
| `export/` | Original protocol C++ bot; tensor/text/native prediction agreement |
| `eval/` | Complete-policy speed, frozen original-arena tournament, map-clustered paired analysis |
| `configs/` | Exact measured training dependencies |

After `python3 code/rl/build.py`, run a trained bot with:

```sh
code/build/bc-bot experiments/rl/2026-11-06-bc-v1/training/weights.txt 2
```

It reads the regular CodinGame protocol on stdin and writes one command plan per line. Style 2 is the tested equal teacher mixture. Styles 0/1 exist as teacher-conditioning inputs but are not separate validated candidates.

The simulator's terminal flag must be checked before advancing another turn. A joint step receives both plans selected from the same pre-state. Native simulation covers legal game mechanics; the original Java arena supplies process timeouts and authoritative match results. Compiled binaries, environments and derived feature arrays are ignored local caches.

PPO uses the same bot executable and actor format; replace the weight path with `experiments/rl/2026-11-06-ppo-v1/training/weights.txt`. The training-only critic is not part of deployment.

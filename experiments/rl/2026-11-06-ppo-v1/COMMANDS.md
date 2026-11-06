# Execution commands

Run from the repository root. Raw output directories must be new. The saved maps, checkpoints and manifests identify the actual first run; rerunning these now is reproduction on known maps.

## Build and correctness

```sh
python3 code/rl/build.py
python3 code/rl/data/ppo_maps.py --out experiments/rl/2026-11-06-ppo-v1/maps.json
code/arena/.venv-rl/bin/python code/rl/train/test_ppo.py --maps experiments/rl/2026-11-06-ppo-v1/maps.json --out experiments/rl/2026-11-06-ppo-v1/tests-cpu.json --device cpu
code/arena/.venv-rl/bin/python code/rl/train/test_ppo.py --maps experiments/rl/2026-11-06-ppo-v1/maps.json --out experiments/rl/2026-11-06-ppo-v1/tests-mps.json --device mps
```

The MPS test and benchmark used permitted local execution with Metal access; the sandbox reports MPS unavailable. The initial functional pilot used `--steps 1500 --games 16 --workers 4 --device cpu --pilot --minutes 5` with output `pilot-cpu`. It precedes the categorical sampling boundary correction from `<=` to `<` for the zero-probability/U=0 edge case. The representative CPU/MPS benchmarks and main run use the corrected sampler.

## Pilots and main training

```sh
code/arena/.venv-rl/bin/python code/rl/train/ppo.py --maps experiments/rl/2026-11-06-ppo-v1/maps.json --out experiments/rl/2026-11-06-ppo-v1/benchmark-cpu --steps 10000 --games 64 --workers 4 --device cpu --pilot --minutes 5
code/arena/.venv-rl/bin/python code/rl/train/ppo.py --maps experiments/rl/2026-11-06-ppo-v1/maps.json --out experiments/rl/2026-11-06-ppo-v1/benchmark-mps --steps 10000 --games 64 --workers 4 --device mps --pilot --minutes 5
code/arena/.venv-rl/bin/python code/rl/train/ppo.py --maps experiments/rl/2026-11-06-ppo-v1/maps.json --out experiments/rl/2026-11-06-ppo-v1/training --steps 1000000 --games 64 --workers 4 --device cpu --minutes 60
```

Both representative pilots use the same initial weights, seed and three complete 64-game collection/update iterations. Floating-point backend differences change later sampled trajectories, so actual decisions differ slightly. Compare their complete elapsed throughput, not an isolated optimizer rate. The main run starts again from frozen BC; pilot updates are not carried forward.

## Export, original arena and final audit

```sh
code/arena/.venv-rl/bin/python code/rl/train/test_ppo.py --maps experiments/rl/2026-11-06-ppo-v1/maps.json --out experiments/rl/2026-11-06-ppo-v1/tests-trained.json --device cpu --checkpoint experiments/rl/2026-11-06-ppo-v1/training/checkpoint.pt
code/arena/.venv-rl/bin/python code/rl/export/verify.py --training experiments/rl/2026-11-06-ppo-v1/training --data code/build/rl-cache/bc-v1-clean --out experiments/rl/2026-11-06-ppo-v1/export-verification.json
python3 code/rl/eval/tournament.py --weights experiments/rl/2026-11-06-bc-v1/training/weights.txt --ppo-weights experiments/rl/2026-11-06-ppo-v1/training/weights.txt --seeds 4101:4102 --smoke --out experiments/rl/2026-11-06-ppo-v1/smoke
python3 code/rl/eval/tournament.py --weights experiments/rl/2026-11-06-bc-v1/training/weights.txt --ppo-weights experiments/rl/2026-11-06-ppo-v1/training/weights.txt --seeds 7001:7050 --out experiments/rl/2026-11-06-ppo-v1/confirmation
python3 code/rl/eval/analyze.py experiments/rl/2026-11-06-ppo-v1/confirmation --before bc --after ppo --opponents v6 lacoz khoufou --out experiments/rl/2026-11-06-ppo-v1/comparison.json
python3 code/rl/eval/verify_run.py experiments/rl/2026-11-06-ppo-v1/confirmation --out experiments/rl/2026-11-06-ppo-v1/verification.json
python3 code/archive_run.py experiments/rl/2026-11-06-ppo-v1
python3 code/restore_records.py
```

Timed arena games run serially after learning stops. The two old smoke maps check the frozen deployment path and are excluded from final strength estimates. The final panel has seven pairings on each of 50 maps, both seats: 700 games. BC/PPO are rerun alongside each other, not compared against BC's previous 6001–6050 results. Opponent revision, rules, limits and decoder remain fixed.

Logs, representative sampled games and complete arena records are packed into deterministic `records.tar.gz` archives with personal paths normalized. Derived feature buffers, compiled binaries, local environments and rolling recovery checkpoints are ignored caches.

# Execution commands

Run from the repository root. Existing output directories are retained; use new names for reproductions. `--steps` is the cumulative number of additional controlled-player decisions beyond the frozen PPO v1 checkpoint.

## Maps and bridge validation

```sh
python3 code/rl/data/generate_maps.py --seeds 10001:12000 --out experiments/rl/2026-11-06-ppo-v2/maps-2000.json
python3 code/rl/league/build.py
code/arena/.venv-rl/bin/python code/rl/league/test_league.py --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --out experiments/rl/2026-11-06-ppo-v2/league-tests
```

The separate league collector was initially compiled with the same flags before the build wrapper was added. `league-tests/summary.json` records actual bridge validation.

## Pilots

```sh
code/arena/.venv-rl/bin/python code/rl/train/ppo_long.py --out experiments/rl/2026-11-06-ppo-v2/pilot-long --maps experiments/rl/2026-11-06-ppo-v1/maps.json --init experiments/rl/2026-11-06-ppo-v1/training/checkpoint.pt --initial-weights experiments/rl/2026-11-06-ppo-v1/training/weights.txt --steps 10000 --minutes 5 --pilot
code/arena/.venv-rl/bin/python code/rl/train/ppo_league.py --out experiments/rl/2026-11-06-ppo-v2/pilot-league --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --init experiments/rl/2026-11-06-ppo-v1/training/checkpoint.pt --initial-weights experiments/rl/2026-11-06-ppo-v1/training/weights.txt --steps 20000 --minutes 5 --pilot
```

The initial `pilot-long/ppo_long.py` snapshot predates the final source-freeze/resume bookkeeping; its math and rollout recipe are the same. Pilot optimization is not carried into production training.

## Longer-training control

```sh
code/arena/.venv-rl/bin/python code/rl/train/ppo_long.py --maps experiments/rl/2026-11-06-ppo-v1/maps.json --init experiments/rl/2026-11-06-ppo-v1/training/checkpoint.pt --initial-weights experiments/rl/2026-11-06-ppo-v1/training/weights.txt --out experiments/rl/2026-11-06-ppo-v2/control-long --steps 1000000 --minutes 120
python3 code/rl/eval/panel.py --spec experiments/rl/2026-11-06-ppo-v2/dev-long1m-spec.json --out experiments/rl/2026-11-06-ppo-v2/dev-long1m
python3 code/rl/eval/analyze.py experiments/rl/2026-11-06-ppo-v2/dev-long1m --before ppo1 --after long1m --opponents lacoz khoufou --out experiments/rl/2026-11-06-ppo-v2/dev-long1m-comparison.json
python3 code/rl/eval/verify_panel.py experiments/rl/2026-11-06-ppo-v2/dev-long1m --out experiments/rl/2026-11-06-ppo-v2/dev-long1m-verification.json
code/arena/.venv-rl/bin/python code/rl/train/ppo_long.py --maps experiments/rl/2026-11-06-ppo-v1/maps.json --init experiments/rl/2026-11-06-ppo-v1/training/checkpoint.pt --initial-weights experiments/rl/2026-11-06-ppo-v1/training/weights.txt --out experiments/rl/2026-11-06-ppo-v2/control-long --resume experiments/rl/2026-11-06-ppo-v2/control-long/final.pt --steps 3000000 --minutes 120
```

The first timed development panel finished before the control resumed and before the main league run started. Original referee games run serially with the frozen 1000/50 ms limits.

## Broader opponent pool

```sh
code/arena/.venv-rl/bin/python code/rl/train/ppo_league.py --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --init experiments/rl/2026-11-06-ppo-v1/training/checkpoint.pt --initial-weights experiments/rl/2026-11-06-ppo-v1/training/weights.txt --out experiments/rl/2026-11-06-ppo-v2/league-a --steps 3000000 --minutes 150 --seed 20261108
```

The league run and the second control block share the local CPU. Per-run wall time includes this contention; it is not an isolated throughput benchmark. Source snapshots, configuration, block requests and complete optimization logs identify the actual executions.

## Continuation correctness

```sh
code/arena/.venv-rl/bin/python code/rl/train/test_resume.py --out experiments/rl/2026-11-06-ppo-v2/resume-tests
```

Both the long and league-without-Lacoz recipes produced identical actor/critic tensors, optimizer states, opponent pool, NumPy sampling state and exported weights after a split run. Original wall-timed Lacoz behavior is intentionally excluded from this determinism test. The short tests ran while the two larger training jobs continued; their timings are not hardware benchmarks.

## Road-observation variant validation

```sh
python3 code/rl/roads/build.py
code/arena/.venv-rl/bin/python code/rl/roads/test_roads.py --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --out experiments/rl/2026-11-06-ppo-v2/roads-tests
code/arena/.venv-rl/bin/python code/rl/train/ppo_roads.py --out experiments/rl/2026-11-06-ppo-v2/pilot-roads --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --init experiments/rl/2026-11-06-ppo-v1/training/checkpoint.pt --initial-weights experiments/rl/2026-11-06-ppo-v1/training/weights.txt --steps 20000 --minutes 5 --pilot
code/arena/.venv-rl/bin/python code/rl/roads/verify.py --training experiments/rl/2026-11-06-ppo-v2/pilot-roads/step-00022346 --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --records experiments/rl/2026-11-06-ppo-v2/roads-tests/sample-records.json.gz --out experiments/rl/2026-11-06-ppo-v2/roads-export-verification.json
clang++ -std=c++17 -O3 -Wall -Wextra -Wpedantic code/rl/roads/bot.cpp -o code/build/roads-bot
```

The native road library was rebuilt after adding diagnostic export/anchor entry points; the collector and feature logic were unchanged. The exact pilot sources are retained under `pilot-roads/sources/`. The road binary uses style 3; frozen anchor binaries and ordinary policies use style 2. `panel.py` supports an explicit `policy_variants` mapping and compiles separate binaries, preserving the original standard-policy deployment source.

The MacBook was connected to AC power during the sustained runs. A bounded `caffeinate -s -t 14400` process kept the system awake on AC while this active experiment ran; it does not keep the display awake or create a recurring task.

The standalone road protocol was checked against native actions with:

```sh
code/arena/.venv-rl/bin/python code/rl/roads/protocol_check.py --weights experiments/rl/2026-11-06-ppo-v2/pilot-roads/weights.txt --binary code/build/roads-bot --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --records experiments/rl/2026-11-06-ppo-v2/roads-tests/sample-records.json.gz --out experiments/rl/2026-11-06-ppo-v2/roads-protocol-verification.json
```

All 246 complete command plans matched, across both player orientations. This is an untimed protocol check under training load, not a competitive result.

## Map-only control

After the longer-training control finished at 3,002,813 additional decisions, the following run started alongside the continuing league run:

```sh
code/arena/.venv-rl/bin/python code/rl/train/ppo_long.py --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --init experiments/rl/2026-11-06-ppo-v1/training/checkpoint.pt --initial-weights experiments/rl/2026-11-06-ppo-v1/training/weights.txt --out experiments/rl/2026-11-06-ppo-v2/map-only --steps 1000000 --minutes 90 --seed 20261108
code/arena/.venv-rl/bin/python code/rl/train/test_resume.py --recipes roads --out experiments/rl/2026-11-06-ppo-v2/resume-roads-test
```

The map-only arm starts from frozen PPO v1, not from the 3M control. The road resume check is a separate short deterministic test with the wall-timed teacher disabled.

## Complete-state original-Java replay audit

```sh
python3 code/rl/eval/verify_java_panel.py experiments/rl/2026-11-06-ppo-v2/dev-long1m --out experiments/rl/2026-11-06-ppo-v2/dev-long1m-java-verification.json
```

All 200 development games passed, including every intermediate score, unit count, edge, triangle/capture flag and terminal status. This untimed replay audit is safe to run during learning; it is not another strength/timing panel. The separate roads split/resume test also passed with identical learned tensors and exports.

## Main road-observation run

After the map-only arm finished at 1,002,950 additional decisions, the following started alongside the continuing original league run:

```sh
code/arena/.venv-rl/bin/python code/rl/train/ppo_roads.py --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --init experiments/rl/2026-11-06-ppo-v1/training/checkpoint.pt --initial-weights experiments/rl/2026-11-06-ppo-v1/training/weights.txt --out experiments/rl/2026-11-06-ppo-v2/roads-a --steps 1000000 --minutes 90 --seed 20261108
```

It restarts from the same frozen PPO v1 checkpoint with the recorded constant-input conversion; pilot updates are not reused.

After the main road block completed, its immutable 1,002,234-decision checkpoint passed the same export and protocol checks:

```sh
code/arena/.venv-rl/bin/python code/rl/roads/verify.py --training experiments/rl/2026-11-06-ppo-v2/roads-a/step-01002234 --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --records experiments/rl/2026-11-06-ppo-v2/roads-tests/sample-records.json.gz --out experiments/rl/2026-11-06-ppo-v2/roads-a-export-verification.json
code/arena/.venv-rl/bin/python code/rl/roads/protocol_check.py --weights experiments/rl/2026-11-06-ppo-v2/roads-a/weights.txt --binary code/build/roads-bot --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --records experiments/rl/2026-11-06-ppo-v2/roads-tests/sample-records.json.gz --out experiments/rl/2026-11-06-ppo-v2/roads-a-protocol-verification.json
```

The original league job was still training during these untimed correctness checks. All 11,324 logits agreed within 2.29e-5, all 206 anchor plans and all 246 standalone command plans matched.

## Common development panel

All four production training blocks finished before these timed games started. The panel freezes seven policies: PPO v1, longer-control 1M/3M, map-only 1M, league 1M/3M and roads 1M. The retained specifications contain the exact checkpoint paths and hashes. The 56 smoke games passed with zero technical errors and 1,490 matching native transitions.

```sh
python3 code/rl/eval/panel.py --spec experiments/rl/2026-11-06-ppo-v2/dev-common-smoke-spec.json --out experiments/rl/2026-11-06-ppo-v2/dev-common-smoke
python3 code/rl/eval/verify_panel.py experiments/rl/2026-11-06-ppo-v2/dev-common-smoke --out experiments/rl/2026-11-06-ppo-v2/dev-common-smoke-verification.json
python3 code/rl/eval/panel.py --spec experiments/rl/2026-11-06-ppo-v2/dev-common-spec.json --out experiments/rl/2026-11-06-ppo-v2/dev-common
```

The common development set is the previously inspected seeds 6001–6025, both seats, every policy against Lacoz and khoufou. Pair order rotates cyclically and the first executed seat alternates by map. Its 700 games are for selection; the 100 final-confirmation maps are still unopened.

The common panel completed all 700 clean games and passed both replay audits:

```sh
python3 code/rl/eval/verify_panel.py experiments/rl/2026-11-06-ppo-v2/dev-common --out experiments/rl/2026-11-06-ppo-v2/dev-common-verification.json
python3 code/rl/eval/verify_java_panel.py experiments/rl/2026-11-06-ppo-v2/dev-common --out experiments/rl/2026-11-06-ppo-v2/dev-common-java-verification.json
python3 code/rl/eval/analyze.py experiments/rl/2026-11-06-ppo-v2/dev-common --before ppo1 --after league3m --opponents lacoz khoufou --out experiments/rl/2026-11-06-ppo-v2/dev-common-comparison.json
python3 code/rl/eval/panel.py --spec experiments/rl/2026-11-06-ppo-v2/dev-safeguards-spec.json --out experiments/rl/2026-11-06-ppo-v2/dev-safeguards
```

`common-screen-decision.json` records the actual ranking and the three safeguard candidates. The 350-game safeguard panel is separate from the common Lacoz/khoufou screen.

All three initial leaders passed the safeguards: league3m won 42/50 against PPO v1, long3m and roads1m each won 39/50; all won 50/50 against v6. The PPO v1 control won 48/50 against v6. All 350 games were clean; 9,115 full states / 8,765 transitions matched original Java. `followup-training-decision.json` freezes the continuation targets before launching them. Pre-continuation summaries/hardware records were copied to `block1-summary.json` and `block1-hardware.json` in each continuing run.

```sh
python3 code/rl/eval/verify_panel.py experiments/rl/2026-11-06-ppo-v2/dev-safeguards --out experiments/rl/2026-11-06-ppo-v2/dev-safeguards-verification.json
python3 code/rl/eval/verify_java_panel.py experiments/rl/2026-11-06-ppo-v2/dev-safeguards --out experiments/rl/2026-11-06-ppo-v2/dev-safeguards-java-verification.json
code/arena/.venv-rl/bin/python code/rl/train/ppo_league.py --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --init experiments/rl/2026-11-06-ppo-v1/training/checkpoint.pt --initial-weights experiments/rl/2026-11-06-ppo-v1/training/weights.txt --out experiments/rl/2026-11-06-ppo-v2/league-a --resume experiments/rl/2026-11-06-ppo-v2/league-a/final.pt --steps 5000000 --minutes 190 --seed 20261108
```

The bounded AC-only keep-awake process was stopped and replaced with `caffeinate -s -t 10800` for the continuation/evaluation phase. It is owned by this active run and will be stopped on completion.

The league continuation stopped at its time cap after **4,836,947** cumulative additional decisions, 98,432 games and 11,411.79 seconds. The 5M sample target was not reached. The final immutable checkpoint is `league-a/step-04836947`; native diagnostics were 84/84 against BC and 75/84 against PPO v1. These are not original-arena confirmation results.

After the league process exited, the road continuation started:

```sh
code/arena/.venv-rl/bin/python code/rl/train/ppo_roads.py --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --init experiments/rl/2026-11-06-ppo-v1/training/checkpoint.pt --initial-weights experiments/rl/2026-11-06-ppo-v1/training/weights.txt --out experiments/rl/2026-11-06-ppo-v2/roads-a --resume experiments/rl/2026-11-06-ppo-v2/roads-a/final.pt --steps 2000000 --minutes 65 --seed 20261108
code/arena/.venv-rl/bin/python code/rl/export/verify.py --training experiments/rl/2026-11-06-ppo-v2/league-a/step-04836947 --data code/build/rl-cache/bc-v1-clean --out experiments/rl/2026-11-06-ppo-v2/league-a-extended-export-verification.json
```

The export check and packaging of completed artifacts run during the road training block, not during timed competitive evaluation.

The road continuation stopped at its cumulative time cap after **1,791,068** additional decisions, 35,968 games and 3,912.88 seconds. The 2M sample target was not reached. Its immutable checkpoint is `roads-a/step-01791068`. Native diagnostics were 80 wins / 2 draws / 2 losses against BC and 60/84 wins against PPO v1.

```sh
code/arena/.venv-rl/bin/python code/rl/roads/verify.py --training experiments/rl/2026-11-06-ppo-v2/roads-a/step-01791068 --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --records experiments/rl/2026-11-06-ppo-v2/roads-tests/sample-records.json.gz --out experiments/rl/2026-11-06-ppo-v2/roads-a-extended-export-verification.json
code/arena/.venv-rl/bin/python code/rl/roads/protocol_check.py --weights experiments/rl/2026-11-06-ppo-v2/roads-a/step-01791068/weights.txt --binary code/build/roads-bot --maps experiments/rl/2026-11-06-ppo-v2/maps-2000.json --records experiments/rl/2026-11-06-ppo-v2/roads-tests/sample-records.json.gz --out experiments/rl/2026-11-06-ppo-v2/roads-a-extended-protocol-verification.json
```

All 11,324 logits matched within 1.91e-5, all 206 anchor plans and all 246 standalone plans matched. The last protocol check ran after training had stopped. Its inherited generic note was corrected to be context-neutral, with actual execution context added to the report; numeric results and hashes were unchanged. The verifier now uses that neutral note for future runs.

`production-summary.json` records all four final run totals: 10,633,778 additional controlled-player decisions, 218,880 training games and 21,587.60 summed training seconds. The exact finalist roster, actual budgets and hashes are frozen in `dev-finalists-inputs.json` and the adjacent panel specification. No confirmation maps have been opened.

## Final development selection panel

All training and upload work stopped before this serial 1,150-game arena. The five candidates are league3m, long3m, roads1m, league_extended (4,836,947 decisions) and roads_extended (1,791,068), with PPO v1 as control. Every candidate plays Lacoz/khoufou/v6 and directly plays PPO v1 on the same 25 maps from both seats.

```sh
python3 code/rl/eval/panel.py --spec experiments/rl/2026-11-06-ppo-v2/dev-finalists-spec.json --out experiments/rl/2026-11-06-ppo-v2/dev-finalists
```

## Final development selection and confirmation launch

The 1,150-game finalist panel completed with all games clean. Both audits passed before selection:

```sh
code/arena/.venv-rl/bin/python code/rl/eval/verify_panel.py experiments/rl/2026-11-06-ppo-v2/dev-finalists --out experiments/rl/2026-11-06-ppo-v2/dev-finalists-verification.json
code/arena/.venv-rl/bin/python code/rl/eval/verify_java_panel.py experiments/rl/2026-11-06-ppo-v2/dev-finalists --out experiments/rl/2026-11-06-ppo-v2/dev-finalists-java-verification.json
python3 code/rl/eval/analyze.py experiments/rl/2026-11-06-ppo-v2/dev-finalists --before ppo1 --after league3m --opponents lacoz khoufou v6 --out experiments/rl/2026-11-06-ppo-v2/dev-finalists-comparison.json
python3 code/rl/eval/select_ppo_v2.py experiments/rl/2026-11-06-ppo-v2
code/arena/.venv-rl/bin/python code/rl/export/verify.py --training experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173 --data code/build/rl-cache/bc-v1-clean --out experiments/rl/2026-11-06-ppo-v2/selected-export-verification.json
python3 code/rl/eval/panel.py --spec experiments/rl/2026-11-06-ppo-v2/confirmation-spec.json --out experiments/rl/2026-11-06-ppo-v2/confirmation
```

Selection froze league3m and style 2 before opening seeds 9001–9100. The 1,800-game confirmation runs serially without concurrent training or uploads. The final test size is fixed.

## Completed confirmation and full audit

All 1,800 final games completed; the model and test size were not changed. The following commands passed after timed matches stopped:

```sh
code/arena/.venv-rl/bin/python code/rl/eval/verify_panel.py experiments/rl/2026-11-06-ppo-v2/confirmation --out experiments/rl/2026-11-06-ppo-v2/confirmation-verification.json
code/arena/.venv-rl/bin/python code/rl/eval/verify_java_panel.py experiments/rl/2026-11-06-ppo-v2/confirmation --out experiments/rl/2026-11-06-ppo-v2/confirmation-java-verification.json
python3 code/rl/eval/analyze.py experiments/rl/2026-11-06-ppo-v2/confirmation --before ppo1 --after ppo2 --opponents lacoz khoufou v6 bc --out experiments/rl/2026-11-06-ppo-v2/confirmation-comparison.json
python3 code/rl/eval/training_digest.py experiments/rl/2026-11-06-ppo-v2/control-long experiments/rl/2026-11-06-ppo-v2/map-only experiments/rl/2026-11-06-ppo-v2/league-a experiments/rl/2026-11-06-ppo-v2/roads-a --out experiments/rl/2026-11-06-ppo-v2/training-digest.json
```

`confirmation-decision.json` additionally records the selection-before-confirmation timestamp and hash checks, unchanged BC/PPO-v1/v6 controls, all clean outcomes, fresh-map counts and the measured primary gain. `resources.json` separates production training, panel time and goal-to-tournament wall time. `code/rl/configs/selected-policy.json` identifies the verified local RL model without changing main v6.

## Packaging

After all training, tournaments and audits finished, complete records were packaged without removing loose local copies:

```sh
python3 code/archive_run.py experiments/rl/2026-11-06-ppo-v2
```

This includes all 4,256 timed arena games, their specifications/logs, full optimization histories and sampled training trajectories. The 218,880 training games are summarized by rollout; they are not all stored as full replays. Binary executables/environments remain local caches. Tracked-file SHA256 inventory and archive restoration are checked before publication.

# Isolated strategy variants

| Variant | Base | Strategy change |
|---|---|---|
| v2 | experiments/2026-11-05-baseline-v2-validation/bot.cpp | Frozen original control |
| v3-multispawn.cpp | v2 | Multiple SPAWN commands per turn; each triangle spent once; original army cap and income reserve retained |
| v4-reset.cpp | v3 | Empty one spent neutral triangle until recapture becomes legal; temporarily block incoming moves and spawns on its corners |
| v5-protection.cpp | v3 | Adjust final positions to reduce surrounding risk, considering spawned units, visible forces and one-move enemy reinforcement |
| v6-attack.cpp | v3 | One ATTACK on the largest reachable enemy stack of at least four; require six own units and one per triangle corner; account for three consumed units and the spent triangle before movement/spawning |

v5 branches from v3 because v4 reduced development performance. Protection is therefore compared with v3, not v4. v5 makes up to six local movement adjustments while retaining useful captures. Coefficients were fixed before its run, not tuned on measured outcomes. Road changes remain unimplemented.

Freeze each source before its measured run. Do not replace a source after observing its results; use a new variant and output folder. Promote a candidate to `code/bot.cpp` only when measurements support it, retaining older variants.

```sh
python3 code/benchmark_public.py --source code/variants/v3-multispawn.cpp --label v3-multispawn --seeds 1001: 1050 --out experiments/new-series
```

`benchmark_ablation.py --variants label=source.cpp ...` schedules variants together but executes games sequentially, interleaving on each map/seat/opponent and rotating order. `analyze_incremental.py --pairs before:after ...` sets the correct comparison bases.

Keep all outcomes, including timeouts. Report wins caused by opponent errors separately; they do not establish greater strategic strength. Earlier plans and results are in `experiments/2026-11-05-incremental/`; ATTACK evaluation is in `experiments/2026-11-05-attack/`.

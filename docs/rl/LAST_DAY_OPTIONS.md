# Last-day options: retain the measured search advantage

Assessment: 8 November 2026, approximately 19:25 UTC. **Recommendations, not an approved or started campaign.** Official deadline: 9 November 09:00 UTC; preserve the earlier 02:00 UTC research cutoff and seven-hour final-check reserve. Estimates below are planning caps, not measured implementation times or promises of success.

## What is established

The [RL-v5 report](../../experiments/rl/2026-11-08-rl5/deadline-search/REPORT.md) and independent audits establish a useful local D16 teacher: +5.4167 percentage points against the three-opponent external composite, map-paired 95% interval [+1.25, +9.5833], 1,120 games, no technical errors. On a second, different map set, the unchanged teacher also outperformed the compact student. This is not a live leaderboard guarantee: two khoufou versions are related and several opponents are saturated.

The compact student was technically correct but rejected: −2.9167pp versus control and −9.1667pp versus teacher. Its dataset contained only 413 training roots from 12 maps, with one seed and two 400-update rounds. Data coverage, representational limits, distribution shift and objective mismatch remain competing explanations; none has been identified as the cause.

Generic PPO continuation, the particular exploiter pilot and difficult-start curriculum have not demonstrated a new deployable gain. Repeating them unchanged is not the best-supported last-day choice. A large GNN, BTR or MuZero rewrite has a poor fit to the remaining time and existing evidence.

## Ranked options

### 1. Package the useful teacher directly using lower-precision weights

**Highest priority.** Keep the bounded full-plan search, critic and diverse response models; deduplicate the shared actor/enemy weight set. Investigate a single, declared per-channel int8 or mixed-precision representation and decode to the existing float kernels at startup. This avoids relying on the failed attempt to teach all search behavior to a single small actor.

A fresh read-only [storage diagnostic](../../sources/2026-11-08-teacher-storage.json) checked all four frozen weight hashes. Their 99,332 total parameters occupy 397,328 float32 bytes. Three simple lossless encodings still need at least 178,117 15-bit symbols, before code. Plain float16 needs 105,955 symbols before code and therefore does not by itself fit the 100,000-unit source limit. Hypothetical int8 needs 52,978 symbols before scales/code: plausible room, **not a verified package**.

Suggested cap: 90–120 minutes for size/decoder/development checks. Reject early if the full source, initialization or whole-turn runtime cannot fit with margin. Quantization changes the policy: old D16 wins cannot be relabelled as results of the quantized bot. Compare logits, selected plans and fresh full games against both original D16 and league3m; preserve the independent confirmation and zero-own-error requirement. A technically valid package with lost strength must not be submitted.

### 2. A smaller search bot, with an explicit trade-off in opponent modeling

**Fallback if direct packaging fails.** Build one declared compact variant with the existing actor and a compact value function, and fewer/cheaper enemy-response policies. Use remaining storage/latency for evaluating coherent complete plans rather than independent unit moves. Keep a complete baseline plan and deadline reserve. This is a new candidate, not the same measured D16.

Suggested cap: 60–90 minutes for one development variant, not a combinatorial sweep. A reduced two-network representation may need lower precision or a smaller critic as well; two unchanged float32 networks already exceed the limit before code. Stop if the simplification loses the advantage on diverse opponents or cannot meet size/runtime. A high win rate against its own actor is insufficient: the Summer 2026 Ramza postmortem describes exactly that failure mode.

The main risk is removing diversity that may matter for robustness; its isolated causal contribution has not been measured. A single response model must not be treated as equivalent to the original ensemble. Do not open reserved final maps to choose among packaging variants.

### 3. A materially different, better-covered distillation pilot

**More uncertainty; longer-term value, weaker last-day priority.** Start from preserved league3m, collect substantially more diverse teacher decisions on declared training maps and the current student distribution. Diagnose the minority of teacher-changed decisions separately; use advantage/margin-aware targets or a small structured plan-ranking correction, while anchoring unchanged decisions. Test whether the compact representation can actually express the useful corrections before scaling data or training.

This is not "another 400 updates" or permission to assume data shortage is the diagnosis. Suggested pilot cap: 2–3 hours including collection and a fixed development comparison. Select by full-game performance/retention, not just imitation loss; then freeze once before independent confirmation. Stop if changed-plan fidelity and fresh full-game retention do not improve together. Do not spend the final-check reserve trying more seeds after a failed gate.

## Recommended allocation

Choose option 1 first; keep option 2 as a bounded fallback. Option 3 should not run in parallel with timed evaluations and should be deferred if the first two consume the research window. Three suggestions are not a recommendation to start three competing CPU campaigns.

Before any live replacement: one frozen deployable source, an independent reserved-map comparison with paired uncertainty and technical losses retained, exact export/source hashes, whole-turn timing, and a small official read/play check. OAuth and a ranking submission are separate authorized actions. If no candidate passes, retain the known bot; neither integration nor a dated ranking decline authorizes automatic rollback.

See [the evidence review](AI_COMPETITION_EDGE.md) for the broader research and winner accounts. The reason these three options concentrate on search is evidence prioritization, not a claim that all other RL methods are intrinsically inferior.
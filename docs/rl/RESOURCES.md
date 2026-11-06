# Local resources and coding workflow

As of **2026-11-06**. All future runtime/work estimates are **MODEL_INFERENCE**, not measured training results.

## Available machine and measured starting point

Read-only hardware inspection found an **Apple M4 MacBook Air**, **24 GB unified memory**, **10 CPU cores (4 performance, 6 efficiency)** and **10 GPU cores**. PyTorch was not found in the current `python3` environment; other environments were not exhaustively inspected. No package installation or training occurred during this research.

The latest original-referee benchmark recorded 55,901 candidate decision states over 33.678 summed match-process minutes: approximately **27.7 candidate decisions/s**. This includes subprocesses and normal match recording; it is not an optimized simulator or an RL learner benchmark. At that rate, merely collecting 10M such decisions takes about **100 hours**, before training. [Local report](../../experiments/2026-11-06-attack-holdout/REPORT.md).

Use an in-memory C++ simulator with batched Python training. Start with PyTorch CPU/MPS; compare both rather than assume a small network runs faster on the GPU. Apple documents MPS support and still labels the backend beta. JAX-Metal is explicitly experimental with unsupported functionality, so a CUDA/JAX competition package is not automatically portable. MLX is a possible later backend, but no MLX throughput or learner compatibility claim is made here. [PyTorch on Mac](https://developer.apple.com/metal/pytorch/), [JAX on Mac](https://developer.apple.com/metal/jax/).

## Conditional training time

Here a **sample** means one controlled player's full-turn decision used by the learner. If both players provide data, one joint game turn can produce two samples. Do not compare this with Atari video frames or optimizer updates.

`training hours = samples / measured end-to-end samples_per_second / 3600`.

| Sustained end-to-end training speed | 1M samples | 10M samples | 100M samples |
|---:|---:|---:|---:|
| 100 samples/s | 2.8 h | 27.8 h | 11.6 days |
| 500 samples/s | 0.56 h | 5.6 h | 2.3 days |
| 1,000 samples/s | 0.28 h | 2.8 h | 27.8 h |

These are scenarios, **not a measured 100–1,000 range for this game**. Include simulation, feature encoding, rollout inference and optimizer updates in the measured speed. Add evaluation, data preparation, engineering and repeated seeds separately. Three seeds roughly triple the corresponding training compute.

For calibration, linrock reports only 80–160 samples/s for a small Orbit Wars learner on an M-series MacBook. That game's work per step differs; neither its speed nor its three-day PPO run can be transferred directly here. [Primary report](https://www.kaggle.com/competitions/orbit-wars/discussion/733686).

Initial planning envelopes:

| Work | Bounded first experiment | Planning envelope after implementation |
|---|---|---|
| BC | 50k–300k verified labels, small network | Reserve 0.5–4 h for an initial fit/evaluation attempt; label generation may cost more. Re-estimate after one epoch. |
| BC + PPO | 100k smoke, then 1M samples | Hours for a pilot; a useful 5M–10M attempt could consume one to several nights. Strength is unproven. |
| Value + search | Small value fit and fixed candidate set | Similar small-model fit, plus potentially expensive search-label generation and external matches. |
| Plan-level Q-learning | 100k–1M samples with bounded replay | More reuse of data, but update cost must be timed; no assumed speedup over PPO. |
| Full learning from scratch | Tens/hundreds of millions of samples | Potentially days to weeks of repeated runs. Defer until simpler controls establish value. |

A first end-to-end prototype could require **2–5 focused development days**, before substantial tuning. This is a rough engineering estimate with simulator correctness as the largest uncertainty, not a deadline commitment. Research has not already completed that implementation work.

## Memory and disk

Start around 0.1–0.5M parameters. Float32 weights alone occupy roughly 0.4–2 MB; optimizer state, activations, replay, features and Python objects can dominate the actual footprint. Aim initially for a measured **8–12 GB process budget**, preserving room for the OS and development tools; reduce batching if swapping appears. This is a proposed cap, not observed memory usage.

For replay storage, derive allocation from serialized transition size: 100,000 records at 10 KB each are approximately 1 GB before overhead. Store compact state/actions and recompute bulky features when economical. Do not copy BTR's million-image-transition defaults into 24 GB unified memory. Keep a bounded checkpoint set and allocate roughly 5–15 GB of local experiment space initially, subject to actual free space and measured record sizes.

Measure sustained performance for at least 10–15 minutes; a short startup burst is insufficient for an overnight estimate. Training must resume safely after interruption or laptop sleep. No automatic overnight schedule or background monitor is created by this plan.

## Coding subscriptions are a separate resource

Existing coding subscriptions support design, implementation and analysis. The local Python/C++ process executes the games and weight updates. Do not invoke an LLM on every game turn or training sample; that would create an entirely different latency and usage budget.

Recommended work allocation:

| Model/tool | Bounded work |
|---|---|
| GPT-6 Astra | Simulator/action contract; representation and reward design; review of parity failures; experiment decisions; final interpretation |
| GPT-6 Luna | Implement specified modules, run already defined checks/experiments, repair localized failures, produce compact reports |
| Existing Claude Code access | Optional independent review of simulator edge cases or a frozen diff; no assumed quota or model tier |

For the first functioning prototype, budget roughly **6–8 substantial Astra work packets** and **15–30 focused Luna packets**. A packet means one bounded deliverable with inputs, acceptance criteria and a saved result, not one chat message or a known percentage of a subscription. Begin with simulator + BC and revise the estimate from actual usage. Additional search/Q-learning tracks add work.

Keep a short task contract for each packet: exact files, immutable inputs, desired behavior, checks, time/sample cap, deliverable and failure conditions. Return aggregate metrics and a few diagnostic cases rather than repeatedly feeding full game archives or long logs into model context. Use Astra again when the specification is wrong or the interpretation is uncertain, rather than spending many cheap retries on an ambiguous task.

Official Standard purchased-credit rates list Astra at **250 / 25 / 1,250 credits** per million input / cached-input / output tokens, and Luna at **2.5 / 0.25 / 12.5**. That is a **100-fold rate difference for the same token mix**, not 100 times as many included subscription tasks. For illustration, 100k uncached input plus 20k output tokens correspond to 50 versus 0.5 purchased credits at those rates. This is not an estimate of this research turn's usage. [Official pricing](https://learn.chatgpt.com/docs/pricing).

Included limits, banked balances, reset times and the second subscription's allowance were not inspected. They cannot be inferred from monthly price or API token prices, and separate account allowances are not assumed to be pooled. Use the account's [usage dashboard](https://chatgpt.com/codex/settings/usage) for actual remaining capacity. No paid-credit purchase or external GPU spend is part of this plan.

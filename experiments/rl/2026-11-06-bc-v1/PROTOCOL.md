# BC v1 protocol

Recorded before training or opening the confirmation panel, 2026-11-06.

- Scope: a native simulator and a small behavior-cloning policy trained on both frozen public teachers. No PPO, paid compute, contest submission or baseline replacement.
- Hardware: local Apple M4 MacBook Air, 24 GB. Measure CPU and MPS instead of assuming either is faster.
- Rules: pinned original referee, league 3, all five mechanical command families. Preserve simultaneous phase ordering, resource reservations, roads, captures and terminal scores.
- Data: reconstruct existing archived games. Exclude corrupt/incomplete decisions and report every exclusion. Split by map content, never by individual turns; training 80%, validation 20% using a fixed content-hash split. Teacher identity is a feature, with a fixed mixed-teacher mode for evaluation.
- Initial model: compact shared candidate-scoring MLP, legality-constrained sequential full-turn decoding. Features include house/triangle/graph relations and the current friendly allocation, but no current opponent action or future state. This is a smaller first control than the proposed graph encoder. All strategy scores are learned; mechanical masks are deterministic.
- Validation: compare native transitions with the original Java rules, archived viewer states and targeted edge cases. Verify native/PyTorch inference agreement. Report teacher-label coverage and validation accuracy separately from strength.
- Final panel: seeds 6001–6050, both seats, against v6, Lacoz 7f190183 and khoufou 372c1cd6. Also rerun v6 against both public opponents on those maps. Check map-content overlap. Freeze the checkpoint before opening this panel. All games use the original timed Java arena, sequentially.
- Primary results: wins/draws/losses, clean results, errors/timeouts, paired map-cluster confidence intervals for BC versus v6 against each public opponent. A small one-training-seed experiment; no automatic promotion. Preserve all runs, including failed training or evaluation attempts.
- Artifacts: source, configuration, split/source hashes, model weights, measured speed, training history and compressed full evaluation records on `rl/research`. Derived training arrays remain rebuildable local caches.

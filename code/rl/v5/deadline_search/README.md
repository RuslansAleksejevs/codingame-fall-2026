# Isolated deadline-bounded lookahead

This implementation and its evidence belong to the independent RL-v5 experiment
in `experiments/rl/2026-11-08-rl5/deadline-search/`. Read its REPORT, STATUS and
pre-result protocols before interpreting a result. The teacher and student have
different gates; a passing teacher is not a source-compliant deployed bot.

## Boundaries

Original v3/v4/search/export/arena files are read-only dependencies. New adapters
live here. `search.hpp` wraps the existing exact simulator/search interfaces;
`io.hpp` restores absolute player order and settled state from complete official
observations. `bot.cpp` emits one complete command line and flushes before its
diagnostics. It does not send early replacement outputs or relax referee limits.

D16 preserves a completed greedy plan, accepts only complete all-response
evaluations, and cooperatively stops optional work16ms after the first score
token or20000choice forwards. Atomic work/preemption and pre-token/referee timing
remain unbounded. Emergency WAIT is distinguished from the completed baseline.
The control uses the same wrapper and unchanged actor, with optional search off.

The student uses the actual selected proposal's deterministic generator trace.
`trace.cpp` records each legal prefix and exact float32 feature matrix; it never
sorts or reparses an output command to create a target. `student_labels.py`
retains every eligible fixed-turn root and checks the selected counterfactual
transition against original Java. `student_train.py` runs the one predeclared
two-round CPU pilot; separate dev CE chooses the checkpoint, not game outcomes.
`student_package.py` verifies bit/argmax/command parity before independent games.

## Evidence flow

Teacher: build/diagnose/contracts -> original-referee regression/development ->
technical-only selection/freeze -> four fixed confirmation blocks -> frozen
analysis and independent raw audit. Student: pre-result protocol -> tiny trace
contracts -> collector/trainer freeze -> fixed collections/two training rounds ->
dev-only selection -> package contracts -> student freeze -> four fixed fresh
comparison blocks -> frozen analysis and raw/label-integrity audits.

`panel.py` preserves raw original JSON, portable gzip, stderr, exact command
specifications, ordered schedules, dependency hashes and measured durations.
`verify.py` checks complete native/Java trajectories. Its sole unpaired-output
exception is the original referee's normal terminal survivor check; terminal
score/done and normal endings must agree. Failed attempts are retained.

Every heavy command must acquire the existing exclusive wrapper from repository
root, without changing its owner/state/caps:

```text
python3 code/rl/v4/compute_slot.py --status
python3 code/rl/v4/compute_slot.py --owner search-teacher --minutes 25 -- code/arena/.venv-rl/bin/python -B code/rl/v5/deadline_search/<recorded-stage>.py <recorded-arguments>
```

These are the historical command form, not permission to rerun a closed gate.
Outputs are create-only; do not delete or overwrite them to repeat a stage.
The exact executed arguments/versions/hashes live in command/manifests and the
portable lease ledger. Build products stay in ignored experiment `build/`;
scientific datasets/checkpoints and portable source stay in the evidence tree.

No tool here is a ranking-submission workflow. No paid compute, Git mutation,
credential persistence or IDE writes are part of this experiment. Platform
read/play requires its separate package/strength/authorization conditions.
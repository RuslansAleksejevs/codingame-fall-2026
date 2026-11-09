# Commands and resource accounting

All commands run from the repository root. No paid compute/API is used.
The exclusive wrapper's original state and owner cap are unchanged.

```sh
python3 code/rl/v4/compute_slot.py --status
python3 code/rl/v4/compute_slot.py --owner search-teacher --minutes 25 -- code/arena/.venv-rl/bin/python -B code/rl/v6/compact_d16/package.py
python3 code/rl/v4/compute_slot.py --owner search-teacher --minutes 25 -- code/arena/.venv-rl/bin/python -B code/rl/v6/compact_d16/stage.py contracts
```

The package command ran twice: initial static attempt and a preserved second
attempt correcting only signed-decoder portability. Their terminal lease
durations were7.6213774578645825s and7.270920207723975s. Exact compiler commands,
versions, return codes and source/binary identities are in the package manifests
and individual `*-command.json`/logs. Later finite stages use `stage.py`, which
captures terminal stdout/stderr and command duration. The final phase ledger
will use actual exclusive-wrapper events, not summed nested command times.

Initial cumulative search-teacher consumption4569.00871229358s; this phase
allows at most9000additional seconds while preserving the original14400s cap.
Each lease is at most25minutes. Research ends no later than2026-11-09T02:00Z.
The source/technical feasibility checkpoint is2026-11-08T21:45Z.

After independent release, the non-decision driver
`.context/rl6-compact-d16/finite_final.py` invoked only frozen `stage.py`
commands. Exact wrapper commands and terminal receipts are in `execution/`.
It completed confirm1 and stopped at confirm2exit1; no later block ran.
The driver never reset/renamed the shared state directory or changed a source.

Post-stop, `postmortem.py` replayed existing block2 trajectories, extracted the
original WAIT record, invoked the frozen raw audit/analyzer and wrote all
observed counts. It made no new bot call or game. Its full command/output and
terminal duration are in `postmortem-run-command.json` and its log.

Closure uses `archive.py` under the same exclusive wrapper to normalize portable
host paths, preserve original hashes, archive source/evidence and verify every
member. `resource-ledger-final.json` and `COMPLETION.json` bind actual final
wrapper durations, including archive/closure; they intentionally remain outside
the archive to avoid self-referential hashes.
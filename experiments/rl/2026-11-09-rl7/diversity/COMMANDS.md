# Commands and actual durations

Run from the original repository root. No new environment was installed.
All substantial work uses `python3 code/rl/v7/compute_slot.py --owner diversity
--minutes N -- code/arena/.venv-rl/bin/python -B ...` (N<=25). The wrapper's
authoritative new ledger is `.context/rl7-compute/events.jsonl`; the old ledger
is never charged/reset by this pilot. Per-command logs/durations are retained in
`execution/`, optimizer/config versions in `models/*/config.json`.

| UTC completion | Wrapped command after Python | Actual lease seconds | Result |
|---|---|---:|---|
|2026-11-09T00:07:07.884Z|`code/rl/v7/diversity/contracts.py` (5min lease)|1.968694|PASS7disclosed roots; existing exactFP32 teacher/trace/Java contracts|
|2026-11-09T00:12:18.917Z|`code/rl/v7/diversity/job.py collection1` (15min lease)|90.242515|Synthetic6tests/datafreezePASS;64games/oneLacoztimeout;63cleanJavaPASS; collection stop before labels/updates|
|2026-11-09T00:20:53.958Z|`code/rl/v7/diversity/job.py collection-a1` (15min lease)|159.931467|A1freeze/9testsPASS;label retained old games without rerun;64remaining planned games/labelsPASS|
|2026-11-09T00:31:32.272Z|`code/rl/v7/diversity/finish_training.py` (5min lease)|92.276193|Labeldev32games/509roots+assemblyPASS;seed1narrow/broad800updates each; nativeparityPASS; first referencecompile blocked before command parity|
|2026-11-09T00:37:08.476Z|`code/rl/v7/diversity/finish_seed2.py` (2min lease)|6.188055|Both prescribed seed2models800updates; seed1not rerun|
|2026-11-09T00:38:04.033Z|`code/rl/v7/diversity/complete_exports.py` (reviewed full-access5min lease)|27.469314|Same-compiler exactexport/parity all4PASS; allweightsunchanged; candidatefreeze and coverageaudit|
|2026-11-09T00:46:06.540Z|`code/rl/v7/diversity/job.py gamedev1` (10min lease)|217.886995|200/200games,0technicalerrors; Java replay5,650states/5,450transitionsPASS; slot yielded to D16|
|2026-11-09T00:52:03.115Z|`code/rl/v7/diversity/job.py gamedev2` (10min lease)|215.450989|200/200games,0technicalerrors; Java replay5,643states/5,443transitionsPASS; slot yielded|
|2026-11-09T00:57:32.378Z|`code/rl/v7/diversity/job.py gamedev3` (10min lease)|248.666680|200/200games,0technicalerrors; Java replay6,698states/6,498transitionsPASS; slot yielded to D16 metadata audit|
|2026-11-09T01:03:22.930Z|`code/rl/v7/diversity/job.py gamedev4` (10min lease)|212.888771|200/200games,0technicalerrors; Java replay5,775states/5,575transitionsPASS; all800complete|
|2026-11-09T01:04:53.721Z|`code/rl/v7/diversity/job.py gamedev-decision` (1min lease)|0.781054|Frozen paired-map analysisPASS; promise=false; final stays closed|
|2026-11-09T01:08:30.689Z|`code/rl/v7/diversity/closeout.py` (1min lease)|0.443494|Frozen/protected identities,808decision bindings,960raw/portable records,3,200updates and unopened final auditPASS|

Minor file-preservation operations before A1 (not a substantial compute job):
`tar -cf .../pre-a1-sources.tar` preserved four small source files. Extended
attribute reads were unavailable. `tar -df ...` was unsupported (exit1).
Read-only `tar -Oxf ... <source> | shasum -a 256` matched all four originals;
content SHA bound in A1. No repeat of blocked metadata access or game occurred.

Closed:12leases,1,274.194223seconds (21.236570heavy minutes),external spend0.
Collection, optimization and game-dev games are complete and never rerun.
`final-freeze` and `final1`..`final4`/`final-decision` were NOT executed because the
prospective promise gate failed. No next dispatch/automatic phase is scheduled.
No platform/OAuth/Git/push/IDE/paid commands are part of this pilot.

Post-exit `pgrep -fl 'code/rl/v7/diversity/|experiments/rl/2026-11-09-rl7/diversity/'`
returned exit3 in the sandbox (process service unavailable). The exact same
reviewed read-only query returned exit1/no matches. No process was killed by this
query. Shared wrapper status:available/no unclosed leases. Product pending timer
listing:empty. Exact versions are in `environment.json`; no environment installed.
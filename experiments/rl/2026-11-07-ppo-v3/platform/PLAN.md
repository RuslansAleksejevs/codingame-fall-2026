# B2M official platform tests

Authorized2026-11-08; recorded05:43:32UTC. Test games only. Training remains
stopped, the independent2,200-game panel is not resumed, and competitive
submission/publication/IDE overwrites are not authorized.

Frozen source: `../handoff-b2m/bot.cpp`, SHA256
`b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214`.
The local package already passed exact weights and4,978 replay-command checks.
It remains an experimental development winner, not independently promoted.

The existing API client runs without `--allow-submit`, requesting only
`challenge:read challenge:play`. Credentials stay only in process memory;
authorization codes/URLs/tokens must not be written into these records.
Current state as of2026-11-08T06:06:17Z: all10 authorized tests completed and
audited. No technical errors/timeouts/warnings. B2M lost to the Gold boss and
won2/4 paired replays versus3/4 for league3m. Strength improvement is not
demonstrated. See REPORT.md and verification.json. Fresh deadline is
2026-11-09T09:00:00Z; deployed41657621 remains unchanged, currently348/986,
Gold209/389. Client exited cleanly; no token persisted. No further work or
competitive submission is authorized automatically.

The following pre-test plan has been executed. After approval, read the live challenge, statement, exact deadline, current
submission, eligible opponents and limits. Then run a bounded smoke/compatibility
series, initially at most10 games: self-play/boss checks and, where eligible,
replays against existing opponents from both seats, with the preserved base as
a comparison. Stop on candidate technical failures and inspect complete logs.
Do not treat a handful of platform games as an independent strength estimate.

Use contest endpoints, not the permanent puzzle. All test requests leave
`overwrite_ide_code`, `overwrite_ide_game_parameters` and `show_in_ide` false.
Tests are serial, respecting live limits and `wait=30`; no training is running.
Preserve request metadata, source hashes, full sanitized results and timing.
No reserved final-map seeds40001–40100 are intentionally opened.

API reference checked2026-11-08:
https://www.codingame.com/api/v1/docs/api
# Packaging and live deployment commands

Working directory: repository root, branch `rl/research`.
Dates use UTC in API evidence; the experiment directory uses the local start date.

```sh
python3 code/rl/export/package.py
python3 code/rl/export/package.py --league silver
code/arena/.venv-rl/bin/python code/rl/export/verify_package.py
python3 -u code/platform/codingame_session.py
python3 code/platform/analyze_live.py
python3 code/platform/summarize_ranking.py
```

The session client receives JSON lines. `auth_start` and, after browser acceptance,
`auth_poll` obtain scoped authorization. No token or device credential is saved.
The exact endpoint reference is https://www.codingame.com/api/v1/docs/api.

Read the contest, stub generator, progress, opponents and submission history before testing.
All code requests use `language: C++` and load `submissions/ppo-v2-league3m.cpp`.
Test calls use `POST /challenges/fall-challenge-2026/test-games?wait=30&format=json`.

Initial smoke tests:

- `opponents: [boss]`, `game_options: seed=120001`.
- `opponents: [6839684]`, `game_options: seed=120002` (B4LBU).
- `opponents: [me]`, `game_options: seed=120003` (both seats use the same source).
- `replay_game_id: 917924447`, to reproduce the initial ranked timeout.

After transposing the dense-layer weight layout, repeat the timeout replay and the
same self-play seed. Compare both complete output sequences and stderr plan timings.
These paired platform tests use identical code weights and game options.

Submit with `POST /challenges/fall-challenge-2026/submissions`.
Read `/submissions/{submission_id}` to verify the accepted source exactly.
Save that full response with deterministic gzip compression.
Read `/progress` until ranking and eligible promotions complete, refreshing the contest
statement after a promotion. Read `/leaderboard?around_me=true` for the public rank.
Read `/battles?limit=100`, then `before=<next_before>` while present, and selected or
complete `/games/{game_id}?format=json` logs as stated in the report.

All response files are sanitized and kept under this experiment directory.
`package-initial.py`, `package-initial.json`, `package-verification-initial.json` and
`submission-source.json.gz` preserve the first version, including its timing limitation.
Later optimization does not overwrite that evidence. No retraining or paid compute is used.

After Gold promotion, use the full profile. The two Gold smoke tests use
opponent 6855982 / seed120005 and opponent6849383 / seed120006.
Saved ranked-game JSON is compressed with `gzip.compress(raw, mtime=0)`;
analysis reads both JSON and gzipped JSON directly. Ranking summaries require
completed progress, a fully ranked leaderboard entry, complete battle pages and
a saved log for every finished battle in that frozen snapshot.

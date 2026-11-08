# B2M platform test result: technically clean, no demonstrated strength gain

As of2026-11-08T06:06:17Z. PROJECT_REPORTED analysis of saved official API
responses (SOURCE_VERIFIED raw evidence). The bounded10-game series is complete;
no further games, training, scheduled continuation or submission are running.

All10 games compiled and completed without own errors, command warnings,
timeouts, opponent technical errors or global failures. B2M lost to the Gold
boss. In four paired archived-game replays, B2M won2/4 and preserved league3m
won3/4. This small diagnostic series does not demonstrate an improvement and is
not the independent2,200-game confirmation cancelled with the research stop.

## Frozen tests and results

The source is [B2M](../handoff-b2m/bot.cpp), SHA256
`b87388adc48e8806edca275a589f5fe036f8e837ff1ebcd7e4a69276646ff214`.
[Requests](test-requests.json) cap the series at10 games. The
[paired replay selection](paired-replays.json) was recorded before replay tests:
the four most recent distinct eligible Gold opponents in the saved battle list,
two games in each seat. Selection used known archived outcomes, not blind maps.

| Opponent | Own seat | B2M result / test ID | League3m result / test ID |
|---|---:|---|---|
| Metamong | 1 | Loss /918415387 | Loss /918415650 |
| RAFIK | 1 | Loss /918416026 | Win /918416136 |
| dr.frankenstein | 0 | Win /918416348 | Win /918416520 |
| utfart | 0 | Win /918416667 | Win /918416826 |

Self-play smoke918414170 and Gold-boss smoke918414903 precede these eight games.
All four pairs match the original map properties, own seat and opponent agent
ID. API property-line ordering differs between original and replay logs;
comparison canonicalizes property keys while retaining every value exactly and
rejecting duplicate keys. Three synthetic canonicalization checks passed.
Opponent source/version stability beyond the returned agent ID is not proven.

B2M produced249 turn outputs including both self-play seats; maximum reported
planning time7,910microseconds. Baseline produced145 outputs, maximum7,024us.
`plan_us` measures the bot's planning instrumentation, **not total platform CPU
time**. No platform timeout occurred; this is not an exhaustive timing bound.

Reproduce the complete per-game audit:

```sh
python3 code/platform/analyze_v3_tests.py --out experiments/rl/2026-11-07-ppo-v3/platform/verification.json
```

[Verification](verification.json) records raw-log hashes, outcomes, command
counts, warnings/errors, map parity, source preservation and published state.
Assertions passed for all10 complete clean logs, four matched pairs, four
source/checkpoint hashes and the unchanged deployed source and submission IDs.

## Live state and boundaries

Fresh [challenge response](challenge-start.json) confirms the exact deadline
2026-11-09T09:00:00Z (01:00PST). [End progress](progress-end.json) reports the old
submission41657621 at348/986, Gold209/389, score13.65; this is **not B2M's rank**.
The initial snapshot was347/986. The submission remains current, and its
downloaded source matches preserved fallback SHA256
`199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1` exactly.
Submission IDs/languages/current flags are unchanged. API `submitted_at` values
drifted7ms between GETs, so full-response byte equality is not asserted.
Original league3m checkpoint9ba362b2 and weightsdcc99a63 remain unchanged.

The client requested only read/play and ran without `--allow-submit`. Every
test left `show_in_ide`, `overwrite_ide_code` and
`overwrite_ide_game_parameters` false. No competitive submission or IDE write
was performed. Credentials stayed in process memory; the client exited cleanly
after testing, with no token/authorization code stored in project files.
External compute spend0; no paid resources, commit/push or research restart.
Reserved final seeds40001–40100 were not intentionally opened.

Initial diagnostic GETs used incorrect IDs from an interim conversation
summary and omitted `format=json`. Those records are preserved but excluded
from the tests and conclusions. Correct saved API data determined the replay
selection; no test was launched using the incorrect IDs.

Next action requires a separate decision: keep the proven deployed fallback or
explicitly authorize an experimental B2M leaderboard submission. A submission
needs `challenge:submit` authorization; no automatic replacement is enabled.
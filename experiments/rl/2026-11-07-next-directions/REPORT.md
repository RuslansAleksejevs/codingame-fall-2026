# Gold replay diagnosis and next RL experiments

As of **2026-11-07**. Provenance: **PROJECT_REPORTED**, derived from archived platform logs. No new competitive games, training, model selection or submission occurred.

The [research proposal](../../../docs/rl/NEXT.md) recommends a search teacher with compact-policy distillation, followed by an independently tested exploiter league. Reset curricula and a graph/objective policy are additional options.

## Reproduction

```sh
python3 code/rl/eval/diagnose_gold.py --out experiments/rl/2026-11-07-next-directions/diagnostics.json.gz
```

The script uses `code/build/libtryangle.dylib`, built by the existing simulator workflow. Input is the exact 92-game list in `experiments/rl/2026-11-06-live-ppo-v2/battles-final.json`, submission 41657621. Every compressed source log has its SHA256 recorded in the output. The previously selected policy and all submitted code remain unchanged.

All 92 final scores and native terminal conditions match. All **2,714** available own pre-action army/income observations match. Each platform log retains one unpaired output at termination; it is recorded and not applied, since the paired commands already reproduce the exact terminal score. This check does not compare every hidden/internal referee field with Java at every frame. The broader native/Java mechanical validation is documented in the earlier PPO report.

## Observations

- 52 wins, 40 losses, median game length 28 turns overall.
- After five completed turns, 32/40 future losses already have fewer friendly than enemy troops; the median army gap is -2.
- After ten completed turns, 38/40 future losses are behind in troops, versus 17/52 future wins. Median gaps are -7 and +1 respectively. All games reach this observation.
- Opponents use road commands in **two** losses: game 917935678 has 8 ADD_PATH and 1 REMOVE_PATH; game 917932090 has 7 ADD_PATH. Counting action categories separately would incorrectly report three games.
- In executed paired turns the actor uses 126 ATTACK commands, five ADD_PATH commands and no REMOVE_PATH commands. Its maximum recorded planning time is 18.926 ms. These are descriptive counts, not recommendations to force any action type.

The saved full timelines permit further analysis. Loss/win grouping and platform matchmaking are selected observational samples: these associations do not establish causal weaknesses or unbiased strength estimates. In particular, later observations exclude already-finished games. The original platform technical audit records zero own warnings/crashes/timeouts in this Gold panel.

## Training diagnostic cross-check

Read `experiments/rl/2026-11-06-ppo-v2/league-a/history.jsonl`, restrict to `steps <= 3002173`, and summarize the last 100 entries. Median `update.clip_fraction` = 0.24237, `explained_variance` = 0.81707, `final_rollout_kl` = 0.00731. No `actor_early_stopped` event occurs in the first 947 entries. This does not establish a plan-length clipping problem or calibrated values on Gold states; those require targeted measurements.

The replay check runs locally in seconds. External compute spend: **$0**. No subscription consumption estimate was made. Proposed training times in the research document are explicitly unmeasured estimates.

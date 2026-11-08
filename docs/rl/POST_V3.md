# After PPO-v3: change the learning problem, validate transfer

As of 2026-11-08, approximately 07:30 UTC. **Research proposal only.** No new
training, test games, submissions, rollback or Git commit/push is authorized by
the request to discuss alternatives. The stopped PPO-v3 campaign stays stopped.

Follow-up: the subsequent request explicitly authorized three separate working
chats and repository synchronization. The bounded new work is governed by
[RL-v4 coordination](v4/COORDINATION.md); the evidence and proposals below retain
their original observation time and are not retroactively described as results.

## What is established

The [live submission report](../../experiments/rl/2026-11-07-ppo-v3/live-submission/REPORT.md)
records B2M's completed ranking: 382/989, score 12.90, versus the old league3m's
356/987, score 13.51 immediately before replacement. All 95 games were clean,
41 wins and 54 losses. These changing matchmaking snapshots are not a paired
effect estimate. They give no observed live improvement, but do not prove that
PPO itself cannot work. The independently tested PPO-v2 improvement remains real.

New reconstruction of those same saved games, not new evaluation:
[diagnosis summary](../../experiments/rl/2026-11-07-ppo-v3/live-submission/diagnosis-summary.json).
All final scores and 3,543 own pre-action army/income observations match. No
replay mismatches were found. All 95 games were still running after ten turns.

| After ten completed turns | Wins | Losses |
|---|---:|---:|
| Behind in army | 17/41 | 52/54 |
| Median army gap | 0 | -6 |
| Median owned-triangle gap | +1 | -1 |

At turn five the army deficit occurs in 30/41 wins as well as 43/54 losses.
An early deficit alone is not a sufficient diagnosis. The later divergence
suggests examining opening development and recovery, not adding an army/spawn
reward. Enemy road commands occur in 9/54 losses: they matter to coverage, but
do not explain most losses by their mere presence. These are associations.

The frozen v3 recipe already tried prioritized diverse opponents, two independent
continuations, frequent checkpoints and within-trajectory averaging. Calling
another identical continuation a new approach would obscure the intervention.
The independent 2,200-game final was not run after the campaign was stopped;
B2M was explicitly a development-selected experimental deployment.

## Recommended next experiments, separately

1. **Deliberately trained exploiters, then a champion response (small PSRO-style
   league).** Train two different opponents specifically to beat frozen league3m,
   with B2M retained as a control. This differs from v3's priority sampling among
   already available historical networks. Admit an exploiter only after it has
   reproducible wins on unseen development maps. Train a champion response against
   a small mixture, preserving public anchors and opponents held out from training.
   Exploiting a single network is not the promotion criterion for the champion.
2. **Failure-state curriculum as a separate ablation.** Mix a small fraction
   (initial proposal: 10–20%) of recoverable turn-2–10 positions with normal full
   games. Include successful controls, diverse fresh games and the real starting
   state. Restore the complete simulator state and verify it before use. Changed
   positions require opponents to make new decisions; replaying their recorded
   future commands is invalid. Keep terminal win/loss reward. Test whether this
   improves complete games, not just recovery from selected positions.
3. **Complete-plan search teacher and distillation, conditional on strength.**
   The completed pilot was promising: +7.14 percentage points across three
   external opponents on 28 confirmation maps, paired 95% interval [0, 15.48].
   Its teacher gate explicitly failed; no search labels were generated. A new
   experiment would first test value ranking and broaden independent confirmation,
   not lower that gate after seeing the result. Only then distil improved joint
   plans into the compact actor. The five-network teacher is not presently a
   competition-ready package. Its current PPO critic is not a proven reliable
   value function on search-generated states.

**First choice for one bounded new cycle:** the exploiter league. The curriculum
is a controlled alternative, not an unmeasured addition to the same run. Search
distillation remains a promising next branch if the teacher earns confirmation.
These priorities are MODEL_INFERENCE, not measured gains or a selected run.

The actor currently scores 128 handcrafted features with a 128–128–64–1 MLP,
constructing triangle spending followed by per-unit movements in a fixed order.
It does track pending resources and triangle opportunities; it is not blind to
all coordination. The critic pools node statistics rather than encoding the full
graph arrangement. A graph critic or prefix-aware value model is a plausible
later ablation. A large new actor, MuZero, or several simultaneous architectural
changes have excessive implementation/validation risk for the remaining window.
Changing optimizer names alone does not address demonstrated distribution shift.

## Use CodinGame earlier, without tuning blindly to rank

- Treat the 95 analysed games as development material permanently, never a new
  holdout. They expose strategic styles missing from an easy local panel; a few
  replays cannot reproduce closed-source opponents faithfully.
- After a candidate passes local controls, run a predeclared paired platform
  test panel against several available Gold opponents. Match map, side and
  opponent version, and verify these identities in the saved API responses.
  Platform tests need their applicable authorization; no requests were made here.
- Use occasional completed ranking submissions as external validation, not after
  each checkpoint. Record exact source, matchup logs, own failures and the full
  ranking snapshot. Rank alone is noisy and changes with the field. More exposure
  is useful; repeatedly selecting on the same opponents is not independent proof.
- Freeze one finalist before opening reserved maps 40001–40100. Retain the
  existing paired confidence intervals and technical/regression guards; do not
  relax them because B2M looked promising on the adaptive development panel.

Official deadline, verified by the authenticated API before the last submission:
**2026-11-09T09:00:00Z**. At this note there are about 25.5 hours left, and about
18.5 hours to the prior 02:00 UTC research cutoff. Preserve the final seven-hour
window. This supports at most a bounded selected cycle with evaluation, not a
promise to implement every alternative. No new compute has been started.

## Reproduce the new read-only diagnosis

From the repository root, run the following Python body with `python3 -c` or an
interactive Python session. The adapter only supplies the gzip reader in memory;
it creates no new game and changes no archived file. Raw hashes are in audit-final.

```python
import gzip, json, sys
from pathlib import Path
sys.path.insert(0, "code/rl/eval")
import diagnose_gold as diagnosis
root = Path("experiments/rl/2026-11-07-ppo-v3/live-submission")

class ArchivedJSON:
    def __init__(self, path):
        self.path = path
    def read_bytes(self):
        return gzip.compress(self.path.read_bytes(), mtime=0)

battles = json.loads((root / "battles-009.json").read_text())
games = [diagnosis.replay(
    ArchivedJSON(root / "games" / (str(b["game_id"]) + ".json")), b
) for b in battles["battles"]]
assert not any(g["mismatches"] for g in games)
print("observation_checks", sum(g["observation_checks"] for g in games))
for label, subset in [("all", games), ("wins", [g for g in games if g["win"]]),
                      ("losses", [g for g in games if not g["win"]])]:
    print(label, json.dumps(diagnosis.summarize(subset), indent=2))
```

Additional evidence: [original directions and research references](NEXT.md),
[v3 protocol](../../experiments/rl/2026-11-07-ppo-v3/PROTOCOL.md),
[search decision](../../experiments/rl/2026-11-07-ppo-v3/search/decision.json),
[actor/decoder](../../code/rl/models/policy.hpp),
[critic features](../../code/rl/league/rollout_league.cpp).
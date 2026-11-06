# PPO self-play implementation

As of 2026-11-06. This extends the frozen [BC v1 policy](IMPLEMENTATION.md). The exact first-run contract is in the [PPO protocol](../../experiments/rl/2026-11-06-ppo-v1/PROTOCOL.md). It does not replace the main v6 bot.

## What learns

The actor starts from BC's 24,833 parameters. Its candidate features, legal action space, resource reservations, canonical command order and greedy deployment remain unchanged. A second 24,833-parameter MLP estimates the eventual result from the current observation. This critic is used only during training; its inputs pool the shared node features and global context. It adds no cost to the playing bot and is not yet a validated search evaluator.

A training action is the entire turn plan. The actor samples each legal conditional choice at temperature 0.7 and stores its features, mask and selected index. The probability of the complete plan is the product of these conditional probabilities. PPO therefore sums their log probabilities and clips **one ratio per turn**, with one shared advantage. Clipping every unit decision separately would be a different objective.

Different latent choice sequences can emit equivalent command plans. The learner optimizes the probability of its sampled sequence, which is a valid expanded action representation; it does not claim to sum the probabilities of all equivalent printed plans. Evaluation is greedy, as it was for BC, rather than temperature sampling.

The critic receives no opposing current action, final score or future state. Both players generate their plans before the simulator applies either. Terminal win/loss/draw rewards are +1/-1/0 with no intermediate shaping. GAE is computed separately on complete player episodes, with zero bootstrap at every true terminal, including the 200-turn limit.

## Self-play and updates

Four native threads collect independent complete games. Half the games use the current stochastic actor on both sides and learn from both seats. One quarter use frozen greedy BC; one quarter use a sampled frozen stochastic snapshot. Controlled seats are balanced. The historical pool starts with BC, refreshes every 100,000 controlled-player decisions and retains four actors. A fixed seed per game makes the same collection independent of worker scheduling.

Each update uses flat candidate features with padded logits only. Mini-batches contain all choices of 128 whole turns. Four PPO epochs use actor Adam 3e-5, critic Adam 3e-4, ratio clip 0.1, gradient cap 0.5, gamma 0.995 and GAE lambda 0.95. The small entropy term uses average conditional entropy per turn, so army size does not directly multiply its coefficient. Further actor epochs stop if the measured full-rollout approximate joint KL exceeds 0.03; critic updates continue. This is an empirical safeguard, not a hard KL constraint.

Before every update, PyTorch replays all native sampled log probabilities. Nonfinite parameters/losses, invalid plans or an unexplained probability mismatch abort training. Saved statistics distinguish games, joint simulator turns, controlled-player decisions, categorical groups and optimizer steps.

Checkpoint selection uses 42 fixed BC validation maps, both seats, against greedy BC. The trained checkpoint with the highest score rate wins, with earlier checkpoints breaking ties. The final checkpoint is also retained. The initial BC weights are the comparison control and cannot be labeled as a trained PPO result. Training maps, selection maps and final confirmation maps have separate roles.

## Reproduction

Prepare the environment, original referee and frozen opponents as in the main README and BC guide. The following commands use new output directories; seed 7001–7050 results are no longer blind after the first report.

```sh
python3 code/rl/build.py
python3 code/restore_records.py
python3 code/rl/data/ppo_maps.py --out /tmp/ppo-maps.json
code/arena/.venv-rl/bin/python code/rl/train/test_ppo.py \
  --maps /tmp/ppo-maps.json --out /tmp/ppo-tests.json --device cpu
code/arena/.venv-rl/bin/python code/rl/train/ppo.py \
  --maps /tmp/ppo-maps.json --out experiments/rl/ppo-retrain \
  --steps 1000000 --games 64 --workers 4 --device cpu --minutes 60
python3 code/rl/eval/tournament.py \
  --weights experiments/rl/2026-11-06-bc-v1/training/weights.txt \
  --ppo-weights experiments/rl/ppo-retrain/weights.txt \
  --seeds 7001:7050 --out experiments/rl/ppo-retest
python3 code/rl/eval/analyze.py experiments/rl/ppo-retest \
  --before bc --after ppo --opponents v6 lacoz khoufou --out /tmp/ppo-comparison.json
python3 code/rl/eval/verify_run.py experiments/rl/ppo-retest --out /tmp/ppo-verification.json
```

The CPU/MPS pilots use the same command with `--pilot --steps 10000 --minutes 5` and separate output directories. Access to Metal may require permitted local execution outside a restrictive sandbox. CPU is a complete supported path.

A rolling checkpoint is saved after each full collection/update in `code/build/rl-cache/<output-directory-name>/latest.pt`. Resume with the same output directory and settings plus `--resume PATH`; use distinct output-directory names for concurrent unrelated runs. Checkpoints retain actor, critic, both optimizers, random-generator states, counters, the frozen opponent pool and history. A resumed wall cap includes already recorded elapsed training time. Only trusted local checkpoint data should be loaded.

Text weights use the existing native inference format. Run the actor through `code/build/bc-bot WEIGHTS 2`; no Python, PyTorch, critic or teacher process is needed by that bot. Export checks compare saved tensors with C++ logits and choices. Original-referee serial games enforce process time limits; native rollout throughput is not a contest latency measurement.

## Interpretation and retained evidence

The first experiment is one training seed, with greedy checkpoint selection against BC. A higher development win rate can reflect specialization against that control. The fresh final panel tests transfer to v6 and the original frozen Lacoz/khoufou programs, with paired maps, both seats, separate technical errors and map-clustered intervals. Those intervals measure map uncertainty, not variability across independent training runs.

The branch retains code, protocol, map split, pilots, tests, selected and final checkpoints, milestone weights/results, optimizer history, representative full rollouts, source hashes and complete original-arena records. Per-candidate training feature buffers are transient derived data and are not all archived. Costs and speed are measured separately from unobservable coding-subscription quota usage.

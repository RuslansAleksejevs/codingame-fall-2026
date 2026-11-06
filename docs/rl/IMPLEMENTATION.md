# Native simulator and BC v1

As of 2026-11-06. This page documents the frozen BC baseline. The later [PPO extension](PPO.md) fine-tunes its actor without changing the decoder or rules. Local implementation and measurements; no contest submission.

## Simulator

`code/rl/sim/simulator.hpp` ports the mechanical rules of the pinned referee, `eulerscheZahl/TryAngle-Catch@b6913124a10de328316ff42906448a18cb948431`. The original source remains in the attributed source archive. Map generation stays with the original Java referee; the C++ simulator loads its generated geometry and initial units.

State includes positions, sorted roads, both armies, remaining unmoved troops, triangle owner/initial owner/recapture flags, scores, decision count and terminal status. Both plans are parsed from the same pre-state. Resolution preserves ATTACK → MOVE → SPAWN → ADD_PATH → REMOVE_PATH, one special action per player per animation batch, geometric road-cost ordering, shared troop reservations, shortest-path tie breaks, surrounding before captures, repeated capture settlement, income and terminal ordering. Removed triangle objects remain alive while already parsed actions reference them, as in Java.

The C ABI exposes create/clone/state/step/delete. Python uses `ctypes`; environment transitions do not launch Java or render frames. Debug drawing is mechanically inert and omitted from the native state. Invalid commands are counted, but the native library is not a replica of the runner's process management, timeout messages or visualization. Those remain tested in the original arena.

Verification includes complete Java Board/TaskManager state transitions, independent pre-decision unit reconstruction from archived viewer frames, archived terminal scores, and randomized populated maps with simultaneous attacks and road edits. The random cases are reproducible with seed 20261106. The headless Java oracle uses the original classes, with only observation serialization and terminal-condition bookkeeping outside them.

## Learned policy

This first control uses an **MLP with 24,833 parameters**, dimensions 128 → 128 → 64 → 1 and ReLU hidden layers. It scores each legal candidate. It is smaller than the graph network proposed in the research plan; it establishes a cheap, complete behavior-cloning baseline before a richer encoder or PPO.

The 128 features are shared by training and C++ inference:

- 16 global/style features: time, scores, army/income totals, board size, pending army, decoder progress and teacher mixture.
- 7 action-kind indicators: stay, move, keep triangle, spawn, attack, add road, remove road.
- 26 features each for source, target and the mean of the three triangle corners: original/pending troops, neighborhood, ownership, available troops, triangle readiness, distance to enemies and oriented coordinates.
- 27 relational features: geometry, capture flags, available corner resources, distances to missing corners, immediate triangle-completion/emptying changes and attack target troops.

The feature encoder uses only the current observation and already selected friendly choices. It never reads the opposing current command, a future state or final outcome. There is no copied teacher planner, v6 fallback, search or learned value head in this candidate. Handwritten logic provides feature extraction and mechanical legality; the network chooses among candidates.

## Full-turn decoding and teacher coverage

First visit owned triangles in canonical corner order. Choose keep, one of three spawns, or every mechanically available attack/road action. Reserve one original troop from each corner for costly actions; a spawn changes projected occupancy but cannot pay a same-turn cost. Then visit original units by house ID, choosing stay or a neighboring destination for each unit. Earlier friendly allocations update later features. Output commands are resolved by the referee's priorities, independently of their printed order.

Teacher nonadjacent moves become their actual one-step shortest-path destinations; amounts become individual unit decisions. Debug commands are ignored explicitly. Every mechanical command family is represented, including ATTACK and both road operations. Teacher order is canonicalized, so this decoder does not represent arbitrary priority-sensitive permutations of several attacks.

An audit compared normalized and recorded plans with the actual opposing plan on all 55,782 usable teacher turns. Exactly **one** changed the resulting transition because of attack ordering. That turn is excluded from the final dataset and is fully recorded in `label-audit.json`. It belonged to validation; the clean rerun produced identical trained weights. Coverage of observed effects is **55,781 / 55,782**, not a guarantee of equivalent behavior against every possible opposing command. Two complete games with Lacoz timeouts are excluded separately.

Training data comes from frozen Lacoz and khoufou playing against v3/v6 in the historical 1,600-game confirmation archive. It is not teacher-vs-teacher or self-play data. All states of a map share one split: 158 training maps, 42 validation maps, selected by a fixed map-content hash. The new confirmation panel uses seeds 6001–6050 with content-overlap checks.

The mixture feature is a teacher one-hot on half the training examples and equal weights on the other half. Evaluation always uses the equal mixture. Cross-entropy normalizes over each legal candidate group; teacher frequency is balanced and triangle-spend decisions receive weight 2. AdamW, clipping, seed, batch sizes, checkpoint selection and both complete runs are recorded. The best checkpoint is selected by validation loss, before tournament results.

## Artifacts and reproduction

Run from the repository root after restoring/building the existing referee and opponents as described in the main README:

```sh
python3 -m venv code/arena/.venv-rl
code/arena/.venv-rl/bin/python -m pip install -r code/rl/configs/requirements.txt
python3 code/rl/build.py
python3 code/restore_records.py
python3 code/rl/sim/validate.py --games 400 --out /tmp/sim-parity.json
python3 code/rl/sim/random_validate.py --out /tmp/random-parity.json
python3 code/rl/data/audit_labels.py --out /tmp/label-audit.json
code/arena/.venv-rl/bin/python code/rl/data/build_dataset.py \
  --out code/build/rl-cache/rebuild \
  --report /tmp/dataset.json --exclude-audit /tmp/label-audit.json
code/arena/.venv-rl/bin/python code/rl/train/bc.py \
  --data code/build/rl-cache/rebuild --out experiments/rl/retrain \
  --device auto --epochs 10
code/arena/.venv-rl/bin/python code/rl/export/verify.py \
  --training experiments/rl/retrain --data code/build/rl-cache/rebuild \
  --out /tmp/export-check.json
python3 code/rl/eval/tournament.py \
  --weights experiments/rl/retrain/weights.txt \
  --seeds 6001:6050 --out experiments/rl/retest
python3 code/rl/eval/analyze.py experiments/rl/retest --out /tmp/comparison.json
```

Output directories must be new. Seeds 6001–6050 become development data after this report; reproducing those games is not a new blind confirmation. MPS availability depends on access to Metal; the sandbox initially reported it unavailable, while a permitted local process detected and used it. `--device cpu` is supported. MPS arithmetic can differ on another library/device version; checkpoint/data hashes identify exact artifacts.

Saved `weights.txt` is a portable text model loaded directly by `code/build/bc-bot WEIGHTS 2`. `checkpoint.pt` contains model/optimizer/RNG state for inspection or a future resume implementation; the current trainer starts fresh and has no resume CLI. Load only the repository's trusted checkpoint. No Python or PyTorch is needed by the playing bot. The training arrays are derived local caches, approximately 2.5 GB, with recorded hashes and a rebuild command; they are not uploaded. Full teacher source records already exist in committed archives. Both small checkpoints, text weights and complete evaluation records are retained on the branch.

The local native bot currently uses an external weights file and several C++ headers. It has not been packaged or validated as a single-file contest IDE submission; platform source-size/memory limits remain unverified. A short supervised run and one training seed do not establish the strength or scaling potential of subsequent reinforcement learning.

# Early-state curriculum: bounded controlled pilot

Protocol recorded 2026-11-08 before new results. Status: pilot closed; candidate
rejected by the original development gate. The protocol below is retained.
All observations from the 95 B2M platform games are development data. Early
army deficits are associated with losses; they do not establish a causal army
problem. No army, spawn or income shaping is allowed.

## Restoration contract

Only fully settled pre-decision boundaries at completed turns 2, 4, 6, 8, 10
are eligible. The task queue must be empty. Persist coordinates, current edges,
units, remaining units, scores, absolute completed turn, terminal flag,
surrounding-pass flag, ordered triangle vertices, owner, initial owner and both
capture flags. Restore without calling settle or adding income again.
Record map/content hashes, initial board and exact prefix commands separately.
Validate native snapshots against sequential original Java replay, direct Java
restoration and changed continuations. Recorded commands may reproduce the prefix
and validation trajectory only. After intervention both players plan again.

## State bank and recoverability

Use the archived 95-game audit (wins and losses), plus 16 fresh self-play games
on already-training maps. Training seed/map content is disjoint from development.
For each archived game take the latest turn in 10, 8, 6, 4, 2 whose controlled
side wins at least one of four live continuations: league3m and B2M as learner,
each against league3m and an older PPO anchor, all greedy. If none wins, exclude
that game; never relabel it recoverable from army heuristics. This is a limited
operational screen, not a proof of strategic recoverability. Cap archival banks
at 24 losses and 12 wins, selected in ascending game ID before testing. Include
16 fresh self-play states from the same turn schedule. Keep all screening
outcomes, including exclusions and moves to earlier turns.

## Matched experiment

Intervention: 15% of episodes start from the bank, uniformly across loss, win and
fresh categories, then uniformly within category and the already scheduled seat;
85% start normally. Control:
100% ordinary starts. Both continue the identical frozen league3m actor, critic
and optimizer state with identical PPO configuration, seed, fixed opponent
schedule and update sample budget. Keep standard decoder, terminal +1/0/-1 and
live opponents. No historical PPO-v3 resume, dynamic league or search additions.
Training opponents: 50% current self-play, 25% frozen league3m, 12.5% older PPO,
12.5% Lacoz; the same mixture for both arms. A restored external opponent receives
a fresh initial protocol message at its first decision, then new observations.
**Pre-training correctness amendment (2026-11-08):** inspection found that Lacoz
retains its turn counter, original home nodes and opponent-learning history.
Cold-starting it at turn 10 would misrepresent that policy. Therefore Lacoz
episodes remain ordinary starts in both arms. Draw restored starts only among
the 87.5% stateless neural matchups, with probability 0.15 / 0.875, keeping the
overall target 15% and the exact same opponent schedule. No results motivated
this amendment. The earlier proposed cold-start behavior is not implemented.
Train only the selected learner seat in every game, including self-play, so
state-bank seat selection is explicit. Report actual start proportions and
decision/episode differences. Equal decision counts are the primary budget;
equal 12-minute caps bound each initial arm (pilot total at most 30 minutes).
The first target is 100,000 complete-turn decisions per arm; finish the final
episode but truncate learning arrays only at complete-episode boundaries, and
report any small overshoot. Identical worker counts; no parallel heavy processes.

## Evaluation and continuation gate

Use only whole games from the true initial state. Dev seeds 61001–61060 must pass
canonical and legacy content comparison with the shared exclusion registry and
other branches. Use 61001–61012 for a first screen: frozen candidate, matched
control and league3m versus Lacoz, old khoufou and B2M, plus candidate versus
control and league3m. Report per-opponent paired, map-clustered 95% bootstrap
intervals. Recovery win rate is diagnostic only. Expand to the next 28 maps only
if the candidate has positive pooled external point gain over the matched
control, no opponent loss worse than 10 percentage points, no own technical
failure, and direct score above 50% versus control. This screen is adaptive,
not independent confirmation. If promising, repeat the training seed before
using the remaining 20 dev maps. Stop an unpromising branch honestly.

Technical restoration/Java failures stop training until corrected. No reading,
generation or play on global 40001–40100 or 65001–65040. One cross-branch finalist
must be frozen by the coordinator before the global final opens. No submission,
Git operation, external API game or paid resource in this branch. Total heavy
budget at most four hours, slots at most 25 minutes, hard stop
2026-11-09T02:00:00Z. External compute spend: $0.

## Outcome recorded after the experiment

Both matched100k-decision arms completed, including14.86% restored episodes in
the treatment. On12 content-audited full-start development maps, all264 games
were technically clean. Curriculum minus ordinary continuation was+6.94pp
(95% paired map-bootstrap CI -1.39,+16.67); direct play was11W11L2D, exactly50%.
The declared direct-score condition required strictly above50%, so there is no
expansion, retraining or promotion. Versus league3m directly it was10W14L.

The exact results, source/runtime hashes, state-parity evidence, budget mismatch
limitations and corrected interim-summary erratum are in the
[report](../../../experiments/rl/2026-11-08-rl4/curriculum/REPORT.md).
The subsequent frozen-bank recovery diagnostic cannot change this decision.
It completed288 live continuations with7,988 Java states matching exactly.
Recovery wins per96games were55curriculum,59control,57league3m; there is no
observed recovery advantage on this biased training bank either. Both policies
remain rejected; the restoration code and evidence are retained for review.
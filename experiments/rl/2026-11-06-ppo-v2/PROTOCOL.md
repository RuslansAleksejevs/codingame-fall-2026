# PPO v2 improvement campaign

Recorded before new training or opening the confirmation maps, 2026-11-06.

## Objective and boundaries

Strengthen the frozen PPO v1 actor, especially against Lacoz, using the local MacBook Air M4. Initial additional budget: up to 20 million controlled-player decisions and six hours of training, reassessed against measured development results. No paid compute, main-branch promotion or live submission. Keep every attempted run and separate development evidence from final confirmation.

The starting policy is PPO v1 at 752,998 decisions, SHA256 `8b9f669b3b4047eb75d1ff1df2ea9cc8e61de59629de1c9260f8a954b40ae7e7`. BC and original v6/Lacoz/khoufou remain frozen. Native mechanics, actor representation and deployment decoder initially stay unchanged.

## Staged experiments

1. **Longer-training control:** warm-start the selected PPO v1 actor/critic/optimizers; retain the original 158 training maps, terminal reward, PPO hyperparameters and 50/25/25 current/BC/history opponent mix. Collect up to 5 million additional decisions with checkpoints near 1M, 3M and 5M. Use a fresh fixed training RNG seed. This measures longer training with the same recipe, not exact continuation of the original random stream.
2. **Map and opponent diversity:** enlarge training maps using the original Java generator, excluding all selection/confirmation maps. Keep old anchors and introduce the stronger PPO v1 plus a wider historical pool; record the actual sampling distribution. Compare at a matched additional sample budget. Implement and validate this separately from the longer-training control.
3. **Independent training / targeted follow-up:** spend the remaining budget on an independent seed of the strongest promising recipe, or a recorded targeted intervention if development evidence shows a clear bottleneck. Do not silently change a running experiment. Any new intervention gets its own configuration and rationale before its results.

CPU optimization and native collection run locally; timed original-arena evaluations run after training pauses. Each block saves actor, critic, optimizers, opponent pool, RNG state, counters and sources. Do not change the frozen BC/PPO v1 files. Training code changes use new entry points or versioned modules, preserving the original reproductions.

## Development and selection

Previously inspected maps are now development data. Native quick checks use the 42 original BC validation maps against BC and PPO v1. Original-arena screens use seeds 6001–6025, both seats, against frozen Lacoz and khoufou, with v6 and PPO v1 added for finalists. These maps are excluded from training. They are deliberately not called a new holdout.

Rank trained candidates primarily by clean score rate against Lacoz on the fixed development panel, with safeguards against substantial regression versus khoufou/v6 and direct PPO v1. Use the same complete panel for every compared candidate, report paired differences and all technical outcomes. Break ties by the equally weighted development panel, then lower training cost. Saturated BC win rate is a diagnostic, not the primary selection objective.

## Fresh confirmation

Reserve **seeds 9001–9100**, 100 maps, both seats. Do not generate or inspect them until the selected candidate is frozen. Compare the selected candidate and PPO v1 against v6, Lacoz, khoufou and BC (1,600 games), plus 200 direct candidate-vs-PPO-v1 games: **1,800 games**. Check map-content novelty against all historical, new training and development maps, not seed numbers alone. Use the original serial 1000/50 ms referee and unchanged opponent revisions.

Primary evidence: paired clean-game score-rate difference against Lacoz, map-clustered 95% interval, plus per-opponent safeguards and direct PPO v1 results. A useful target is at least +15 percentage points against Lacoz with a positive paired lower interval and no material loss of the v1 strengths against v6/khoufou. This is an aspiration, not a claimed result. No optional extension of the final sample because an interval is close. If a final attempt fails, retain it and declare its maps development data before designing any later experiment with another untouched confirmation set.

All measured outcomes, runtime, memory, failed attempts, source/model hashes and full final records are saved in the private `rl/research` branch. Repository text stays English and does not assign idea ownership to individuals. Coding subscription quota is not measurable here; external compute spend remains zero.

## Addendum: fixed diversity recipe (before its training results)

The original Java generator produced 2,000 new training maps, seeds 10001–12000. All 200 archived BC-generation maps were regenerated exactly; the new corpus has no content overlap with the 425 previously inspected maps. The original 42 validation maps remain diagnostics only.

The map-only ablation uses `ppo_long.py` on this new corpus with the original opponent distribution and hyperparameters. The league arm uses `ppo_league.py` on the same corpus, with 50% current-vs-current games, 25% greedy frozen anchors (90% PPO v1 and 10% BC within that category), 12.5% historical opponents (uniform over up to 12 snapshots; half greedy, half sampled), and 12.5% unchanged original Lacoz. Snapshots refresh every 250,000 controlled decisions. Learner seats are balanced. Rewards, actor features, PPO loss, optimization and 64-game/4-worker rollouts remain unchanged. All arms start at the same PPO v1 checkpoint. Compare 1M/3M/5M checkpoints where justified by development results and local runtime.

The unchanged Lacoz Python source runs in persistent isolated processes, with fresh globals for every game and its original 30 ms search budget. This is a training bridge, not the timed confirmation arena. Original-Java observation and full-state checks passed for 16 games/495 transitions/1,022 inputs, including two Lacoz games; a separate optimization pilot completed 22,686 decisions/448 games (56 against Lacoz), with zero errors. Original timed evaluation remains serial and runs while training is paused.

The first 1M longer-training checkpoint has already been screened on development maps (28/50 Lacoz, 50/50 khoufou; PPO v1 18/50 and 47/50). These results informed continuation of the longer-training control. No final-confirmation map has been opened. The diversity arms have not yet produced selection results.

Training may run in two concurrent local jobs (four collector workers and four Torch threads per job, alternating collection/optimization). There is no timed opponent evaluation during concurrent training. Report both summed per-job elapsed time and campaign wall time; those runtimes include contention and are not a controlled hardware-speed comparison. Keep memory below the 24 GB local limit.

## Addendum: targeted road-observation experiment (before selection results)

The first longer-training development panel uses very few ADD_PATH actions (14 commands across 50 Lacoz games), while the opponent uses road construction. Inspection of the fixed 128 actor inputs found no explicit count of triangles created or destroyed by a proposed road. This is a representational hypothesis, not a causal explanation of the losses.

An isolated `roads` variant reuses three inputs that are constants for style 2: the two teacher-style flags (0.5, 0.5) and a constant 1. For ADD_PATH/REMOVE_PATH it observes the signed number of affected empty triangles and friendly/enemy majority corners after paying the three-unit cost; other actions receive zeros in those slots. The input size, network size, legal-action decoder, reward, PPO objective and remaining observations stay the same. The initial constant contributions are folded into the first-layer bias, and the new columns start at zero. Their Adam moments and the folded first-bias moments are reset; other optimizer state is retained. Consequently this is a feature/reparameterization experiment, not a claim of an isolated feature-only causal effect. Initial actor/critic outputs agree within floating-point rounding. All historical learner models receive the same conversion, while frozen BC/PPO v1 anchors retain their original style-2 inputs.

Before training, 16 games/483 full transitions matched original Java; 40 independent road effects matched original geometry changes, worker-count determinism passed, and native/PyTorch joint likelihoods matched. The main variant will start again from frozen PPO v1 on the same 2,000 maps and the same league recipe/seed, initially for 1M additional decisions. Its original-arena comparison will include the 1M league checkpoint. Preserve its pilot and all outcomes, including failure to improve.

To stay within the measured local time budget, first screen the map-only and road variants at 1M each; extend only promising recipes after the common development panel. The longer control and original league blocks already target 3M. Budget the remaining time for an independent seed or a further promising block. Final seeds 9001–9100 remain untouched.

Before the common development and final panels, add deterministic cyclic rotation of pair execution order and alternate the first executed seat by map index. Every planned pairing/map/seat still runs exactly once. This reduces fixed execution-order effects during serial wall-timed evaluation; the initial 200-game development screen used its recorded listed order. The panel manifest records the chosen order.

For the finalist safeguards, define a practical development screen before the common panel: allow at most a 6-percentage-point drop from the simultaneously evaluated PPO v1 against each of khoufou and v6 (three games in a 50-game panel), and require at least 60% direct score against PPO v1. These are selection screens, not significance tests; final paired intervals and all outcomes are still reported. Screen all candidates on Lacoz/khoufou first, then add v6/direct PPO v1 for the leading candidates, continuing down the development ranking if a safeguard fails.

All 29 local original-referee Java files were compared byte-for-byte through their Git blob hashes with the pinned public source tree; every file matched. The later panels also snapshot the Python/Java match harness and record its compiled class hash and JDK version.

## Addendum: bounded continuation after the common screen

The completed 700-game common screen had no technical failures. Against Lacoz, PPO v1 won 16/50; long1m 26/50, long3m 32/50, maps1m 27/50, league1m 23/50, league3m 34/50 and roads1m 29/50. Every new candidate won 50/50 against khoufou; PPO v1 won 47/50. The top three are receiving the pre-recorded v6/direct-PPO-v1 safeguards before further training. The common screen passed full-state Java/native replay for 19,237 transitions.

Conditional on those safeguards, prioritize continuation of the observed leader, **league-a to 5M cumulative additional decisions**, with a **190-minute cumulative run cap**. It improved from 23 to 34 Lacoz wins between 1M and 3M. The 34-versus-32 advantage over the longer control is only two development games; it is not evidence that the league method is reliably superior across training seeds.

Use the remaining smaller block for **roads-a to 2M cumulative additional decisions**, capped at **65 cumulative run minutes**, if its safeguards pass. At the matched 1M budget it scored 29/50 versus league1m's 23/50. Road actions remain rare, so this supports another measured continuation, not a claim that construction explains its result. Both runs retain their frozen sources, optimizer settings, maps and seed, and resume their own complete checkpoints. Run the blocks sequentially, with no timed arena alongside training. A sample target may be missed at the wall cap; report the actual saved checkpoint.

Together with completed control/map-only runs, those cumulative caps allow approximately six summed production-training hours (up to 359.38 minutes before small iteration/correctness overhead). Pilots and evaluation are separately accounted. Preserve the pre-continuation summaries and hardware metadata; immutable 1M/3M checkpoints remain selectable. This is the protocol's targeted follow-up option, not an independent-seed replication.

After both continuations, evaluate the three prior leaders, both extended models and PPO v1 on the same complete development panel: each against Lacoz/khoufou/v6, and each candidate directly against PPO v1. With five candidates plus the control this is 1,150 games on the same 25 development maps. Apply the already specified primary ranking, safeguards and tie-break rule using that panel, rather than pooling repeated games on the same maps as independent observations. Freeze the selected model and its feature variant before generating the untouched final seeds 9001–9100.

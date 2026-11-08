# Frozen pre-result protocol: search teacher

Recorded 2026-11-08 before any new game or diagnostic rollout. Classification:
USER_CONFIRMED for the bounded local execution; MODEL_INFERENCE for hypotheses
and thresholds; measured results will be PROJECT_REPORTED.

## Preservation and resources

- Unchanged league3m actor: `experiments/rl/2026-11-06-ppo-v2/league-a/step-03002173/weights.txt`,
  SHA256 `dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb`.
- Checkpoint SHA256 `9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663`;
  preserved fallback SHA256 `199c6a2d2c0a7e9438351aad25e6eeda5816111b9fb672cdc0eb302052cd19c1`.
- Reuse the v3 frozen critic export, league3m/long3m/extended response models,
  exact simulator and corrected absolute-player-order protocol. Hash them.
- Local CPU only, zero external spend, at most four summed heavy hours;
  first pilot at most 30 minutes, each CPU lease at most 25 minutes.
- All heavy work uses the coordinator's exclusive CPU lease after COMPUTE_READY.
  Research hard stop 2026-11-09T02:00:00Z; official deadline 09:00:00Z.
- No shared-source edits, old experiment changes, Git operations, new agents,
  OAuth, platform games, submission or rollback.

## Frozen teacher and diagnostic

Only one teacher candidate is tested: existing search2, four proposed complete
plans including unchanged greedy, sampling temperatures .15/.35/.7, exact
two-turn simultaneous rollouts, three fixed enemy models, .5 mean + .5 minimum
value, .02 improvement margin, gamma .995, and 30ms budget in timed games.
Root enemy plans are chosen independently of our action. Later actions of
both players are recomputed from each counterfactual state. No changed-state
trajectory uses recorded future enemy commands. The critic is not presumed
accurate outside the actor distribution.

The isolated diagnostic exposes all deduplicated candidate plans and their
scores at horizons 1, 2, 4, 8 and complete greedy continuation. Root states
come from fresh normal games on seeds 62001–62006, both seats, turns 0/5/10.
Three different frozen response models are continuations, not independent
external strength evidence. Report pairwise sign concordance (excluding tied
terminal values), regret of the chosen plan, changes relative to greedy,
mean/min aggregation and per-model results. Long deterministic continuations
are a diagnostic proxy, not ground-truth optimal values. Zero parse errors,
root immutability, deterministic replay, baseline inclusion, terminal ±1/0
and original Java agreement are mandatory. No diagnostic becomes a training
dataset merely by being saved. Depths4/8 are diagnostic only, not extra
candidates selected after observing outcomes.

## Maps, selection and strength gates

All map contents must be audited against the previous registry, later v3
development maps, saved platform maps and other new branches' contributions.
Seeds are identifiers, not proof of novelty. Duplicates stop the stage; do not
silently replace them or extend samples. Seeds40001–40100 and65001–65040 stay
closed. Diagnostic62001–62006 and screen62007–62018 are permanently development.
Confirmation62019–62058 is independent of this branch's diagnosis/screen;
62059–62060 is a technical reserve, never a post-result power extension.

1. Build/contracts and diagnostic, plus tiny timed smoke on diagnostic maps.
2. Screen on exactly12 maps62007–62018: search2 and unchanged greedy against
   Lacoz, new khoufou070bc128, old khoufou372c1cd6 and league3m, both seats,
   rotating execution order. 192 games. Continue only if equal-weight external
   gain >=5pp, direct score >=55%, no external opponent gain below -5pp,
   and zero own/control errors. A failed screen ends this branch.
3. If screen passes, freeze the same configuration and evaluate exactly40
   maps62019–62058, split into finite CPU leases fixed before results. Same
   opponents plus v6 and BC regression guards. 960 games in total. No
   interim strength decisions; aggregate all completed predefined chunks.
4. Teacher strength gate: external mean gain >=5pp over Lacoz/new/old khoufou;
   paired map-bootstrap 95% lower bound strictly >0; direct score >=55%
   with map-bootstrap 95% lower bound strictly >50%; no per-opponent point
   regression >5pp including v6/BC; zero own/control errors; >=36 complete
   paired maps for every opponent and >=36 complete composite maps.
   Bootstrap uses 10,000 resamples, seed20261106, whole maps/both seats.
   Also report every per-opponent paired CI without claiming each significant.
5. Original native/Java replay agreement is required. Technical outcomes are
   retained and excluded pairwise, never counted as strategic wins. Teacher
   runtime/budget truncation is reported separately from offline ranking.

Failure or inconclusive evidence ends the branch without large label generation
or student training. The previous v3 result is context, not pooled evidence.
This panel remains development evidence for the overall three-branch selection.
The coordinator freezes one overall finalist before opening any global final.

## Conditional compact student

Only after the teacher strength gate passes: write a second pre-result training
protocol specifying small data volume, seed, plan target distributions,
autoregressive replay/label legality and exact representability, a mixture of
anchor/current-policy states, bounded optimization and independent student
evaluation. Student must retain teacher gain in complete games and pass exact
export/single-file/50ms checks. A good teacher alone is not a finished candidate.
No GNN/MuZero/BTR expansion or other approach is silently substituted.
# Complete-plan search and conditional distillation

As of 2026-11-08T09:16Z. Completed and rejected; no student training.
A new bounded local experiment, not a resume of PPO-v3.
Implementation and evidence live in `code/rl/v4/search_teacher/` and
`experiments/rl/2026-11-08-rl4/search-teacher/` respectively.

The frozen v3 search2 result remains **not confirmed**: external +7.14pp on
28 maps, paired map-cluster 95% CI [0, 15.48]. Its criterion is not changed.
The new experiment independently checks the same search recipe, with an
explicit off-policy ranking diagnosis before conditional student training.

See the [pre-result protocol](../../../experiments/rl/2026-11-08-rl4/search-teacher/PROTOCOL.md)
and [status](../../../experiments/rl/2026-11-08-rl4/search-teacher/STATUS.md).
The [final report](../../../experiments/rl/2026-11-08-rl4/search-teacher/REPORT.md)
records36 diagnostic roots,219 counterfactual continuations,1,095 exact Java
snapshots and four clean timed smoke games. The frozen depth2 critic ranking
agrees with long deterministic continuation in33/54 non-tied pair comparisons;
this is a limited response-model diagnostic, not confirmed teacher strength.
No competition submission, platform games, paid compute or shared-source
modifications are part of this branch. The five-network teacher is offline;
it is not a source-size-compliant submission.

The fixed40-map/960-game confirmation completed without candidate changes.
External gain4.824561pp (38 common paired maps),95%CI[0.438596,10.087719]pp,
misses the predeclared5pp minimum. Three own timeouts also fail the zero-error
requirement; one late raw internal planning log is75.244ms. All four technical
records, including one separate control-opponent timeout, remain retained.
Direct score97.5%,95%CI[93.75,100], does not override the failed broad gate.
Teacher strength FALSE; labels/student0; no further games or global-final
exposure. Integrate research evidence only, not a submission candidate.

## Conditional student: static interface finding, not an executed stage

The existing `models/policy.hpp::labels` sorts each house's movement destinations
when reconstructing a plan. That can preserve the joint movement result while
changing the autoregressive prefix and its feature vectors. Therefore simply
feeding search command strings through the old BC label builder does not prove
that the reconstructed labels are the teacher's actual sampled decisions.
Canonicalization also needs an explicit command-order/transition check.

For a future separately authorized teacher that passes its own gate, prefer
recording the candidate generator's exact
legal choices, features and prefixes in a new branch-local trace adapter.
Check that replaying these choices renders the exact selected complete plan,
that all soft target masses sum to one, and that masked choices are legal.
Do not silently use the old builder's style0/1 or its feature rewriting for
the style2 PPO actor. No target data or training has been started on this basis.
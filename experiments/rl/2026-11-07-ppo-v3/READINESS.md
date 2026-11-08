# PPO-v3 execution readiness

As of 2026-11-07T23:53:46Z. PROJECT_REPORTED unless stated otherwise.

- Authorized: local PPO-v3 implementation, two independent continuation seeds,
  expanded evaluation, bounded search pilot, averaging, packaging and platform
  verification. No submission, publication, commit/push or paid resources.
- Checkout: `rl/research`, starting commit `4baecdf3ad593f642fa13ca939fb76dd07c004c0`;
  initially clean. Existing checkpoints and submissions must remain unchanged.
- Base: `../2026-11-06-ppo-v2/league-a/step-03002173/checkpoint.pt`,
  SHA256 `9ba362b28947b126df6b97e006d53d2ae860d37f5736d89f3e3c65c595ee8663`.
- Weights: SHA256 `dcc99a63778fcfe363c09b809461d34b34d99fa92d4dfa12574a8092ad1719eb`.
  Both hashes verified in this execution. Published fallback remains unchanged.
- Existing CPU environment: Python 3.14.6, torch 2.15.0, NumPy 2.5.4,
  SciPy 1.18.1, Apple Clang 17.0.0, existing JDK 17.0.21+9.
- No API key or OAuth is needed for local training. Platform OAuth is separate,
  memory-only, read/play scope, submission disabled by default in the client.
- Saved official deadline: 2026-11-09T09:00:00Z (01:00 PST, 10:00 CET),
  source `../2026-11-06-live-ppo-v2/challenge.json`. Fresh API check pending.
- Hard research cutoff: 2026-11-09T02:00:00Z, preserving seven hours.
- No old seed range is considered a fresh holdout. Content-hash exclusions will
  be rebuilt before the final panel. Old 139/200 vs Lacoz is historical evidence.
- Process read required reviewed execution. One unrelated long-running Python
  process was observed; it is not stopped or modified. No Java/native bot process
  appeared in the filtered process snapshot. The Python process belongs to a
  different project; it was not inspected beyond its working directory or stopped.
- External compute spend: zero.

## Executed checks

- Builds succeeded through reviewed execution after sandbox temporary-file denial.
- Existing bridge: 16 games, 490 original-Java transitions and 1,012 observations
  matched; no external opponent errors.
- Legacy continuation smoke only: 6,261 decisions / 128 games / 10.47 seconds.
  It is not called PPO-v3 and does not initialize production.
- Original-arena smoke: 16 clean games against Lacoz, both khoufou versions and
  v6 on known maps. 356 native transitions matched. No strength claim from smoke.
- PPO-v3 contracts: 14 games / 409 transitions matched original Java; complete
  plan log-probability maximum error 3.82e-5, terminal-only rewards verified.
  Split/resume produced identical actor/critic, optimizers, opponent pool, RNGs,
  difficulty scores and export. Initial failed test found a relative-path logging
  bug; its records remain in `v3-tests`, corrected repeat in `v3-tests-2`.
- PPO-v3 pilot: 22,254 decisions / 512 games / 34.56 seconds; 58 Lacoz games,
  2,013 external calls, zero external errors, parent peak RSS 1.19 GB.
- Initial exclusion registry: 2,561 canonical and 686 legacy map hashes from
  218 source files, including archived platform game options.
- 400-game frozen-base development panel completed: Lacoz 59/80 wins,
  new khoufou 71/80, old khoufou 72/80, v6 74/80, BC 73 wins / 2 draws / 5 losses.
  All games clean. All 10,637 transitions and 11,037 full states matched Java;
  40 maps had no canonical/legacy overlap. This is a development baseline, not
  a PPO-v3 strength result.
- At 2026-11-07T23:57:29.729707Z the real first-block campaign started.
  Seed A reached 29,417 decisions / 640 games in 42.07 seconds; recovery saved.
  `campaign-status.json` and `train-a-block1.log` contain live progress. The driver
  proceeds through A, isolated screening, independent B, isolated screening.
- First OAuth device code expired without approval. No token was obtained;
  the process was closed. Local training is unaffected. Fresh platform access
  and exact-deadline recheck still require a new user-confirmed device flow.
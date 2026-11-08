# Curriculum status

Research closed as of 2026-11-08T09:14:18Z. Both100k arms, full-start screen and
final recovery diagnostic completed. Candidate rejected by the frozen
direct-score gate; no further training, games or development. Packaging and
closure checks are recorded separately in completion.json.

- Runtime confirmed by coordinator: GPT-6 Astra, effort max, codex_second,
  regular tier. No runtime configuration changes.
- Root/contest/repository instructions and current diagnosis read.
- Protocol: `docs/rl/v4/CURRICULUM.md`, recorded before results.
- Full-state boundary format includes remaining units and initial triangle
  ownership, in addition to the public snapshot. Queue is empty at this boundary.
- All 95 archived games: 3,638 full states / 3,543 transitions match original
  Java; 475 native restores and 475 direct Java restores match exactly.
- Bank: 48 states on 48 distinct original maps (20 losses, 12 wins, 16 fresh
  training self-play states). Four screened losses excluded by the frozen
  recovery criterion. 384 live continuations / 18,268 Java state checks passed.
- Bank SHA256: `2604762ff2c317d33ede69e4371b4bd0c6a74ae46543aa5726102b8a87ad7fc0`.
- Contracts passed: 10 live games / 406 Java state checks; reward is terminal
  only; old-logp error 4.58e-5; worker determinism and exact split/resume passed.
- Initial failure records retained: sandbox temporary-file denial, then a
  comparator that fabricated Java parse counters. The latter was corrected:
  native counters are diagnostic, all physical/hidden fields remain exact.
  The one nonzero archival counter belongs to the opponent after turn 21, not
  to the controlled bot. All 475 early boundaries and generated plans are clean.
- Correctness amendment before training: stateful Lacoz always gets ordinary
  starts in both arms. The 15% overall curriculum share is drawn only from
  stateless neural matchups; no false reset of Lacoz's history or turn counter.
- COMPUTE_READY received. Heavy work is always behind the shared lease.
  Completed smoke released the lease at 08:09:05Z, after 63.79 seconds.
- Control100k finished: 100,020 decisions / 3,049 complete training episodes /
  48 updates / 233.85 training seconds, restored games0. Of 3,072 collected
  episodes, 23 complete episodes (748 decisions) were unused at the final
  budget boundary; no partial episode was used. Target overshoot20 decisions.
  Opponent episodes: current1517, league3m767, olderPPO382, Lacoz383.
  Teacher384 collected games / 13,435 calls / errors[]. Export1000/1000 argmax,
  maximum logit error2.29e-5. All frozen source hashes still match.
  Weights SHA256 `21c6da38b91e236ffa29a6663af4a2a97d9a83efbbf3c7d6541b9ac277165762`.
  Commands: `pilot-control-commands.json`; logs: `pilot-control-command*.log`.
- The 167,498,374-byte raw preflight evidence was losslessly archived into
  `preflight-evidence.tar.gz` (4,387,514 bytes); every member SHA256 verified.
  Original raw files remain on disk. Archive SHA256:
  `5b9e69f1c55808f4aedf1bd5c9ae183daeefb82536f2faa591efc270a8a48780`.
- Lease released08:30:30Z (239.46s). Next queue: search-teacher confirmation1,
  then curriculum100k in its own lease, then paired whole-game development.
- Treatment finished08:40:33Z, exec44exit0 / 238.25s lease:100,013 decisions /
  3,157 used complete episodes / 50 updates / 233.325 training seconds.
  Restored469 episodes (14.8559%),12,209 decisions (12.2074%):loss155/win160/fresh154.
  Opponent episodes: current1579,league3m788,olderPPO394,Lacoz396. Of3,200
  collected episodes,43 complete episodes/1,373 decisions were unused at the
  final budget boundary; partial episodes0,overshoot13.
  Teacher400 collected games / 13,844 calls / errors[]. Export1000/1000 argmax,
  maximum logit error2.29e-5. Source manifest identical to control:
  `05157018f183bb484dbc61e314bc7a55f0d6f94bf896b63765f0f891114d14c5`.
  Weights SHA256 `7689e7cc277d26d76af80edd8ab95829786397e872fd53a43af1707667a8636f`.
- Before treatment, three additional actual post-road states (turns47/34/22)
  passed direct restore/live continuation checks:82 Java states,zero mismatches.
  This separate process did not change the training bank or RNG.
- Full-start screen:264 clean games on12 novel maps61001–61012. Native8,304
  transitions and Java8,568 full states passed. Own/opponent/invalid errors0.
- Primary curriculum-minus-control paired gains (95% map CI), percentage points:
  Lacoz0[-20.83,+16.67], khoufou-4.17[-12.50,0], B2M+25[+12.50,+37.50],
  pooled+6.94[-1.39,+16.67]. Direct11W11L2D=50%; the gate required>50%.
  Curriculum versus league3m directly10W14L. Do not promote either pilot arm.
- Original and stricter coverage guard both reject. All opponents have24/24
  clean pairs; the analyzer's21versusdeclared22 minimum did not affect outcome.
- An erroneous interim summary is withdrawn explicitly in REPORT.md. The
  authoritative `final-data-audit.json` independently recomputed all rates,
  W/L/D groups, paired gains and intervals from raw matches and checked hashes.
  Its SHA256 is1e3ec2c3b325de63058d1578e71db17a39b3d3ea7b5ad31975b8fc6a086205e6.
- Heavy leases total832.389seconds before the optional final diagnostic.
  The actual screen lease ended08:53:41Z after285.674seconds.
- Final diagnostic completed09:14:18Z: frozen48-state training bank×2live
  anchors×3frozen policies=288games;22.465seconds lease. Curriculum55W41L,
  ordinary control59W37L,league3m57W39L,all0draws;96games each. All7,988Java
  states matched. These are biased training-bank diagnostics, not strength.
  Pre-game plan/code/state/policy/audit hashes all matched.
- Heavy resource through the final diagnostic854.854seconds. REPORT is frozen;
  next actions are full raw archive under its own lease, six pure unit tests,
  read-only contest check and exact final file inventory. No game remains.
- Final packaging records are pilot-evidence-archive.json and completion.json;
  original data are preserved, private prefixes normalized in archive copies
  only. Coordinator alone handles Git and shared organizational records.
- No global-final or61013–61060 maps opened. The failed gate remains closed.
- Existing frozen source/checkpoints and organizational state are untouched.
- No paid compute, platform action or Git operation. External spend: $0.
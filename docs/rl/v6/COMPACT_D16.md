# Compact D16: isolated delivery experiment

Final outcome as of2026-11-08T20:58Z: REJECTED incomplete final. Packaging and
504-game development admission passed. The independent final stopped after
656/4200games because of one emergency WAIT before baseline generation. No
referee timeout occurred in that game. Final strength is inconclusive, and no
platform or ranking action occurred.

The separately authorized prospective protocol is
`experiments/rl/2026-11-08-rl6/compact-d16/PROTOCOL.md`.
All closed v3/v4/v5 decisions remain closed. The v5 student is not reused.

Four unique float32 weight sets retain the actor, critic and all three response
roles, with shared actor/response0 storage. Matrix rows use symmetric9-bit
integers, float32 scales and float32 biases. Activations and the original
inference kernel are unchanged. Weights are restored once at process startup;
the delivered C++17 source has no external weight/runtime dependency.

The precision was selected without game outcomes: deterministic12/11/10/9/8
packages, highest precision meeting98000UTF16 plus compilation and exact codec.
Attempt2 selects9bits,94123UTF16, source SHA256
`22ccbbe3fedd8cdb7bae8c232b62269ee5b7cde838b23afb4405692b92e5a5c9`.
Attempt1 is retained; attempt2 corrects unsigned-to-signed conversion to strictly
defined signed subtraction. The quantizer and decision rule did not change.

The amalgamation extracts the frozen simulator, observation decoder, features,
FastNetwork, value features, D16 search and absolute-player I/O. It omits unused
training/C-ABI/old-main paths and replaces file storage with in-memory storage.
Token-preserving minification is checked. Full original source identities are
recorded in package manifests. No frozen file is modified.

Actual contracts covered5544both-seat roots,22176stream commands and114500
bitexact logit pairs, with200deterministic-cap root contracts and89nonbaseline
partial-stop cases. Quantization changed2897/5544unlimited plans(52.2547%);
maximum observed original/quantized logit difference was2.17236328125.
This is neither a strength claim nor an export mismatch: the compact program
exactly reproduces the quantized reference, while quantization itself changes
the policy. The independent coordinator storage audit also passed.

The six disclosed regression games had zero own/opponent errors or emergency
fallbacks. All225outputs had timing records; maximum internal through-flush
was16.1045ms. Full Java/native replay matched226states/220transitions.
The coordinator independently reparsed the raw regression records and verified
all60development freeze identities. Twelve new development maps passed
canonical/legacy novelty against2918canonical maps and302source manifests,
including all exposed v5 main/student partitions. At that development
checkpoint, reserve maps were still unopened. The later approved final
generated40001–40020;40021–40100 and65001–65040 stayed unopened.

The completed504-game development has0own/control/teacher errors and1Lacoz
error. Independent child/coordinator audits agree. External gain is+6.9444pp
all-games(95%mapCI[-1.3889,15.2778]) and+4.5455pp clean-paired
(CI[-3.0303,12.1212],11/12maps). Direct league3m21/24; directB2M13/24.
These are admission results, not final evidence of improvement over deployedB2M.
503clean games replay exactly through13951Java/native states and13448transitions.

The actual final stop is candidate/league3m/40016/seat1/turn27: input-read wall
interval17.7745ms exhausted the16ms clock before any decoder/network call.
The raw27th output is WAIT; the engine-valid game ended as a78:-1win, but the
prospective zero-emergency gate failed and analysis counts it as a technical
loss. The root cause of the read interval is UNKNOWN; it is not isolated parser
CPU time. The remaining3544games were not played, and no failed game was rerun.

Partial complete-pair external gain is+1.1111pp all-games
(95%mapCI[-4.4444,6.6667],15maps) and+2.3810pp clean
(CI[-3.5714,8.3333],14maps). These are not successful final results. Exact
Java replay covers655/656final games, excluding one opponent-error game and
including the emergency game. Independent closing audit agrees with rejection.
The detailed report is
`experiments/rl/2026-11-08-rl6/compact-d16/REPORT.md`.

Search remains depth2, four proposals, three responses, temperatures.15/.35/.7,
mean/minimum weights.5/.5, margin.02, gamma.995,16ms from the first score token,
and20000forward cap. Only complete selected plans can replace the baseline.
Exactly one command line is emitted per observation. Internal through-flush
timing excludes startup, pre-first-token scheduling and the final log write;
it is not a platform CPU measurement.

Validation sequence:100 old full-game streams/both seats and deterministic
contracts; six disclosed regression games; one504-game fresh development
admission; only if admitted and independently released, one4200-game reserved
final. The65001–65040 reserve remains closed. No training or platform action is
performed by the implementation agent. The coordinator independently audits
storage, raw records and whole-map uncertainty before any official validation.
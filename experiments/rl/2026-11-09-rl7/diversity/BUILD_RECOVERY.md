# Build environment recovery, before any game-development

Observed2026-11-09T00:31:32UTC: fixed labeldev/assembly and both seed1 students
completed. Narrow1 native/text parity passed10,546/10,546groups, maximum logit
error3.0517578125e-5, exact float32 weights. Exact source package was generated.
The existing v3 verifier then failed its FIRST compile (unmodified reference
source), before any packed-command comparison or strength game.

`narrow1-verify.log`, `narrow1-verify-command.json`, `execution/optimize1-2.log`
and `execution/optimize1-end.json` retain this failure. The nested historical
verifier prints only CalledProcessError, not captured compiler stderr; therefore
the exact original compiler cause is not directly established in this record.
The separate D16 lane reported the same host compiler could not create xcrun
temporary/cache files in its sandbox and passed unchanged after reviewed host
execution. This is context for the recovery, not a claim to have independently
reproduced its failure cause.

Preserve the empty failed `models/narrow1/verify` directory by renaming it to
`verify-attempt1-failed`, then run the SAME verifier/source/compiler under one
reviewed full-access shared lease. No TMPDIR/alternate-compiler workaround,
deletion, weight edit, retraining, changed objective or relaxed parity test.
Finish the two prescribed seed2 models once in an ordinary local lease; export
all four unchanged models. Existing source/checkpoint/weight/failure evidence
remains. No game-development is permitted until all four export contracts pass.

This is ordinary implementation/environment recovery, not a scientific protocol
amendment or evidence that the original blocked compiler command passed.
Actual reviewed execution outcome will be recorded in `export-recovery.json`;
this document does not presume success. No additional CPU budget is requested.
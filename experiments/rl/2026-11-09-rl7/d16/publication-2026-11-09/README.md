# D16 publication-only snapshot,9November2026

This new append-only directory packages the existing D16 evidence for the
coordinator's authorized private repository publication. It runs no game,
inference, training, platform request or Git operation. All prior D16 source,
reports, failures and original raw files stay frozen and byte-identical.

`inventory.json` maps each original repository-relative file and SHA256 to its
export SHA256, recording any project/home-path normalization in the copy. For
gzip evidence the decompressed UTF8 is screened and normalized if necessary;
unchanged gzip files keep their exact original bytes. Historical verifier hashes
still refer to the original loose files, not to normalized export bytes.

`evidence.tar.gz` contains file-only repository-relative members plus the exact
inventory. Every member is fully streamed and SHA-verified after creation; all
original inputs, including excluded regular files, are rehashed unchanged.
`archive.json` binds the archive and inventory and summarizes counts/exclusions.
Compiled builds/binaries/environments/cache/scratch, private-chat, credential and
permission-execution records are not publication evidence. Scientific compiler
and run logs, including failed attempts, are retained unless screening flags
sensitive content. Screening logs name only the file/reason, never a secret.

If the archive exceeds48MiB, `archive-parts/manifest.json` describes verified
48MiB-or-smaller pieces created with the existing `code/split_evidence.py`.
The complete original archive remains locally preserved. Restore only into a
fresh destination, inspect safe member names, and never overwrite existing
scientific evidence. The coordinator independently audits/stages this snapshot.

The ranking was still in progress when these frozen reports were captured.
Submission41672652 is accepted, not a final leaderboard-strength claim. Known
runtime caveat: a ranked normal turn reached22.097ms internally with no official
error; the16ms cooperative check is not a hard response-time guarantee. A later
final result must be a separately dated append, not a rewrite of this snapshot.
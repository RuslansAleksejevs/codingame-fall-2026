# Publication-only snapshot, 2026-11-09

PASS at2026-11-09T01:54:08.566Z. This is an append-only portable export of the
completed pilot, NOT new research or a changed result. No Git/API action was
performed by the pilot agent. All pre-publication pilot files remain unchanged.

Use [attempt2/PUBLICATION.json](attempt2/PUBLICATION.json) and
[attempt2/inventory.json](attempt2/inventory.json) as the authoritative receipt
and per-file original/export SHA-256 ledger. The archive has4,227safe regular
file members:4,226payload files plus the inventory. Every member's full content
was hashed and recursively scanned; all5,198selected/excluded input files were
rehashed unchanged, and125frozen/protected identities passed.

## Publication payload

The archive is60,292,844bytes, SHA-256
`1eb876975fa85572585c7585e46a636c01ea80e43af5a19aa1f74e51a2127691`.
Because it exceeds48MiB, the existing `code/split_evidence.py` produced two
byte-exact verified parts. Publish the parts and manifest, not a redundant copy
of the larger local `attempt2/evidence.tar.gz` as well.

|File under `attempt2/archive-parts/`|Bytes|SHA-256|
|---|---:|---|
|`evidence.tar.gz.part-000`|50,331,648|`f15868cdaf3232ba10d5c7756c15814ac8f92798a73c9e626943b011f9de6dc0`|
|`evidence.tar.gz.part-001`|9,961,196|`04c7ddf147675ab9493dbfff997f277e28fc63fed724740260af1a28b1789267`|

[Parts manifest](attempt2/archive-parts/manifest.json) SHA-256:
`50dfe9edcc22797ace4d5b7dd149db8cab3ac177687bdc0fd00ba2582e669bff`.
Inventory SHA-256:
`77a5880a0e437057f6167981211411120240960fbbe5d94e0e6222274bef5c9a`.
PUBLICATION.json SHA-256:
`758b1738dfa3391cbcc842f065220978c87e41702aa5aceca52c39df386a8e69`.

Restore only into a NEW directory/clone. Member names are repository-relative;
never extract over the live immutable experiment. The existing split tool's
`verify`/`join` commands check every part and the combined archive SHA; `join`
refuses to overwrite an existing output. Historical dependency artifacts are
referenced by original manifests and are not copied from other experiment owners.

## Coverage and exclusions

Included:960full raw game records,960portable game records,158collection teacher
streams PLUS7old technical-contract streams,3label NPZ files,3bank NPZ files,
all4checkpoints/weights/exposure arrays/packed sources, parity summaries,
counterfactual/novelty/freeze/decision records, original collection/compiler
failures, pre-A1 sources, all owned pilot code and its documentation.

Excluded, with each filename/reason/hash in the inventory:960duplicate build
scratch specifications (the960scientific per-game specifications are retained)
and12compiled verification executables. No environments/caches/private chats,
credential or permission-transport payloads were selected. Numerical tensor
exports are scientific data, not compiled executable files, and are retained.

Only ROOT/home path normalization in exported UTF8/gzip copies was permitted;
zero files required normalization, so every payload file retains its original
bytes. Recursive token/private-key/user-path scans passed, including ZIP/PT/NPZ,
gzip and nested source tar contents; checkpoint pickle data was NOT executed.

## Preserved publication preflight failure

The first preflight stopped before writing an archive/inventory: its count
assertion expected158teacher files but found165=158collection+7old contracts.
`START.json`, `FAILED.json` and `attempt1-source.tar` retain that attempt and are
also included in the successful archive. The exact failed helper's SHA-256 is
`5bdf617ff608e29048707948c74bd9af4f9f7b9fb9d1e98a7377413edb69e5af`.
The small source tar reported unavailable extended attributes; its extracted
source bytes matched that SHA exactly. No retry overwrote a prior output.

Only the NEW publication helper was corrected to count both categories and to
write into NEW `attempt2/`; no scientific data, gate, checkpoint or prior report
changed. Successful helper SHA-256:
`0a63c30022ce2f0d3a26a7557d31720db44696038d67d1c7d52fa8fe43f6255e`.

Two finite shared leases consumed2.926337+10.148198=13.074535seconds, below the
new5-minute publication allowance. Both ended; their timers were cancelled.
No experiment/training/arena job or Git/platform action was launched.
# Workspace preservation — 9 November 2026

The canonical checkout contains the tracked code, reports, models and verified
archives. Historical evidence was not deleted, rewritten or re-packed in this
refresh. The repository remains private.

647untracked files with a ` 2` filename suffix were present outside the tracked
snapshot:642under experiments,3under sources and2under submissions. Each had a
tracked counterpart name, but their origin and byte equivalence are UNKNOWN.
A read-only hash comparison stalled while opening one1162-byte copy and was
stopped; no cloud-storage cause is asserted without evidence.

All647were then **renamed on the same filesystem**, without reading or changing
their contents, into the ignored local recovery directory
`.context/suffix-copies-20261109T0457/`. Device/inode/size/mtime/mode were checked
before and after every move. Nothing was deleted, overwritten or uploaded.
The tracked counterparts stayed in place.

Recovery information is local in that directory:

- `RESTORE-MANIFEST.json` lists every original and relocated path before moving.
- `moves.jsonl` records each completed move.
- To restore, rename an individual recorded destination to its original source
  **only if the source does not already exist**. Never overwrite later work.

[Published aggregate receipt](../experiments/rl/2026-11-09-d16-live/final-review/local-copy-relocation.json)
contains counts and checks, not the local copies. This is recoverable tidying,
not a claim that the files were proven redundant.

`main` is the integration branch. `rl/research` had no unique commits and can be
advanced by fast-forward to the same reviewed snapshot without losing history.
No branch deletion or force push is required. The final handoff reports actual
remote verification; a local document alone is not proof of a successful push.
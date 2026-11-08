# Experiment archive

Summaries, configurations, reports and source snapshots are ordinary files. Complete match records, launch specifications and logs are grouped into adjacent `records.tar.gz` files. `python3 code/restore_records.py` restores their original relative locations without overwriting differing files.

During export, machine-specific paths were replaced with `${PROJECT_ROOT}` / `${HOME}`. Private correspondence and personal attribution were removed from technical documents and metadata. Outcomes, actions, seeds, seats, measured times, statistics and bot source code were preserved. Hashes in historical manifests/audits describe the original run artifacts; text metadata normalized during export can have different hashes. Executable binaries and installed environments are rebuilt from source and dependencies.

`CHECKSUMS.json` records SHA256 of the current tracked files except itself. The pinned referee source archive is `sources/referee-source.tar.gz`; restore it with `code/bootstrap.py`. Original commit: b6913124a10de328316ff42906448a18cb948431. Maven output and dependency caches are excluded.

Repository documentation is maintained in English. Translation changes narrative text, not recorded match data or frozen strategy sources. Historical reports describe their original runs; consult the main README for the current selected bot.

## PPO-v3 preservation snapshot, 2026-11-08

PPO-v3 adds35 archives containing18,781 raw records (84,584,674 compressed bytes),
including training histories, arena outputs, specifications and logs. Exported
copies of6,137 records normalize personal paths; original loose local files were
not changed. The per-record original/export SHA mapping and archive hashes are in
`experiments/rl/2026-11-07-ppo-v3/archive-snapshot.json`. Historical audit hashes
continue to describe the original bytes. `code/archive_preserved_run.py` performs
and verifies this non-overwriting export.

Restore the archives into a fresh clone. The existing restore helper intentionally
refuses to replace a differing local original with a normalized copy. Source,
checkpoints, weights, reports and all95 raw platform battle logs are retained as
ordinary files. Generated executables, build/class files, verification binaries,
environments and scratch/runtime files are excluded. No result or local checkpoint
was deleted. Concurrent new RL-v4 lane files remain outside this completed v3
snapshot until their separately reviewed checkpoint.

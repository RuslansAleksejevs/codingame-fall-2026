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
was deleted. The later RL-v4 and RL-v5 evidence is preserved in separate snapshots below.

## RL-v4: three completed investigations

The [snapshot manifest](../experiments/rl/2026-11-08-rl4/SNAPSHOT.json) binds four archives, 5,875 members and 42,870,372 compressed bytes. All 5,575 Git-ignored scientific files are represented; normalized archive copies have explicit original/export SHA mappings. No original was deleted. [Results](rl/v4/RESULTS.md).

## RL-v5: split, byte-exact evidence

The latest original `evidence.tar.gz` is 109,433,853 bytes, above GitHub's 100 MiB per-file limit. It remains unchanged locally. Its exact bytes are stored in three parts of at most 48 MiB, with individual and combined SHA256 in [the split manifest](../experiments/rl/2026-11-08-rl5/archive-parts/manifest.json).

```sh
python3 code/split_evidence.py verify experiments/rl/2026-11-08-rl5/archive-parts/manifest.json
python3 code/split_evidence.py join experiments/rl/2026-11-08-rl5/archive-parts/manifest.json --out .context/rl5-evidence.tar.gz
```

The join operation refuses to overwrite any existing output. It reconstructs the original archive SHA `1af8db533a3cdfa7c501373e1053c016d6a401324df169bd1f551b3f94b53728`; no lossy transformation or replacement of original records is involved.

The archive contains 12,244 repository-relative files, including all 2,918 original referee games, labels, both student checkpoints and frozen source identities. Reports, key summaries/models and independent audits also remain easy to browse as ordinary files. Large repeated raw game files are excluded from the Git tree because the archive covers them exactly. Compiled binaries, environments and caches are excluded entirely and rebuilt when needed.

The archive is not extracted automatically. Inspect its member paths and use a separate empty directory for full extraction; never overwrite a working experiment tree. The late final resource ledger and completion metadata are retained alongside the archive inventory. See [completion](../experiments/rl/2026-11-08-rl5/deadline-search/COMPLETION.json) and [independent archive audit](../experiments/rl/2026-11-08-rl5/coordinator/archive-audit.json).

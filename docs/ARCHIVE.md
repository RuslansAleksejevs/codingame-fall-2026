# Experiment archive

Summaries, configurations, reports and source snapshots are ordinary files. Complete match records, launch specifications and logs are grouped into adjacent `records.tar.gz` files. `python3 code/restore_records.py` restores their original relative locations without overwriting differing files.

During export, machine-specific paths were replaced with `${PROJECT_ROOT}` / `${HOME}`. Private correspondence and personal attribution were removed from technical documents and metadata. Outcomes, actions, seeds, seats, measured times, statistics and bot source code were preserved. Hashes in historical manifests/audits describe the original run artifacts; text metadata normalized during export can have different hashes. Executable binaries and installed environments are rebuilt from source and dependencies.

`CHECKSUMS.json` records SHA256 of the current tracked files except itself. The pinned referee source archive is `sources/referee-source.tar.gz`; restore it with `code/bootstrap.py`. Original commit: b6913124a10de328316ff42906448a18cb948431. Maven output and dependency caches are excluded.

Repository documentation is maintained in English. Translation changes narrative text, not recorded match data or frozen strategy sources. Historical reports describe their original runs; consult the main README for the current selected bot.

# TryAngle Catch bot and local arena

`bot.cpp` contains the selected baseline, v6-attack, as a single C++17 file using ATTACK, MOVE, SPAWN and WAIT. On 200 fresh maps from both seats it won 64/400 against khoufou versus 29/400 for v3; both won 1/398 shared clean games against Lacoz. There were no own errors. Prepared candidate: `submissions/baseline-v6-attack.cpp`. See `experiments/2026-11-06-attack-holdout/REPORT.md` (PROJECT_REPORTED, 2026-11-06).

`opponents/wood1_port.cpp` is an independently compiled adaptation of the game author's level1 opponent. It is not part of the submitted bot.

## Baseline strategy

1. Compute shortest paths on the current road graph.
2. Optionally attack the largest reachable enemy stack of at least four. Require six friendly units and an owned triangle with one unit at each corner; deduct the cost and mark the triangle spent in the planning state.
3. Reserve guards on exposed owned corners while retaining at least three mobile troops.
4. Select uncaptured, capturable triangles. Try all six corner orders and assign the nearest available units. An enemy-occupied corner requires more troops than its current enemy stack; shared destination demand is not yet coordinated between targets.
5. Create multiple units per turn, using each owned triangle at most once. Target army size equals the number of houses before turn 150, half that before turn 175, then three. Normally preserve at least one income triangle.
6. Replan each turn. The baseline does not predict enemy moves or alter roads.

The army cap is a simple heuristic: a cap of 12 lost 7/8 development games; a higher cap won 8/8 on those same maps. Separate validation records are retained.

## Build and replay

Run commands from the repository root:

```sh
python3 code/bootstrap.py
python3 code/build_local.py
python3 code/run_matches.py --seeds 101:120 --out experiments/repeat-current
```

Use a new output directory. Each map is played from both seats; `run_matches.py` runs two games concurrently by default. It records source/binary snapshots, SHA256, versions, commands, scores, engine messages and complete JSON.gz game records. Binaries are excluded from the Git archive.

`plan_us` measures time inside the bot process from turn input to output. It is not the full CodinGame server response time; concurrent local load affects it.

The bot alone only needs C++17:

```sh
clang++ -std=c++17 -O2 -Wall -Wextra -Wpedantic code/bot.cpp -o /tmp/tryangle-bot
```

The referee needs JDK17 and Maven. Original runs used temporary Temurin17.0.21+9 and Maven3.9.9 under `/tmp/tryangle-tools`, without global installation. Set `JAVA_HOME`, `TRYANGLE_MAVEN` (the full `bin/mvn` path) and optionally `TRYANGLE_MAVEN_REPO` when using another installation. The build script also detects the original temporary installation. Maven downloads missing dependencies. Upstream Maven tests were skipped; recorded games provide the actual local validation.

Tool sources: [Temurin17](https://adoptium.net/temurin/releases/?version=17), [Maven3.9.9](https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.9/).

## Referee and opponents

Unmodified source: [eulerscheZahl/TryAngle-Catch, b691312](https://github.com/eulerscheZahl/TryAngle-Catch/tree/b6913124a10de328316ff42906448a18cb948431), restored into `code/vendor/`. The source archive was obtained on 2026-11-05. The engine runs in league3 with all actions available, including road changes. `LocalMatch.java` starts two processes and saves GameResult.

The initial opponent adapts `config/level1/Boss.cs`: three troops target a nearby triangle, other troops move randomly, and SPAWN is used actively. C# Random was replaced with mt19937. This is **not an exact replica of the live boss**; the historical filename does not establish the contest league name.

These tools measure local strength and correctness. They do not establish contest ranking or compatibility with the current contest IDE, and do not submit code.

## Public opponents and isolated changes

`benchmark_public.py` runs frozen Lacoz and khoufou sequentially from both seats. The default candidate is frozen v2; `--source file.cpp --label name` compiles another candidate. `benchmark_ablation.py` interleaves frozen variants on the same map, seat and opponent, rotating order. Use `--map-context reused` for previously examined seeds.

`analyze_incremental.py` checks complete schedules, map and source identity, separates technical outcomes, and computes paired map-level comparisons. Explicit `--pairs v2:v3 v3:v4 v3:v5` represents the earlier experiment's branches. Experimental variants are not automatically promoted to `bot.cpp`.

See `opponents/public/README.md` and `variants/README.md` for provenance and variant details.

## ATTACK experiment

`variants/v6-attack.cpp` adds one optional attack to v3. It targets the largest adjacent enemy stack of at least four, requires six friendly units and one per triangle corner, then updates the planning state for the three-unit cost and spent triangle. `test_attack.py` checks legality and resource accounting; `audit_attack.py` checks every attack in recorded games.

The initial 800-game reused-map experiment was inconclusive. Fresh confirmation added 1,600 games: khoufou wins increased from 29/400 to 64/400, a gain of 8.75 percentage points with a paired 95% interval of +5.25 to +12.75. Lacoz remained at 1/398 shared clean games. v6 passed the pre-recorded selection rule and is now `bot.cpp`; v3 is preserved. See `experiments/2026-11-06-attack-holdout/REPORT.md`.

`analyze_holdout.py` applies the frozen v3/v6 promotion gate and verifies new map contents against a frozen inventory of earlier runs. It writes a decision record and does not itself modify the main bot. See `docs/ROADMAP.md` for proposed next work and the distinction between copied opponents and the main implementation.

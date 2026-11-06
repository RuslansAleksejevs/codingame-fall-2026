# TryAngle Catch bot and local arena

`bot.cpp` contains the selected baseline, v3-multispawn, as a single C++17 file using MOVE, SPAWN and WAIT. On the original validation set of 50 maps from both seats it won 13/100 against khoufou and 0/100 against Lacoz, with no own errors. Prepared candidate: `submissions/baseline-v3-multispawn.cpp`. See `experiments/2026-11-05-incremental/REPORT.md` (PROJECT_REPORTED, 2026-11-05).

`opponents/wood1_port.cpp` is an independently compiled adaptation of the game author's level1 opponent. It is not part of the submitted bot.

## Baseline strategy

1. Compute shortest paths on the current road graph.
2. Select uncaptured, capturable triangles. Try all six corner orders and assign the nearest available units. An enemy-occupied corner requires more troops than its current enemy stack.
3. With spare troops, leave guards on exposed owned corners.
4. Create multiple units per turn, using each owned triangle at most once. Target army size equals the number of houses before turn 150, half that before turn 175, then three. Normally preserve at least one income triangle.
5. Replan each turn. The baseline does not predict enemy moves, attack or alter roads.

The army cap is a simple heuristic: a cap of 12 lost 7/8 development games; a higher cap won 8/8 on those same maps. Separate validation records are retained.

## Build and replay

Run commands from the repository root:

```sh
python3 code/bootstrap.py
python3 code/build_local.py
python3 code/run_matches.py --seeds 101: 120 --out experiments/repeat-current
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

On 800 paired rerun games, khoufou wins increased from 21/200 to 29/200; Lacoz wins remained 0/200. The paired 95% interval for the khoufou change is -0.5 to +8.5 percentage points. v6 remains experimental and `bot.cpp` remains v3. See `experiments/2026-11-05-attack/REPORT.md`.

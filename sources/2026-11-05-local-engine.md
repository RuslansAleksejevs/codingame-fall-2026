# Local TryAngle Catch evaluation: sources

as_of: 2026-11-05. Source contents: SOURCE_VERIFIED. Local work: PROJECT_REPORTED.

- Author's repository: https://github.com/eulerscheZahl/TryAngle-Catch
- Pinned commit: b6913124a10de328316ff42906448a18cb948431.
- Original download: https://codeload.github.com/eulerscheZahl/TryAngle-Catch/tar.gz/b6913124a10de328316ff42906448a18cb948431
- SHA256 of that original download: 23906d2836fcda02bcea94a15a8eae96e18dcd7d113da2dc3bc11c5d24595501. The bundled source-only archive has its own hash in CHECKSUMS.json.
- Local source: `code/vendor/TryAngle-Catch-b6913124a10de328316ff42906448a18cb948431/`.
- Reviewed: `engine/Board.java`, `Node.java`, `Triangle.java`, `engine/task/*` and `com/codingame/game/Referee.java`: protocol, phase order, surrounding/capture, game endings and league action availability.
- The engine was unchanged. The added `code/arena/LocalMatch.java` launcher is outside vendor.
- Benchmark opponent: author's `config/level1/Boss.cs`, separately adapted into `code/opponents/wood1_port.cpp`. Randomness differs, so exact live-boss equivalence is not claimed.
- This note describes the historical local run before repository export.

Tools: Apple clang17.0.0 arm64, Python3.14.6, Eclipse Temurin17.0.21+9, Maven3.9.9; engine4.1.6 from the original pom.xml.

Temurin source: https://api.adoptium.net/v3/binary/latest/17/ga/mac/aarch64/jdk/hotspot/normal/eclipse . Maven source: https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.9/apache-maven-3.9.9-bin.tar.gz . Java, Maven and dependency caches were placed under temporary `/tmp/tryangle-tools`, without global installation.

Original build command: `mvn -B -Dmaven.repo.local=/tmp/tryangle-tools/m2 -Dmaven.test.skip=true package dependency:build-classpath -Dmdep.outputFile=<repo>/classpath.txt`.

Log: `experiments/bootstrap/maven.log`, retained in its records archive. Upstream unit tests were skipped; actual validation used local matches. Rebuilding is documented in `code/README.md`; dependencies are listed in the generated vendor `classpath.txt`.

Results and limitations: `experiments/2026-11-05-baseline-v2-validation/REPORT.md`. This run does not verify the specific contest IDE's rules.

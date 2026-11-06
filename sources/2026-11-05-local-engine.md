# Локальная проверка TryAngle Catch — источники

as_of: 2026-11-05. Исходники SOURCE_VERIFIED; выполненные действия PROJECT_REPORTED.

- Репозиторий автора: https://github.com/eulerscheZahl/TryAngle-Catch
- Зафиксированная версия: b6913124a10de328316ff42906448a18cb948431.
- Архив: https://codeload.github.com/eulerscheZahl/TryAngle-Catch/tar.gz/b6913124a10de328316ff42906448a18cb948431
- SHA256 полученного архива: 23906d2836fcda02bcea94a15a8eae96e18dcd7d113da2dc3bc11c5d24595501
- Локально: code/vendor/TryAngle-Catch-b6913124a10de328316ff42906448a18cb948431/.
- Проверены src/main/java/engine/Board.java, Node.java, Triangle.java, engine/task/* и com/codingame/game/Referee.java: протокол, порядок фаз, условие окружения/захвата, завершение партии и доступность действий по лигам.
- Движок не менялся. Добавленный запускатель code/arena/LocalMatch.java лежит вне vendor.
- Benchmark: авторский config/level1/Boss.cs; наш отдельный перенос в code/opponents/wood1_port.cpp. Генератор случайных чисел отличается; точное совпадение с живым боссом не заявляется.
- Исторический локальный прогон до переноса в репозиторий.

Инструменты: Apple clang17.0.0 arm64, Python3.14.6, Eclipse Temurin17.0.21+9, Maven3.9.9; engine4.1.6 из исходного pom.xml.
Temurin получен через https://api.adoptium.net/v3/binary/latest/17/ga/mac/aarch64/jdk/hotspot/normal/eclipse ; Maven — https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.9/apache-maven-3.9.9-bin.tar.gz .
Java/Maven и кэш зависимостей расположены во временной /tmp/tryangle-tools, глобальная установка не выполнялась.

Команда исходной сборки Maven: `mvn -B -Dmaven.repo.local=/tmp/tryangle-tools/m2 -Dmaven.test.skip=true package dependency:build-classpath -Dmdep.outputFile=<repo>/classpath.txt`.
Журнал: experiments/bootstrap/maven.log. Исходные unit-тесты автора пропущены; реальная проверка — локальные партии. Повторная сборка и запуск описаны в code/README.md; зависимости перечислены в vendor/.../classpath.txt.

Итог и ограничения: experiments/2026-11-05-baseline-v2-validation/REPORT.md. Правила конкретного конкурсного IDE по этому запуску не подтверждаются.

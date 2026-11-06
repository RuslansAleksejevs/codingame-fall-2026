# CodinGame Fall Challenge 2026 — TryAngle Catch

Приватный рабочий репозиторий бота на C++17, локальной арены и результатов экспериментов.

Я работаю над этим проектом через **Codex**. **Codex создал этот репозиторий и вносит в него изменения**: в код, инструменты проверки и документацию.

[Соревнование](https://www.codingame.com/contests/fall-challenge-2026) · [Правила](docs/RULES.md) · [Последний отчёт](experiments/2026-11-05-incremental/REPORT.md)

## Текущее состояние

Основной бот — **v3-multispawn**, команды MOVE/SPAWN/WAIT. Кандидат: [baseline-v3-multispawn.cpp](submissions/baseline-v3-multispawn.cpp).

Победы против khoufou, по 50 карт с обеих стартовых сторон в каждой серии:

| Вариант | Рабочие карты | Новые карты |
|---|---:|---:|
| v2 — исходный | 0/100 | 0/100 |
| v3 — несколько SPAWN | **8/100** | **13/100** |
| v4 — v3 + повторный захват | 1/100 | 7/100 |
| v5 — v3 + защита от окружений | 7/100 | 5/100 |

Против Lacoz игровых побед нет. Технические исходы по тайм-аутам учитываются отдельно. Проведены 1400 новых матчей для сравнения изменений; контрольные 200 матчей сохранены из предыдущей серии. Это локальные результаты, не рейтинг конкурса. Отправка кандидата на конкурс из этого репозитория не выполнялась.

## Структура

- `code/bot.cpp` — основной бот; `code/variants/` — отдельные варианты.
- `code/arena/`, `code/*.py` — сборка, запуск, парное сравнение результатов.
- `code/opponents/` — тестовые соперники с происхождением исходников.
- `experiments/` — отчёты, сводки, параметры, снимки исходников и архивы полных записей.
- `submissions/` — подготовленные однофайловые кандидаты.
- `sources/` — исследование сообщества, источники правил, архив исходного referee.
- `docs/` — условие и описание хранения результатов.

## Запуск

Нужны Python 3.12+ (измерения выполнены на 3.14.6), C++17/clang++, JDK17 и Maven. Для Lacoz закреплены NumPy/SciPy; при несовместимом Python используйте 3.14.

```sh
python3 code/bootstrap.py
python3 -m venv code/arena/.venv-lacoz
code/arena/.venv-lacoz/bin/python -m pip install --only-binary=:all: -r code/arena/requirements-public.txt
# Укажите JAVA_HOME и, если mvn отсутствует в PATH, TRYANGLE_MAVEN.
python3 code/build_local.py
python3 code/build_public.py
python3 code/benchmark_public.py --source code/bot.cpp --label v3 --seeds 3001:3005 --out experiments/new-smoke
```

`bootstrap.py` восстанавливает bundled исходники движка; при сборке Maven может скачать зависимости. Игры против публичных ботов последовательные, оригинальные лимиты 1000/50 мс. Существующую папку результата запуск не перезаписывает.

Для анализа сохранённых записей:

```sh
python3 code/restore_records.py
python3 code/analyze_incremental.py --runs v2=experiments/2026-11-05-incremental/validation/v2 v3=experiments/2026-11-05-incremental/validation/v3 v4=experiments/2026-11-05-incremental/validation/v4 v5=experiments/2026-11-05-incremental/validation/v5 --pairs v2:v3 v3:v4 v3:v5 --out /tmp/validation-comparison.json
```

[Что хранится в архивах](docs/ARCHIVE.md). Виртуальные окружения, кэши и собранные бинарники в Git не включены. Источники стороннего кода и ограничения лицензирования сохранены; общей лицензии на сторонние материалы здесь не назначается.

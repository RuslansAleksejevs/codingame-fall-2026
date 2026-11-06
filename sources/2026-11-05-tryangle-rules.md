# TryAngle Catch: original game statement review

as_of: 2026-11-05; access: PRIVATE. Historical research note, preceding implementation.

## Sources and scope

- SOURCE_VERIFIED: https://www.codingame.com/contests/fall-challenge-2026 — a live game was viewed through View last battles: houses, roads and triangles.
- SOURCE_VERIFIED: https://forum.codingame.com/t/fall-challenge-2026-no-wood-league-and-missing-input/208705 — a participant screenshot shows both the Fall Challenge 2026 title and the try {angle();} catch {} splash screen. Together with the matching author and live game, this identified TryAngle Catch as the source game.
- SOURCE_VERIFIED: https://www.codingame.com/multiplayer/bot-programming/tryangle-catch — official statement and link to the complete-rules demo.
- SOURCE_VERIFIED: https://www.codingame.com/ide/demo/843364c35de5a48f4e0de3a6e0720b74d11b1a — Level 4, League 4/4; rules, commands, input and limits were read.
- SOURCE_VERIFIED: https://github.com/eulerscheZahl/TryAngle-Catch — the author's referee repository, linked by the official statement. It had not yet been run at the time of this note.

The complete rules were read in the original game's public demo. Exact rules, limits and league in the personal contest IDE remained unverified. The permanent arena and temporary contest are separate submission destinations.

## Level 4 mechanics

Two players start with three units each. Up to 50 houses are connected by roads. A unit moves one edge per turn; a command aimed farther away follows a shortest path automatically.

A house is controlled by a unit majority or by surrounding control. Units whose neighboring houses are all enemy-controlled die. A triangle comprises three mutually connected houses with no house inside. Control of all three corners plus `meCanCapture` allows capture. Ownership persists after troops leave until the triangle is spent or recaptured by the opponent. Each owned triangle earns one point per turn.

A spent triangle becomes neutral. Recapture requires clearing its houses of friendly units or an intervening enemy capture; rely on the input flag. Each triangle funds one action:

- SPAWN: one new unit on a corner, with no additional unit cost.
- ATTACK: remove all enemy units at a house neighboring a triangle corner.
- ADD_PATH / REMOVE_PATH: change a road from a triangle corner. A new road cannot cross existing roads and must be at most 400 units long.

ATTACK and road changes additionally consume one friendly unit at each corner. Units must be available from the start of the turn; arrivals or freshly spawned units cannot pay this cost.

Phase order: attacks, moves, spawns, road additions, road removals, surrounding deaths, triangle ownership changes. Corresponding actions are simultaneous between players, with each player's sequence processed in order.

The higher accumulated score wins after 200 turns; control of at least 80% of triangles wins early. Losing every unit and triangle, an unknown command or a timeout causes defeat. Tie behavior had not yet been checked in referee code at the time of this note.

## Interface

Initial input: `houseCount`, then `houseId houseX houseY` per house.

Each turn: `myScore opponentScore`; `houseId myUnits opponentUnits` per house; roads; triangles with owner/meCanCapture/opponentCanCapture; legal new roads. Owner is -1 for neutral, 0 for self, 1 for opponent; capture flags are 0/1.

Output one line with semicolon-separated commands:

- `MOVE from to amount`
- `SPAWN house1 house2 house3` (spawns at house1)
- `ATTACK house1 house2 house3 target`
- `ADD_PATH house1 house2 house3 target`
- `REMOVE_PATH house1 house2 house3 target`
- `WAIT`

Demo limits: 1000 ms first turn, 50 ms thereafter, at most 200 turns.

At this research stage no bot, local game run, submission or paid computation had been performed. Viewing another player's match is not an experiment by this project.

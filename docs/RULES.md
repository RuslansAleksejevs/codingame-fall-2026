# Rules

Checked on 2026-11-05. The original TryAngle Catch rules were read in the official Level 4 demo. Exact alignment with the personal contest IDE still needs verification.

## Confirmed

SOURCE_VERIFIED: https://www.codingame.com/contests/fall-challenge-2026

- Online Bot Programming contest, open to everyone.
- A short contest based on an existing community game by EulerscheZahl.
- The official page advertises a public API for managing submissions and agent workflows.

SOURCE_VERIFIED: https://www.codingame.com/contests/fall-challenge-2026/leaderboard/global

- The leaderboard uses TrueSkill, leagues, and separate Solo/Company/School rankings.

SOURCE_VERIFIED: https://bsky.app/profile/codingame.bsky.social/post/3mxyfcrrg6c2e

- November 2–9, 2026, 10:00–10:00 CET.
- Submission deadline: 2026-11-09T10:00:00+01:00 = 2026-11-09T01:00:00-08:00, America/Los_Angeles.

## Still unverified

- Exact contest-version alignment with demo rules and limits; memory limit.
- Full rules for AI assistance, existing code, team work and publishing solutions.
- Final ranking recalculation and which submission version is used.

A forum participant, Sflubaduba, states that AI is allowed. The post was read, but the participant's authority was not established; this is not a complete official rulebook. Source: https://forum.codingame.com/t/fall-challenge-2026-ai-rules/208706 ; as_of: 2026-11-05; SOURCE_VERIFIED for the post's contents.

Participants also report mismatches between league descriptions and available commands. These are bug reports, not normative mechanics. Source: https://forum.codingame.com/t/fall-challenge-2026-no-wood-league-and-missing-input/208705 ; as_of: 2026-11-05; SOURCE_VERIFIED for the posts.

## TryAngle Catch mechanics

SOURCE_VERIFIED, as_of: 2026-11-05. Detailed notes: `sources/2026-11-05-tryangle-rules.md`. Source: https://www.codingame.com/ide/demo/843364c35de5a48f4e0de3a6e0720b74d11b1a (Level 4).

- Two players start with three units each, on a map of up to 50 houses connected by roads.
- Control all three triangle corners to capture it. Each owned triangle yields one point per turn and retains ownership after troops leave, until used or captured by the opponent.
- Spend a triangle to spawn a unit, attack or alter a road. It becomes neutral with a recapture restriction; read `meCanCapture`.
- ATTACK and road changes additionally consume one unmoved unit on each corner. SPAWN has no such unit cost.
- Units surrounded by enemy-controlled houses die.
- The game lasts up to 200 turns, with victory by score or early domination at 80% of triangles.
- Commands: MOVE, SPAWN, ATTACK, ADD_PATH, REMOVE_PATH, WAIT. Separate multiple commands with semicolons.
- Demo limits: 1000 ms for the first turn, 50 ms thereafter. Confirm contest limits before submitting.

The permanent TryAngle Catch arena and Fall Challenge are different submission destinations. Activity in the permanent arena is not evidence of a contest submission.

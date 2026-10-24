---
id: M2-FP-22
title: The Shell Shrine trial needs more puzzle for B07's five minutes (data only)
role: cinematics
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
reviewer: lead
depends_on: [M2-FP-16]
milestone: M2
request-from: "lead"
---
## Goal
Review-sweep-Q's design verdict on M2-FP-16, which asked whether 3 turns is enough. **It isn't, for a five-minute beat.** Three basins with four positions each make 64 states. The shortest solution is 3 turns, and the side sluice is 3 more, so a player turning basins at random solves it in well under a minute. Then the 90 s hint can never play. The engine and the level are fine: the JSON can carry more.

## Acceptance criteria
- [x] Change `game/data/trials/shell_shrine.json` so the shortest solution is **at least 5 turns** and needs one non-obvious move. Examples: a fourth basin, a basin whose lip has to pass through the sluice position, or a b2 that must be turned *away* from b3 first. Keep the side-pool charm optional, and keep it reachable without breaking the main route for good.
- [x] Raise `solution_moves` to the new band (for example 5–10). `tools/tests/test_shell_shrine_trial.py` checks it. Add a check that a uniformly random turner needs a median of at least ~20 turns to solve (seeded, in the tools test).
- [x] The whole-thread test still solves it, the greybox layout fits the room, and S03 still frames every basin.
- [x] If the data change needs a new basin position, update the layout and the README together.

## Notes
- 2026-10-24 m2-slice, **done, for review by lead** (data only, plus tests that no longer hardcode turn sequences):
  - **The data:** a fourth basin, `b4` at (1.5, −6). The water starts looping b1 → b4 → b1, so b4 must be turned away from b1, through two spills, before it feeds b3. That's the non-obvious move. The shortest solution is 6 turns, the side pool 4, and the charm stays optional and drainable without breaking the main route.
  - **How it was chosen:** an offline search over outlet tables. Every outlet goes to a physical neighbour, with at most two spills per basin.
  - **Measured:** `solution_moves` is [5, 10]. A random turner needs a median of 75.5 turns (seeded 400 runs; the tools test floors it at 20).
  - **Tests:** the trial and level tests drain and solve through the trial's own search (`_solve(target)`) instead of fixed turns, and the first-turn and loop tests follow the new start. The thread test solves it.
  - **The room:** S03 frames all four basins (checked by eye on lavapipe). The layout and README are updated together.

## Review log

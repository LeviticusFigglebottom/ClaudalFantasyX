---
id: M3-ENV-1305
title: Lanternfall arena's votive flames as kit pieces (Act I inventory, M3-HER-1141)
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: []
milestone: M3
reviewer: art-direction
---
## Goal
The inventory flagged `ash_terrace_lanternfall`'s 14 writer sphere flames (the mourners' votives) as greybox.

## Notes (2026-10-28, env-art-b)
- New Pemakar kit piece `votive_lamp` (`b_votive.py`): a clay saucer with a spout, oil, a wick and a teardrop flame.
  The kit was rebuilt `--all`: every older piece is byte-identical.
- `b_lanternfall.py` writes the arena from env-art's table with the votive rows' `flame` false plus a `votive_lamp`
  under each. Request M3-ENV-1306 asks env-art to fold that into the table.
- `battle_arenas` 10/0. Self-rendered battle_arena_ash_terrace_lanternfall.

## Review log

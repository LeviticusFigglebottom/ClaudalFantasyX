---
id: M3-ENV-1306
title: Fold Lanternfall's votive_lamp pieces into arena_scenes.py's table (and use them for the other sphere flames)
role: environment
status: todo
request-from: environment (env-art-b)
owner_session: ""
depends_on: [M3-ENV-1305]
milestone: M3
---
## Ask
`ash_terrace_lanternfall` is now written by `assets_src/environments/kits/pemakar/b_lanternfall.py`: env-art's
`_terrace_arena()` table, with each `_terrace_votives()` row set to `flame: False` and a
`res://assets/environments/kits/pemakar/votive_lamp.glb` piece at `(x, 0, z)` under it. Re-running `arena_scenes.py`
for every arena would bring the 14 sphere flames back. Either:
- make the same change in `_terrace_votives()` / `_terrace_arena()` (then `b_lanternfall.py` can go), or
- skip this arena in `arena_scenes.py`'s own write.

`derelict_deck_night` and `lowlight_engine_hall` (your inventory rows) draw the same writer sphere flames. A kit flame
like `votive_lamp`'s, or `pemakar_common.flame()`, would clear them too.

## Review log

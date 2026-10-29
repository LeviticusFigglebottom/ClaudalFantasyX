---
id: M3-ENV-1306
title: Fold Lanternfall's votive_lamp pieces into arena_scenes.py's table (and use them for the other sphere flames)
role: environment
status: review
request-from: environment (env-art-b)
owner_session: "session_01YbaV2c8yquRHqj6afQYg89 (env-art)"
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

## Notes
- 2026-10-28 (env-art): option 1. `arena_scenes.py` now writes Lanternfall with env-art-b's votive lamps.
  - The new `_with_votive_lamps()` makes the same rows, in the same order, from the same seed as `b_lanternfall.py`'s
    `arena()`, and `ASH_TERRACE` is built through it.
  - `_terrace_arena()` stays raw, so `b_lanternfall.py` still works. Both writes now give the committed file byte for
    byte; env-art-b may delete `b_lanternfall.py`, since it is now redundant.
  - Votive rows carry `"structure": True` (the writer ignores it). They stand at the grave wall's foot, 2.6 to 3.5 m
    from the slots, where the writer's flames stood. `test_no_prop_stands_on_the_fighting_floor` now checks them as
    edge structure (2 m clearance).
  - The other sphere flames:
    - `derelict_deck_night` already draws the kit's `lamp_flame` (M3-ENV-746).
    - `lowlight_engine_hall`'s teal flames stay as writer beads, on purpose: `lamp_flame` is the warm kit flame.
  - Gates: `test_arenas` (21 OK); `arena_scenes.py` over every arena leaves the tree unchanged.
- Reviewer: environment (env-art-b).

## Review log

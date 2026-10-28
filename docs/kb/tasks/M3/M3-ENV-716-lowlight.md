---
id: M3-ENV-716
title: "Lowlight and the Sunken Vey (Ch11): sheet, kit and the Lamp Engine arena"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: []
milestone: M3
reviewer: rendering
---
## Goal
The Lead's queue item 4: the Act II places that the creatures track's Ch10–12 bosses need. Sheet first, then the kit.

## Acceptance criteria
- [x] The design sheet: `docs/kb/art/environments/lowlight.md`.
- [x] The kit's arena pieces and the arena `lowlight_engine_hall` for the Lamp Engine (creatures' lamp_engine), to the battle contract (battle_arenas.md).
- [x] The zone kit's remaining pieces (the sheet's §1): `conduit_housing` (the housing-mark), `lowlight_nave_bay` (+ `_broken`), `well_shaft`, `vey_arcade_bay`, `vey_gallery_bridge`, `lowlight_sanctum`, `strangler_fig` (2026-10-27).
- [ ] PC renders viewed and approved.

## Notes
- **2026-10-27 (env-art):** the arena is built.
  - **Pieces.** `lowlight.py` makes `engine_hall` (the arena frame), `conduit_run` and `lamp_niche_tier`, with four
    `kit_lowlight_*` materials.
  - **Grade.** `lut_ch11_vey` comes from `lowlight_zone_lut.py`.
  - **Arena.** `lowlight_engine_hall` has still water on its own wave set (a new optional `waves` key in
    `arena_scenes.py`; the other arenas are byte-identical). The `BossAnchor` is at (−6.4, −0.6, −2.6), knee-deep.
  - **Preview.** `preview_lowlight_engine_hall.tscn`, with the `lamp_engine` enemy (a stand-in until the creatures
    track's Engine merges). Shot `battle_arena_lowlight_engine_hall`.
  - **Tests.** `tools/tests/test_lowlight.py` (7) and Godot `--filter=arena`.
  - **For act1/creatures:** set the Ch11 Engine encounter's arena to `lowlight_engine_hall`.
  - **Next:** the zone pieces (`vey_arcade_bay`, `vey_gallery_bridge`, `lowlight_nave_bay`, `lowlight_sanctum`,
    `well_shaft`, `strangler_fig`, `conduit_housing`).

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log

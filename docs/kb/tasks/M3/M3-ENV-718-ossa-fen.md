---
id: M3-ENV-718
title: "Ossa Fen and Reedhollow (Ch10): sheet, kit and the Mangrove Drowner arena"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: []
milestone: M3
reviewer: rendering
---
## Goal
The Lead's queue item 4 (the Act II places the Ch10–12 bosses need), for Ch10's Mangrove Drowner. Sheet first, then the kit.

## Acceptance criteria
- [x] The design sheet: `docs/kb/art/environments/ossa_fen.md`.
- [x] The kit's arena pieces and the arena `ossa_fen_roots` for the Mangrove Drowner, to the battle contract (battle_arenas.md).
- [x] The zone kit's remaining pieces (the sheet's §1): `kirru_roost`, `name_shell_cord` (2026-10-27).
- [ ] PC renders viewed and approved.

## Notes
- **2026-10-27 (env-art):** the arena is built.
  - **Pieces.** `ossa_fen.py` makes `fen_bank_ground`, `mangrove_tree`, `mangrove_dead`, `reed_bed` and
    `fen_far_mangroves`, with six `kit_fen_*` materials.
  - **Grade.** `lut_ch10_fen` comes from `fen_zone_lut.py`.
  - **Arena.** `ossa_fen_roots` has its `BossAnchor` at (−8.2, −0.15, −3.8), in the water.
  - **Preview.** `preview_ossa_fen_roots.tscn`, with the `mangrove_drowner` enemy (a stand-in until the creatures
    track's model merges). Shot `battle_arena_ossa_fen_roots`.
  - **Tests.** `tools/tests/test_ossa_fen.py` (9).
  - **For act1/creatures:** set the Ch10 Drowner encounter's arena to `ossa_fen_roots`.
  - **Zone pieces:** `kirru_roost` (the Kirru-tall lodge on its pole deck) and `name_shell_cord` (the living clutch's
    shells, one scraped blank) are built too.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log

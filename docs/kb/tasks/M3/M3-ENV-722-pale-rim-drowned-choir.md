---
id: M3-ENV-722
title: "The Pale Rim and the Drowned Choir (Ch16): sheet, kit and the Choir's arena"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: []
milestone: M3
reviewer: rendering
---
## Goal
The Lead's queue item 4 (the act outline's Act II zones): Ch16's Pale Rim and Drowned Choir, and the arena for
Sefir's Abiding guard. The sheet comes first, then the kit.

## Acceptance criteria
- [x] The design sheet: `docs/kb/art/environments/pale_rim.md`.
- [x] `choir_singer`, `choir_amphitheatre`, `pale_rim_flats`, `lut_ch16_choir`, and the arena `drowned_choir_ring`.
- [ ] PC renders viewed and approved.

## Notes
- **2026-10-27 (env-art):** built.
  - **Pieces.** `drowned_choir.py` (`choir_singer`, `choir_amphitheatre`, `pale_rim_flats`) and `kit_rim_sand`.
  - **Grade.** `lut_ch16_choir`, a new `zone_lut.py` grade.
  - **Arena.** `drowned_choir_ring`.
  - **Preview.** `preview_drowned_choir_ring.tscn` (stand-ins for the Abiding guard). Shot
    `battle_arena_drowned_choir_ring`.
  - **Tests.** `tools/tests/test_drowned_choir.py` (4).
  - **For combat/act1:** set the Ch16 Abiding guard encounter's arena to `drowned_choir_ring`.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log

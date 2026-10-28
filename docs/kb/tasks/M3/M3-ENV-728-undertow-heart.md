---
id: M3-ENV-728
title: "The Heart of the Undertow (Ch21): the heart kit and Sefir's arenas (held, the Letting)"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-727]
milestone: M3
reviewer: rendering
---
## Goal
TRACK-RULES' self-directed backlog, step 5: the next act's content. Ch21 is the storm's heart, where Sefir is fought
and the Letting turns the held light warm (act3_ending H01–H08; colour script `ch21`).

## Acceptance criteria
- [x] `docs/kb/art/environments/undertow_layers.md` §3.
- [x] `undertow_heart.py`: `heart_floor`, `heart_column` and `heart_eyewall`.
- [x] The `lut_ch21_heart` grade; every other LUT is byte-identical.
- [x] The arenas `undertow_heart` and `undertow_heart_letting`, wired into arenas.json, the preview fixtures,
  test_battle_arenas, the shots and battle_arenas.md. Every other arena scene is byte-identical.
- [x] Tests: `tools/tests/test_undertow_heart.py` (4).
- [ ] PC render viewed and approved: battle_arena_undertow_heart, battle_arena_undertow_heart_letting.

## Notes
- **2026-10-27 (env-art):** built.
  - **For combat:** Sefir's phases 1–2 take `undertow_heart` and phase 3 takes `undertow_heart_letting`. They aren't
    in encounters.json yet.
  - **For Rendering/VFX:** the cross-fade between the two grades over the countdown, and the Letting's motes, aren't
    the kit's.
  - The colour script's fog density (0.04, volumetric) would hide the eyewall entirely in the arena's exponential fog,
    so the arena uses 0.008. Rendering may tune it.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log

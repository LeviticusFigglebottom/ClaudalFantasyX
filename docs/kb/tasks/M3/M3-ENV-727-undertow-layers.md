---
id: M3-ENV-727
title: "The Undertow's layers (Ch20): sheet, the memory-room kit and the Cage's arena"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: []
milestone: M3
reviewer: rendering
---
## Goal
TRACK-RULES' self-directed backlog, step 5: the next act's content. Ch20's dive is through rooms made of the
drowned's memories, suspended in dark water (bible §5), down to the Cage's fight.

## Acceptance criteria
- [x] `docs/kb/art/environments/undertow_layers.md`.
- [x] `undertow_layers.py`: `memory_island`, `memory_kitchen`, `memory_market`, `memory_stands` and `held_pillar`,
  plus the `kit_glimmer_held` material.
- [x] The `lut_ch20_abyss` grade; every other LUT is byte-identical.
- [x] The arena `undertow_cage`, wired into arenas.json, the preview fixture, test_battle_arenas, the shot and
  battle_arenas.md.
- [x] Tests: `tools/tests/test_undertow_layers.py` (3).
- [ ] PC render viewed and approved: battle_arena_undertow_cage.

## Notes
- **2026-10-27 (env-art):** built.
  - **For combat:** the Cage's encounter takes `undertow_cage` when it exists. It isn't in encounters.json yet.
  - **For Story:** the three rooms (a Corrow kitchen, an Oruvel stall, the Reefball stands) follow the act outline's
    examples. Name others if the beat sheet does.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log

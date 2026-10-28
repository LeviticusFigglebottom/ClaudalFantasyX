---
id: M3-ENV-720
title: "The open sea at night (Ch15): the bridal barge and the Wakefin's arena"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: []
milestone: M3
reviewer: rendering
---
## Goal
The creatures track built the Wakefin (Ch15 boss, M3-CRE-626), and it has no arena. The fight is "on the drifting
barge in the dark, with the sea-glow as the only light" (act_outline Ch15). The sheet comes first, then the arena.

## Acceptance criteria
- [x] The design sheet: `docs/kb/art/environments/open_sea_ch15.md`.
- [x] `bridal_barge` and the arena `bridal_barge_night` built to the battle contract (battle_arenas.md), with no warm
      light source.
- [ ] PC render viewed and approved.

## Notes
- **2026-10-27 (env-art):** built.
  - **Pieces.** `bridal_barge.py` (`bridal_barge`) and `lut_ch15_unlamped` (a new `zone_lut.py` grade).
  - **Arena.** `bridal_barge_night`, with its `BossAnchor` in the water off the bow.
  - **Preview.** `preview_bridal_barge_night.tscn` with the `wakefin` enemy (a stand-in until the creatures model
    merges). Shot `battle_arena_bridal_barge_night`.
  - **Tests.** `tools/tests/test_bridal_barge.py` (5).
  - **For act1/creatures:** set the Ch15 Wakefin encounter's arena to `bridal_barge_night`.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log

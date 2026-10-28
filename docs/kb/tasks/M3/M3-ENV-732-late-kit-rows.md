---
id: M3-ENV-732
title: "Act II zone pieces in review rows: a preview and seven shots, so the unplaced Ansedra, Keth, Lowlight and Ossa Fen pieces are seen rendered"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-716, M3-ENV-717, M3-ENV-718, M3-ENV-721]
milestone: M3
reviewer: rendering
---
## Goal
TRACK-RULES' backlog, step 4. Twenty-two Act II zone pieces that no arena or zone places had never been rendered, so
the "parts look primitive" audit couldn't see them.

## Acceptance criteria
- [x] `late_kit_rows.py` writes `game/levels/_tests/late_kit_rows/late_kit_rows.tscn`:
  - the pieces in rows: Ansedra, Keth, Lowlight, Ossa Fen;
  - one plain daylight grade (`ch05_ashcrown_day`) and a ground plane.
- [x] Shots: `kitrow_ansedra_court_hall`, `kitrow_ansedra_basin_stacks`, `kitrow_keth_cloudloom_house`,
  `kitrow_keth_road_details`, `kitrow_lowlight_nave_bays`, `kitrow_lowlight_vey_details`, `kitrow_fen_roost_cord`.
- [ ] The renders viewed, and anything that reads primitive fixed.

## Notes
- **2026-10-27 (env-art):** built. This is shape review only: each zone's own light is its sheet's.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log

---
id: M3-ENV-723
title: "Hollowmere, the Saltwright flotilla (Ch17): sheet, kit and grade"
role: environment
status: blocked
blocked-by: ADR 0041
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: []
milestone: M3
reviewer: rendering
---
## Goal
The Lead's queue item 4 (the act outline's later zones): Ch17's Hollowmere. The sheet first, then the kit and
the zone's grade. No battle is staged in Ch17, so there is no arena.

## Acceptance criteria
- [x] The design sheet: `docs/kb/art/environments/hollowmere.md`.
- [x] The kit, `hollowmere.py`: `hm_lashed_hulls`, `hm_windmill`, `hm_tide_wheel`, `hm_signal_lamp`,
  `dace_hull_frame` and `hm_far_flotilla`.
- [x] The grade: `assets/environments/zones/ch17/` (`hollowmere_grades.py`): `lut_act3_dusk` (zone_lut `act3_dusk`,
  with the new `white_cap` option; every other LUT is byte-identical), the Environment, and the sun row.
- [x] Tests: `tools/tests/test_hollowmere.py` (5).

## Notes
- **2026-10-27 (env-art):** built. Placing it is act1-chapters' job: the composition is in hollowmere.md §1.
  There is no screenshot shot yet, because nothing places these pieces; the rendering review comes with the zone's
  first shot.

- **2026-10-28 (env-art): paused by ADR 0041** (Act I at final quality first; later-act work stops). The work stays committed and pushed as is; nothing is reverted. Resume when the human lifts the pause.

## Review log

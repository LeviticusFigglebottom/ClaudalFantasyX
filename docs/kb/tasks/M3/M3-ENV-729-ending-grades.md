---
id: M3-ENV-729
title: "The Ending's grades: ending_unbinding, ending_dock and post_credits (Environments, LUTs, key rows)"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-728]
milestone: M3
reviewer: rendering
---
## Goal
TRACK-RULES' self-directed backlog, step 5: the next act's content. The game closes on three frames (act3_ending.md
E1–E7); each needs its grade before Cinematics can stage it.

## Acceptance criteria
- [x] `docs/kb/art/environments/ending.md`.
- [x] `ending_grades.py`: three Environments, the LUTs `lut_ending_lift`, `lut_ending_dock` and `lut_post_credits`
  (zone_lut.py; every other LUT byte-identical) and `ending_grades.json` (key, rim, lamp and sea-glow rows).
- [x] Tests: `tools/tests/test_ending_grades.py` (3).
- [ ] Rendering: a mood frame for each, once Cinematics stages them (no shot from env-art; the sets are the Kite,
  Haluna's dock and Oruvel).

## Notes
- **2026-10-27 (env-art):** built. Follow-up: Oruvel's rebuilt variant for E7 (new lamp posts, fresh planks among
  the old) isn't in the Oruvel kit yet.

## Review log

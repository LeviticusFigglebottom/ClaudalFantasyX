---
id: M4-A2P-045
title: "The open sea at night and Hollowmere's first visit at final quality"
role: environment
status: review
owner_session: env-art-b
depends_on: []
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
The drifting barge zone (the bier, the stern, the bow at dawn in fog) on `bridal_barge.py`, the shoal's place, and Hollowmere's first visit placed from the built kit (M3-ENV-723, hollowmere.md §1): the dock, the supper, the pyre-raft. Hollowmere is shared with Act III: build it once.

## Acceptance criteria
- [ ] As M4-A2P-040, for Ch15 and Hollowmere.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch15.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30: started by env-art-b under ADR 0205.
- 2026-10-30 (env-art-b): Hollowmere's first visit dressed. Ch15's sea (`ch15_open_sea.md`) is not done yet.
  - `tools/act2/ch15_hollowmere_dressing.py`, in the greybox's frame: the walk at y 0, the lagoon at −0.9, so no mark
    moves.
  - New pieces in `hollowmere.py`: the dock modules, `pyre_raft`, `hm_ship`, `hm_supper_table`, `hm_oil_lamp`.
  - The dawn grade and `lut_ch15_hollowmere_dawn`.
  - Shots `ch15_hollowmere_*`; tests `test_hollowmere_dressing.gd` and `tools/tests/test_ch15_hollowmere_dressing.py`.
  - Reviewer: rendering, on the PC: the dawn fog's density (0.018 against the spec's 0.03) and the lamps.

## Review log

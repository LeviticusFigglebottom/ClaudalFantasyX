---
id: M4-A2P-041
title: "The Sunken Vey and Lowlight dressed, lit and walkable at final quality"
role: environment
status: blocked
blocked-by: ADR 0203
owner_session: ""
depends_on: []
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
Place the built kit (M3-ENV-716, 735) per lowlight.md §5: galleries, the conduit court and its housing-mark (with M3-ENV-719), the engine hall, the well-shaft and the drowned sanctum's view, the grade and the core-release warm lift.

## Acceptance criteria
- [ ] As M4-A2P-040, for Ch11; nothing frozen (ADR 0015).
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch11.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- 2026-10-30 chapters (act1-chapters): **a regular-fight arena is missing.** Sunken Vey's galleries (`ch11_vey_rays`, `ch11_vey_urchins`) have no arena, so they would fight on
  the sandbox's stage. Please add `sunken_vey_gallery` (arenas.json) with this zone's kit. chapters then names it on the rows and
  drops them from `ACT2_NO_ARENA_YET` in `tests/integration/test_act1_encounters_resolve.gd` (docs/kb/plan/act2/chapters).

## Review log

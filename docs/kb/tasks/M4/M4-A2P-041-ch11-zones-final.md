---
id: M4-A2P-041
title: "The Sunken Vey and Lowlight dressed, lit and walkable at final quality"
role: environment
status: doing
owner_session: "env-art (claude/env-art, 2026-10-30)"
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

- 2026-10-30 (env-art): **built**, `tools/act2/ch11_lowlight_dressing.py`. The walks and rooms are built from the
  greybox (`vey_zones.py`, `lowlight_zones.py`). Around them stand the kit's arcades, columns, figs, the housing (the
  mark), the bench and the well-shaft. Ch11's grey-noon grade and still water. env-art's previews
  (`game/levels/_tests/ch11_zones/`) were viewed at twenty cameras. Tests: `tools/tests/test_ch11_lowlight_dressing.py`.
  The mount, and the open choices (the well's mouth, wading, underwater), are chapters' (M4-A2P-0411). The Engine's
  field look is creatures' `lamp_engine`.
- 2026-10-30 chapters (act1-chapters): **a regular-fight arena is missing.** Sunken Vey's galleries (`ch11_vey_rays`, `ch11_vey_urchins`) have no arena, so they would fight on
  the sandbox's stage. Please add `sunken_vey_gallery` (arenas.json) with this zone's kit. chapters then names it on the rows and
  drops them from `ACT2_NO_ARENA_YET` in `tests/integration/test_act1_encounters_resolve.gd` (docs/kb/plan/act2/chapters).

## Review log

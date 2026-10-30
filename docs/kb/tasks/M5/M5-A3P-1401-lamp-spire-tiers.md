---
id: M5-A3P-1401
title: "Ch19 Lamp Spire: the four tiers' interior kit (tier shell and stair, a lamp-engine still burning, the founders' quarters)"
role: environment
status: review
owner_session: "claude/env-art"
depends_on: []
reviewer: art
milestone: M5
request-from: lead
---
## Goal
act3_ch19 I05–I06: four tiers up the founders' lamp-tower. Lit Age lamps are still burning there (bound light, steady),
with lamp-engines, conduits, and the founders' living quarters preserved like a museum (a child's height marks on a
door frame). `iskarra_spire.py` (M3-ENV-726) has only the crown and the anchor-engine. This adds the tiers' kit, in
the same file, on Iskarra's materials:
- `spire_tier`: one tier's round shell inside the tower (r 10). A flagged floor with its stairwell opening; the
  clad wall with arched windows onto the dusk; a ring of conduit channels in the floor; the spiral stair's flight up
  to the next tier. Four of them stack into the dungeon.
- `spire_lamp_engine`: a Lit Age lamp-engine still running. A ceramic housing, bronze conduit, and a salt-glass lamp
  with its bound core (steady teal, `kit_bound_core`, as the anchor-engine).
- `spire_quarters`: the founders' room as they left it. Two cots, a table set for two, shelves, a chest, and a door
  frame with a child's height marks cut into it.

## Acceptance criteria
- [x] Three pieces in iskarra_spire.py within their budgets, with glbs, imports, PROVENANCE rows and manifest rows.
- [x] A kit preview (or the iskarra kit preview) shows them; viewed at a walker's eye.
- [x] Tests extended (test_iskarra_spire). Bound light only; no banned terms; nothing frozen (ADR 0015).

## Notes
The ch19 zone's greybox, puzzles and staging stay the Act III chapters' track's; this kit is what they stack.

**Done (env-art, 2026-10-30):**
- Built: spire_tier 3186/340 tris, spire_lamp_engine 416/104, spire_quarters 972/96, each with glb, import,
  PROVENANCE row and manifest row. iskarra.md §3 is updated.
- Viewed at a walker's eye, in a staged pair of stacked tiers with an engine and the quarters, under a low dusk sun:
  the quarters with the door frame, the lamp-engine with its conduits, the stair and the windows.
- Two fixes after viewing:
  - The rectangular flags left wedge gaps to the void at each ring's outer edge. The floor now lies on a stone bed,
    whose underside is the ceiling of the tier below.
  - `quad_strip(smooth=False)` leaves every normal up, so the deck's underside now takes face normals.
- test_iskarra_spire gains two checks: the stairwell stays open where the flight arrives, and the quarters keep the
  child's height marks.

## Review log

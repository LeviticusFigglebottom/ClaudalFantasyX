---
id: M4-C10-02
title: Ch10 "Fen of the Kirru" greybox, the first of Act II (ch10/ossa_fen, ch10/reedhollow) before the beat sheet
role: cinematics
status: blocked
blocked-by: ADR 0041
owner_session: act1-chapters (claude/act1-chapters)
depends_on: []
reviewer: environment
milestone: M4
request-from: lead
---
## Goal
The Lead approved the Act II greybox (Ch10 onward, M4) after Act I's polish (2026-10-27; TRACK-RULES' self-directed
backlog). Ch10's geography from act_outline.md (Ch10), act1_ch09.md §10 (where Act II starts: Ossa Fen's edge at
dusk, Pell stopping at the edge while the others walk on) and the colour script's `ch10` (overcast dusk, tannin
water), so the story slots in when the beat sheet (M4-C10-01, narrative) lands.

## Done (act1-chapters, 2026-10-27)
- `tools/act1/ch10_greybox.py` writes both layouts. **Ossa Fen**: the dry bank at the fen's edge (FenEdge; Pell at
  `pell_edge`), level root-walks with root rails over the water, mangrove trunks, a side pocket north, the Drowner's
  clearing (DrownerArena) and the way on (`to_reedhollow`). **Reedhollow**: the reed causeway (Gate, `to_fen`), a ring
  of twelve platforms round the lagoon, eight reed houses, the shore with the clutch's stone (Shore, `clutch`).
- `Ch10Zone` (Ch05Zone's calls); the two scenes with a Cast node; `locations.json` rows; `chapters/ch10.json` (arrive:
  the chapter becomes 10; the walk there and back; Pell out of Reedhollow's party); flags `ch10_started`,
  `ch10_reached_reedhollow`; `game/data/loc/ch10.csv` (the location names) imported in project.godot.
- `tests/integration/test_ch10_thread.gd` (the flow) and `test_ch10_walkable.gd` (the root-walks, the pocket, the ring).

## Next
- The beat sheet's story (M4-C10-01): scripts, the farewell-tide, the Drowner (creatures' M3-CRE-621 and an
  encounter with sim bands), the side scene, barks; Pell in the formation when his kit lands (M3-C09-07).
- Ch9's act break hands off here instead of the end card, once the Lead switches Act II on.
- When Pell is a party hero: Reedhollow keeps him out with a `party` step on arrival and one putting him back on the
  way out (a zone's own `party` only fills an empty party), as ch13.json does for Kerrid and the Sanctum.
- Env-art's fen and village kits (a request once the beat sheet names the shots).

## Review log

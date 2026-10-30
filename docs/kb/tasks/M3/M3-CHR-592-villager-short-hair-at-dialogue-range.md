---
id: M3-CHR-592
title: "Villager short and cropped hair at dialogue range (Ione's chips and hard fringe; Moll's square fringe line)"
role: character
status: review
owner_session: "characters (claude/characters)"
depends_on: [M2-CHR-524]
milestone: M3
request-from: ""
reviewer: rendering
---
## Goal
At dialogue range (`villager_ione_face`, `moll_face`, self-rendered 2026-10-29) the cropped hair still reads as
unfinished: Ione's crown is rectangular dark chips and her fringe ends on a hard, blocky line over the forehead; Moll's
crop ends on a straight square line across the brow.

## What was tried and why it did not help (2026-10-29)
A per-card stagger of the fringe's spill past the hairline plus tip-ended hairline cards (villager_hair, opt-in) changed
nothing visible: the hard line is the **painted scalp hairline** under the cards, and the chips are the **scalp-layer
cards** themselves (the villagers' `short` kind samples Asha's long-hair atlas, whose columns read as square chips when
a card is 2-3 cm long). Reverted, not committed.

## Plan
- Ione (and every villager with `kind: short` or `cropped`): build the scalp layers on toma_hair's short-hair atlas and
  `_tuft` cards (M2-CHR-524's fix for Toma, Kerrid and Moll), opt-in per villager so the others stay byte-identical.
- The painted hairline: feather it into a broken edge where cards end (`HAIRLINE_FEATHER`, as Sabe's, Ione's and Hobb's
  already have) and let a share of the front cards run past it by a varied length.
- Moll: his hairline is toma_hair's shared square `male` table; give `hairline_v` an optional per-character wander so
  the front breaks up without changing Toma (verify toma byte-identical).

## Acceptance criteria
- [x] `villager_ione_face` and `moll_face` show a broken, soft fringe edge and no square chips; viewed before and after.
- [x] Every other villager and hero job byte-identical; changed jobs identical on the three numpy paths.

## Notes
- 2026-10-29 (characters): done.
  - `tufts` (villager_hair, write_materials): short and cropped hair on toma_hair's three layers and short-hair
    atlas, rooted inside the villager's own hairline; `grey_strands` has a tufts form (grey cards on the sparse
    column, narrower). On for Ione, the gatekeeper, the clerk, Kell, Tavi, the ferrymaster, Garo, Hobb, Sabe and the
    scaleman (before/after viewed). Fenn stays on the old cards (his thin white hair read as a bald dome on tufts).
  - Moll: `_hair.front_break` (moll_hair.hairline_v; toma_hair's in_hair, _roots_inside, scalp_cards and build_hair
    take an optional hairline, default Toma's): the fringe ends on a broken edge instead of a straight line.
  - Their manifest portraits were re-rendered to match.

## Review log

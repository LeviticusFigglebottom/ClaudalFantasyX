---
id: M3-ENV-752
title: "FAST-TRACK: the opening cinematic reads greyscale (the human's playtest)"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-724]
milestone: M3
reviewer: lead
priority: high
---
## Goal
The human's playtest found the Prologue's first scene ("Everyone I'm going to tell you about...", `prologue_dead_city`,
shots P01 and P02) GREYSCALE: grey buildings and props. Clear every grey set from it.

## What was grey, and the fix
1. **The integration build's Prologue is still primitives.** `prologue.tscn` on the integration branch (7855d016)
   builds the City from boxes and cylinders. slice-polish mounted env-art's `iskarra_city.tscn` and a WaterSurface on
   `claude/m2-slice` (ead04bab, 2ab7a66e, c2c9b802, 28b0f97a), but that hasn't reached integration. **For the Lead:
   merge m2-slice's Prologue commits in big14.** (M3-ENV-739 asked for exactly this; it is done on m2-slice.)
2. **The final city itself read near-monochrome.** It was rendered through m2-slice's mount in a worktree. The cool
   `lit_ceramic` towers and the paving went grey under the dusk's teal fill, and the reef glaze went slate. Fixed
   in d2ae3cb2:
   - warm whites: ceramic `#EEE3CB`, tile `#F4E7C9`, paving `#EFDDB4` (sand_dry);
   - gilt domes and finials (`kit_gold_leaf`; small in frame, inside the palette's gold fraction);
   - a bluer glaze (`#1F7FC2`).
   This keeps iskarra.md's "white and gold at dusk, with one saturated note".

## Acceptance criteria
- [x] Self-rendered and viewed with the new materials, through m2-slice's prologue: slice_prologue_p01 and
      slice_prologue_vigil_line show cream towers, gold domes and blue bands, with no grey left. The Iskarra previews
      P01, I02 and I03 were viewed too.
- [ ] The Lead merges m2-slice's Prologue with this, then re-approves the drifted baselines: iskarra_p01/i02/i03 and
      slice_prologue_*.

## Review log

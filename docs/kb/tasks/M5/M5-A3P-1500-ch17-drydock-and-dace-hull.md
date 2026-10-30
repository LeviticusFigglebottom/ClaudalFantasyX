---
id: M5-A3P-1500
title: "Ch17 Hollowmere: the dry-dock berths and Dace's hull as Rhen finds it (cabin, engine bay, half-rigged sails)"
role: environment
status: doing
owner_session: "env-art-b (claude/env-art-b)"
depends_on: []
reviewer: environment
milestone: M5
request-from: lead (ADR 0207: Act III in the track's own lane)
---
## Goal
The environment half of [act3_ch17.md](../../story/act3/act3_ch17.md) §9 ("the dry-dock berths and Dace's hull
(unfinished Kite) at `ch17/hollowmere`"). Ch17 re-uses Ch15's zone, which env-art-b already dresses
(`tools/act2/ch15_hollowmere_dressing.py`). The new rooms are the berths, the hull's deck, its cabin (the ledger, B05)
and its engine bay (the first lamp, B10).

## The reading (env-art-b's default; the story track may overrule it in review)
The art doc (`docs/kb/art/environments/hollowmere.md`) has the hull as a bare frame, "nothing on it finished". The
Ch17 sheet asks for a cabin, an engine room, a Lit Age brass keel and sails "cut like a flare-kite", and Ch18's Kite
(`kite.py`, env-art) has a hatch amidships with the ledger chest beside it. One hull serves all three:
- **The stern third, decked:** Dace planked both sides of the stern third and decked it, so he could live aboard. A
  hatch drops to the **cabin** in the hold below, with his bunk, the ledger on a fold-down desk, the **chart wall**
  (Corrow circled) and the **tool rack** (his hooks, the make of Rhen's).
- **The engine bay:** forward of the cabin, the hold opens to the first lift-engine bed, empty: the cradle the Kite's
  `kite_engine` will sit in. This is where B10's first lamp is fitted.
- **The bare bow:** the forward two-thirds stay bare ribs, with the near side's five strakes (Ch15's read is
  unchanged from the arrival).
- **The keel** takes a Lit Age brass shoe (`kit_iskarra_bronze`), and **the mast** is stepped with one kite wing
  half-rigged: two of the five battened panels bent on, the rest furled on the boom. That's Virel's shape, planted,
  not paid (B04).
- **Ch15 and Ch17 show the same piece**: nobody has touched the hull in eleven years, so it isn't a variant.

## The berths
`hm_drydock_berth`: an empty floating berth like Dace's (a pontoon, cradle blocks, shear-legs, a fender post at the
outer corner), placed in a row of four along the dry-dock walk, with Dace's at the end (B03: "the last one"). The
**first berth** (B07) gets the old fender post Tobin sat on, its top worn pale, and the rotted keel of a first hull
in the mud under the water.

## Acceptance criteria
- [ ] `dace_hull_frame` is revised in `hollowmere.py`: a decked stern with a hatch and a cabin below (bunk, desk and
      ledger, chart wall, tool rack), an empty engine bed, a brass keel shoe, and the mast with a half-rigged kite
      wing. It stays within budget and is rebuilt with its manifest row.
- [ ] `hm_drydock_berth` (new) is built and placed four times, the first one with Tobin's post.
- [ ] The zone dressing places them, with walk collision for the hull's deck, hatch ladder and cabin floor, and
      lights for the cabin (one oil lamp) and the engine bed (cold, until B10 lights it).
- [ ] Eye-height renders of the berths at noon, the hull at dusk (H04, H07), the cabin (H05) and the engine bay
      (H09), viewed.
- [ ] PROVENANCE rows; banned-terms clean; tests (`tools/tests/test_hollowmere.py` and the zone's Godot test).

## Requests out
- **act1-chapters / Act III chapters:** the Ch17 marks: the cabin's reading seat, the hatch, the engine bed and the
  first berth's post. The layout is theirs; env-art-b will post the coordinates here when the piece is built.

## Review log

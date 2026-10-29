---
id: M3-ENV-705
title: "Colour pass on the Act I kits under their zone grades (the human: no greyscale or flat scenes)"
role: environment
status: doing
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: []
milestone: M3
request-from: lead
reviewer: rendering
---
## Goal
The human has complained about greyscale and flat scenes. Check every env-art kit under its zone's light and
grade and lift the frames that read grey, without breaking each zone's colour-script intent.

## Acceptance criteria
- [x] A colourfulness ranking of every env-art baseline (mean HSV saturation, luminance, contrast). Lowest:
      the Shell Shrine interior (S02 0.086, S03 0.095), Ashcrown A10 (0.105) and A01 (0.135).
- [x] Ashcrown: `lut_ch05_ashcrown` keeps full saturation outside the leaf greens (was ×0.88) and lifts the
      copper, lacquer and ember accents +18% (was +6%). `ashcrown.md` updated. PC render requested.
- [ ] View the PC renders of A01, A04, A10; re-approve or adjust.
- [ ] The Shell Shrine interior: proposed to slice-polish with M3-ENV-704 (its grade and GI are theirs; the kit
      stone `kit_shrine_stone` is env-art's and can warm a step if they want it with the rebake).
- [x] `causeway_route_afternoon` read as bleached beach (luminance 0.75, saturation 0.16). Its ground now takes the
      B06 zone's own `kit_causeway_ground`, not the generic `kit_ground`.
      - **Correction after viewing gpu/render-env-art-179069d and big12's baseline:** the change only matched the
        arena to the field. The B06 field is itself pale sand flats (slice_causeway_head), so the arena still reads
        pale; the earlier "wet-dark tidal mud" was wrong.
      - The read is now consistent with the field. Darkening both is a zone-grade question for Rendering and the
        Lead, not an arena fix.
- [ ] Brine Shoals B01/B05: the colour script desaturates ch06 on purpose (×0.9, "brown-grey flats ... so the
      camp's orange carries the frame"); left as designed unless the human's review names them.
- **2026-10-27 (env-art): the white barge's trim.** B05 read the barge as flat white.
  - **Added:** a gilt Level line, red panel studs, gilt capitals, a white fringe, white curtains tied back at the
    posts, a red prow post with the Level sign, and a cushion.
  - **Limits held:** red and gold stay within test_order_colours_stay_small (commit b7182ba1).
- **2026-10-27 (env-art): the Order chapel's articulation.** H07 read the chapel as a plain box.
  - **Added, keeping it crisp and straight as haluna.md asks:** marble corner and bay pilasters, a dentil course,
    arched marble window heads, two marble steps to the door, and arched openings in the cupola's drum.
  - LOD0 is 5.5k tris against a 9k budget.
- **2026-10-27 (env-art): the Pemakar massif's lower flank.** P04 and P11 read it as a bare smooth slope.
  - **New piece** `flank_rocks`: basalt boulders, scree, dry scrub and ash lenses.
  - **Placement:** 36 patches on the gentler ground round the harbour (`pemakar_layout.py`, FLANK_PATCHES), clear
    of the tiers, the quay and the sea.
- **2026-10-27 (env-art): Lowlight's piers.** In 43492e8's render they read as plain blocks. Each now has a sunk
  panel on every face, a copper conduit band, and a stepped capital (`_pier_trim`).
- **2026-10-27 (env-art): the Ossa Fen bank's litter.** c990e2c read the battle floor as bare mud.
  - **Added:** fallen leaves lying flat, twigs, crab holes and mud puddles, all under 4 cm and 1.3 m clear of every
    slot (`_bank_litter`).
- **2026-10-27 (env-art): the Underway gallery's walls.** `battle_arena_underway_tower` read its walls as bare slabs:
  the bays were clad only on the outer face, and the fight sees the inner one.
  - **Added to the inner face** of `tower_bay`, `tower_bay_solid` and `tower_bay_broken`: a cast skirting, a stepped
    cornice (gone on the broken bay), a fillet down each pier's edge, the window's sill and head framed, and sponge and
    coral crust low on the wall. LOD0 is 1.9–2.3k tris against 3.5–4.5k.

---
id: M3-C05-1213
title: Ch5 greybox to final, ch05/pemakar on env-art's Pemakar kit (the quay, the stair, the market, forge, inn, graves, the crown)
role: cinematics
status: review
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M3-ENV-03, M3-C05-02]
milestone: M3
reviewer: qa
request-from: ""
---
## Goal
Swap Pemakar's flat greybox to env-art's ten-tier town in the kit's frame, keeping every beat (B01-B06, B11) and the
day variant.

## Acceptance criteria
- [x] `tools/act1/ch05_pemakar_dressing.py`: the preview's pieces (tiers, stairs, houses, graves, lamps, the massif,
      Ashcrown on the rim), the Lanternfall night (388 lamps, the leaf-boats, the far and sea lights) following the
      greybox's Lamps block so the day variant puts it out, a quay of the kit's wall and tread modules, the Ch4
      ferry alongside; collision: treads and walls as boxes, the ten flights as ramps between cheeks and parapets,
      the harbour road up the massif's own rows, the quay, the bounds; houses, smithy as trimesh, graves and shrine
      boxes as boxes, the massif as an LOD0 trimesh. Story points moved once (`--relayout`).
- [x] ZoneKitDressing: `multimeshes`, `far_lights`, a light's own `color`, `"collide": "trimesh_lod0"`.
- [x] KitWalkProbe reads the kit's box colliders and (opt-in) queries the physics space for the trimesh pieces.
- [x] `test_ch05_pemakar_kit`: the night follows Lamps; the quay climbs to the crown; the tiers reach the market,
      forge, inn gate and graves; every mark, actor, spawn and trigger stands on a floor in the open.
- [x] Shots `ch05_pemakar_harbour`, `ch05_pemakar_crown` rendered on the PC, viewed, approved. Baselines approved by the Lead's gates (big13 1fa92b81 / a4410fd9; tracks never write baselines, TRACK-RULES).

## Notes
- The kit's tiers are dressing, not lanes: house_b's veranda and house_a's plinth close a tier's front lane, and each
  tier's roofs reach over the next tier's lane. So the story keeps near the stair (the kit keeps |x| < 3.4 clear):
  the smithy trades places with the house_b by the stair on tier 0, and the inn (tier 2's veranda house) moves along
  its arc from x -14 to -6.6 with its shrine-box.
- The day variant (B11) uses the kit's dusk grade as a stand-in: the kit has no day grade (M3-ENV-1214).
- The wake-wall, the sea-cut weir's lip and the crown bell stay greybox stand-ins (M3-ENV-1214).

## Review log
- 2026-10-29 act1-chapters: to review (every criterion met; the stand-ins listed in Notes wait on their own requests).

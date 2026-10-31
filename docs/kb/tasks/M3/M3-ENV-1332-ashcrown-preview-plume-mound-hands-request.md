---
id: M3-ENV-1332
title: "Ashcrown kit preview (PC pass 7 row 79): the plume reads as clay, the A10 mound is untextured, A01's hands are flat black"
role: environment
status: todo
owner_session: ""
depends_on: []
reviewer: environment
milestone: M3
request-from: environment (env-art-b)
---
## Goal
The PC's pass 7 row 79 flags three of the Ashcrown **kit preview's** own shots (`game/levels/_tests/ashcrown_kit`,
env-art's; `ashcrown_preview_shots.json`):
- `ashcrown_a10_plume_from_the_rim`: the plume reads as solid, lumpy clay, and the foreground mound is untextured.
- `ashcrown_a01_approach`: the giant hands are flat, unlit black cut-outs.

The PC's re-measure on big37 found them unchanged because env-art-b's plume fix lives in the Ch5 zone only. The kit's
`ac_plume_day` is unchanged, and the preview uses it.

## What already works in the zone (env-art-b, ch05_ashcrown_dressing.py `PLUME_LOOK`)
The zone's plume is `game/levels/ch05/ashcrown/ashcrown_plume_day_material.tres`, a copy of `ac_plume_day` with:
- a warm grey-brown ash body (`col_body` 0.52/0.49/0.46, `col_body_top` 0.62/0.59/0.55) and lighter shade;
- softer, feathered billows (`detail_bump` 0.55, `near_detail` 0.6, `mottle` 0.3, `edge_soft` 0.75,
  `alpha_mottle` 0.12);
- the sun through its edges and on its rim (`back_scatter` 0.7, `rim_energy` 0.35);
- the crater's fire up the column (`ember_energy` 0.6, `ember_height` 0.18, `vent_glow_height` 0.16) and a darker
  shade side (`shade_lift` 0.15).

Viewed in ch05_ashcrown_tiers, _forecourt, _crown and _court, it reads as ash, not clay.

## Ask (env-art: kit and preview)
1. Take `PLUME_LOOK` into the kit's `ac_plume_day`, or point the preview's plume row at the zone's material.
2. Texture A10's foreground mound: the preview's ground near the rim.
3. A01's hands: give them a shaded material (they read unlit) and a fill on the approach.

## Acceptance criteria
- [ ] a10 and a01 on the PC read as ash, a textured mound and modelled hands.

## Review log

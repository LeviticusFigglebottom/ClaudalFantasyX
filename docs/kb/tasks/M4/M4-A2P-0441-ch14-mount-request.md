---
id: M4-A2P-0441
title: "Mount env-art's Ch14 dressing in ch13/ansedra_lacquer_court; the lagoon's level and the dusk fill (request to chapters)"
role: cinematics
status: todo
owner_session: ""
depends_on: [M4-A2P-044]
milestone: M4
request-from: environment
reviewer: environment
---
## Goal
M4-A2P-044 (env-art) built the Lacquer Court's look on the greybox (`tools/act2/ch14_court_dressing.py`): the
dressing, the grade (colour script ch14, `lut_ch14_wedding`), and the water (the lacquer lagoon, still). The preview
is `game/levels/_tests/ch14_zones/ansedra_lacquer_court_dressed.tscn`.

## Ask (the zone's scene and layout are yours)
- [ ] **Mount the dressing.** Add a `Water` (WaterSurface at y −0.95, `publishes_water_level`, the zone's waves and
      material), a `Tide` and a `Dressing`, as the preview does.
- [ ] **The lagoon's level.** The greybox's `Water` block stands at −0.3, over the barge's deck (−0.6) and level with
      the water-steps' middle. The dressing sets the lagoon at −0.95, under the deck. Match the block, or tell
      env-art the level you want.
- [ ] **The dusk fill.** At the layout's sun (4°, 1.2) and ambient (0.5, #2E3448), the court's centre reads near-black
      at a walker's eye on lavapipe. The lanterns light only the colonnade. Consider an ambient of about 0.8, or judge
      it on the real GPU first (env-art's PC-QUEUE).

Rendering's (M4-A2P-047): the escape's ripples.

## Review log

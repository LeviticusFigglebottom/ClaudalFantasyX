---
id: M4-A2P-0451
title: "Mount env-art's Ch15 open-sea dressing; a Hollowmere greybox zone for Ch15's first visit (request to chapters, rendering)"
role: cinematics
status: todo
owner_session: ""
depends_on: [M4-A2P-045]
milestone: M4
request-from: environment
reviewer: environment
---
## Goal
M4-A2P-045 (env-art) built `ch15/open_sea`'s look (`tools/act2/ch15_open_sea_dressing.py`): Merel's barge at the
greybox's size on its deck, the unlamped ch15 grade, the night sea. The preview is
`game/levels/_tests/ch15_zones/open_sea_dressed.tscn`.

## Ask
- [ ] **chapters: mount the dressing.** In `open_sea.tscn`, add a `Water` (WaterSurface at the barge's waterline,
      −0.6, `publishes_water_level`, `lagoon_waves.tres`, the zone's night-sea material, `sea_glow_energy` 0.12), a
      `Tide` and a `Dressing`, as the preview does. The greybox's Water block (−0.3) sits over the waterline: match it
      or say the level you want.
- [ ] **chapters: a Hollowmere greybox zone** for Ch15's first visit (the dock, the supper, the pyre-raft; hollowmere.md
      §1). There isn't one, so env-art can't place the kit (M3-ENV-723, built and previewed). Hollowmere is shared
      with Act III: one zone.
- [ ] **rendering: the shoal's held dead** under the water (the Shoal block, 30 × 20 at −3), and the dawn fog at the
      bow.

## Review log

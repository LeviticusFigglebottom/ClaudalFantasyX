---
id: M2-ENV-10
title: The B06 Saltgrass Causeway route at final quality (the slice's "one route")
role: environment
status: doing
owner_session: "env-art"
depends_on: [M2-ENV-08]
milestone: M2
request-from: lead
reviewer: rendering
---
## Goal
An M2-review blocker from the Lead's intro audit: SPEC §10's "one route" is B06, the Saltgrass Causeway
(`ch03/saltgrass_causeway`, vertical_slice.md B06, haluna.md §2): about 280 m of playable path out over the
low-tide flats from Haluna's causeway head to the Shell Shrine's islet, under `ch03_causeway` (14:30). m2-slice
builds the greybox gameplay (rails, encounters, the three banters' triggers); env-art builds the world and hands
it over with a swap-in note.

## Acceptance criteria
- [ ] Tidal flats ground (exposed at low tide −0.7 m; channels and tidepools fill from the sea plane), the
      causeway's slab path, pilgrim marker posts every ~20 m (one broken, C04), coral heads, saltgrass on 70 % of the
      ground above −0.2 m (haluna.md §2.3), tidepools for C03, the Lit Age ring with its glint (C05), the shrine islet
      on the horizon (C01), and the widened Drownbell disc for B10 (shared with M2-ENV-11's battle arena).
- [ ] A shipped dressing scene (outside `_tests/`, M2-ARC-04) that m2-slice instances, driven by a generated layout,
      all pieces reproducible with PROVENANCE rows, `verify_blender_builds` identical.
- [ ] `ch03_causeway` lighting and grade per haluna.md §0 (sun 52°/250°, key `#FFEAD8` 3.0, sky fill `#A9DCF2` 0.6,
      exposure 0.65, `lagoon_clear` ×1.5 pools).
- [ ] Composed views C01–C07 at the brief's lenses, viewed on lavapipe; register at most two as baselines.
- [ ] A swap-in note for m2-slice (the scene, the path polyline for rails and triggers, banter anchor points,
      collision source).

## Review log

---
id: M2-RND-100
title: "Prewarm the final Saltgrass Causeway: its entry and first visible frame (ADR 0029/0037)"
role: rendering
status: todo
owner_session: ""
depends_on: [M2-FP-108]
reviewer: cinematics
milestone: M2
request-from: cinematics
---
## Goal
M2-FP-108 (claude/m2-slice a419d87b) swaps B06 from the greybox to env-art's final route
(`assets/environments/zones/saltgrass_causeway/saltgrass_causeway_dressing.tscn`, dressed off the tree in
GreyboxZone.build()). The causeway is not in `game/data/settings/prewarm_materials.json` `first_run_scenes`, and the
kit and route materials aren't listed for it. On lavapipe the first visible frame after the swap took 1707 ms
(tools/cutscene_frames log), against the 50 ms visible-frame budget.

## Acceptance criteria
- [ ] Measure `slice_sweep` with a causeway segment on the PC (real GPU, `--budget`).
- [ ] Add the causeway's materials (and the scene, if harvesting is the right tool) to the prewarm data, so that its
  entry and first visible frame meet ADR 0029/0037.
- [ ] If the dressing itself costs too much on the worker thread, tell cinematics: the zone can split it.

## Review log

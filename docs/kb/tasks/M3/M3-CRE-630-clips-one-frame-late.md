---
id: M3-CRE-630
title: "Creature GLB clips play one frame (1/30 s) late: fix in the kit at the next batch rebuild"
role: character
status: todo
owner_session: ""
reviewer: art
depends_on: []
milestone: M3
request-from: lead
---
## Goal
Found by the Lamp Engine build (M3-CRE-623) and confirmed on the Mangrove Drowner: in every creature GLB the clips
reach their keys one frame (1/30 s) later than authored. A hit authored to peak at 0.10 s peaks at 0.13 s in the
file; strikes land a frame after their creatures.json `contact`. Nothing is broken (the hit snap at 0.1 s still
holds a struck pose; one frame of contact lag is under the choreography's tolerance), but the timing drifts from
the sheets and the data.

## Acceptance criteria
- [ ] Find the off-by-one in `export_creature` (assets_src/creatures/common/creature_kit.py: the baked frame range
      or the action's start frame) and fix it in the kit
- [ ] Rebuild every creature job in one batch (a kit change rebuilds them all, pipeline.md); Blender verify
      identical after; re-measure peaks against the contacts (the measuring scripts in the M3-CRE-623/624 task
      files)
- [ ] One PC render of every creature and battle_choreo shot, viewed; re-approve the drift

## Notes
- The Avalanche Ram's measured hit peak at 0.10 s suggests its build may already compensate. Check it before the
  batch.

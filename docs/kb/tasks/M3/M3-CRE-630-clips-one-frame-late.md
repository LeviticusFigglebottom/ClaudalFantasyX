---
id: M3-CRE-630
title: "Creature GLB clips play one frame (1/30 s) late: fix in the kit at the next batch rebuild"
role: character
status: review
owner_session: "creatures (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY, branch claude/creatures)"
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
- [x] Find the off-by-one in `export_creature` (assets_src/creatures/common/creature_kit.py: the baked frame range
      or the action's start frame) and fix it in the kit
- [x] Rebuild every creature job in one batch (a kit change rebuilds them all, pipeline.md); Blender verify
      identical after; re-measure peaks against the contacts (the measuring scripts in the M3-CRE-623/624 task
      files)
- [ ] One PC render of every creature and battle_choreo shot, viewed; re-approve the drift

## Notes
- The Avalanche Ram's measured hit peak at 0.10 s suggests its build may already compensate. Check it before the
  batch. (Checked: it does not. It keys every frame from the same bake, and its 0.10 s was measured from its first
  key.)
- **Done (2026-10-27):** `export_creature` keyed frame f + 1 for clip time f / FPS, and the glTF exporter counts
  from frame 0. Keys are now at frame f and the NLA strip starts at 0. The reef crab's hit peaks at 0.100 s (was
  0.133) and its attack ends at 1.200 s (was 1.233). All 46 kit-dependent jobs were rebuilt: 42 creature GLBs
  changed, and no material or wildlife output did. Blender verify identical ×46; Godot creature 37/0, battle 687/0,
  post_import 21/0.
- The PC render waits for M3-CRE-631, so one render cycle covers both rebuilds.

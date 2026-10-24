---
id: M1-ENV-08
title: Vegetation LOD hysteresis hole (a plant at a switch distance can be invisible from a still camera)
role: environment
status: doing
reviewer: rendering
owner_session: "worktree-agent-a573ddba06eb06eb2"
depends_on: [M1-ENV-03]
milestone: M1
request-from: "rendering"
---
## Goal
`VegetationPlant` gives LOD *n*'s end and LOD *n+1*'s begin the same switch distance, each with a `lod_margin_m`
(2 m) hysteresis. Godot's hysteresis widens a range only for an instance that is already visible. So a plant first
seen within the margin of a switch, from a camera that hasn't moved since load, can be drawn by neither LOD. Found in
M1-ENV-03 v2 (`docs/kb/qa/gpu/2026-10-23-env-03-vegetation.md`, "v2"): in the base build, one palm at the 120 m
switch was missing from `haluna_h02_tidewall_lane`. v2 fades the last LOD, which drops the hysteresis there and draws
it. The 45 m switch (LOD0 → 1) still has the hole.

## Acceptance criteria
- [ ] No plant within `lod_margin_m` of a switch is invisible on the first frame from a still camera. One way: overlap
      the ranges (LOD *n* ends at switch + margin, LOD *n+1* begins at switch − margin, no hysteresis), or keep the
      hysteresis on one side only.
- [ ] The switches still don't flicker when a camera dithers at the switch distance (`tools/gpu_bench/lod_pop.tscn`).
- [ ] A test (below), and GPU drift listed for the veg_* and haluna_* shots.

## Notes
- **Repro:** with `tools/gpu_bench/lod_pop.tscn` or the vegetation test scene, park the camera so one palm is at
  44–46 m and capture on the first settled frame. The palm is missing, and it appears once the camera moves.
- **Test idea:** a unit test can't see Godot's visibility culling. Assert the ranges instead: for every switch,
  LOD *n*'s `[begin - begin_margin, end + end_margin]` and LOD *n+1*'s overlap, *and* the inner ranges
  `[begin + begin_margin, end - end_margin]` of LOD *n* and *n+1* leave no gap. That inner-range condition is the
  one the current setup fails. A GPU check: `RenderingServer` visibility isn't queryable, so use a capture
  (`capture_preset`) of a one-palm scene with the camera at switch ± 1 m.
- **Cost:** an overlap draws both LODs over a 4 m band (a few plants), so it's negligible next to the 6 m alpha
  fade it replaces.

## Review log

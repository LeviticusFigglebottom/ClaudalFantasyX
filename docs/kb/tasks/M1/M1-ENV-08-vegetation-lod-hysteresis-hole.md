---
id: M1-ENV-08
title: Vegetation LOD hysteresis hole (a plant at a switch distance can be invisible from a still camera)
role: environment
status: done
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
- [x] No plant within `lod_margin_m` of a switch is invisible on the first frame from a still camera. One way: overlap
      the ranges (LOD *n* ends at switch + margin, LOD *n+1* begins at switch − margin, no hysteresis), or keep the
      hysteresis on one side only.
- [x] The switches still don't flicker when a camera dithers at the switch distance (`tools/gpu_bench/lod_pop.tscn`).
- [x] A test (below), and GPU drift listed for the veg_* and haluna_* shots.

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
- **Done in M1-ENV-09 (2026-10-24, worktree-agent-a573ddba06eb06eb2).** See that task's Notes. Each LOD is now the
  `visibility_parent` child of the next, so the hysteresis stays on one side only (the parent's begin), and there is
  no overlap. On lavapipe, `game/levels/_tests/vegetation/lod_sweep_probe.gd` gives: still camera, LOD0 up to 47 m
  and LOD1 from 48 m; sweeping in, LOD1 down to 44 m and LOD0 from 43 m; sweeping out, LOD0 up to 47 m. That's 4 m
  of hysteresis, so dithering at 45 m doesn't flicker. I did not run `tools/gpu_bench/lod_pop.tscn` (it's a GPU
  bench); the probe's in/out sweeps measure the same thing. Shot drift: only `veg_beach_wide` (rmse 0.030), which
  is the missing palm now drawn. haluna_* are all within limits.

## Review log
- 2026-10-24 review-sweep-Q (rendering): **approve.** Folded into M1-ENV-09 and verified there. Each LOD is the `visibility_parent` child of the next, so there is one state machine per switch, and the 44–47 m still-camera hole is gone. On lavapipe `lod_sweep_probe` passes, and the base fails 16 rows. The PC got `LOD_SWEEP PASS` on Vulkan (2026-10-24-env-09-lod-check.md). `test_vegetation_plant.gd::test_a_distance_sweep_draws_exactly_one_lod` replaces the margin-equality test, which can't apply to a chain. `--filter=vegetation`: 17/0. veg_beach_wide was re-approved by the Lead (0bfac12).

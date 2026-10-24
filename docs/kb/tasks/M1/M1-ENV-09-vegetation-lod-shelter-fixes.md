---
id: M1-ENV-09
title: Vegetation follow-ups from review-sweep-O (last-LOD hysteresis gap, ShaderGlobals cache)
role: environment
status: done
owner_session: "worktree-agent-a573ddba06eb06eb2"
depends_on: [M1-ENV-03]
milestone: M1
request-from: "lead"
reviewer: rendering
---
## Goal
These are review-sweep-O's findings on M1-ENV-03 v2 (commit 4ca20cc). None blocks; each is small.

## Acceptance criteria
- [x] **The last switch has a hysteresis gap** (vegetation_plant.gd `_apply_lod`, ~:143-150). With `lod_end_m` 45/120/400, LOD1 ends at 120 with an end margin of `lod_margin_m` (2 m). Now that the last LOD fades, its begin margin is 0. Under `FADE_DISABLED`, Godot's margin is hysteresis: a hidden LOD1 only reappears under 118 m, while LOD2 hides under 120 m. So a camera moving in through 118-120 m draws **neither** LOD of the palm, and a camera moving out through 120-122 m draws **both**. The 45 m switch is symmetric and fine. Fix it: when the last LOD fades, give the LOD before it an end margin of 0 too, or move the fade onto a separate instance. Then add a test that, for every switch, the outgoing end margin equals the incoming begin margin.
- [x] **ShaderGlobals goes stale.** vegetation_test.gd:54-57 restores `PINNED_GLOBALS`, including `hymn_sun_direction`, through `RenderingServer.global_shader_parameter_set` directly. `ShaderGlobals` then still returns the test's sun to the next scene's AUTO plants. Restore through `ShaderGlobals.set_value`, and make `get_value`'s fallback the project setting's default (`shader_globals/<name>`), not `Vector3.UP`.
- [x] **The shelter probe runs once.** Note in vegetation.md "Shelter" that a time-of-day change doesn't re-probe, or re-probe when ShaderGlobals writes a new sun.
- [moved to M1-ENV-11] Check the AUTO shelter against the Haluna collision the first-playable branch builds (`haluna_zone.gd` `collision.build()`), once that branch merges: confirm which physics layer it uses against `shelter_mask` = 1. **Routed** (Lead, 2026-10-24): the cloud track
  on `claude/m2-slice` owns Haluna (`game/levels/ch02/**`), so this item is theirs. See Notes.

## Notes (2026-10-24, environment, worktree-agent-a573ddba06eb06eb2; M1-ENV-08 folded in)
- **The fix is a dependency chain, not margin bookkeeping.** Two independent `FADE_DISABLED` ranges at one switch
  can't avoid both a hole and a double draw: each keeps its own hysteresis state, and a fresh instance starts
  hidden. That also explains M1-ENV-08's 44–47 m still-camera hole. Now each LOD is the `visibility_parent` child
  of the next LOD in its chain (`VegetationPlant.lod_range` / `lod_mesh`, chained per base name). Godot draws a
  child only while its parent is hidden for being too close, so the parent's begin check, with its margin as the
  hysteresis, is the only state machine for that switch. The last LOD still fades out over 394–406 m, and it now
  crossfades in over 118–122 m on top of the opaque LOD1. That band is the "or a crossfade" case. Without the
  fade, the 120 m switch gets the plain hysteresis.
- **The test asked for** ("the outgoing end margin equals the incoming begin margin") doesn't apply to a chain, so
  `tests/unit/test_vegetation_plant.gd::test_a_distance_sweep_draws_exactly_one_lod` replaces it. It models Godot's
  range check (measured, see the probe below) and sweeps 0.5–390 m in 0.25 m steps from a still camera, moving in
  and moving out, with the fade on and off. Each step must draw exactly one LOD opaque, or that one plus the faded
  LOD2 within 2 m of 120 m.
- **GPU proof** (lavapipe): `game/levels/_tests/vegetation/lod_sweep_probe.gd` reads back three coloured probe
  LODs at 40–50, 114–126 and 390–410 m in 0.5 m steps. The new code gives `LOD_SWEEP PASS`. The base code (da9513b)
  gives `FAIL 16`: a still camera drew nothing at 44–47 m, sweeping in drew nothing at 119–120 m, and sweeping out
  drew LOD1 and LOD2 together at 121–122 m.
- **ShaderGlobals** (`game/core/shader_globals.gd`; the task allowed the Architect path): `reset(name)` restores
  the project.godot default, and `default_value(name)` is new. `get_value` falls back to the project default and
  then to `fallback`. A real change notifies `LISTENERS_GROUP`. `vegetation_test.gd` and `haluna_mood.gd`
  `_exit_tree` restore through `reset`. Found along the way: `vegetation_test.tscn` lacked
  `node_paths=PackedStringArray("sun_node")`, so `sun_node` was always null and the scene never wrote its sun. It's
  fixed. No vegetation shader reads `hymn_sun_direction`, so there's no visual change from it.
- **Shelter re-probe:** AUTO plants join the listener group and re-probe on the next physics frame when the sun
  turns by more than `SHELTER_REPROBE_DEG` (0.5°). Requests coalesce through a one-shot `physics_frame` connection,
  which dies with the plant. vegetation.md "Shelter" is updated.
- **Routed Haluna item, for the cloud track:** `haluna_collision.gd` builds plain `StaticBody3D`s (ground, props,
  bounds), which are on the default layer 1, so they are on `shelter_mask` 1. Two things to check there:
  (a) the AUTO probe runs on the first physics frame after the plant's `_ready`, so if `collision.build()` runs
  later (prebuild on a worker thread), the plants probe before the collision exists and won't re-probe until the
  sun moves. Call `probe_shelter()` / `request_shelter_probe()` on each plant after `build()`. (b) A ground body on
  layer 1 can shelter a plant whose crown ray meets a slope toward a low sun, which is physically right but worth a
  look. I didn't touch any Haluna scene.
- **Not mine:** `tests/screenshots/capture_setup.gd` (QA) still sets and restores shot `globals` directly, so a
  shot that overrides `hymn_sun_direction` would leave ShaderGlobals stale. The fix is `ShaderGlobals.set_value` /
  `reset` there. The same LOD hole exists in `haluna_dresser.gd` and `asset_import_rules.gd` `_apply_lod`, filed
  as **M1-ENV-10**.
- **Shot drift (lavapipe, HYMN_SHOTS = the 3 veg + 5 haluna shots):** `veg_beach_wide` rmse **0.03014** (limit
  0.008). This is the intended change: the baseline is missing a whole palm (centre-left, about 120 m), which sat in
  the old hole, and the new capture draws it. The Lead should re-approve. Within limits: veg_backlit_fronds 0.00000,
  veg_frangipani_close 0.00000, haluna_h01 0.00189, h02 0.00326, h03 0.00114, h04 0.00000, h07 0.00075.

## Review log
- **2026-10-24, rendering (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB): the LOD-chain criterion passes on the GPU.**
  Report: `docs/kb/qa/gpu/2026-10-24-env-09-lod-check.md`.
  - `lod_sweep_probe.gd` on Vulkan (RX 9070 XT) gives `LOD_SWEEP PASS` for the still camera, sweeping in and
    sweeping out. All three passes give the same 118.5–121.5 m crossfade.
  - The real palm, stepped and with a moving camera (5 m/s) in both directions, shows no pop and no hole. The
    trunk stays opaque. It draws one LOD outside 118.5–122 m and LOD1 plus the fading LOD2 inside the band. A
    one-frame LOD1 overlap as it enters, moving in, isn't visible (no luminance change).
  - The band costs +0.07, +0.09 and +0.11 ms at Low, High and Ultra 1440p with 40 palms in it at once (about 2 µs per
    palm).
  - The shelter-against-Haluna criterion is still open: it waits on the first-playable branch. So I'm leaving the
    status at review.
- 2026-10-24 review-sweep-Q (rendering): **approve-with-fixes.** Criteria 1–3 verified in code. `VegetationPlant.lod_range` and `lod_mesh` handle the chain, including saltgrass's two chains. `ShaderGlobals.reset`, `default_value` and the listener group are there, and `get_value` falls back to the project.godot default. Shelter re-probes coalesce through a one-shot physics_frame connection, with a 0.5° threshold. The missing `node_paths` for `sun_node` is fixed. The PC's GPU check is rigorous: still, in and out sweeps, a real palm moving at 5 m/s, and the crossfade's cost per palm. Criterion 4 (the Haluna shelter) was routed to m2-slice, but nothing carried it, so it moves to **M1-ENV-11**, together with the capture_setup.gd ShaderGlobals bypass the notes found. M1-ENV-10 (the same hole in haluna_dresser and asset_import_rules) is already filed.

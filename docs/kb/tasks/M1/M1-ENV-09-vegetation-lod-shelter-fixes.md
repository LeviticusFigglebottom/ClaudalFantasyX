---
id: M1-ENV-09
title: Vegetation follow-ups from review-sweep-O (last-LOD hysteresis gap, ShaderGlobals cache)
role: environment
status: todo
owner_session: ""
depends_on: [M1-ENV-03]
milestone: M1
request-from: "lead"
reviewer: rendering
---
## Goal
These are review-sweep-O's findings on M1-ENV-03 v2 (commit 4ca20cc). None blocks; each is small.

## Acceptance criteria
- [ ] **The last switch has a hysteresis gap** (vegetation_plant.gd `_apply_lod`, ~:143-150). With `lod_end_m` 45/120/400, LOD1 ends at 120 with an end margin of `lod_margin_m` (2 m). Now that the last LOD fades, its begin margin is 0. Under `FADE_DISABLED`, Godot's margin is hysteresis: a hidden LOD1 only reappears under 118 m, while LOD2 hides under 120 m. So a camera moving in through 118-120 m draws **neither** LOD of the palm, and a camera moving out through 120-122 m draws **both**. The 45 m switch is symmetric and fine. Fix it: when the last LOD fades, give the LOD before it an end margin of 0 too, or move the fade onto a separate instance. Then add a test that, for every switch, the outgoing end margin equals the incoming begin margin.
- [ ] **ShaderGlobals goes stale.** vegetation_test.gd:54-57 restores `PINNED_GLOBALS`, including `hymn_sun_direction`, through `RenderingServer.global_shader_parameter_set` directly. `ShaderGlobals` then still returns the test's sun to the next scene's AUTO plants. Restore through `ShaderGlobals.set_value`, and make `get_value`'s fallback the project setting's default (`shader_globals/<name>`), not `Vector3.UP`.
- [ ] **The shelter probe runs once.** Note in vegetation.md "Shelter" that a time-of-day change doesn't re-probe, or re-probe when ShaderGlobals writes a new sun.
- [ ] Check the AUTO shelter against the Haluna collision the first-playable branch builds (`haluna_zone.gd` `collision.build()`), once that branch merges: confirm which physics layer it uses against `shelter_mask` = 1.

## Review log

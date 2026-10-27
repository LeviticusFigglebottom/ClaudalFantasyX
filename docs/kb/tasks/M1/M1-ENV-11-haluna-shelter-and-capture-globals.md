---
id: M1-ENV-11
title: Haluna's AUTO shelter after its collision build; capture_setup restores shader globals through ShaderGlobals
role: architect
status: done
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
reviewer: environment
depends_on: [M1-ENV-09, M2-FP-05]
milestone: M1
request-from: "lead"
---
## Goal
Review-sweep-Q on M1-ENV-09. Criterion 4 there (check the AUTO shelter against Haluna's collision) was routed to the m2-slice track, but no task carried it. M1-ENV-09's notes also found a second ShaderGlobals bypass, in `capture_setup.gd`, outside the Environment path.

## Acceptance criteria
- [x] **Haluna (m2-slice owns `game/levels/ch02/**`).** Confirm when the AUTO plants' first shelter probe runs relative to `HalunaZone.prebuild()` / `collision.build()`, both on the WorkerThreadPool path (M2-FP-05) and on the main-thread path. If any plant can probe before the bodies are in the physics space, call `request_shelter_probe()` on every `VegetationPlant` after the build. Confirm that the collision bodies sit on layer 1, against `shelter_mask` 1. Add a test: a plant behind a Haluna wall, toward the sun, reads as sheltered after entry.
- [x] **capture_setup.gd (QA owns `tests/screenshots/**`; coordinate).** Set and restore shot `globals` through `ShaderGlobals.set_value` / `reset`, not `RenderingServer.global_shader_parameter_set`. Then a shot that overrides `hymn_sun_direction` won't leave AUTO plants aiming at a stale sun. No baseline should move; run the veg_* and haluna_* shots to confirm.

## Notes
- 2026-10-24 m2-slice, **done, for review by environment** (and QA for `capture_setup.gd`):
  - **Found a real gap (main-thread path):** `HalunaCollision.build()` added its three bodies to the tree first and their shapes afterwards. A shape added to a body already in the physics space is only queryable after the next physics step, but the AUTO plants probe on the first physics frame after entry, before that step. So with the zone instanced on the main thread (tests, capture, prewarm scans), every AUTO plant saw an empty world and stayed open, and nothing re-probed until the sun moved. Measured: right after entry, even a vertical ray found no ground.
  - **The WorkerThreadPool path was fine:** it builds off the tree, so the bodies enter with their shapes.
  - **The fix:** `build()` now fills the bodies' shapes before adding the bodies, so both paths are queryable at once. No re-probe hook is needed.
  - **Layers:** the bodies are on layer 1, matching `shelter_mask` 1.
  - **Test:** `tests/integration/test_haluna_shelter.gd`. The walk collision is on the shelter layer, and every AUTO plant has its probe scheduled after entry. A plant just north of house_tile_b (0.2 m outside its inset box), toward the 74° noon sun, reads as sheltered; one on the open beach doesn't.
  - **`capture_setup.gd`:** shot globals are set and restored through `ShaderGlobals.set_value` / `reset`, not `RenderingServer` directly, so the AUTO plants hear the shot's sun and its restore. The veg and haluna shots are byte-identical before and after (and pass against their baselines).

## Review log
- **2026-10-27, environment (env-art, session_01YbaV2c8yquRHqj6afQYg89): approved.**
  - **The fix is in place:** `HalunaCollision.build()` adds each body only after its shapes (line 74 on), and
    `capture_setup.gd` sets and restores globals through `ShaderGlobals`.
  - **Check run:** `--filter=haluna_shelter` is 2 run, 0 failed.
  - **Shots:** the veg and Haluna shots have been re-rendered since on the PC and the cloud server with no
    shelter-related drift.
  - QA's half (`capture_setup.gd`) reads correctly from here. Done.

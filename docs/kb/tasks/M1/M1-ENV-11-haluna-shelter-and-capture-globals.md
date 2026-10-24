---
id: M1-ENV-11
title: Haluna's AUTO shelter after its collision build; capture_setup restores shader globals through ShaderGlobals
role: architect
status: todo
owner_session: ""
reviewer: environment
depends_on: [M1-ENV-09, M2-FP-05]
milestone: M1
request-from: "lead"
---
## Goal
Review-sweep-Q on M1-ENV-09. Criterion 4 there (check the AUTO shelter against Haluna's collision) was routed to the m2-slice track, but no task carried it. M1-ENV-09's notes also found a second ShaderGlobals bypass, in `capture_setup.gd`, outside the Environment path.

## Acceptance criteria
- [ ] **Haluna (m2-slice owns `game/levels/ch02/**`).** Confirm when the AUTO plants' first shelter probe runs relative to `HalunaZone.prebuild()` / `collision.build()`, both on the WorkerThreadPool path (M2-FP-05) and on the main-thread path. If any plant can probe before the bodies are in the physics space, call `request_shelter_probe()` on every `VegetationPlant` after the build. Confirm that the collision bodies sit on layer 1, against `shelter_mask` 1. Add a test: a plant behind a Haluna wall, toward the sun, reads as sheltered after entry.
- [ ] **capture_setup.gd (QA owns `tests/screenshots/**`; coordinate).** Set and restore shot `globals` through `ShaderGlobals.set_value` / `reset`, not `RenderingServer.global_shader_parameter_set`. Then a shot that overrides `hymn_sun_direction` won't leave AUTO plants aiming at a stale sun. No baseline should move; run the veg_* and haluna_* shots to confirm.

## Review log

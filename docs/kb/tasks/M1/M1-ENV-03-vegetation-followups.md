---
id: M1-ENV-03
title: Vegetation follow-ups (review-sweep-B)
role: environment
status: review
reviewer: rendering
owner_session: "session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/env-03-vegetation; routed by the Lead)"
depends_on: [M1-ENV-02, M1-ENV-01]
milestone: M1
request-from: "rendering"
---
## Goal
Rendering-side findings on vegetation, scheduled after the mood test (which uses the vegetation) merges.

## Acceptance criteria
- [x] translucency_shadow_floor no longer lets plants under eaves glow
- [x] Capture under FXAA (as water does) and restore threshold 0.008
- [x] LOD fade (no palm pop against sky)
- [x] Overdraw measured (debug_draw OVERDRAW capture) with a budget
- [x] Assets tagged PLACEHOLDER until Art Director sign-off
- [x] Wind flutter cap noted for GPU TAA motion test

## Notes
PC GPU session (Lead-routed; branch `gpu/env-03-vegetation`). Report: `docs/kb/qa/gpu/2026-10-23-env-03-vegetation.md`.
- **Eaves.** The instance uniform `inst_translucency_shelter` turns the through-shadow floor off. `VegetationPlant`
  sets it automatically: a crown-height ray toward the sun that hits a collider means sheltered. It can also be set
  by hand. GPU bench: the glow under a roof (mean 0.013, p99 0.23 linear luminance) is removed. Needs collision on
  buildings; the Haluna kit has none yet.
- **FXAA capture.** The vegetation test swaps TAA for FXAA under capture.tscn, as the water does, and the three veg
  shots are back at the default 0.008 threshold. On this GPU, two shot orders differ by RMSE ≤ 0.0001.
- **LOD fade.** A 6 m cross-fade with `VISIBILITY_RANGE_FADE_SELF` and overlapping fade bands; the last LOD fades out
  at 400 m. +0.04 ms. Tested.
- **Overdraw.** Measured in layers per pixel; the budget is in vegetation.md (wide ≤ 2.5 mean / p99 ≤ 12, close-up
  ≤ 5 / 14).
- **PLACEHOLDER.** `docs/kb/art/environments/vegetation_placeholders.md` lists the assets pending Art sign-off.
- **Flutter cap.** 0.02 m at 3.5 Hz, recorded in vegetation.md with the RND-15 ghosting measure.
- **Drift:**
  - `veg_backlit_fronds`, `veg_frangipani_close` and `veg_beach_wide`: TAA → FXAA, RMSE 0.022–0.044 on the GPU.
  - `haluna_h02_tidewall_lane` and `haluna_h03_lintel_gull`: 0.012, a palm in a fade band.
  - Not overwritten. Environment and Art re-approve.

## Review log

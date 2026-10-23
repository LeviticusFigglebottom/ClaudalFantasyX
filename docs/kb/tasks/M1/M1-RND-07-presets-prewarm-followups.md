---
id: M1-RND-07
title: Graphics presets and prewarm follow-ups from the Environment review
role: rendering
status: review
reviewer: environment
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-07-presets)
depends_on: [M1-RND-05, M1-RND-06, M1-ENV-02]
milestone: M1
request-from: "environment"
---
## Goal
Environment's review notes on RND-05/06 plus the water stream's requests.

## Acceptance criteria
- [x] Prewarm entries accept optional mesh/multimesh keys so real vertex formats and instancing pipelines compile
- [x] Prewarm SubViewport matches the game viewport's TAA
- [x] Vegetation detail setting (visibility-range LOD bias, MultiMesh density, small-foliage shadows)
- [x] Low preset maps to vegetation_foliage_low and water quality tiers (move WaterSurface.PRESET_QUALITY into graphics_presets.json)
- [x] Low preset AA: FXAA shimmer on alpha-tested foliage addressed
- [x] Register glimmer and water materials (as .tres) for prewarm

## Notes
- 2026-10-23 PC GPU session: all items done with real-GPU measurements (prewarm hitch cold/warm, Low AA shimmer, vegetation_detail, per-preset on Haluna). Report: docs/kb/qa/gpu/2026-10-23-rnd-07.md. Low AA changed FXAA -> TAA (measured). Request M1-ENV-05 for Environment adoption (groups, apply_tiers, WeatheringTide, prewarm mesh keys).

## Review log

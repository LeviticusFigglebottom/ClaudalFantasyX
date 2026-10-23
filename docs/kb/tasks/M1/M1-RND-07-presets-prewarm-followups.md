---
id: M1-RND-07
title: Graphics presets and prewarm follow-ups from the Environment review
role: rendering
status: doing
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-07-presets)
depends_on: [M1-RND-05, M1-RND-06, M1-ENV-02]
milestone: M1
request-from: "environment"
---
## Goal
Environment's review notes on RND-05/06 plus the water stream's requests.

## Acceptance criteria
- [ ] Prewarm entries accept optional mesh/multimesh keys so real vertex formats and instancing pipelines compile
- [ ] Prewarm SubViewport matches the game viewport's TAA
- [ ] Vegetation detail setting (visibility-range LOD bias, MultiMesh density, small-foliage shadows)
- [ ] Low preset maps to vegetation_foliage_low and water quality tiers (move WaterSurface.PRESET_QUALITY into graphics_presets.json)
- [ ] Low preset AA: FXAA shimmer on alpha-tested foliage addressed
- [ ] Register glimmer and water materials (as .tres) for prewarm

## Notes
-

## Review log

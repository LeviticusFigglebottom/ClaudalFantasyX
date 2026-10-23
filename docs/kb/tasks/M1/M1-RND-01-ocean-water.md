---
id: M1-RND-01
title: Ocean and shallows water shader with test scene
role: rendering
status: review
owner_session: rendering-stream-2
depends_on: []
milestone: M1
request-from: ""
reviewer: environment
---
## Goal
SPEC §8.2 item 1, the signature element.

## Acceptance criteria
- [x] Gerstner waves, depth absorption, caustics on seabed, shoreline foam, crest SSS, refraction
- [x] Test scene game/levels/_tests/water/ with 3 fixed shots (4: shallows, lagoon, horizon through a drowned arch, night with sea-glow)
- [x] Cost measured on the recommended tier, with a low preset defined. Relative costs come from the software renderer; GPU milliseconds are estimates. See docs/kb/tech/water.md "Cost".

## Notes
- Docs: `docs/kb/tech/water.md` (parameters, placing water in a zone, the height query, tiers, the caustics decision, cost, gotchas).
- Shaders: `game/shaders/water/` (tiers Low/Medium/High/Ultra plus the river flowmap variants). Node and height query: `game/world/water/` (`WaterSurface.height_at(xz, time)`).
- GPU/CPU parity of the waves is tested: 1024 points, max error 0.5 mm (`test_water_waves.gd::test_gpu_shader_matches_cpu_mirror`, which runs only where the software renderer is installed).
- Sea-glow uses the glimmer stream's `hymn_sea_glow()` (M1-RND-02), gated by `hymn_glimmer.a` and never cut on any tier.
- The colour-script absorption triple did not reach the art ramp. The test material is art-tuned; numbers are in the M1-ART-01 review log.
- Needs from others (not done here, outside my paths): preset → water tier in `graphics_presets.json`; prewarm registration of the water variants; an optional `hymn_sea_glow` global or a zone field for the sea-glow energy.

## Review log

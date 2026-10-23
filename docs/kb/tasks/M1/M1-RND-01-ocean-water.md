---
id: M1-RND-01
title: Ocean and shallows water shader with test scene
role: rendering
status: done
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
- 2026-10-23 environment (review-sweep-B): **approve with fixes**. This is usable for zone authoring today. A single `WaterSurface` node with a `WaveSet` and a look material, a pure `height_at` with tested GPU/CPU parity, a pausable clock, tiers that never drop sea-glow, and clear placement and gotcha docs are exactly what Environment needs. Against art direction (references.md §1.7 and the color script), the look is about two-thirds of the way. The 0.3–4 m turquoise band and depth-graded colour read correctly, and the night lamp glints and arch reflections are good. But the caustics read as synthetic, the 0–0.3 m band is grey-green rather than aqua-tinted sand, and near-camera water looks smooth and mercury-like. It is not yet at the "signature element" bar.
  - **should-fix (two sources of truth):** the colour-script absorption triples (`0.45 / 0.065 / 0.045` m⁻¹, used in all 25 frames) don't render ("near-white over noon sand"), and the test material uses `2.0 / 0.5 / 0.42`. Zone authors can't follow the colour script as written. Rendering and Art should agree on the mapping (a documented `absorption_scale`, or new triples) and update the color_script water rows in one change, so the per-frame values can be used as written.
  - **should-fix (caustics look):** the pattern is a uniform Voronoi web with the same line width everywhere and no bright filament junctions. It reads as cracked glass or pool tiles (`water_shallows` foreground), and it visibly tiles at 10–40 m in `water_lagoon`. Combine two domain-warped layers multiplicatively (min or product) so junctions focus into hot spots, vary width with depth more strongly, and fade the contrast with view distance as well as water depth. This is a shader change, so Environment can't do it with material parameters.
  - **should-fix (missing global for weathering):** art README convention 3 says stone weathering reads "a global `tide_line_y` and water-height uniform", but `WaterSurface` doesn't publish one, and `project.godot` has no such global. Haluna's tide-wall wet band, the causeway boulders and the Drownbell flood (−0.7 → +0.6 m over 8 s) all need it. Have `WaterSurface` write a `hymn_water_level` global (current Y and datum) each frame, and test that an animated node Y moves foam, caustics and the global together.
  - **should-fix (zone-level sea-glow):** `sea_glow_energy` is a per-material value, and it is gated on `hymn_glimmer.a`, the mote energy. Zones need one per-frame value from the colour script, independent of motes. Add the `hymn_sea_glow` global (your own open item, also raised in the M1-RND-02 review) before Haluna night (`ch02_night` 0.12) is authored.
  - **should-fix (shrine water):** the Shell Shrine needs basin pools whose level animates (the trial fills the inner pool) and Ilun's net caustics. "Can swap the pattern function" means a shader edit, which Environment can't do. Expose a caustic pattern selector or a tiling pattern texture as a material uniform, and confirm that small authored pool meshes (non-river) are supported with shore foam.
  - **should-fix (pipeline):** the preset → tier mapping in `graphics_presets.json` and prewarm registration of all six variants are both still open. Environment can't put water in a cutscene zone until prewarm exists (SPEC §4.2, no hitch over 50 ms).
  - **nit:** near-field water in `water_horizon` shows large smooth sky-reflection blobs. Raise `roughness_near` or the strength of the near detail normals, so the 1–10 m band breaks up.
  - **nit:** in `water_night` there is a hard white elliptical glint at about (395, 390) that reads as a sprite. Clamp the glint size and break it up with the ripple normals for low-elevation and moon lights.
  - **nit:** foam width is a vertical depth, so vertical faces (the test slab, seawalls, tide-walls, pillars) get almost no contact foam or wet line. Add a contact term from the screen-space depth difference for steep geometry. Shore run-up and a wet-sand darkening band would also sell the beach.
- 2026-10-23 lead: closing on review-sweep-B approve-with-fixes; should-fix items are tracked in M1-RND-08.

---
id: M1-ENV-02
title: Procedural palm, frangipani, and grass with wind shader
role: environment
status: done
owner_session: environment-stream-1
reviewer: rendering
depends_on: []
milestone: M1
request-from: ""
---
## Goal
SPEC §7.4 vegetation.

## Acceptance criteria
- [x] L-system or Geometry Nodes generator in assets_src/environments/vegetation/ (stochastic parametric L-system for frangipani; seeded numpy generators for palm, saltgrass, beach vine; Blender 5.0.1 glTF export)
- [x] Wind shader with a global wind uniform (`hymn_wind` / `hymn_wind_time`, vertex-colour weights, Low tier variant)

## Notes
- Everything is documented in docs/kb/art/environments/vegetation.md: parameters, adding a species, the wind channel convention, LODs, budgets, and an honest quality assessment.
- Shots `veg_backlit_fronds`, `veg_frangipani_close`, `veg_beach_wide` (scene `game/levels/_tests/vegetation/vegetation_test.tscn`) have approved baselines.
- Follow-ups for other roles:
  - Rendering: map the Low preset to `vegetation_foliage_low.gdshader`.
  - Character/M1-ART-02: absorb `VegetationPlant` (material map + visibility-range LODs) into a vegetation post-import script.
  - QA: add a `tests/unit` compile test (for now, `tools/tests/test_vegetation.py` runs `vegetation_shader_check.gd` headless).

## Review log
- 2026-10-23 rendering (review-sweep-B): **approve with fixes**. The shader is correct: an energy-conserving wrap diffuse, a height-correlated Smith GGX, `LIGHT_COLOR / PI` matching Godot 4's convention, and a custom transmission term that sensibly works around built-in BACKLIGHT being multiplied by full shadow. The mip coverage boost is a good call for scissored cards, and the wind channel convention is clean and documented. At wide and middle distance (`veg_beach_wide`) the species read correctly, and the self-assessment ("55–65% of a shipped AAA set": a starburst-regular crown, a grey-pipe frangipani bark, one-colour grass) matches what the baselines show. The issues are mostly about TAA and alpha in motion, light leaks and the test gate.
  - **should-fix (TAA and wind):** Godot does not produce motion vectors for vertex-shader displacement driven by globals (`hymn_wind_time`), so swaying cards reproject with zero motion, and TAA will smear or ghost alpha-scissored edges in motion, worst on the fast `COLOR.a` flutter. The stills can't show this. Capture a moving sequence on a GPU, cap the flutter amplitude on high-contrast sky-silhouette cards (palm leaflets), and record the result in vegetation.md. If ghosting is visible, test `ALPHA_HASH` against scissor under TAA, and FXAA on Low.
  - **should-fix (light leak):** `translucency_shadow_floor` (0.35) gives every shadowed leaf 35% sun transmission whatever the occluder is, so a frangipani under a Haluna eave or a cliff will glow. Scale the floor by crown depth (for example `mix(floor, 0.0, UV2.x)`, so only leaves inside a crown keep it) or add a per-instance "open sky" uniform. Add a test shot of a plant fully shadowed by a building.
  - **should-fix (test gate):** `threshold_rmse` 0.018 (2.25× the project default) is there only because the TAA jitter phase follows the global frame count. Do what the water rig does: swap TAA for FXAA under the capture scene, then return these shots to 0.008. Right now a real 1% regression in the alpha edges would pass.
  - **should-fix (LOD popping):** visibility-range LODs have no fade, so a 12–15 m palm against open sky will pop at 45/120/400 m, which is very visible in H01-type wides. Enable `visibility_range_fade_mode` (self/dither) at runtime, and turn it off only under capture.
  - **should-fix (cost, measurable now):** cost is unmeasured. Before Haluna dressing, capture `veg_beach_wide` and a dense crown close-up with `debug_draw = OVERDRAW` (this works on lavapipe) and record the overdraw factor. Alpha overdraw, not triangles, is the risk. Also do the open preset → `vegetation_foliage_low` mapping, and register both variants in `prewarm_materials.json`, since first-reveal compiles risk the SPEC §4.2 50 ms hitch.
  - **should-fix (placeholder policy):** "no PLACEHOLDER metadata needed, final-intent" doesn't fit a self-assessed 55–65% set. SPEC §8.4 relies on that tag to stop a zone being called art-complete. Tag the assets PLACEHOLDER until the revision pass, or have the Art Director sign them off as final in the zone gate.
  - **nit:** in `veg_backlit_fronds` the sun disc sits beside the crown, not behind it, so the forward lobe (`translucency_focus`) is barely exercised and the crown reads front-lit. Reframe so the sun is directly behind the leaflets, which is the case the term exists for.
  - **nit:** `tex_normal_trans` uses `hint_default_black`. An unassigned map gives a (−1, −1) normal tilt and zero translucency. Add a validator check or a `has_normal_map` bool.
  - **nit:** Godot flips only `NORMAL` on back faces, not the tangent frame, so back-face normal-map relief is mirrored. This is low impact on leaves, but note it in the gotchas.
  - **nit:** RG normals packed with B translucency under BC1/BC3 VRAM compression will band. Prefer the BPTC (high-quality) import for `*_normal.png`.
- 2026-10-23 lead: closing on review-sweep-B approve-with-fixes; should-fix items are tracked in M1-ENV-03.

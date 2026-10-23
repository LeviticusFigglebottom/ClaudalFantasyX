---
id: M1-RND-04
title: Skin, hair, eye, and cloth shaders for the M1 hero
role: rendering
status: done
owner_session: rendering-stream-4
reviewer: character
depends_on: []
milestone: M1
request-from: ""
---
## Goal
SPEC §8.2 items 4–6, supporting M1-CHR-02.

## Acceptance criteria
- [x] Pre-integrated skin with detail normal (`game/shaders/character/character_skin*`: analytic pre-integrated SSS fitted to the d'Eon six-Gaussian profile, with a max error of 0.018 against the integrated LUT; per-channel normal blur; sun-penumbra scatter; thin-region transmission; dual-lobe GGX; tiled pore detail normal; skin-mask micro-roughness; the `painterly` stylisation uniform)
- [x] Kajiya-Kay hair with dithered alpha + TAA (`character_hair*`: two shifted lobes on a flow-map tangent, strand variation, a back-lit transmission lobe, and temporal IGN dither in the opaque pipeline, chosen over hashed, static, blended and alpha-to-coverage with measurements; alpha scissor on Low)
- [x] Cornea and refraction eye (`character_eye*`: object-space eyeball with parallax refraction at IOR 1.376, concave iris, caustic, limbal ring; `character_cornea`: analytic-normal wet shell with specular AA; plus the eye-occlusion and tear-line helpers)
- [x] Cloth sheen with an embroidery mask (`character_cloth*`: Charlie sheen, embroidery, anisotropic gold thread, clear-coat lacquer, `verse_count` bands S0–S7 and the S8 dissolve, wind via vertex colours aligned with vegetation)

## Notes
- Delivered 2026-10-23 by rendering-stream-4. Parameters, tier differences, the map and geometry contracts for Character, the wind convention, cost estimates, and an honest fidelity assessment are in `docs/kb/tech/character_shading.md`.
- Tiers: Low, Medium and High variants per family (Ultra uses High). Every variant shares one uniform set, so `CharacterShaderTiers.apply_to_tree(root, tier_for_preset(id))` swaps tiers without losing parameters.
- Test stage: `game/levels/_tests/character_shading/shading_test.tscn`. The procedural test props come from `assets_src/characters/shader_test/` (Blender script plus numpy textures, 19 PROVENANCE rows). Shots: `char_skin_eye_closeup`, `char_hair_backlit`, `char_cloth_gold`, `char_low_compare`. Baselines are approved and bit-exact on re-capture.
- Tests: `tests/unit/test_character_shading.gd` (11): every variant compiles headlessly with its uniform contract, tiers share uniforms, includes compile alone, `verse_count` is an int 0..7, every preset maps to a tier, tier swapping keeps parameters, the fit constants match the generator and behave, prewarm registration, and stage assembly.
- Prewarm: 18 shader entries scoped to the test stage, with a `tier` key. ShaderPrewarm should filter by tier (RND-06), and the hero's scenes should be added when M1-CHR-02 lands.
- Deviations to confirm with Art: the hair secondary lobe at 0.3 instead of 0.5 for black hair (0.5 reads bronze on a flat sheet), `#8A5A3A` as the hair transmission colour, and the warm eye-occlusion tint.
- Everything was measured on lavapipe. GPU cost is estimated only (0.4–0.9 ms per hero for a 1440p close-up).
- Reviewer (Character): check that the map and geometry contracts in character_shading.md ("Map authoring requirements") are workable for the procedural Asha build, especially the eye object-space contract, the lid requirements, the hair flow-map variation, and the band-id texture. Also judge whether the painterly range is the right SPEC §14 fallback.

## Review log
- 2026-10-23 character (review-sweep-C): **approve with fixes**. The shader set and tier contract are solid, and the map/geometry contract is mostly buildable from a procedural Blender pipeline: the test-prop script already shows sorted triangulation, MikkTSpace tangents from Godot and `FLOAT_COLOR` wind attributes. I checked the char_* baselines against the doc. The eye is convincing (refraction, limbal ring, lid occlusion), cloth sheen, gold thread and the S8 dissolve edge read well, and hair transmission works against the rim. As the author says, the bust reads as a mannequin. That is a geometry gap, so the §14 uncanny-valley risk stays open until the Asha head exists. Painterly 0.2 is the right default. 1.0 as a fallback reads as cel, as stated, and needs authored albedo colour zones to be a real fallback. Ship it with the contract gaps below closed.
  - should-fix: `game/shaders/character/character_cloth_body.gdshaderinc:75,115` and contract row `character_shading.md:141`. `tex_band_id` is `filter_linear_mipmap`, and the contract says "mipmaps on for every map" (line 127). Bilinear filtering and mips between band 7 and blank 0 produce the values 1/7–6/7, which decode to bands 1–6. At `verse_count` 3, a texel-wide outline of hidden band 7's artwork shows. At battle distance the mips average whole hidden bands down into revealed ids, so S4+ bands leak in at range. Fix: `filter_nearest` (no mips) for the id map, and exempt id maps from the "mipmaps on" rule in the doc.
  - should-fix: character_shading.md:152 and the Wind section. The contract doesn't say how to author the vertex colours. A Blender *Byte Color* attribute is stored in sRGB and goes through a transfer on export, so a painted weight or phase of 0.5 arrives as about 0.21. The test props avoid this only because `build_shader_test_meshes.py:65` uses `FLOAT_COLOR`. Fix: state "use a FLOAT_COLOR point attribute named …, exported as COLOR_0" in the contract.
  - should-fix: character_shading.md:135 (detail normal). Pores tile in UV space, so the contract needs **uniform texel density across the head's UV islands**, with `detail_tiling` stated as a formula: tiles per UV unit = (mm of skin per UV unit) ÷ 27.5. "16 on a spherical UV" doesn't transfer, and unequal islands give visible pore-scale jumps at seams.
  - nit: character_shading.md:136. `*_hair` B ("vary it per strand or per layer") is a texture channel. When cards share one atlas, per-layer variation needs a separate atlas region per layer, or a per-card attribute (UV2.x). Vertex colour is taken by wind. Say which one the pipeline should use.
  - nit: eye contract. "+Z is the gaze (Blender −Y)" is correct for the glTF Y-up export, but say explicitly that the object transform must be applied with the origin at the eyeball centre *before* parenting to the eye bone. A bone-relative rotation baked into the mesh breaks the object-space iris.
- 2026-10-23 lead: closing on review-sweep-C approve-with-fixes; contract fixes in M1-RND-09, and the authoring implications were forwarded to M1-CHR-02.

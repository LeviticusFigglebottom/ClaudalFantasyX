---
id: M1-RND-04
title: Skin, hair, eye, and cloth shaders for the M1 hero
role: rendering
status: review
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

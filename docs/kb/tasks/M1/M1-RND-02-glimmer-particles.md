---
id: M1-RND-02
title: Glimmer motes (GPU particles, curl noise, gathering around the living)
role: rendering
status: review
owner_session: rendering-stream-3
reviewer: environment
depends_on: []
milestone: M1
request-from: ""
---
## Goal
SPEC §8.2 item 3.

## Acceptance criteria
- [x] Curl-noise motion, bloom, additive trails (`game/shaders/glimmer/glimmer_motes_process.gdshader`: one shared `hymn_curl_fbm3` field; HDR soft billboards with a core, a halo, and a velocity-stretched tail; Environment glow blooms them)
- [x] Attractor API so motes gather around and swirl near characters (`GlimmerField.add_attractor()`, up to 8 per field, plus the `hymn_glimmer_focus` global)
- [x] Test scene with a dusk shot and a night shot (`game/levels/_tests/glimmer/`: `glimmer_dusk`, `glimmer_night_held`, and `glimmer_release` at 50% of the release; baselines approved)

## Notes
- Delivered 2026-10-22 by rendering-stream-3. API, meaning rules, tunables, cost estimates, and gotchas: `docs/kb/tech/glimmer.md`.
- Modes: RELEASED (gold, rising spiral), HELD (cyan, sideways and down, absorbed by the sea), MACHINE (teal, still). `release(duration = 1.5 s, origin)` lerps hue and direction together in Oklab. It travels outward from the origin as a wave and still finishes the whole field in 1.5 s. Art should confirm this reading of colour-script rule 1.
- Night sea-glow: `hymn_sea_glow()` in `game/shaders/include/glimmer.gdshaderinc`, for the water stream (M1-RND-01) to call. Until then, `glimmer_sea_glow_overlay.gdshader` works as a `next_pass` on any sea material. It is gated by `hymn_glimmer.a > 0` and clamped to 0.04–0.15.
- Quality tiers by GraphicsSettings preset id: count ×0.35 / 0.6 / 1.0 / 1.5, trails off on Low, still-water reflection off on Low. No tier removes the motes.
- Tests: `tests/unit/test_glimmer_state.gd` (11) and `tests/unit/test_glimmer_field.gd` (16) cover colours vs palette, motion ranges vs the colour script, every pushed uniform existing in the shaders, and include constants vs palette.
- Costs are estimates. The lavapipe timings are CPU, not GPU.
- Follow-ups: register the glimmer materials in `prewarm_materials.json` (save them as `.tres` first). The screenshot order sensitivity (about 0.003 RMSE) is noted in glimmer.md.
- Reviewer (Environment): check that the test scenes read as "sacred and eerie" at the colour-script energies, that the zone-side contract (write `hymn_glimmer.a` per frame, or motes and sea-glow are off) suits zone authoring, and that still-water reflection fits lagoon zones.

## Review log

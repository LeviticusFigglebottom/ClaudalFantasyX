---
id: M1-RND-02
title: Glimmer motes (GPU particles, curl noise, gathering around the living)
role: rendering
status: done
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
- 2026-10-23 environment (review-sweep-B): **approve with fixes**. The API is clean and zone-friendly: a `GlimmerField` node, data-driven tunables, attractors that follow nodes, a field-wide `release()` wave from an origin, determinism for captures, and tiers that never remove the effect. HELD reads correctly in `glimmer_night_held` (cyan, sideways and down, with faint sea-glow beneath), and the Oklab lerp avoids mud mid-release. But the meaning rules read only partly. Released motes rise but don't spiral, and against a dusk sky they read as white sparkle rather than gold. Bound is not captured at all. Two slice requirements are also not supported yet.
  - **should-fix (slice H06):** there is no fixed-count, non-respawning field. `planned_amount()` = 450 × `amount_multiplier` × tier scale, with a 14 s lifetime that respawns, so H06's "exactly 9 on every preset, no respawn" (color_script `ch02`, Art request a) can't be authored, and it would be 3 motes on Low. Add `fixed_count` (which bypasses the tier scale), `one_shot`, and optional authored spawn points.
  - **should-fix (bound on a moving carrier):** motes are world-space (`motes.local_coords = false`, `glimmer_field.gd:456`), so a MACHINE field parented to Ilun (C10), a Vowbound summon or the Kite's lamps will leave its motes behind as the carrier moves. That breaks "moves only with its body" (Art request b). Use local coords for MACHINE, or add the carrier's velocity, and add a unit test with a moving parent.
  - **should-fix (capture the third rule):** there is no bound baseline. Add a `glimmer_bound` shot (a housing stand-in, ideally with a moving carrier) so "still = bound" is regression-gated like the other two.
  - **should-fix (released doesn't spiral):** `spiral_rate_rad_s` 0.3 is about 21 s per turn against a 14 s lifetime, so no mote completes a turn, and `glimmer_dusk` shows straight vertical streaks. Bible §2 and color script rule 1 say "slow vertical spirals". Raise it to about 0.8–1.2 rad/s (2+ turns per life), or tighten the radius so the curvature shows in the trails. Also map the `.dlg` cue kwargs (`motion=spiral_up`, `rate=slow`, `drift=down_seaward`, `count`, `form`) to explicit field parameters, since there is no `rate` today.
  - **should-fix ("sacred and eerie" vs. generic sparkle):** the dusk field fills the whole sky at even density, and the pale `#FFE9B8` core reads white against the warm horizon, so the shot looks like a screensaver. Warm the halo toward gold (your open item; Art to confirm) and give fields a density gradient, clustered near the figure and the water and sparse high in the sky. For HELD, the test field spawns high in the sky. Held motes should live low (0–3 m above the water, near the mourner), which is what makes them read as sinking. Show this in the test scene, because zone authors will copy it.
  - **should-fix (zone contract):** gating sea-glow on `hymn_glimmer.a` couples two things that zones author separately. A night frame that needs sea-glow but has motes on fixed energies must still set `a > 0`, which also lights every follow-scene field. Add a separate `hymn_sea_glow` energy global (shared with the M1-RND-01 review) and keep `a` for motes only. `ending_dock` then sets both to 0 explicitly.
  - **nit:** at 50% release, motes near the figure streak horizontally outward, which reads as a burst more than a lift. Rotate the velocity through vertical (slerp the direction, then scale the speed) instead of lerping the vector through the radial and swirl terms.
  - **nit:** the still-water reflection pass works only on calm water. On choppy lagoons nothing reflects the motes, because the water's SSR ignores transparents. Long term, the water shader should take a mote-reflection term.
  - **nit:** the glimmer.md example value "Ch2 2.5" is stale (Ch2 is 0.6, and 2.5 is Ch3; Art request c). Large near-lens halos in `glimmer_release` read as camera bokeh, so cap the screen-space halo size. Register the materials as `.tres` for prewarm (open item).
- 2026-10-23 lead: closing on review-sweep-B approve-with-fixes; should-fix items are tracked in M1-RND-08.

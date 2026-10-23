---
id: M1-RND-16
title: Scoped graphics override for storm cutscenes (FSR2 dither workaround)
role: rendering
status: doing
owner_session: "worktree-agent-aa764c62452184711"
depends_on: [M1-RND-11]
milestone: M1
request-from: "environment"
---
## Goal
M1-RND-11 found that the Undertow body's dither only partly integrates under FSR2 (−36 %, against −85 % under native TAA), because Godot 4.6 has no FSR2 reactive mask for transparent materials (docs/kb/qa/gpu/2026-10-23-rnd-11.md, "Mitigation for storm close-ups on High"). High is the default preset and uses FSR2, and the storm shots are Ch1, Ch8 and Ch20-21. The mitigation is prose only: cinematics needs an API so it does not rediscover this (review-sweep-I on RND-11, S4; filed by M1-RND-15).

## Acceptance criteria
- [ ] `GraphicsSettings` scoped override API, e.g. `push_override(owner, {"aa": "taa", "scaling_3d_mode": "fsr1"}) -> handle` / `pop_override(handle)`, applied behind a cut (no mid-shot pipeline switch), restored exactly on pop or when the owner leaves the tree, and never written to the player's settings.cfg
- [ ] Nested or overlapping overrides resolve deterministically (last pushed wins; popping restores the one below); tested headless
- [ ] Prewarm compiles the override's pipeline variant before the cut (`ShaderPrewarm.match_viewport` sees the overridden state, or the cutscene requests a prewarm for it)
- [ ] The Undertow's `temporal_jitter` gate (`UndertowStorm.viewport_is_temporal`) follows the override frame-exactly
- [ ] PC GPU: storm close-up dither crop measured on High with the override (target: within 10 % of native TAA), plus the override's cost
- [ ] docs/kb/tech/undertow.md and graphics_settings.md document the API; M2 cinematics tasks reference it

## Notes
- Alternative to weigh: add the storm to an FSR2 reactive mask if a later Godot exposes one (track upstream; ADR if we pin a newer engine).

## Review log

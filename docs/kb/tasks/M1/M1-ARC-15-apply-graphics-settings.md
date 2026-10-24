---
id: M1-ARC-15
title: The game never applies GraphicsSettings (presets have no effect in play)
role: architect
status: done
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M1-RND-12]
milestone: M1
request-from: "environment"
---
## Goal
Review-sweep-K on RND-12: no game code calls GraphicsSettings.apply or apply_current (only tools/gpu_bench), so sky_detail, vegetation_detail and every preset never reach the game, which runs the Ultra paths.

## Acceptance criteria
- [x] Boot applies the saved or default preset before the first scene; the settings menu applies on change; zone loads re-apply the per-scene parts (sky, water, Undertow tiers)
- [x] An integration test that boots, sets Low, and asserts the sky, vegetation, water and Undertow tiers are active
- [x] Confirm the incremental radiance cubemap updates when the sun turns (RND-12 S2)

## Notes
- 2026-10-23 architect (worktree agent-ad4be3355309b7593):
  - New `game/core/graphics_runtime.gd` (GraphicsRuntime).
  - Boot calls `GraphicsRuntime.boot(get_viewport())`.
  - SceneRouter gained `attach_graphics_hook`. This is a small additive hook in Systems-owned scene_router.gd: the new scene root's `ready` signal triggers the per-scene apply.
  - The menu API is `select_preset` / `set_override`. No graphics menu exists yet, so I filed M1-UI-10 for it.
  - Test: `tests/integration/test_graphics_runtime.gd` (6 tests).
  - graphics_settings.md has two new sections: "Applying in the game (M1-ARC-15)" and "Sky radiance and a turning sun".
- RND-12 S2:
  - Haluna's sun is Light Only, so the sky shader never sees it. Turning it changes neither the sky nor the radiance.
  - With Light and Sky, the Incremental radiance does follow the sun, converging within about 64 frames on lavapipe.
  - Probe: `tools/gpu_bench/sky_sun_probe.gd`. GPU checks are listed in the doc.
- Not done here:
  - ShaderPrewarm still stages authored tiers, not the preset's variants (Rendering follow-up).
  - Characters spawned at runtime need `CharacterShaderTiers.apply_to_tree` themselves.
  - M1-ENV-05's item "call apply_tiers after a zone loads" is now done by GraphicsRuntime.

## Review log
- 2026-10-24 review-sweep-Q (environment): **approve.** GraphicsRuntime is real. `boot()` applies the global part and arms the hook, and SceneRouter's `attach_graphics_hook` runs `apply_scene` on the new root's `ready` (main thread, after HalunaZone's prebuild). Settings changes go through `apply_now`, and the system tiers cover water, weathering, Undertow, glimmer, underwater and characters. `test_graphics_runtime.gd` boots, sets Low and asserts the tiers. The RND-12 S2 radiance answer is evidenced with a probe. 'Prewarm stages authored tiers' was resolved since, by M1-RND-22's `preset_tier` filter. `--filter=graphics`: 51/0.

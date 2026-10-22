---
id: M1-RND-06
title: Shader-cache warmup scene hooked into SceneRouter.prewarm_requested
role: rendering
status: review
owner_session: rendering-stream-1
reviewer: environment
depends_on: []
milestone: M1
request-from: ""
---
## Goal
SPEC §4.2: no hitch over 50 ms on battle transitions.

## Acceptance criteria
- [x] Warmup scene renders every registered material off-screen once (`game/core/shader_prewarm.tscn`; registry `game/data/settings/prewarm_materials.json`; spatial, particles, canvas_item, sky, and fog materials are supported)
- [x] Measured transition frame time logged (`finished(stats)` signal with `max_frame_ms` over `measure_frames`, printed, with a warning above `hitch_budget_ms` = 50)

## Notes
- Delivered 2026-10-22 by rendering-stream-1. Tests are in `tests/unit/test_shader_prewarm.gd` (6, headless): it completes, reports, and frees itself; filters by scene; hooks the router; and compiles the shader include.
- **Hook:** `ShaderPrewarm.install(router)` connects to `prewarm_requested` without changing `scene_router.gd`'s behaviour, but something must call it once. The proposed one-line change, for the Systems Architect, who owns `game/core/scene_router.gd`, goes at the end of `SceneRouter._ready()`: `ShaderPrewarm.install(self)`.
- End-to-end check (scratch script, not committed): real frames through `SceneRouter.change_scene("res://game/core/boot.tscn")` on 4.6.3 headless. Prewarm completed, logged stats, and freed itself. `spawn` plus `start` cost about 6 ms. The scene-swap frame itself measured **51–71 ms** with the dummy renderer, which is CPU-side work, *before* any GPU pipeline compile, so it's already over the 50 ms budget. The likely causes are the boot scene's first instancing or MSDF font glyph generation. This needs a QA or profiling look on real hardware.
- Shader conventions: `game/shaders/README.md`. Shared include: `game/shaders/include/common.gdshaderinc`. Global uniforms: `include/globals.gdshaderinc`, which needs `[shader_globals]` registered in `project.godot` before use.
- Headless runs Godot's shader *front end* (preprocessor, includes, parsing, type checks), lazily on first use. It does not run the GPU back end or check global-uniform registration.
- Reviewer (Environment): check that the registry format and `scenes` filter suit zone materials, and register zone materials as they land.

## Review log

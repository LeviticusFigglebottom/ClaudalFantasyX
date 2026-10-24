# 0028 — The Undertow's half-resolution body is a compute pass on the game camera's Compositor

- **Status:** proposed (Rendering; the Lead to accept on merge)
- **Date:** 2026-10-24
- **Roles affected:** Rendering, Tech (cameras, cutscenes), Environment (zone scenes with a storm)
- **Author role:** Rendering (PC GPU session, M2-RND-01)

## Context
SPEC §8.2.9 makes the Undertow the most important visual. M2-RND-01 put its raymarched body at half resolution
to fit the storm's GPU budget (High 4.94 → 2.27 ms). The body rendered in a SubViewport that sees only the body,
so it had no opaque depth. The composite stood in for it with an analytic test: drop the storm where the opaque
surface is nearer than the wall's foot cylinder.
- Geometry inside that cylinder wasn't occluded.
- A pillar placed inside the wall in the test scene was painted over completely, as if it weren't there
  (`docs/kb/qa/gpu/2026-10-23-m2-rnd-01-start.md`, "Compute body").
- Cinematics with the storm close, such as a boat in the eyewall or Ch20–21, need exact occlusion.

## Options
1. **Keep the SubViewport and feed it the game view's depth** through a small CompositorEffect copy. The
   SubViewport renders before the game view, so the depth would be a frame late, and reprojecting it is
   approximate.
2. **March the body as a compute pass in the game view** (a CompositorEffect at PRE_TRANSPARENT). It gets this
   frame's opaque depth and writes a texture that the existing composite lays over the frame in the transparent
   pass.
3. **Full resolution everywhere**, as Ultra does. Too costly on the recommended tier.

## Decision
Option 2. It's the default wherever a RenderingDevice exists (Forward+ and Mobile); the SubViewport path stays as
the fallback (Compatibility, headless) and as the A/B control (`UndertowStorm.half_res_compute = false`). Ultra
(full resolution) keeps the spatial body, which already clips against depth per sample.
- **One source of truth for the march.** The spatial body and the compute pass call the same
  `undertow_march()` (`undertow_body_march.gdshaderinc`).
- **Generated glue.** The compute side's uniform block, its GDScript layout and the flattened shader are
  generated from the spatial uniform declarations by `tools/rendering/gen_undertow_compute.py`. Godot's
  `.glsl` importer expands one include level only, and doesn't re-import when an included file changes. The
  twins carry a hash of the flattened body, so they change, and re-import, whenever it does. A unit test fails
  on stale outputs.
- **Attachment.** UndertowHalfRes keeps its effect on the *current* game camera's `Compositor`, creating one if
  the camera has none. It checks every frame, moves the effect when the camera changes, and removes it on
  teardown.

## Consequences
- **Exact occlusion inside the volume,** at full-resolution edges: the march clips at the farthest surface in
  each low-res pixel, and the composite drops pixels whose surface is nearer than what the storm shows.
- **Cheaper:** High 1440p Day 2.56 → 2.45 ms, Eye 3.11 → 2.84 ms, with no SubViewport pass.
- **Other camera code may set or replace `Camera3D.compositor`:** the storm re-appends its effect the next
  frame. A cutscene that adds its own compositor effects should append rather than replace, to skip that
  one-frame gap. The effect runs at PRE_TRANSPARENT, so its order among other effects doesn't matter for the
  storm.
- **The compute pipeline is created on the first frame the storm draws** (from SPIR-V baked at import). It isn't
  in the M1-RND-15 prewarm list yet; M1-RND-22 (prewarm hitch floor) should cover it.
- **Editing the storm's uniforms** means re-running the generator; the test catches a stale run.

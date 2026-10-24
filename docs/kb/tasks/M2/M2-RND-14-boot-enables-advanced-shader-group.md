---
id: M2-RND-14
title: Turn on Forward+'s advanced shader group at boot, whatever the AA setting (engine deadlock exposure)
role: rendering
status: todo
owner_session: ""
reviewer: qa
depends_on: [M2-QA-02]
milestone: M2
request-from: "qa"
---
## Goal
M2-QA-02 found a Godot 4.6.3 deadlock: `ShaderRD::version_get_shader()` holds a shader's version mutex while it waits for that shader's compile group, and pool pipeline compiles for the same shader block on that mutex. The window opens when the "advanced" scene-shader group (VoxelGI, motion vectors, SSS, lightmap variants) is turned on lazily, after a scene's shaders are loaded. Their compile is then queued behind pipelines already in flight. The capture harness now avoids it (`warm_shader_groups`, docs/kb/qa/screenshots.md "Engine deadlock").

In the game, the prewarm boot bring-up turns TAA on before any level loads, so the group is on early **when TAA is on**. A player with TAA off (and no SSS or lightmap at boot) turns the group on in the first VoxelGI room instead: the Shell Shrine, with the whole hall loaded. On a GPU the window is milliseconds, so the risk is low, but it should not depend on an AA setting.

## Acceptance criteria
- [ ] At boot, before any level's materials load, one render turns the advanced group on whatever the player's AA setting. For example, a hidden 8 px TAA SubViewport drawn once by the prewarm bring-up (see `ScreenshotCapture._warm_shader_groups`).
- [ ] No visible frame or measurable hitch at boot (ADR 0029 hidden-frame rules).
- [ ] A test that the bring-up does it with TAA off in the settings.

## Notes
- The engine fix itself (release the version mutex around the group wait, or wait collaboratively) belongs with the M1-ARC-17 / ADR 0032 engine-build decision.

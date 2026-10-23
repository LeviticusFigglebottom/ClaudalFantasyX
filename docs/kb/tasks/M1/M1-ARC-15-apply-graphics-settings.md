---
id: M1-ARC-15
title: The game never applies GraphicsSettings (presets have no effect in play)
role: architect
status: todo
owner_session: ""
depends_on: [M1-RND-12]
milestone: M1
request-from: "environment"
---
## Goal
Review-sweep-K on RND-12: no game code calls GraphicsSettings.apply or apply_current (only tools/gpu_bench), so sky_detail, vegetation_detail and every preset never reach the game, which runs the Ultra paths.

## Acceptance criteria
- [ ] Boot applies the saved or default preset before the first scene; the settings menu applies on change; zone loads re-apply the per-scene parts (sky, water, Undertow tiers)
- [ ] An integration test that boots, sets Low, and asserts the sky, vegetation, water and Undertow tiers are active
- [ ] Confirm the incremental radiance cubemap updates when the sun turns (RND-12 S2)

## Review log

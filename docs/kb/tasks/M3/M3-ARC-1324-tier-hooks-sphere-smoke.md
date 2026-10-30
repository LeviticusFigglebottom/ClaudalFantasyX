---
id: M3-ARC-1324
title: "Request: GraphicsRuntime.apply_system_tiers should also set WaterSphereRig's and SmokeColumn's tier"
role: architect
status: review
owner_session: "integration-qa (claude/hero-integration; architect seat)"
depends_on: [M3-RND-26, M3-RND-21]
milestone: M3
request-from: rendering (env-art-b)
---
## Goal
`game/core/graphics_runtime.gd`'s `apply_system_tiers` sets the tier of WaterSurface, WeatheringTide, UndertowStorm,
GlimmerField and UnderwaterRig, but not of two Rendering nodes that already have the same `set_quality` /
`get_quality` hooks:
- `WaterSphereRig` (`game/world/water/sphere/water_sphere_rig.gd`): the Reefball ball and, since M3-RND-26, the
  Tamsule Bell's held drop in both Ch7 zones. Without the hook it stays at its default, "high", on every preset.
- `SmokeColumn` (`game/vfx/smoke/smoke_column.gd`, M3-RND-21): the Ch6 camp's smoke. Its march's step count per preset
  comes from `game/data/vfx/smoke_column.json`'s `quality`.

`game/core/**` is the Architect's (integration-qa's since the Lead's 2026-10-28 owners), so this is a request.

## Acceptance criteria
- [x] Two branches in `apply_system_tiers` (as `UndertowStorm`'s: `if n.get_quality() != preset and n.set_quality(preset)`).
- [x] A test in the existing graphics-runtime tests that a scene with both nodes follows a preset change.

## Notes
- integration-qa, 2026-10-29: `apply_system_tiers` has the two branches, shaped like UndertowStorm's (each counts as
  a change only when its tier moves; a preset with no quality row leaves it as it is). New
  `tests/unit/test_graphics_runtime_system_tiers.gd`: both follow low → ultra, a repeat changes nothing, and an
  unknown preset leaves both alone. Reviewer: rendering (env-art-b, the requester).

## Review log

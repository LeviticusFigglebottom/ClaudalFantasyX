---
id: M1-ENV-05
title: Adopt vegetation_detail groups, preset tiers and hymn_water_level in Environment scenes
role: environment
status: todo
owner_session: ""
depends_on: [M1-RND-07, M1-RND-08]
milestone: M1
request-from: "rendering"
---
## Goal
M1-RND-07 and M1-RND-08 added the hooks Environment asked for. Rendering did not edit Environment-owned scenes or scripts, so these need adopting:

## Acceptance criteria
- [ ] Tag vegetation nodes with the `graphics_presets.json "vegetation_groups"`: `vegetation_lod` (meshes with authored `visibility_range_*`), `vegetation_multimesh` (grass/scatter MultiMeshInstance3D), `small_foliage` (grass, vines: nodes whose shadows Low may drop). Measured on an RX 9070 XT with the vegetation test tagged at runtime: vegetation_detail low saves 9-12% of the frame (docs/kb/qa/gpu/2026-10-23-rnd-07.md).
- [ ] Call `GraphicsSettings.apply_tiers(zone_root)` after a zone loads (Low swaps foliage to `vegetation_foliage_low` via `shader_families`).
- [ ] `WeatheringTide` (haluna_mood): read its tier from `GraphicsSettings.preset_tier(preset, "weathering")` instead of its own `PRESET_QUALITY`, and read `hymn_water_level` (x = current water Y, y = tide_line_y datum) instead of pushing per-material uniforms.
- [ ] Zone prewarm entries: the vegetation entries now carry `mesh` / `multimesh` (palm, frangipani, saltgrass); add `mesh` keys for kit materials whose meshes have non-default vertex formats, and the zone scene paths to `scenes`. With `scene_materials` on, inline materials of the incoming scene are prewarmed automatically.
- [ ] (added by M1-RND-15) Set `publishes_water_level = true` on each zone's sea WaterSurface (haluna_mood `Water`): it defaults to **false** since M1-RND-15, so pools and rivers never drive the zone's level, and a second publisher warns. `hymn_water_level` and `hymn_zone_sea_glow` are reset on every SceneRouter zone change, so a night zone must call `GlimmerField.set_scene_sea_glow(energy)` itself; `ending_dock` calls `set_scene_sea_glow(0.0)`, a hard off no material can override.

## Notes
Rendering tested all hooks with synthetic nodes; see tests/unit/test_graphics_settings.gd and test_water_surface.gd.

## Review log

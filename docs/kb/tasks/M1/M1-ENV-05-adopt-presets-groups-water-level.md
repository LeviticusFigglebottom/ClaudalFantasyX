---
id: M1-ENV-05
title: Adopt vegetation_detail groups, preset tiers and hymn_water_level in Environment scenes
role: environment
status: review
owner_session: "worktree-agent-aa764c62452184711"
depends_on: [M1-RND-07, M1-RND-08]
milestone: M1
reviewer: rendering
request-from: "rendering"
---
## Goal
M1-RND-07 and M1-RND-08 added the hooks Environment asked for. Rendering did not edit Environment-owned scenes or scripts, so these need adopting:

## Acceptance criteria
- [x] Tag vegetation nodes with the `graphics_presets.json "vegetation_groups"`: `vegetation_lod` (meshes with authored `visibility_range_*`), `vegetation_multimesh` (grass/scatter MultiMeshInstance3D), `small_foliage` (grass, vines: nodes whose shadows Low may drop). Measured on an RX 9070 XT with the vegetation test tagged at runtime: vegetation_detail low saves 9-12% of the frame (docs/kb/qa/gpu/2026-10-23-rnd-07.md).
- [x] (via M1-ARC-15) Call `GraphicsSettings.apply_tiers(zone_root)` after a zone loads (Low swaps foliage to `vegetation_foliage_low` via `shader_families`).
- [x] `WeatheringTide` (haluna_mood): read its tier from `GraphicsSettings.preset_tier(preset, "weathering")` instead of its own `PRESET_QUALITY`, and read `hymn_water_level` (x = current water Y, y = tide_line_y datum) instead of pushing per-material uniforms.
- [x] Zone prewarm entries: the vegetation entries now carry `mesh` / `multimesh` (palm, frangipani, saltgrass); add `mesh` keys for kit materials whose meshes have non-default vertex formats, and the zone scene paths to `scenes`. With `scene_materials` on, inline materials of the incoming scene are prewarmed automatically.
- [x] (added by M1-RND-15) Set `publishes_water_level = true` on each zone's sea WaterSurface (haluna_mood `Water`): it defaults to **false** since M1-RND-15, so pools and rivers never drive the zone's level, and a second publisher warns. `hymn_water_level` and `hymn_zone_sea_glow` are reset on every SceneRouter zone change, so a night zone must call `GlimmerField.set_scene_sea_glow(energy)` itself; `ending_dock` calls `set_scene_sea_glow(0.0)`, a hard off no material can override.

## Notes
Rendering tested all hooks with synthetic nodes; see tests/unit/test_graphics_settings.gd and test_water_surface.gd.

- 2026-10-23 environment (worktree-agent-aa764c62452184711), to review (rendering):
  - **Groups.** `VegetationPlant` tags every LOD mesh with an authored range `vegetation_lod`, and with
    `small_foliage = true` (the beach vines, in vegetation_test.tscn and `plant_kinds.beach_vine_patch.small_foliage`
    in haluna_layout.json) `small_foliage`. `VegetationScatter.tag()` puts grass scatters in `vegetation_multimesh` +
    `small_foliage` (+ `vegetation_lod` when they have a range); the Haluna dresser uses it for its scatters. Group
    names come from data: new `GraphicsSettings.vegetation_group(VEG_GROUP_*)`. Palms, frangipani and kit pieces keep
    their shadows. tests/unit/test_vegetation_groups.gd (tagging, Low -> High round trip on the real scene, dresser).
  - **apply_tiers after a zone loads: depends on M1-ARC-15** (First Playable session, `GraphicsRuntime.apply_scene`
    via SceneRouter's hook calls `apply_tiers` and `apply_system_tiers`, which sets `WeatheringTide.quality` from
    `quality_for_preset`). Not duplicated here; the API this branch exposes is what it calls.
  - **WeatheringTide.** Tier from `GraphicsSettings.preset_tier(preset, "weathering")` (`PRESET_QUALITY` removed,
    `TIER_NAMES` maps the tier names). It no longer writes material uniforms: it moves the sea to
    `water_height_y` and sets its `tide_line_y`; the sea publishes `hymn_water_level`; `env_weathering_body` and
    `env_ground` read the global (their `tide_line_y` / `water_height_y` uniforms are gone). Without a sea the tide
    writes the global itself.
  - **Publisher.** haluna_mood `Water` has `publishes_water_level = true` (the only one; tested). No night
    Environment zone exists yet, so no `set_scene_sea_glow` call was needed; the first night zone must make it.
  - **Prewarm.** Kit entries got `mesh` keys (a kit .glb with the real COLOR/UV2 format), the weathering tier
    variants draw on `tidewall_straight.glb`, and every Haluna and vegetation entry lists
    `game/levels/ch02/haluna/haluna.tscn` (and the mood scene). Added the two runtime-applied vegetation materials
    that had no entry (`frangipani_bark`, `beach_vine`). The generated terrain (`env_ground`) still prewarms on a
    quad (no static mesh to point at).
  - Shots: the five haluna_* and three veg_* shots render byte-identical before and after (lavapipe).

## Review log
- 2026-10-23 rendering (review-sweep-L, fresh reviewer): **approve, with should-fixes.** No blockers.
  - **What I read:** `git show` 88fcbaa: weathering_tide.gd, vegetation_plant.gd, vegetation_scatter.gd, haluna_dresser.gd, haluna_mood.tscn, the env_ground and env_weathering_body shaders, prewarm_materials.json, and test_vegetation_groups / test_environment_shaders. I also read water_surface.gd's publisher (:95-139).
  - **Checks:** Godot `--filter=` vegetation_groups 4/0 failed, environment_shaders 11/0, haluna 7/0, water_surface 13/0, graphics_settings 24/0. validate_data 0/0. No shots re-run, because the authors report byte-identical renders and the Lead's gate covers them.
  - **Single publisher:** exactly one WaterSurface per scene has `publishes_water_level = true`: haluna_mood `Water` (:94), water_test and undertow_test. The playable zone haluna.tscn instances the mood scene at identity and adds no water of its own. The publisher warns on a second one (water_surface.gd:100-110) and clears the level on exit. OK. No material still sets the removed `tide_line_y` / `water_height_y` uniforms (grep across .tres, .tscn and .json is empty).
  - **Should-fix:**
    - **S1: a sea that doesn't publish leaves the shaders on a stale level.** If `water` is set but `publishes_water_level` is false, `_ready` only warns (weathering_tide.gd:49-50), and `_push` moves the sea but writes no global (:81-85). Every weathering and ground material then reads 0,0 or the previous zone's value. Fall back to writing the global when `water` doesn't publish, as the no-sea branch already does.
    - **S2: the level lags one frame after a tide move.** WaterSurface publishes in `_process` only (water_surface.gd:126-128), so the wet line trails a flood rig's `water_height_y` by a frame, and is 0,0 before the first frame. That's invisible at tide speed. Note it in haluna_mood/README.md for the Drownbell flood rig.
  - **Nits:** env_weathering_body.gdshaderinc:12-14 keeps "the old note" naming the removed uniforms. Delete it rather than annotate it. vegetation_plant.gd:41 tags only LODs that are `visible` when `apply()` runs, so a mesh hidden by `force_lod` then and shown later is never tagged `vegetation_lod`.

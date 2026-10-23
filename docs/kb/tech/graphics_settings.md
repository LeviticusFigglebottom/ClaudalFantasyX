# Graphics Settings and Presets (M1-RND-05)

This page covers the backend for the SPEC §4.2 settings menu. The data lives in `game/data/settings/graphics_presets.json`, the code is `game/core/graphics_settings.gd` (`class_name GraphicsSettings`), and the tests are in `tests/unit/test_graphics_settings.gd`. The menu UI belongs to UI with Rendering (ADR 0002) and only calls this API.

> **Every cost on this page is an estimate.** Nothing here has been measured on a GPU yet. CI runs the headless dummy renderer, which draws nothing. The figures come from typical Godot 4 Forward+ costs for each feature at the stated resolution, and they should be read as ±50%. Replace them with measured numbers once the GPU runner exists (M1-QA-01). Until then, treat the budgets as targets to check, not facts.

## How it works

```gdscript
var gs := GraphicsSettings.new()          # loads graphics_presets.json, preset = default ("high")
gs.load_config()                          # user://settings.cfg [graphics]: preset + overrides
gs.set_preset("medium")                   # clears overrides (pass true to keep them)
gs.set_override("ssr", false)             # custom layer; rejected unless the value is in the option list
gs.save_config()                          # other sections of settings.cfg are preserved
gs.apply_current(get_viewport(), world_environment.environment)
var ops := gs.plan("low")                 # pure: no side effects; what apply() would do
```

- **`resolve(x)`** turns `null` (the current preset plus overrides), a preset id, or `{"preset": id, key: value...}` into a complete, type-normalized settings dictionary. Invalid keys and values are ignored with a warning.
- **`plan(x)`** is pure. It maps the resolved settings to an ordered `Array[Dictionary]` of operations:
  - `{"target": &"viewport", "op": &"set", "name": <Viewport property>, "value": v}`
  - `{"target": &"environment", "op": &"set" | &"gate", "name": <Environment property>, "value": v}`
  - `{"target": &"rendering_server", "op": &"call", "name": <RenderingServer method>, "args": [...]}`
  - `{"target": &"group", "op": &"gate", "group": "gi_voxel", "name": "visible", "value": bool}`
- **`execute(ops, viewport, environment)`** (static) performs those operations. It skips viewport and environment operations when their target is `null`. RenderingServer operations are global and always run.
- **Gates.** A player setting can only turn a feature **off**. It never adds fog, SSR, or GI to a zone that wasn't authored with it. For gated properties, the zone's authored value is captured once in object metadata (`hymn_authored_<property>`), and the result is `authored AND allowed`. A cutscene that changes a gated property at runtime calls `GraphicsSettings.set_authored(env, "volumetric_fog_enabled", true)`.
- **GI mode is a ceiling.** `off` disables SDFGI and hides every VoxelGI node in group `gi_voxel`. `voxel_gi` allows VoxelGI only. `sdfgi` allows both. Each zone still picks its technique (SPEC §8.1), and LightmapGI is baked and always on. **Zones must put VoxelGI nodes in group `gi_voxel`** (Environment role).
- **FSR2 runs its own temporal AA**, so `plan()` forces `use_taa = false` whenever `scaling_mode` is `fsr2` (`rules.temporal_upscaler_modes` in the data).
- **When to apply.** Call `apply` from the settings menu and after each zone load. A zone brings its own Environment, so its gates and quality need applying again. Shadow-atlas resizes reallocate GPU memory, and SDFGI changes make GI reconverge visibly, so apply behind a fade, never per frame. None of these settings needs a restart.

## Settings and the 4.6 API each one drives

Every name below was checked against Godot **4.6.3-stable** with `ClassDB.class_has_method`, `ClassDB.class_get_property_list`, and `ClassDB.class_has_integer_constant`. `test_planned_engine_api_names_exist_in_this_godot` re-checks every planned operation, including argument counts, on each CI run. An engine upgrade that renames an API fails the tests.

| Setting | Options | Engine calls |
|---|---|---|
| `gi_mode` | off / voxel_gi / sdfgi | gate `Environment.sdfgi_enabled`; gate `visible` on group `gi_voxel` |
| `sdfgi_quality` | low / medium / high / ultra | `Environment.sdfgi_cascades`, `Environment.sdfgi_use_occlusion`, `RenderingServer.environment_set_sdfgi_ray_count`, `environment_set_sdfgi_frames_to_converge`, `environment_set_sdfgi_frames_to_update_light` |
| `voxel_gi_quality` | low / high | `RenderingServer.voxel_gi_set_quality` |
| `gi_half_resolution` | bool | `RenderingServer.gi_set_use_half_resolution` |
| `shadow_atlas_size` | 1024–8192 | `Viewport.positional_shadow_atlas_size` |
| `directional_shadow_size` | 1024–8192 | `RenderingServer.directional_shadow_atlas_set_size(size, is_16bits)` |
| `shadow_16_bits` | bool | `Viewport.positional_shadow_atlas_16_bits`, plus the arg above |
| `soft_shadow_quality` | hard / very_low / low / medium / high / ultra | `RenderingServer.directional_soft_shadow_filter_set_quality`, `positional_soft_shadow_filter_set_quality` |
| `volumetric_fog` | bool | gate `Environment.volumetric_fog_enabled` |
| `volumetric_fog_volume_size` / `_depth` | 64–192 / 32–128 | `RenderingServer.environment_set_volumetric_fog_volume_size(size, depth)` |
| `volumetric_fog_filter` | bool | `RenderingServer.environment_set_volumetric_fog_filter_active` |
| `ssr` | bool | gate `Environment.ssr_enabled` |
| `ssr_max_steps` | 16–128 | `Environment.ssr_max_steps` |
| `ssr_roughness_quality` | disabled / low / medium / high | `RenderingServer.environment_set_ssr_roughness_quality` |
| `ssao_quality` | off / very_low … ultra | gate `Environment.ssao_enabled`; `RenderingServer.environment_set_ssao_quality(quality, half_size, adaptive_target, blur_passes, fadeout_from, fadeout_to)` |
| `ssil_quality` | off / very_low … ultra | gate `Environment.ssil_enabled`; `RenderingServer.environment_set_ssil_quality(...)` (same 6 args) |
| `render_scale` | 0.5 / 0.59 / 0.67 / 0.77 / 0.85 / 1.0 | `Viewport.scaling_3d_scale` |
| `scaling_mode` | bilinear / fsr / fsr2 | `Viewport.scaling_3d_mode` = `SCALING_3D_MODE_BILINEAR` / `_FSR` / `_FSR2` |
| `fsr_sharpness` | 0.0–2.0 (0 = sharpest) | `Viewport.fsr_sharpness` |
| `aa` | none / fxaa / smaa / taa / msaa_2x / msaa_4x | `Viewport.use_taa`, `Viewport.screen_space_aa` (`SCREEN_SPACE_AA_DISABLED` / `_FXAA` / `_SMAA`), `Viewport.msaa_3d` (`MSAA_DISABLED` / `_2X` / `_4X`) |
| `lod_threshold` | 0.5 / 1 / 2 / 4 px | `Viewport.mesh_lod_threshold` (the "LOD bias": higher means coarser) |
| `anisotropic_filtering` | off / 2x / 4x / 8x / 16x | `Viewport.anisotropic_filtering_level` (`ANISOTROPY_*`) |

Notes from the verification:
- `SCREEN_SPACE_AA_SMAA` exists in 4.6, so SMAA is offered alongside FXAA. `SCALING_3D_MODE_METALFX_*` also exist but are macOS-only and aren't offered.
- The project setting for the directional shadow size is `rendering/lights_and_shadows/directional_shadow/size`, not `rendering/shadows/...`. It isn't used, because the runtime call above replaces it.
- ProjectSettings equivalents exist for startup defaults (`rendering/environment/volumetric_fog/volume_size` and `volume_depth`, `rendering/global_illumination/sdfgi/probe_ray_count`, `rendering/global_illumination/voxel_gi/quality`, `rendering/scaling_3d/mode`, `rendering/anti_aliasing/quality/screen_space_aa`, `rendering/textures/default_filters/anisotropic_filtering_level`, and `rendering/mesh_lod/lod_change/threshold_pixels`). `project.godot` is left alone: runtime `apply` wins.

## Presets

| | Low | Medium | High | Ultra |
|---|---|---|---|---|
| §4.2 tier | **Minimum** (GTX 1060 / RX 580) | between | **Recommended** (RTX 3060 / RX 6600) | above recommended |
| Target | 1080p, 30–60 fps | 1080p60 on mid cards | **1440p60** | 1440p60 on RTX 3080 / 4070 class |
| GI | off | VoxelGI (low) | SDFGI medium, half-res | SDFGI ultra, full-res |
| Shadows (sun / positional / soft) | 2048 / 2048 / very low | 4096 / 4096 / low | 4096 / 4096 / medium | 8192 / 8192 / high |
| Volumetric fog | 64×32, no filter | 96×64, filter | 128×64, filter | 192×128, filter |
| SSR | off | 32 steps, low roughness | 64 steps, medium | 128 steps, high |
| SSAO / SSIL | very low / off | medium / off | high / medium | ultra / high |
| Render scale | 0.77, FSR1 | 0.85, FSR1 | 0.77, FSR2 | 1.0 native |
| AA | TAA (M1-RND-07: FXAA left alpha-tested foliage shimmering) | TAA | FSR2 temporal | TAA |
| LOD threshold / aniso | 2 px / 4x | 1 px / 8x | 1 px / 16x | 0.5 px / 16x |

Volumetric fog stays **on** even at Low, at the smallest volume. Light shafts and glimmer haze carry the art direction (SPEC §1 pillar 2 and §7.1), and a 64×32 froxel grid is cheap. Players can still turn it off.

## Performance budget per preset (estimates; not measured)

Frame budget: 16.7 ms at 60 fps and 33.3 ms at 30 fps. Costs are GPU milliseconds at the internal render resolution. "Base" is opaque geometry, clustered lighting, sky, glow, and tonemap for a typical M2 vertical-slice view. It depends on the scene and is the shakiest number here.

**High on the recommended tier (RTX 3060, 1440p output, 0.77 → ~1971×1109 internal):**

| Item | Est. ms |
|---|---|
| Base | 5.0 – 7.0 |
| Shadows (4096 sun + atlas, soft medium) | 1.0 – 2.0 |
| SDFGI medium, half-res | 1.5 – 2.5 |
| Volumetric fog 128×64 | 0.7 – 1.2 |
| SSR 64 steps | 1.0 – 1.5 |
| SSAO high (full) + SSIL medium (half) | 1.6 – 2.4 |
| FSR2 to 1440p | 0.6 – 0.9 |
| Procedural sky clouds, `sky_detail` high (measured 0.39 – 0.42 ms on an RX 9070 XT × 2.3 – 2.8, M1-RND-12) | 0.9 – 1.2 |
| **Total** | **≈ 12.3 – 18.7** (target ≤ 16.7) |

High is the tight preset. If measurement shows it over budget, step down in this order: `ssil_quality` medium → low, `render_scale` 0.77 → 0.67 (FSR2 Quality), then SDFGI rays.

**Low on the minimum tier (GTX 1060, 1080p output, 0.77 → ~1478×831 internal):**

| Item | Est. ms |
|---|---|
| Base | 6.0 – 9.0 |
| Shadows (2048, very low) | 0.8 – 1.5 |
| GI | 0 |
| Volumetric fog 64×32, no filter | 0.5 – 0.8 |
| SSAO very low (half) | 0.4 – 0.6 |
| FSR1 + TAA | 0.5 – 0.8 (TAA measured +0.12 ms on an RX 9070 XT at 1080p) |
| Procedural sky clouds, `sky_detail` low (measured 0.21 – 0.24 ms on an RX 9070 XT × 4.2 – 5.0, M1-RND-12) | 0.9 – 1.2 |
| **Total** | **≈ 9.0 – 13.7** (30 fps is safe; 60 fps likely in lighter scenes) |

**Medium on the minimum tier (GTX 1060, 1080p, 0.85):** about 14 – 20 ms (VoxelGI 1–2 ms, SSR 0.8 ms, SSAO 0.7 ms, fog 0.8 ms, TAA 0.3 ms on top of a larger base). That's a 30–60 fps preset for the minimum tier, or 60 fps on GTX 1660 / RTX 2060 class cards.

**Ultra on the recommended tier (RTX 3060, native 1440p):** about 23 – 31 ms. SDFGI ultra at full resolution alone is 4–6 ms, plus SSR 128 steps (2.5–3.5), SSIL high (2–3), and fog 192×128 (2–3). Ultra is **not** expected to hold 60 fps on the recommended tier. It's meant for stronger GPUs and for capturing screenshots and trailers.

**VRAM (approximate, by arithmetic):** a 16-bit shadow atlas is 8 MB at 2048², 32 MB at 4096², and 128 MB at 8192². Ultra holds two 8192² atlases (≈256 MB). The volumetric fog froxel buffers grow with size² × depth, from roughly 5 MB at 64×32 to about 150 MB at 192×128, depending on how many RGBA16F volumes the 4.6 implementation allocates. That needs measuring. The minimum tier has 3–4 GB of VRAM, which Low fits comfortably.

## Per-system tiers, shader families and vegetation detail (M1-RND-07)

- **`presets[].tiers`** gives each system's quality tier: `water` (read by `WaterSurface.quality_for_preset`), `vegetation`, `weathering`. Query it with `GraphicsSettings.preset_tier(preset, system)`. Undertow, glimmer and character tiers are the preset id itself, in their own data.
- **`shader_families`** plus `apply_tiers(root)`: after a zone loads, and after a preset change, call `gs.apply_tiers(zone_root)`. It swaps every material whose shader belongs to a family to the variant for the preset's tier. On Low, foliage goes to `vegetation_foliage_low`.
- **`vegetation_detail`** (low / medium / high / ultra) drives three node groups (`vegetation_groups`), which zones tag:
  - `vegetation_lod`: authored `visibility_range_begin/end` × 0.6 / 0.8 / 1.0 / 1.3 (authored values captured once);
  - `vegetation_multimesh`: MultiMesh `visible_instance_count` fraction 0.5 / 0.75 / 1 / 1;
  - `small_foliage`: `cast_shadow` turned off on Low.

  Measured: −9 to −12 % of the vegetation test's frame on Low.
- **Low AA is TAA** (it was FXAA). Measured on alpha-tested foliage: FXAA removed 10 % of the shimmer, TAA 65 %, for +0.12 ms on an RX 9070 XT (docs/kb/qa/gpu/2026-10-23-rnd-07.md).
- **`sky_detail`** (low / medium / high / ultra, M1-RND-12) sets the procedural sky's quality uniforms on the
  Environment's sky material (`levels.sky_detail`; only uniforms the sky's shader declares, so other skies are
  untouched): march steps 32 / 32 / 40 / 64, erosion octaves 2 / 3 / 4 / 4, erosion seen by the sun samples
  0 / 0 / 0 / 1, radiance-cubemap steps 16 / 24 / 24 / 24. Measured cloud cost on an RX 9070 XT (Haluna H01/H04/H07):
  0.21–0.24 ms (Low, 1080p), 0.34–0.37 (Medium, 1440p), 0.39–0.42 (High, 1440p), 1.1–1.2 (Ultra, 1440p). The
  cost follows the window resolution, not `render_scale`. Below 32 steps the cloud silhouettes step, so no tier goes
  lower (tested).

## Open items
- **Measure** every row above on a GPU runner (M1-QA-01) and replace the estimates. Add a per-preset benchmark camera path to the vertical-slice zone when one exists.
- Localization rows for the `*_key` fields in `graphics_presets.json` (`GFX_PRESET_LOW`, `GFX_GI_MODE`, …) still need adding to `game/data/loc/strings.csv` (owner: Systems/UI). `tools/validate_data.py` doesn't scan `game/data/settings/` yet.
- Zones must tag VoxelGI nodes with group `gi_voxel` (Environment), and vegetation with the `vegetation_groups` (M1-ENV-05).
- The mapping from preset to shader quality variant (`HYMN_QUALITY`, see `game/shaders/README.md`) gets added when the first variant shader lands.

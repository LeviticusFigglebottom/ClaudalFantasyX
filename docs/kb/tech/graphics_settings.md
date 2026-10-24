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
- **When to apply.** The game does this through `GraphicsRuntime` (next section): boot, every SceneRouter zone load, and the settings menu. A zone brings its own Environment, so its gates and quality need applying again. Shadow-atlas resizes reallocate GPU memory, and SDFGI changes make GI reconverge visibly, so apply behind a fade, never per frame. None of these settings needs a restart.

## Applying in the game (M1-ARC-15)

Before M1-ARC-15 nothing in the game called `apply`, so every preset ran the authored (Ultra) paths. `game/core/graphics_runtime.gd` (`class_name GraphicsRuntime`, Systems-owned) now owns the game's one `GraphicsSettings` and applies it at three points:

| When | Who calls | What runs |
|---|---|---|
| Boot, before the title draws | `boot.gd` `_ready`: `GraphicsRuntime.boot(get_viewport())` | Loads `user://settings.cfg` [graphics] (no file: `default_preset`). Applies the **global part**: the Viewport and RenderingServer operations. Arms the per-scene hook. |
| Every zone load | `SceneRouter._swap` → `attach_graphics_hook(node, stats)`, which connects the new scene root's `ready` signal (one-shot) | `GraphicsRuntime.on_scene_entered(root)` → `apply_scene(root)`: the **per-scene part**. `stats["graphics_ops"]` records the count. |
| A settings change | The Graphics page (`GraphicsMenu`, M1-UI-10; see "The Graphics menu" below): `select_preset(id, viewport)` / `set_override(key, value, viewport)` | Saves `settings.cfg`, then `apply_now(viewport)`: the global part plus the per-scene part on `current_scene`. |

The per-scene part, `apply_scene(root)`, does the following:
- **Operations.** It runs the Environment, sky and group operations of `plan()` against the first `WorldEnvironment` under the root. Those are the gates, `sky_detail` uniforms, `gi_voxel` and the `vegetation_*` groups.
- **Shader families.** It calls `apply_tiers(root)`, which swaps foliage to `vegetation_foliage_low` on Low.
- **System tiers.** `apply_system_tiers(root, preset)` sets the tier of each system that keeps its own preset map:
  - `WaterSurface.quality_for_preset`
  - `WeatheringTide.quality_for_preset`
  - `UndertowStorm.set_quality(preset)`
  - `GlimmerField.set_quality(preset)`
  - `CharacterShaderTiers.apply_to_tree`

  A node whose tier already matches is not touched, so a storm or glimmer field is not rebuilt for nothing.

Notes:
- **Why the root's `ready`.** It fires on the main thread, with the scene in the tree, after every child's `_ready`, and before the first frame draws the scene. HalunaZone's worker-thread prebuild has finished by then. When Haluna is instanced on the main thread, its mood dresses itself in `_ready`, so the dressed nodes exist in either case. The hook adds no frame and runs under the opaque fade.
- **Disarmed outside the game.** The test runner, screenshot captures (`tests/screenshots/capture.tscn`) and `tools/gpu_bench` never call `boot()`, so their scenes keep rendering their authored tiers, as before. `boot_title` renders `boot.tscn` and so does apply the default preset, but that is a 2D screen, which the viewport's 3D settings don't change.
- **Tests.** `tests/integration/test_graphics_runtime.gd` covers every point above. It boots with Low saved, loads a fixture through the router hook (a cumulus sky with authored SSR and SDFGI, the three vegetation groups with a foliage-family material, a sea, a weathering tide and an Undertow storm) and asserts each tier against the data. It also checks the disarmed hook, the menu path (select High, then a `vegetation_detail` override, both saved) and the real Haluna zone (Low sky uniforms, water and weathering).
- **Known gaps.**
  - **ShaderPrewarm stages the incoming scene's authored materials.** On Low the swapped variants (water low, weathering low, foliage low, the character low shaders) compile on their first draw, which comes after the hook, under the fade. Making the prewarm stage the preset's variants is a Rendering follow-up.
  - Characters spawned after the zone loads need `CharacterShaderTiers.apply_to_tree(node, CharacterShaderTiers.tier_for_preset(GraphicsRuntime.settings().preset_id))`.
  - Zones still have to tag their vegetation groups (M1-ENV-05). `apply_tiers` after a zone load is now done here.

### Sky radiance and a turning sun (RND-12 S2)

This was measured on lavapipe with `tools/gpu_bench/sky_sun_probe.gd` (haluna_mood, H01, `Sky.process_mode` Incremental, the sun turned 120° about Y). Lavapipe draws through the same Forward+ sky path as a GPU, so the **behavior** carries over. The frame counts depend on the renderer.

- **Haluna's sun never reaches the sky shader.** `Sun.sky_mode` is **Light Only** (`sky_mode = 1`), following the water.md convention that stops the sky's sun disc doubling the water's glint. In that mode Godot hides the light from sky shaders, so `env_sky_cumulus` always runs with `LIGHT0_ENABLED` false. Its sun glow, sun disc and cloud lighting use the fallback: light from the zenith, clouds at 0.3.
  - Turning the sun changed neither the visible sky (pixel diff 0.0000) nor the radiance. The mirror sphere stayed at the noise floor (≈ 0.001) for 64 frames.
  - This is why RND-12's `--spin-sun` measured no re-render cost. Nothing depends on the sun, so nothing re-renders.
  - The same Light Only setting is on undertow_test, water_test and haluna_kit_sheet.
- **With the sun visible to the sky** (`SKY_MODE_LIGHT_AND_SKY`), the Incremental radiance **does** follow it.
  - Godot dirties the sky's reflection when a sky-visible directional light's direction, colour or energy changes.
  - The mirror sphere's difference from its pre-turn image rose from 0.0027 (1 frame) to 0.0064 (64 frames). Its difference from the fully re-rendered reference fell from 0.0041 to 0.0012, the noise floor.
  - So the cubemap is re-rendered and the roughness layers are filtered over the following frames. The mirror mean went from 0.664 to 0.666 against the reference's 0.666.
  - The sky with the sun visible is also brighter: mirror mean 0.66 against 0.57 with Light Only.
- **What to check on a GPU** (Rendering / Art Director):
  1. Decide whether Haluna's sky should see the sun. Today the clouds are lit from the zenith whatever the time of day. Enabling it means re-solving the doubled glint another way, for example by hiding the sky's sun disc in the reflection pass with `AT_CUBEMAP_PASS`, which the shader already branches on. All five `haluna_*` baselines would drift.
  2. If it does: run `gpu_bench --variants=sky --spin-sun=<deg>` with `Sun.sky_mode` set to Light and Sky. Check the frame p99 for the time-sliced re-render, and run this probe on the GPU to see how many frames the reflections take to converge.
  3. A sun that moves continuously dirties the radiance every frame. Watch whether the Incremental mode's higher roughness layers ever finish, because ambient light comes from them. A slow time-of-day sun may need to be stepped, for example re-aimed every N frames.

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

## Scoped overrides (M1-RND-16)

A cutscene or other scene-owned moment can change the game viewport's AA and 3D scaling for its duration
without touching the player's settings. The keys it may name are `rules.override_keys` in
graphics_presets.json: `aa`, `scaling_mode`, `render_scale`, `fsr_sharpness` (the viewport pipeline state;
everything else is per-scene and the zone owns it).

```gdscript
# At a camera cut (or behind a fade): never mid-shot, the pipeline switches on the next frame drawn.
var h := GraphicsSettings.push_override(self, {"aa": "taa", "scaling_mode": "fsr"})
# ... the storm close-up ...
GraphicsSettings.pop_override(h)   # at the cut out; also automatic when `self` leaves the tree
```

- **Layering.** The override is laid on the player's settings (`base`, default: user://settings.cfg, or the
  default preset when there is none; after M1-ARC-15 pass `GraphicsRuntime.settings()`), then planned like
  any preset, so the FSR2 rule (TAA forced off under a temporal upscaler) still holds. Only the viewport
  properties are written: `scaling_3d_mode`, `scaling_3d_scale`, `fsr_sharpness`, `use_taa`,
  `screen_space_aa`, `msaa_3d`.
- **Stacking.** Overrides stack and resolve key by key: the last pushed wins, popping any one re-applies the
  rest in push order, and when the last one goes the viewport gets back exactly the values it had before the
  first (a snapshot, so it also restores a viewport that never had settings applied, like a test's). All
  overrides target one viewport at a time; a push to a second one is refused. Invalid keys or values are
  refused (handle 0) and change nothing.
- **Never saved.** Nothing here calls `save_config`; the player's preset and override layer are untouched.
- **Listeners.** After every push or pop, nodes in `GraphicsSettings.VIEWPORT_STATE_GROUP`
  (`hymn_viewport_state_listeners`) get `on_viewport_state_changed()`. UndertowStorm uses it to re-gate its
  temporal jitter in the same frame.
- **Prewarm.** `GraphicsSettings.override_state(values)` returns the viewport state an override would set
  without applying it. Give it to `ShaderPrewarm.spawn_with_state(scene, SceneRouter, state)` (or set
  `viewport_state` before `start`), so the stage compiles the override's pipeline before the cut. An
  override pushed before a zone loads is seen by the router's own prewarm, which copies the live viewport.
- **Caveat until M1-ARC-15 lands here:** a settings-menu apply while an override is active writes the
  player's AA over it; the cutscene's pop then restores the pre-override snapshot, which is the old setting.
  Menus are not reachable during cutscenes today.

## The Graphics menu (M1-UI-10)

(M2-UI-09: the title's Settings row and the field menu's Settings row now open a Settings hub, Graphics and Accessibility, whose Graphics row is this page; the page is reachable in the field, so the in-game fade below matters: M1-UI-11 on claude/m2-slice.) The title's **Settings** row opens the Graphics page (`game/ui/settings/graphics_menu.gd`, `GraphicsMenu`; logic in `graphics_menu_model.gd`, `GraphicsMenuModel`; layout and value labels in `game/data/ui/graphics_menu.json`). It's a modal page over a dark backdrop, built on `MenuPage`, with the value of each row in the right column. The page shows 14 rows at a time and scrolls with the cursor.

- **Rows.** The preset comes first. It shows the preset's `name_key`, or **Custom** while `is_custom()`. Then comes every setting of this file's `settings`, in order, labelled by its `label_key`.
- **Input.** `ui_left` / `ui_right` step a value through its `options`, wrapping; `ui_accept` and a click on the current row step forward. `ui_up` / `ui_down` move, and `ui_cancel` closes the page.
  - The preset row calls `GraphicsRuntime.select_preset`, which clears every override.
  - A setting row calls `GraphicsRuntime.set_override`.
  - Both save `user://settings.cfg` and apply at once.
- **Values.** Booleans read On or Off. String options read through `value_keys`, so `msaa_2x` shows as "MSAA 2×". `render_scale` reads as a percentage and `lod_threshold` as a multiplier; other numbers print as they are. `tools/tests/test_graphics_menu_data.py` fails if an option has no label or a key has no loc row.
- **A preset change applies behind a veil (M1-UI-11).** Once boot has armed `GraphicsRuntime`, `select_preset` runs `warm_resident_shaders(viewport)` (M1-RND-22), and that warm-up froze a frame for 0.53–1.66 s on the PC. So with `GraphicsRuntime.armed` and the viewport in the tree, `GraphicsMenu` doesn't call the model at once:
  1. It fades an opaque veil in over `apply.fade_out_sec` (the backdrop's `panel_low`, with the `GFX_MENU_APPLYING` card).
  2. It lets `apply.settle_frames` opaque frames draw, so the freeze happens under a covered screen, and only then calls `GraphicsMenuModel.cycle`, which calls `select_preset`.
  3. It holds while the warm-up lives. `GraphicsRuntime.last_warmup` is the node `warm_resident_shaders` returned, and the model tracks it if the change spawned a new one. `GraphicsMenuModel.warmup_done()` is true once its `finished` signal fired, or it freed or was queued for deletion, or it isn't running (a failed `start()`). `apply.max_hold_sec` is a safety net.
  4. It fades back over `apply.fade_in_sec`.

  Throughout, `handle_input` swallows every event, clicks on rows are ignored, `close()` waits, and the veil stops the mouse. When `GraphicsRuntime` is disarmed (tests, captures), nothing warms, so a preset applies at once, as before.
- **A setting row spawns no warm-up, so it has no veil.** `set_override` only saves and runs `apply_now`. The tiers that pick shader variants (character, water, vegetation, weathering, Undertow, underwater) aren't settings: they come from the preset id (`presets[].tiers`, `CharacterShaderTiers.tier_for_preset`, the Undertow and glimmer preset maps). `settings` has no tier key, and an override can't change one. `vegetation_detail` only toggles the vegetation groups (LOD, MultiMesh, small shadows); the foliage shader family follows the preset's `vegetation` tier. What an override does change (a shadow-atlas resize, SDFGI re-converging) happens behind the 2D title with no shader compile. An in-game pause menu would want the same veil for those; there's no pause menu yet.
- **Tests:** `tests/unit/test_graphics_menu.gd`, including the title row, and `tests/unit/test_graphics_menu_apply.gd` (M1-UI-11: armed, the page is inert while the warm-up lives, and the veil lifts after it finishes or frees; a setting row spawns no warm-up). The `boot_title` baseline was re-approved for the fourth row.

## Open items
- **Measure** every row above on a GPU runner (M1-QA-01) and replace the estimates. Add a per-preset benchmark camera path to the vertical-slice zone when one exists.
- ~~Localization rows for the `*_key` fields in `graphics_presets.json`~~: all present. The Graphics page's value labels are checked by `tools/tests/test_graphics_menu_data.py` (M1-UI-10). `tools/validate_data.py` still doesn't scan `game/data/settings/`.
- Zones must tag VoxelGI nodes with group `gi_voxel` (Environment), and vegetation with the `vegetation_groups` (M1-ENV-05).
- The mapping from preset to shader quality variant (`HYMN_QUALITY`, see `game/shaders/README.md`) gets added when the first variant shader lands.

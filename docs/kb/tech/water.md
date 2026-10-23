# Water: ocean, shallows, rivers (M1-RND-01)

SPEC §8.2 item 1, the signature element. Owner: Rendering. Consumers: Environment (zones), Systems (buoyancy and wading via the height query), Cinematics (the weather clock).

| What | Where |
|---|---|
| Shaders (tier wrappers) | `game/shaders/water/water_ocean{_low,_medium,,_ultra}.gdshader`, `water_river{_low,}.gdshader` |
| Shader body | `game/shaders/water/water_surface_body.gdshaderinc` (vertex, fragment, light) |
| Gerstner waves (shared with the probe) | `game/shaders/water/water_waves.gdshaderinc` |
| Caustic pattern (reusable underwater) | `game/shaders/water/water_caustics.gdshaderinc` |
| Night sea-glow | `game/shaders/include/glimmer.gdshaderinc` (glimmer stream, M1-RND-02): `hymn_sea_glow()` |
| Node + height query | `game/world/water/water_surface.gd` (`WaterSurface`), `gerstner_waves.gd`, `wave_set.gd`, `wave_component.gd`, `water_mesh_builder.gd` |
| Test scene and shots | `game/levels/_tests/water/water_test.tscn`; shots `water_shallows`, `water_lagoon`, `water_horizon`, `water_night` |
| GPU/CPU parity probe | `game/levels/_tests/water/wave_parity_probe.tscn` (run by `tests/unit/test_water_waves.gd`) |
| Cost bench | `game/levels/_tests/water/water_bench.tscn` |
| Tests | `tests/unit/test_water_waves.gd`, `tests/unit/test_water_surface.gd` |

## Placing water in a zone

1. Add a `Node3D` with `water_surface.gd` (class `WaterSurface`). Keep it **unrotated and unscaled**: waves live in world XZ, and only its Y (the tide level, `tide_line_y` + the current tide) offsets the rest plane.
2. `wave_set`: a `WaveSet` `.tres` with up to 8 `WaveComponent`s (direction, wavelength, amplitude, steepness, phase). Copy `game/levels/_tests/water/lagoon_waves.tres` (trade-wind lagoon chop plus a 62 m swell) and adjust it. Point the main components along the zone's prevailing wind.
3. `material`: a `ShaderMaterial` `.tres` next to the zone, holding the **look** (colours, absorption, foam, caustics). Copy `water_lagoon_material.tres`. Its `shader` is replaced by the tier variant at runtime, and every authored parameter survives.
4. `quality`: set from the graphics preset with `WaterSurface.quality_for_preset(preset_id)` after the zone loads (and from the settings menu).
5. The mesh is generated: a uniform 0.5 m core of ±48 m, then cells growing ×1.1 out to ±3 km (≈107k vertices, one draw call). For a zone where the camera roams far, set `follow_target` to the camera. The grid then follows it, snapped to whole core cells. For rivers, pools and channels, set `surface_mesh` to the authored mesh (it needs UVs for the flowmap) and `river = true`.
6. Lighting the zone:
   - Write the `hymn_*` globals: `hymn_wind_time` is the wave clock, `hymn_wind` drives ripples and foam drift, and `hymn_sun_direction` aims the caustics.
   - At night, set `hymn_glimmer.a > 0` and `sea_glow_energy` to the colour-script value (0.04–0.15).
   - Set the sun's `sky_mode` to **Light Only**. The shader draws its own sun glint, so the sky's sun disc would double it in reflections.

The test rig (`water_test_rig.gd`) shows all of this in about 100 lines.

### Look parameters (material uniforms, grouped in the inspector)
| Group | Key parameters | Notes |
|---|---|---|
| colour | `col_scatter_shallow` (1–4 m), `col_deep` (>15 m), `scatter_depth_m`, `absorption_per_m` (RGB m⁻¹), `absorption_scale`, `sun_path_factor`, `scatter_energy`, `scatter_wrap` | Beer–Lambert transmittance `exp(-σ·(path + depth·sun_path_factor))`. The scatter colour is output as diffuse albedo, so the zone's own lights, ambient light and shadows light it. |
| refraction | `refraction_strength`, `refraction_depth_m`, `refraction_dispersion` (Ultra) | Screen-space distortion, rejecting samples in front of the water. |
| reflection | `roughness_near/far`, `roughness_far_m`, `ssr_*`, `glint_strength`, `glint_min_roughness` | Engine sky/probe reflection (`SPECULAR` set to water's F0 = 0.0204) wherever the in-shader SSR misses. |
| detail | `detail_scale_per_m`, `detail_strength`, `detail_speed_m_s`, `detail_fade_m`, `wind_reference_m_s`, `wind_chop`, `calm_direction` | Ripples scroll with `hymn_wind` and grow up to `wind_chop`× with wind speed. |
| foam | `foam_shore_width_m` / `foam_wash_depth_m` (**vertical** water depth), `foam_band_*`, `foam_crest_threshold/softness` (Jacobian), `foam_scale_per_m`, `foam_flow_*`, `flow_cycle_s` | Curl-noise advection (two-phase, never stretches). |
| caustics | `caustic_strength`, `caustic_scale_per_m`, `caustic_speed`, `caustic_width`, `caustic_blur_per_m`, `caustic_fade_in_m`, `caustic_falloff_m`, `caustic_mean`, `caustic_chroma` (Ultra) | See "Caustics" below. |
| subsurface | `col_sss`, `sss_strength`, `sss_power`, `sss_distortion`, `sss_crest_lo/hi`, `sss_view_fade_lo/hi` (0.10 / 0.28), `sss_view_height_lo_m/hi_m` (10 / 25), `scatter_view_lift` (1.5) | Sun through thin crests, crest height / Σ amplitude. View-dependent (M1-RND-08): the sharp term peaks looking into the light and the soft wrap term fades as the sun moves behind the viewer, so a sun behind the camera adds no SSS. **High cameras (M1-RND-18):** the crest term fades with view steepness (\|view.y\| from 0.10 to 0.28, about 6° to 16° down), but only for a camera 10–25 m or more above the water it looks at, so low cameras keep their crests. The deep end of the in-scatter (`col_deep`) gains `scatter_view_lift` × the same fade, an even lift in place of the crest patches. The lift is gated by the crest SSS it replaces (M1-RND-18 S1): none with `use_sss` off (the storm sea), and scaled by `sss_strength` / 1.4 (the strength it was tuned at, clamped to 1). |
| sea_glow | `sea_glow_energy`, `glimmer_response` | The glow comes from `hymn_sea_glow()`. It is on only while `hymn_glimmer.a > 0`, and `glimmer_response` brightens the water under `hymn_glimmer_focus`. |
| features | `use_refraction`, `use_caustics`, `use_ssr`, `use_foam`, `use_sss`, `use_detail_normals` | These are uniform across a draw, so the branches are coherent and nearly free. Use them for per-zone art choices (murky water: no caustics). |
| flow (river) | `tex_flow` (RG, 0.5 = still, data texture), `flow_speed_m_s` | Ripples and foam advect along the map (two-phase flow). |

### Test-scene values and colour-script deviations
The test material uses `absorption_per_m = (2.0, 0.5, 0.42)`, `scatter_energy = 0.25`, `col_deep = #1569A0`, `col_scatter_shallow = #1FA3A6`, and day exposure 0.65 (AgX, saturation ×1.12 standing in for the not-yet-built LUT). **The colour-script triples (ch02: 0.45 / 0.065 / 0.045) did not reach the ramp**: they render near-white over noon-lit sand. See the M1-ART-01 review log for the numbers. Zones should start from the test values and tune per frame.

## Height query (gameplay)

```gdscript
var y: float = water.height_at(Vector2(x, z), weather_time)   # world Y of the surface
var n: Vector3 = water.normal_at(Vector2(x, z), weather_time)
```
- `weather_time` must be **the value of `hymn_wind_time`** (the weather system owns it, so cutscenes can pause or scrub it). The query is pure: it takes no time from the engine.
- Gerstner waves move water sideways, so `height_at` first finds the rest point whose displaced position lies over `(x, z)`. It uses 8 fixed-point iterations, which converge to < 1 mm even at steepness 1 (tested).
- Its maths mirror `water_waves.gdshaderinc` exactly: the same packed constants (`GerstnerWaves.pack()`), the same sum, and the same normal and Jacobian. `test_water_waves.gd::test_gpu_shader_matches_cpu_mirror` renders the include on the GPU (software renderer, ADR 0009) and compares 1024 points. The measured maximum error is **0.5 mm** for displacement, 5e-4 for normals and 1e-3 for the Jacobian, all limited by the half-float readback. The test skips (and passes) where the renderer isn't installed. A headless test also pins the shared expressions in the include's source.
- Cost: about **50 µs per call** in GDScript (8 waves × 9 evaluations, measured on this sandbox under load). That's fine for tens of floaters per frame. For hundreds, cache per frame or move to C++.
- The **visual LOD fade** (`lod_fade_wavelengths`) flattens each wave beyond 60 of its own wavelengths from the camera (a 2.2 m wave is gone by about 260 m). The query ignores it. Nothing gameplay-relevant floats that far away.

## Quality tiers

The tier is compile-time (`HYMN_QUALITY`). The geometry, and therefore `height_at`, is identical on every tier.

| Term | Low | Medium | High (default) | Ultra |
|---|---|---|---|---|
| Gerstner geometry (8 waves) | yes | yes | yes | yes |
| Normals | per vertex | per vertex | per pixel | per pixel |
| Ripple layers | 1 | 2 | 3 | 3 |
| SSR (in-shader) | off (sky/probe only) | 12 steps | 20 + 4 refine | 32 + 6 refine |
| Caustic layers | 1 | 1 | 2 | 2, chromatic |
| Refraction | yes | yes | yes | + dispersion |
| Foam advection | wind scroll | curl | curl | curl |
| Absorption, scatter, shore + crest foam, SSS, glint | yes | yes | yes | yes |
| **Night sea-glow** | **yes** | yes | yes | yes |

Low keeps every term that defines the look (colour by depth, foam lines, caustic shimmer, and the night glow, which colour-script rule 3 forbids cutting) and drops the terms whose absence reads only as "less detail": reflections of geometry, the second caustic web, per-pixel wave normals, and two ripple octaves. Preset → tier: low → Low, medium → Medium, high → High, ultra → Ultra (`WaterSurface.PRESET_QUALITY`; it should move into `graphics_presets.json`, see "Open items").

## Caustics: approach and why

**Chosen: a screen-space projector inside the water shader.** The water already reconstructs, from the depth buffer, the world position of whatever it refracts. At that point it evaluates an animated caustic pattern, projected along `hymn_sun_direction` (the pattern coordinate is the point where sunlight entered the surface: `p.xz + sun.xz · depth / sun.y`). It then *multiplies* the refracted seabed colour by `1 + strength · (c − mean)`.

Why not the alternatives:
- **A Decal/projector node** needs a texture. An animated procedural caustic would need a SubViewport rendering every frame. Decal emission ignores sun shadows and lights the seabed above the waterline unless it's carefully clipped, and each body of water needs its own decal box.
- **A seabed-material approach** couples every environment material (sand, stone, coral, props, characters' legs) to water. Every Environment shader would need the include and the water uniforms, and anything without it shows no caustics.
- **The projector** works on any opaque geometry under any water body, with no per-zone setup. Because it multiplies the lit colour, shadowed seabed stays dark (caustics respect shadows for free). Because it modulates around the pattern mean, it redistributes light rather than adding it, so the floor's average brightness is unchanged. It's absorbed by the same Beer–Lambert path, so it fades correctly with depth.

Limits:
- It sees only what is under water *in screen space*. It can't light the underside of geometry, and it doesn't exist when the camera is underwater. The underwater shader (SPEC §8.2 item 2) should reuse `hymn_caustic()` as a light-function-style term on its own surfaces.

Art controls:
- `caustic_strength`, `caustic_scale_per_m`, `caustic_speed`, `caustic_width` (sharpness), `caustic_blur_per_m` (defocus with depth), `caustic_fade_in_m` / `caustic_falloff_m` (the art band, "bright and sharp in 0.3–4 m"), and `caustic_chroma` (Ultra rainbow fringes).
- Shell Shrine net caustics (Ilun) can swap the pattern function.

## Cost

> **Everything in this section that says "GPU" is an estimate.** The only renderer here is lavapipe, which runs Forward+ rasterised on the CPU (ADR 0009). CPU time is **not** GPU time: lavapipe's cost per ALU operation, per texture fetch and per pixel differs from any GPU's. Use the *ratios* between configurations to rank the features, then replace everything with GPU-runner numbers (M1-QA-01 follow-up).

### Method (reproducible)
```bash
~/.cache/hymn/godot-4.6.3+ds-2/godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync \
  --resolution 1280x720 res://game/levels/_tests/water/water_bench.tscn -- --camera=Cameras/Lagoon --cost
```
- 12 configurations, interleaved over 2 rounds, 6 warm-up plus 8 measured frames each, at 1280×720.
- The metric is the **CPU time the Godot process consumes per frame**, read from `/proc/self/stat`. lavapipe rasterises in the process's own threads, so the metric is the work done, and the other agents loading this machine (load average ~10 on 4 cores) cannot inflate it. Wall-clock and timestamp "GPU" times swung ±2× under that load and were useless: a first attempt with them ranked Low above High.
- Run-to-run repeatability is about 1.5%. The noise floor between configurations is about **±50 ms**, so a difference smaller than that means "too cheap to see here".

### Measured (lavapipe CPU ms per 720p frame; "water" = minus the same view without water)
| Configuration | Lagoon view (water ≈ 75% of pixels) | | Horizon view (≈ 55%) | |
|---|---|---|---|---|
| | frame | water | frame | water |
| no water | 799 | 0 | 643 | 0 |
| **Low** | 1266 | **+468** (60% of High) | 923 | **+280** (61%) |
| Medium | 1428 | +629 (80%) | 1034 | +391 (85%) |
| **High** | 1583 | **+784** (100%) | 1104 | **+461** (100%) |
| Ultra | 1909 | +1110 (142%) | 1256 | +614 (133%) |
| High − SSR | 1386 | +588 (SSR ≈ **25%** of High) | 1018 | +375 (≈ 19%) |
| High − foam | 1541 | +743 (≈ 5%) | 1066 | +424 (≈ 8%) |
| High − caustics | 1570 | +771 (< noise) | 1099 | +456 (< noise) |
| High − detail normals / − SSS / − refraction | 1573 / 1645 / 1625 | within noise | 1120 / 1118 / 1096 | within noise |
| High − all optional terms | 1165 | +366 (≈ 47%) | 874 | +231 (≈ 50%) |

Reading:
- The **base** (8-wave Gerstner per pixel, depth reconstruction, absorption and scatter, sea-glow, the custom light function, the transparent-pass screen copy) is about half of the High cost.
- **SSR is the largest single optional term** (20–25%). That's why Low drops it and Medium halves it.
- Ultra's extra 32 SSR steps and chromatic caustics add about 35–40%.
- Caustics, ripples, SSS and refraction are each below this method's resolution (< 5%). That's why Low keeps one caustic layer: it's the look of the shallows and nearly free.

### GPU budget (estimates, not measured)
Derived from an operation count of the High fragment path: about 2,000 ALU ops and about 30 texture fetches per water pixel. The fetches are dominated by SSR's dependent depth reads. Add the transparent-pass screen-texture copy with mips, and the vertex work (107k vertices × 8 waves, negligible). Scale by typical throughput, assuming 30–50% ALU efficiency. Read these as **±2×**:

| Tier on target hardware | Internal resolution, water coverage | Est. GPU ms |
|---|---|---|
| **High on RTX 3060** (recommended tier, 1440p via FSR2 at 0.77) | 1971×1109, ~60% water | **1.0 – 2.0** |
| Ultra on RTX 3060 (native 1440p) | 2560×1440, ~60% | 2.0 – 3.5 |
| Medium on GTX 1060 (1080p at 0.85) | 1632×918, ~60% | 1.0 – 1.8 |
| **Low on GTX 1060** (minimum tier, 1080p at 0.77) | 1478×831, ~60% | **0.4 – 0.9** |

These fit the M1-RND-05 frame budgets: High's ≈ 11.4–17.5 ms already includes SSR and the base, and water replaces the opaque surface it covers. Still, a coast-heavy High frame should budget **2 ms for water**, which is one more reason to keep `ssil_quality` at medium on High. If the measured cost overruns, shed it in this order: SSR steps (`ssr_max_distance_m` / tier), per-pixel normals (Medium behaviour), then the second caustic layer.

## Zone globals (M1-RND-08, M1-RND-15)

| Global | Type | Written by | Meaning |
|---|---|---|---|
| `hymn_water_level` | vec2 | the zone sea's `WaterSurface` every frame (`publishes_water_level`, **off by default** since M1-RND-15: turn it on for the zone's sea only; a second publisher in the tree warns). Reset to (0, 0) when the publisher leaves the tree and by `SceneRouter` on every zone change | x = the sea's rest plane now (the node's world Y: animate the node for tides and the Drownbell flood), y = `tide_line_y`, the datum stone weathering keys its wet band to |
| `hymn_zone_sea_glow` | float | `GlimmerField.set_scene_sea_glow(energy)`; `clear_scene_sea_glow()` | The zone's night sea-glow energy (rule 3). It's **not** gated by the mote energy `hymn_glimmer.a` any more. Three states (M1-RND-15): **> 0** the zone's energy, which a water material's own `sea_glow_energy` > 0 overrides for that surface; **0** unset (the project default, and `SceneRouter` resets to it on every zone change): materials decide; **< 0** hard off, written by `set_scene_sea_glow(0)`: every surface is dark whatever its material says. `ending_dock` must call `set_scene_sea_glow(0.0)`, so no stray material can light SPEC §3.5's dark sea. A night zone must write its own value after loading. Check a frame with `GlimmerField.sea_glow_violation(energy, sun_elevation_deg, scene, beat)`: it knows the floor and ceiling, the night minimum below −6°, and the Ending's E4 0.07 / E5 0.06 exceptions (mirrored from palette.json, tested). |

Environment's `WeatheringTide` (haluna_mood) still pushes `tide_line_y` / `water_height_y` into each material. It can switch to reading `hymn_water_level`.

## Caustics after M1-RND-08

- **Pattern.** Two layers, each with its own two-octave domain warp (curved filaments, not straight polygons). Their union keeps the web; their product focuses the crossings into bright knots, which can exceed 1. Line width varies ×0.6–1.4 and focus ±50 % over metres.
- **Width and fade.** Width grows faster with depth: `caustic_width + caustic_blur_per_m · depth · (1 + depth / caustic_falloff_m)`. Contrast fades with view distance (`caustic_view_fade_m`, 30 m), which removes the lagoon's 10–40 m tiling.
- **Mean.** The subtracted mean is fitted against line width (`tools/gpu_bench/caustic_mean_fit.py`, a numpy replica; refit after any pattern change). The old constant 0.18 was only right at about 4 m and darkened shallow floors on average.
- **Authored patterns.** `caustic_pattern` = Texture uses `caustic_tex` (R = brightness, tiling) drawn as two drifting layers, for authored patterns such as light through Ilun's nets. Set `caustic_mean` to that texture's two-layer mean.

## Gotchas
- **Don't rotate or scale the WaterSurface node.** Waves are world-space, so a rotated node doesn't rotate the waves, and the height query ignores rotation.
- **Sun `sky_mode` = Light Only.** Otherwise the sky's sun disc doubles the shader's glint in the engine reflection.
- **The reflected sky can be dimmer than the visible sky.** `env_sky_cumulus`'s `background_energy` lifts only what the camera sees, not the radiance cubemap the water reflects. Haluna sets 1.5 (its sea reflects a sky at 1/1.5 of the one on screen, validated as `lagoon_clear`); a zone that copies it without re-validating gets a value step between the horizon and the grazing-angle sea (color_script.md, Conventions; M1-RND-12).
- **Transparent pass.** The water reads the screen texture, so it's drawn after opaque geometry. It isn't in the screen texture of *other* refractive materials (glass seen through water, or water seen through glass). It casts no shadow (`cast_shadow` off), and it doesn't write motion vectors (expect slight TAA ghosting on fast glints).
- **Reef lips seen from low cameras.** Screen-space refraction sees only what the unbent view ray hits. Past a drop-off, a low camera's rays miss the deep slope, so the colour steps from "shelf" to "deep" along the lip line (see `water_horizon`). The step is physically plausible, but keep drop-offs irregular in plan (the test seabed wobbles its reef edge), or place cameras higher.
- **Foam widths are vertical depths.** On a 1:30 beach, 0.03 m of depth is about 1 m of sand. Tune the widths against the zone's beach slope.
- **Absorption and the tonemapper.** AgX desaturates anything brighter than about 1.0 linear. If shallows look milky, the fix is more absorption (or less exposure), not more saturation.
- **Camera underwater** isn't handled (the M1 underwater shader item).
- **The globals must be written** (`hymn_wind_time` at least). With the defaults, the waves freeze and the caustics point straight down.
- **Screenshot shots hold the sea still.** `capture.gd` gives the first shot of a run one process frame fewer than later shots, so an animated sea shifted by a frame (RMSE 0.012) depending on its place in `shots.json`. TAA history made it worse. Each water shot therefore pins `hymn_wind_time` to `start_time_s` and swaps TAA for FXAA in its shots.json `setup`, and names its mood (`"." : {"mood": "day" | "night"}`); since M1-RND-13 the rig no longer detects the capture scene, and the capture restores the viewport. The four shots are now identical (RMSE 0.0) whether run alone or after the other shots. Use the bench, or open the scene in the editor, to see the sea move.
- **TIME is never used.** Everything runs on `hymn_wind_time × time_scale`, so cinematics can pause and scrub the sea.
- **High cameras and crest SSS (fixed in M1-RND-18).** From the 40 m survey camera the crest term lit every swell crest into pale-teal sheets (27.5 % of the deep water changed by ΔE_ok > 0.03). It now fades with view steepness for high cameras, and `col_deep` is lifted evenly instead. On the survey: 0.06 % of deep pixels over 0.03, max added 0.050, and the > 15 m band `#15627A` at ΔE_ok 0.019 to `deep_teal_shadow` "+1" (docs/kb/qa/gpu/2026-10-23-rnd-18-sss-crest.md). The low shots are bit-identical.
- **Sun behind the camera (fixed in M1-RND-08).** Two artefacts with a low sun behind the camera, both measured on an RX 9070 XT (`tools/gpu_bench/water_probe.tscn`, `docs/kb/qa/gpu/2026-10-23-rnd-08.md`):
  - The SSS wrap term was view-independent and painted saturated green bands along every swell crest (cyan `col_sss` × a warm low sun). It's now scaled by `toward_light` = ½ − ½·(VIEW·LIGHT): unchanged when back-lit, 0 when the sun is straight behind the viewer. The same term made the large pale crest patches from high noon cameras (M1-ART-04), which are now dimmer.
  - The glint's Schlick term did `pow(1 − vdh, 5)` with an unclamped `vdh`. At the anti-solar pixel VIEW = LIGHT = H, rounding can push `vdh` past 1, and `pow()` of a negative base is undefined (NaN on some drivers, not on the RX 9070 XT), and one NaN pixel blooms into a white disc. `vdh` is clamped now, and the half vector is guarded for LIGHT = −VIEW.
  - Scenes that turned SSS off to dodge the bands (`undertow/storm_ocean_material.tres`) can turn it back on. That changes their shots, so it's left to the scene owners.

## Open items
- Move the preset → water-tier map into `game/data/settings/graphics_presets.json` (Rendering, with M1-RND-05).
- Register the water variants in `game/data/settings/prewarm_materials.json` before any battle or dialogue scene uses water. Each tier is its own pipeline.
- Measure the cost on a real GPU. Hook `WaterSurface.quality` to `GraphicsSettings.apply_current()`.
- Possibly a `hymn_sea_glow` global, or a zone energy in the zone data, so the sea-glow energy isn't a per-material value.

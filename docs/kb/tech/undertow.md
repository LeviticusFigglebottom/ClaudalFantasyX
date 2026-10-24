# The Undertow storm (M1-RND-03)

SPEC §8.2 item 9: "a colossal volumetric storm with animated vortex shading, raymarched or layered, plus glimmer wounds. It is the most important visual in the game." This page covers the prototype: the approach and why, the parts, how zones and cutscenes place and animate it, every tunable, the tiers, the measured relative costs, and an honest assessment with what M2 must add. Owner: Rendering. Consumers: Environment (zones), Cinematics (Ch1, Ch8, Ch20–21 and the ending), Narrative (the light rules).

| What | Where |
|---|---|
| Node (typed API) | `game/vfx/undertow/undertow_storm.gd` (`class_name UndertowStorm`) |
| Pure state (headless) | `game/vfx/undertow/undertow_state.gd` (`UndertowState`): API ranges, clock, tiers, lightning schedule, shape mirrors |
| Meshes | `game/vfx/undertow/undertow_mesh_builder.gd` (`UndertowMeshBuilder`) |
| Tunables | `game/data/vfx/undertow.json` |
| Shared storm maths | `game/shaders/undertow/undertow_common.gdshaderinc` (shape, rotation, wounds, lightning) |
| Raymarched body | `undertow_body.gdshaderinc` + tier wrappers `undertow_body_medium/.gdshader/_ultra` |
| Low-tier body | `undertow_shell.gdshader` (lathe shells) |
| Spray | `undertow_spray.gdshader` |
| Maelstrom sea | `undertow_sea.gdshader` (funnel disc) and `undertow_sea_lid.gdshader` (depth-only lid) |
| Test scene and shots | `game/levels/_tests/undertow/undertow_test.tscn` (driver `undertow_test_rig.gd`); shots `undertow_horizon_dusk`, `undertow_eye`, `undertow_night`, `undertow_horizon_low` |
| Cost bench | `game/levels/_tests/undertow/undertow_bench.tscn` |
| Storm events (M2-RND-05) | `game/vfx/undertow/undertow_events.gd` (`UndertowEvents`); `undertow_streamer`, `undertow_bolt`, `undertow_rain` shaders; the water shader's storm group (reflection); tests `tests/unit/test_undertow_events.gd` |
| Tests | `tests/unit/test_undertow_shaders.gd` (compile, uniforms, no `TIME`, palette, prewarm), `tests/unit/test_undertow_storm.gd` (state, meshes, node) |

## Approach: a hybrid, and why

The storm is kilometres wide (bible §9): in the test it is an eyewall 1.8 km across at the sea, flaring to 3.8 km at the top, 5.4 km thick, 11.5 km tall, with an anvil canopy out to 10.5 km and spiral rain bands to 16 km. Seen from a shore it sits 15–20 km away. Seen from a high Kite it fills the frame from 20 km up. I weighed three options:

| Option | For | Against | Verdict |
|---|---|---|---|
| **FogVolume + custom `fog` shader** (Godot volumetric fog) | Engine-integrated: lights, shadows and GI scatter into it for free, and it composites with everything correctly | The froxel grid is 64–192 cells across the screen and 32–128 slices spread over `volumetric_fog_length`. A body 15–20 km away gets a handful of slices of tens of metres to kilometres each, so its silhouette is a soft blur; the length cannot reach 20 km without making the near field (light shafts, glimmer haze: the zone's real use of fog) unusably coarse. The grid also has to stay sized for the zone, not the storm | **Rejected for the body.** It stays the zone's near-field fog |
| **Layered shells** (stacked lathe shells, a funnel mesh, spray curtains) | Cheap, crisp silhouettes, trivially tiered | Parallax between a few surfaces, no self-shadowing, and visible plates at grazing angles. It reads as layers, not a mass | **Used for Low**, and for spray and the sea on every tier |
| **Raymarch in a proxy mesh** (a closed cylinder, back faces, depth-tested by hand) | Full-resolution silhouettes at any distance, real volume and self-shadowing, inner light that scatters, and one analytic envelope that every other part shares | The most expensive option; noise aliasing needs care | **Used for the body on Medium, High and Ultra** |

So the prototype is a **hybrid**: a raymarched volumetric body (Medium+), stacked shells that follow the *same* envelope on Low, and mesh parts on every tier for the sea funnel, the spray, and the lid that keeps the zone ocean out of the funnel. Every shader includes `undertow_common.gdshaderinc`, so the shells, the body, the spray and the sea agree on the shape, the rotation, the wounds and the lightning, and a tier change never moves the storm.

### The body (raymarch)
- **Proxy:** a closed `CylinderMesh` that bounds the storm (`UndertowState.bound_radius()`), drawn with `cull_front`, so it works with the camera outside or inside (Ch20). The ray is clipped *analytically* to the cylinder and the slab [sea level, top], then to the opaque depth buffer by hand (`depth_test_disabled`). The water is transparent and is not in that buffer, so the sea-level slab stands in for it. It is `blend_premul_alpha`, unshaded, and sorted after the water (`render_priority`).
- **Shape (envelope):** three analytic parts in storm-local cylindrical space: the eyewall (between `eye_r(h)` and `wall_r(h)`, the eye flaring like a stadium), the anvil canopy, and log-spiral rain bands (`theta + band_twist * ln(r / eye)`). Helical **striations** wind up the wall (`striation_*`): the rotating plates that make the vortex read from the side.
- **Rotation and turbulence:** differential rotation, `omega(r) = rotation_rad_s * (eye / r)^rotation_falloff`, fastest at the eyewall. Noise is **two-phase advected** over `flow_cycle_s` (the flowmap trick): two samples rotated back by `omega(r) * t` with staggered resets, cross-faded, so the shear winds the pattern into spirals but never winds it up without bound. On High and Ultra a **curl-noise** warp (`hymn_curl_noise3`, divergence-free) is carried with the flow. An updraft lifts the pattern.
- **Density:** the envelope eroded by fBm (`erosion_*`): a full envelope keeps all but the troughs, a thin one only the crests (billows at the surface, wisps outside).
- **Marching:** `march_steps` per tier, a per-pixel interleaved-gradient-noise offset (TAA resolves it), and **adaptive strides** (`empty_step` × the mean step outside the envelope, `dense_step` inside). A uniform stride undersampled the billows and left streaks along the view rays in the high-angle shot.
- **Lighting:** multiple scattering (M2-RND-01: `cloud.ms_octaves` 3 octaves after Wrenninge 2013; octave i has energy `ms_attenuation`^i 0.35, extinction `ms_extinction`^i 0.25 and phase eccentricity `ms_eccentricity`^i 0.6; 1 octave = the M1 single scattering; no measurable cost) with a dual-lobe Henyey-Greenstein phase, sun transmittance from 1–3 sun-ward samples (envelope only on Medium, coarse noise above), ambient between `col_ambient_bottom` and `_top` with an occlusion term, and a **low-sun reach** (`sun_clear_height`, `sun_low_floor`): a low sun has crossed the outer bands first, so it gilds the upper storm while the lower wall stays dark slate. The albedo is a cool white. The mass reads as `storm_slate` through its own shadow, which is what lets its upper flanks catch the dusk gold (pillar 2: gorgeous and doomed).
- **Aerial perspective:** the storm is `fog_disabled` and hazes itself toward `col_haze` with `haze_visibility_m`, weighted by the mean scattering depth. Match `haze_color` to the zone's horizon/fog colour.

### Glimmer wounds (the light rules)
- **Wound surfaces** are `spawn_wound` `#3FE0C8`: rents in the eyewall's two faces (the eye face and the outer face, `wound_skin_m` deep), inside a height window. The seam pattern is ridged noise mapped on a fixed-radius cylinder (angle around the storm, height), so a seam is a slit *through* the skin, not a 3D sparkle the raymarch would alias. A low-frequency presence field picks which regions are torn (`wound_coverage`). At a rent the wall is thinned (`rent_depth`), so the light behind it shows.
- **Held light** is `glimmer_held` `#7FC6D9`: the pockets pooled behind the wounds (in-scattered inside the wall), the cyan streaks spiralling **down** the maelstrom's throat, and the motes shed. Colour-script rule 1: held light drifts sideways and down. The seams themselves **slide down the wall** (`wound_sink_m_s`), and the throat streaks sink into the funnel (`glow_sink_m_s`). Nothing in the storm rises. (When the Unbinding comes, Ch21, the same uniforms are the place to flip it: the wounds' colour to `glimmer_lift` and their drift upward. That is an M5–M6 task.)
- **Motes** torn off the wounds: the zone places a `GlimmerField` in **held** mode with `sea_direction` toward the storm (the drowned's light is being drawn back) and gives it to `UndertowStorm.motes`. The storm sets its draw `render_priority` above its own so the motes draw over the storm. Glimmer motes are 1.2–4.5 cm. At storm scale they are sub-pixel, so they belong near the camera (the test scene puts them over the water in front of the shore), and the storm's own wounds carry the glimmer at distance.
- **Palette note:** palette.json limits `spawn_wound` to "creature weak points only". I use it for the Undertow's rents, because the Undertow is the source of the spawn and its wounds are the same language (SPEC §7.5, bible §9). **Art should confirm, or extend the usage note** (a request, not something I edited).

### Lightning-like inner glows
Four sites (`lightning.sites`) ride the middle of the eyewall and rotate with it. A deterministic schedule (`UndertowState.flash_levels`, a PCG hash of site and period index, so it never uses wall-clock time or `randf`) fires a stroke plus a weaker re-strike. Cutscenes time one with `force_flash(site, start_s)`. The glow is the ch20 key colour `#C4D6FF`, scattered by the cloud around the site (Gaussian falloff, `lightning_radius_m`). The sea shader lights its foam under a flash with the same sites.

### The sea pulled into the funnel
- `undertow_sea.gdshader` draws an opaque polar disc (rings packed toward the throat) centred on the eye. Its profile is a `1 / (1 + (r / throat)^2)` vortex depression (`funnel_depth_m`, 260 m in the test), faded out by `funnel_radius_m`, plus a surge **lip** heaped against the wall and rotating swell. Foam is streaked along log-spiral streamlines (`foam_pitch`) in coordinates that drift inward (`inflow_m_s`), so it circles and creeps in without winding up. **Foam rings** ride in toward the throat. Held cyan light streaks down the throat. Lightning lights the foam. The night sea-glow comes from `hymn_sea_glow_global` with the zone's energy. The rim dissolves with a stable screen dither between `fade_start_m` and `radius_m`.
- **Reusing the water:** `UndertowStorm.water` takes the zone's `WaterSurface`. Its `col_deep`, `col_foam` and `sea_glow_energy` are copied into the funnel (the storm then darkens the deep colour under itself), so the funnel's rim matches the ocean. The water's API, shader and mesh are untouched.
- **Keeping the ocean out of the funnel: the lid.** The ocean is transparent but writes depth at sea level, so it would cover a funnel that dips below it. `SeaLid` is an invisible disc (radius `fade_start_m`, height = lift + the zone's highest crest from `WaterSurface.waves().amplitude_sum` + `lid.margin_m`), drawn in the transparent pass *just before* the water (`render_priority` −1) and writing depth only. Inside it the ocean fails its depth test and the funnel shows. Nothing is rebuilt when the storm moves. I first carved the ocean by sinking `WaterSurface.surface_mesh` vertices, which also respected the API, but rebuilding the 200k-vertex grid cost about 13 s of GDScript per move, so approach animations were impossible. The lid replaced it.
- **Floaters:** `WaterSurface.height_at()` knows nothing of the funnel. For a boat near the storm use `UndertowStorm.sea_height_at(xz)` (the rest profile without swell, mirrored from the shader and tested).

### Scale cues
Atmospheric perspective on the body and spray; a 9 m boat (0.76 km out) and a 42 m lighthouse on a headland (2.6 km) built from primitives, both a few pixels tall against a storm that fills two thirds of the frame; billow detail down to about 300 m; and the slowness of the motion (0.012 rad/s at the eyewall is about 7° in a 10 s shot).

## Placing and animating it (zones and cutscenes)

```gdscript
var storm := UndertowStorm.new()          # or instance the node in the zone scene
storm.position = village_marker.position  # the point it approaches (any height); unrotated/unscaled
# Sea level is NOT the node's Y: it is the zone ocean's rest plane when `water` is set (below), else
# storm.sea_level_y (set sea_level_from_water = false to force the explicit value). A marker on a 12 m
# headland therefore still puts the funnel, lid and spray on the zone sea.
storm.approach_azimuth_deg = 90.0         # it lies due east (clockwise from north = -Z)
storm.approach_distance_m = 17000.0       # 0 = on top of the marker
storm.water = $Ocean                      # zone WaterSurface: look copied, lid sized to its crests
storm.sun = $Sun                          # key light (sun or moon): colour x energy light the storm
storm.motes = $HeldMotes                  # optional GlimmerField (held), drawn over the storm
storm.ambient_top = Color("#6F7E8E"); storm.ambient_bottom = Color("#0E4A55")
storm.haze_color = zone_fog_colour        # aerial perspective; haze_visibility_m (0 = data value)
add_child(storm)
storm.apply_graphics_settings(graphics_settings)   # or set_quality("low" .. "ultra")
```

| Member | Range (undertow.json `state`) | Meaning |
|---|---|---|
| `intensity` | 0–1 | 0 = asleep (the Calm): lower (`calm_shrink`), thinner, no lightning, shallow funnel. 1 = risen |
| `rotation_rad_s` | 0–0.12 | Angular speed at the eyewall. It falls off outward |
| `wound_intensity` | 0–4 | Wound seams, the pockets behind them and the throat glow. Ch20 and night set-pieces push it |
| `approach_distance_m`, `approach_azimuth_deg` | 0–60 km | Where the storm sits relative to the node. Tween the distance for an approach. Nothing is rebuilt |
| `get_time()` / `set_time(t)`, `playing`, `time_scale` | | The storm clock. It never reads `TIME`: cutscenes pause it (`playing = false`) and scrub it (`set_time`) |
| `force_flash(site, start_s)` | site 0–3 | Strike a site now (`start_s < 0`) or at a storm time, to cut on the flash |
| `set_quality(id)`, `apply_graphics_settings(gs)`, `quality_changed` | low…ultra | Swaps the body (shells or raymarch variant) and the spray layers |
| `storm_center()`, `sea_height_at(xz)` | | The eye's world position, and the funnel surface for floaters |
| `materials()`, `mood_parameters()`, `water_parameters()`, `lid_height()`, `refresh()` | | The uniforms pushed, for tests and debugging. `refresh()` re-applies after changing tunables at runtime |

A cutscene animates it by tweening these properties (`create_tween().tween_property(storm, "approach_distance_m", 4000.0, 12.0)`) and pausing or scrubbing the clock. The test rig (`undertow_test_rig.gd`) does what a zone does, driven by a mood table: key light, environment, approach, wounds, ambient, haze, sea-glow, a timed flash, and the camera aim. Its shots hold the clocks (`hymn_wind_time`, `Storm.playing = false`), use FXAA and name the mood in their shots.json `setup` (M1-RND-13); the rig itself no longer detects the capture. An exported `mood` holds a mood in play too; empty follows the camera.

### Sea level, editor preview and looks (M1-RND-09)

- **Sea level is not the node's Y.** `storm_center().y` is `sea_level()`: the zone `water`'s rest plane (`WaterSurface` global Y) when `water` is set and `sea_level_from_water` is on (the default), else `sea_level_y`. The node itself may sit on a headland or a quay marker.
- **`@tool`.** In the editor the storm builds at `editor_preview_quality` (default `low`: shells, sea funnel, spray; no raymarch) with its clock stopped, plus a footprint gizmo: circles at sea level for the eye, the wall, the funnel, the lid (`sea.fade_start_m`) and the bound radius, and the eye axis up to the storm's height. The gizmo and every built node are internal children, never saved with the scene. The preview tier is never written into `quality`. `WaterSurface` and `GlimmerField` are not `@tool`, so in the editor the storm reads only their properties (no wave crests for the lid, no mote priority).
- **`quality` setter.** Assigning `storm.quality` after `_ready` switches the tier, like `set_quality()`.
- **Looks.** `storm.look` names an entry of `undertow.json "looks"`: shader uniforms pushed on top of the tunables to every storm material ("#hex" = sRGB colour). `day_storm` is the daylight storm wall (Ch1 storm, Ch8 "The Seawall"): albedo toward `storm_slate`, more ambient self-shadow, and a high sun reaching the lower wall (`sun_low_floor`, `sun_clear_height`; the dusk defaults assume a low sun that already crossed the outer bands). Most of the daylight read comes from the *lighting* (the colour script's Ch8 key, fill, slate sky and fog), which the zone provides; the look is the storm's half. The test scene's `day` mood (`Cameras/Day`, shot `undertow_day_ch08`) is the reference.

## Tunables (`game/data/vfx/undertow.json`)

| Section | Keys |
|---|---|
| `colors` | `albedo` (cool white), `wound` = `spawn_wound`, `held` = `glimmer_held`, `lightning` = ch20 key, `foam` = `foam_white`, `sea_deep` = `abyss_navy` (tested against palette.json) |
| `state` | default/min/max for the five API values |
| `shape` | eye radius, flare, wall thickness/taper/softness, height, canopy (height, thickness, radius, softness), bands (radius, height, arms, twist, sharpness, density), striations (spacing, starts, strength, sharpness), `calm_shrink`, `bound_margin_m` |
| `flow` | `rotation_falloff`, `cycle_s` (two-phase), `inflow_m_s`, `updraft_m_s`, curl scale and warp |
| `cloud` | noise and detail scales, erosion (envelope weight, threshold, contrast), `density_per_m`, albedo gain, sun extinction, ambient occlusion, HG lobes, light step, base darkening, low-sun reach, haze visibility, jitter, adaptive strides, storm-side sun and ambient gains |
| `wounds` | scale, width, coverage, presence scale, skin depth, height window, sink speed, energies, rent depth |
| `lightning` | sites, period and spread, duration, chance, decay, re-strike, radius, energy, height window |
| `sea` | funnel (depth, throat, radius), lip, swell, disc (radius, fade, rings, segments, ring power, lift), foam (scale, streak, pitch, amount, rings), darkening, roughness, throat glow and sink |
| `spray` | inner/outer curtain radii, height, scale, rise, density |
| `lid` | segments, margin above the crest |
| `shells` | Low-tier wall fractions, canopy on/off, tessellation, alpha cut |
| `render_priority` | lid −1 < water 0 < spray 1 / shells 1 < body 2 < motes 3 |
| `quality` | per tier: body kind, march steps, spray layers, sea foam octaves |
| `shaders` | shader paths per part and tier |

## Quality tiers

| | Low | Medium | High (default) | Ultra |
|---|---|---|---|---|
| Body | **3 lathe shells + canopy shell** (alpha-hash) | raymarch, 28 steps | raymarch, 32 steps | raymarch, 72 steps |
| Cloud noise (M1-RND-10) | hashed | baked lattice | baked lattice | baked lattice |
| Curl warp shared by N dense steps (`curl_reuse`) | – | – (no curl) | 2 | 2 |
| Per-frame step jitter (`temporal_jitter`, TAA/FSR2 resolves it) | no (Low is TAA since M1-RND-07, but its tier sets `temporal_jitter: false` and its shell body has no march to jitter) | yes | yes | yes |
| Light samples | wrap-lit with a noise self-shadow | 1, envelope only | 2, coarse noise | 3, coarse noise |
| Curl turbulence | no | no | yes | yes |
| Cloud octaves | 3 (on the shell) | 3 | 4 + detail | 5 + detail |
| Wounds, lightning, striations, bands | yes (on the shells) | yes | yes | yes |
| Sea funnel, foam rings, throat glow, lid | yes (2 foam octaves) | yes (3) | yes (4) | yes (5) |
| Spray curtains | 1 | 2 | 2 | 2 |

**Low still reads as the Undertow** (`undertow_horizon_low`): the same silhouette, the helical vortex banding, the rain bands, the cyan rents and the inner flashes, on surfaces instead of in a volume. It loses depth (parallax between three walls instead of a mass), soft self-shadowing and the fine billows, and the shells show as plates at the silhouette. Preset → tier: low → low, medium → medium, high → high, ultra → ultra (`undertow.json quality`, tested against `graphics_presets.json`).

## Cost

### Measured on a GPU (M1-RND-10, RX 9070 XT, whole frame of `undertow_test.tscn`, GPU median ms)

| Preset (tier) | Res | Horizon | Eye | Night | Before M1-RND-10 (Horizon / Eye / Night) |
|---|---|---:|---:|---:|---|
| Low (shells) | 1440p | 1.70 | 2.25 | 1.99 | unchanged |
| Medium | 1440p | 2.90 | 4.00 | 3.74 | 10.42 / 12.34 / 14.86 |
| **High** | **1440p** | **3.95** | **5.35** | **5.04** | 25.80 / 28.35 / 35.72 |
| Ultra | 1440p | 12.92 | 16.22 | 16.82 | 76.09 / 80.71 / 106.36 |
| High | 1080p | 2.27 | 3.12 | 2.89 | 15.07 / 16.75 / 20.50 |

The frame without the storm costs 0.6–1.4 ms of these. Target for High at 1440p was ≤ 6.0 ms on this card (≈ 16.7 ms projected on an RTX 3060, see `docs/kb/qa/gpu/2026-10-23-gpu-report.md` for the projection factors). Per-lever numbers, look diffs and method: `docs/kb/qa/gpu/2026-10-23-rnd-10-undertow-perf.md`. What changed:
- **Baked noise** (`assets_src/vfx/undertow/bake_noise3d.py` → `assets/vfx/undertow/undertow_noise3d.png`, a 64³ RGBA8 3D texture; `undertow.json "noise"`): the cloud fBm, detail, curl and light-sample noise are one trilinear fetch at a quintic-remapped coordinate instead of eight PCG3D hashes. Inside [0, 64)³ lattice cells it *is* the old noise (to 8 bits); outside it repeats, so the billow layout changed (same character). The **wounds keep hashing** (`undertow_common.gdshaderinc` is untouched): their fields span only a few cells, where a wrapped lattice moved the rents.
- **Wounds evaluated only where the cloud has density** (bit-identical image).
- **`curl_reuse`**: the curl warp is recomputed every N dense steps (reset after an empty stride).
- **Fewer steps + `temporal_jitter`**: `jitter_phase` (UndertowState, an R1 sequence over frames) rotates the per-pixel IGN offset each frame, so TAA/FSR2 integrates several step phases.

> The lavapipe tables below predate M1-RND-10 and stay as the record of the feature ranking. Their "GPU budget" estimates are superseded by the measurements above.

### Method (reproducible)
```bash
~/.cache/hymn/godot-4.6.3+ds-2/godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync \
  --resolution 960x540 res://game/levels/_tests/undertow/undertow_bench.tscn -- --camera=Cameras/Horizon
```
The same method as the water bench: CPU time of the Godot process per frame (from `/proc/self/stat`, so other load on the shared 4-core machine cannot inflate it). There are 10 configurations, 2 interleaved rounds, 3 warm-up plus 4 measured frames each, and the minimum is kept. 960×540 matches the shots.

### Measured (lavapipe CPU ms per 960×540 frame; "storm" = the frame minus the same view with the storm hidden)
| Configuration | Horizon (dusk), storm ≈ 45% of pixels | | Eye (high angle), ≈ 85% | |
|---|---|---|---|---|
| | frame | storm | frame | storm |
| no storm (the ocean fills the footprint) | 500 | 0 | 510 | 0 |
| **Low** (shells) | 865 | **+365** (8% of High) | 933 | **+423** (8%) |
| Medium (28 steps) | 2215 | +1715 (36%) | 2615 | +2105 (39%) |
| **High** (44 steps) | 5230 | **+4730** (100%) | 5928 | **+5418** (100%) |
| Ultra (72 steps) | 8665 | +8165 (173%) | 9088 | +8578 (158%) |
| High − body | 518 | +18 | 635 | +125 |
| High − sea (and lid) | 5328 | within noise | 5483 | within noise |
| High − spray | 5283 | within noise | 5635 | within noise |
| High − wounds (`wound_intensity` 0) | 5305 | within noise | 5783 | within noise |
| High at 22 steps | 2820 | +2320 (49%) | 3358 | +2848 (53%) |

Reading:
- **The raymarched body is the storm's cost: 99% (horizon) and 98% (eye) of it.** The sea funnel, lid, spray curtains and wound seams together sit within this method's noise (about ±150 ms here). Note that the sea and lid *replace* ocean pixels, so they can even save time: the ocean is the more expensive surface.
- The body scales with steps (High at 22 steps costs half of High at 44). High costs about 2.7× Medium per frame because of the curl warp, the extra octave and the noisy light samples. Ultra's extra steps cost another 60–70%.
- **Low is cheap** (8% of High) and keeps the read (see Tiers).
- These numbers were taken before the final dusk sun azimuth change (212° instead of 262°) and the larger sea floor. Neither touches the storm's per-pixel work.

### GPU budget (estimates, not measured)
Calibrated against the water bench, the only ratio we have. Water High costs about 0.9 µs of lavapipe CPU per covered pixel and is estimated at 1.0–2.0 ms on an RTX 3060 at 1971×1109 with 60% coverage (water.md). The storm's High body costs about 20 µs per covered pixel on the same method (about 22× water). An operation count agrees: about 3,000 ALU ops per dense step (two-phase fBm, curl warp, coarse light samples, envelope), about 25 dense steps a pixel, so about 75k ops a pixel against water's 2k. Read these as **±2×**:

| Tier on target hardware | Internal res, storm coverage | Est. GPU ms |
|---|---|---|
| **High on RTX 3060** (recommended; FSR2 0.77) | 1971×1109, ~45% (a horizon shot) | **16 – 33** |
| Ultra on RTX 3060 | 2560×1440, ~45% | 45 – 90 |
| Medium on GTX 1060 (1080p, 0.85) | 1632×918, ~45% | 12 – 25 (a 1060 has about 40% of a 3060's ALU) |
| **Low on GTX 1060** (minimum; 1080p, 0.77) | 1478×831, ~45% | **1.5 – 3** |

**The raymarched tiers do not fit the frame budget.** High's whole-frame budget (graphics_settings.md) is 11.4–17.5 ms before the storm, and a storm shot can afford about **2–3 ms**. Low fits. Medium, High and Ultra are 5–15× over. This is a prototype of the *look*. The cost work is M2's first job (see below), and the shots that use the storm (Ch1, Ch8, Ch20–21) are cutscenes, where a lower frame rate or a reduced zone load is negotiable but 30 ms is not.

## Honest assessment against "the most important visual in the game"

**Does it read?** Mostly, yes, for the two required shots:
- **Horizon (dusk):** a colossal, side-lit storm tower filling two thirds of the frame over a darkening sea, with helical banding that says "rotating", rain-band skirts spreading kilometres along the horizon, a gold-lit upper flank against a dark slate lower wall (gorgeous and doomed), cyan rents glowing in the shadow side, a lightning flash inside the base, and a boat and lighthouse a few pixels tall for scale.
- **Eye (high angle):** a hurricane-like ring of cloud around an open eye, at whose bottom the sea is pulled down into a maelstrom with spiral foam and cyan held light sinking into the throat. This is the strongest "this is not an ordinary storm" image.
- **Night:** the mass goes near-black and the wounds and the strike dominate, as the brief asks.
- **Low** keeps the silhouette, banding, wounds and flashes.

**Where it falls short of "the most important visual in the game"** (my estimate: about a third of the way there):
1. **Cost** (above): the raymarched tiers are 5–15× over budget. Nothing else matters until this is fixed.
2. **Cloud surface quality:** the billows are soft and "smoky" at 960×540, with no crisp cauliflower edges, no wispy fractal fringe, and a fairly uniform khaki-gold where lit. The IGN dither shows as grain without TAA (the captures use FXAA for determinism). The striations are too regular: they read as stacked plates at a glance.
3. **Wounds** (M2-RND-05 adds dark torn lips, a halo and curtains of held light: "Storm events")**:** at dusk they read as glowing smears and blobs more often than as torn seams. They are not yet clearly *rents* (dark edges, light pouring out, motes peeling off visibly at the near ones). The held motes (`GlimmerField`) are human-scale and so sub-pixel at storm distance. The storm has no km-scale "mote streamers" coming off its wounds yet.
4. **Integration** (M2-RND-05: reflection, zone shadow and rain, "Storm events")**:** the storm does not appear in reflections (the sea reflects the sky only), does not shadow or darken the zone's light, and adds no rain or near-field weather. The horizon sea in front of it is therefore too calm and too unaffected.
5. **Motion is unproven:** differential rotation, two-phase advection, sinking wounds and flashes all run on the storm clock and are deterministic, but nobody has watched them at frame rate on a GPU. The two-phase cross-fade may "breathe" visibly over `flow_cycle_s`.
6. **Inside the storm** (Ch20) and very close approaches are untested: the proxy works with the camera inside, but there is no near-field detail.
7. (M2-RND-05 adds bolts and the exposure flash: "Storm events".) The lightning is glow only: no bolt geometry, no exposure flash (the colour script wants 2.0× exposure for 2 frames in Ch8).

**What M2 must add** (in priority order):
1. **Make the body affordable.** *Largely done in M1-RND-10 (baked noise, step jitter, curl reuse: High 1440p 25.8–35.7 → 4.0–5.4 ms on an RX 9070 XT). What remains here is headroom:* render it at half or quarter resolution into its own buffer (a compositor effect or SubViewport) with temporal reprojection and a depth-aware upsample. Replace the hash noise with **baked tileable 3D noise textures** generated in-repo (`tools/` script → `.exr`/`.res`, with PROVENANCE rows): one fetch replaces about 150 ALU ops a sample. Use blue-noise jitter plus TAA, and early-out on opacity. Target ≤ 2–3 ms on High. Measure on the GPU runner (M1-QA-01).
2. **Surface detail:** an erosion/detail pass with curl-advected high-frequency noise at the cloud boundary only, a powder term, multiple-scattering approximation (octave-scaled extinction), and irregular striations (noise-modulated phase and spacing).
3. **Wounds as rents:** a dark-edged seam profile, glow that pours *out* (in-scatter into the haze around the rent), km-scale held "streamers" (a storm-scale particle pass or a ribbon mesh) peeling off and sinking toward the sea, plus the zone-scale `GlimmerField` near the camera.
4. **Integration:** capture the storm into the sky/reflection (a low-res storm-only cubemap or a reflection-probe pass) so the sea reflects it; darken the zone's sun and ambient by the storm's shadow along the light direction; add rain curtains, near-field spray and wind-driven chop that grows as `approach_distance_m` falls (the water's `hymn_wind` can carry part of this).
5. **Lightning:** branching bolt meshes for close strikes, an exposure flash hook for the colour script's 2-frame flashes, and the sea lit by the strike.
6. **Cinematics hooks:** an `UndertowStorm` preset per chapter (Ch1 arrival, Ch8 storm wall, Ch20 interior, Ch21 the Letting: wounds turning to `glimmer_lift` and rising via the rule-1 hue lerp), and a timeline/AnimationPlayer track that drives `approach_distance_m`, `intensity` and `force_flash`.
7. **Art review** against the colour script with paintovers, and the `spawn_wound` usage decision.

### Half-resolution body (M2-RND-01)
Medium raymarches the body at `body_scale` 0.5 of the view and High at 0.35 (undertow.json `quality.*.body_scale`, M2-RND-01 min-spec decision below; Ultra 1).
`UndertowStorm.half_res_body_scale` overrides it (−1 = the tier).

How it works (`UndertowHalfRes`, `undertow_composite.gdshader`):
- The body moves to visual layer 20, and the game camera stops drawing that layer.
- A `SubViewport` that shares the world renders only that layer, through a camera that copies the game camera
  every frame. The copy happens on `RenderingServer.frame_pre_draw`, after the camera has moved.
  - The SubViewport is transparent, HDR (`use_hdr_2d`) and linear-tonemapped.
  - Its TAA is off, because TAA does not keep a transparent viewport's alpha.
- The composite is drawn on the body's own proxy cylinder in the game view, premultiplied, so it sorts as the body
  did.
  - It reads the half-res frame through a 3×3 tent, four bilinear taps. At half resolution each march-jitter
    sample covers a 2×2 block, which narrows TAA's neighbourhood clamp so the history couldn't average the jitter
    out; the tent removes the stipple before TAA sees it.
  - **Occlusion:** the SubViewport sees no opaque geometry. So the composite drops a pixel whose opaque depth is
    nearer than where the ray enters the capped cylinder of the wall's foot (eye + wall + skirt radius, slab
    sea → top).
  - Opaque geometry inside that cylinder isn't occluded (the old body clipped against the depth buffer per
    sample). Nothing in the test scene is there. A boat inside the eyewall would need the M2 compute path (below).

Measured (RX 9070 XT, High 1440p, GPU including the SubViewport):

| Camera | Full res | Half res |
|---|---:|---:|
| Day | 4.94 ms | 2.27 ms |
| Eye | 5.41 ms | 2.68 ms |
| Night | 5.06 ms | 2.25 ms |
| Horizon | 3.97 ms | 1.94 ms |

- **Glow dither on High** (FSR2): 0.0092, against 0.0291 at full resolution. That's within 16 % of native TAA
  without the M1-RND-16 cutscene override.
- **Panning** at 0.15° a frame on Ultra reads like the full-res body.

**Superseded as the default by the compute body (next section).** The SubViewport path remains the fallback
(Compatibility, headless) and the A/B control (`UndertowStorm.half_res_compute = false`).

### Compute body (M2-RND-01, ADR 0028)
Where a RenderingDevice exists, the half-res body is `UndertowBodyEffect`, a CompositorEffect on the current
game camera's Compositor; the SubViewport isn't built.
- **Where it runs:** at PRE_TRANSPARENT, after the opaque pass, at `body_scale` of the *internal* resolution (so
  under FSR2's render scale too).
- **Occlusion:** it marches the same `undertow_march()` as the spatial body, clipped at the **farthest** opaque
  surface in each low-res pixel's footprint, from this frame's depth. It writes `body_texture` (premultiplied,
  RGBA16F) and `front_texture` (R32F, the opacity-weighted mean distance of what each ray saw).
- **Composite:** `undertow_composite.gdshader` (`use_front`) samples both in the transparent pass, after the
  water as before, and drops each full-resolution pixel whose own opaque surface is nearer than the front
  distance.
- **Result:** exact occlusion inside the volume, with sharp edges. A test pillar inside the wall (x 7600 m, Day
  camera, `capture_preset --add-box`) is painted over completely by the SubViewport path and occludes the storm
  correctly in the compute path.
- **Source of truth:**
  - The spatial uniforms (`undertow_common_uniforms.gdshaderinc`, `undertow_body_uniforms.gdshaderinc`).
  - `tools/rendering/gen_undertow_compute.py` writes the std140 block (`undertow_compute_params.glslinc`),
    `UndertowComputeLayout` (offsets, defaults, source_color flags), the flattened compute body and the three
    tier twins (`undertow_body*_compute.glsl`, with the spatial variants' macros).
  - Run it after editing a uniform; `tools/tests/test_gen_undertow_compute.py` fails on stale outputs.
- **Packing:** each frame on the main thread (`frame_pre_draw`), from the body material's own parameters (an
  unset one takes its declaration's default; source_color colours are converted to linear, as Godot does), plus
  `hymn_sun_direction` from ShaderGlobals. The render thread adds the view: the camera projection and transform
  and the sizes.
- **Shells:** a hidden body (Low) has no half-res renderer, and the effect skips any frame where the body is
  hidden.

Measured (RX 9070 XT, High 1440p, GPU median, the whole frame):

| Camera | SubViewport | Compute |
|---|---:|---:|
| Day | 2.56 ms | 2.45 ms |
| Eye | 3.11 ms | 2.84 ms |
| Night | – | 2.43 ms |
| Horizon | – | 2.08 ms |
| Day, Medium | – | 1.96 ms |

The look matches the SubViewport path (RMSE 0.003–0.009 on the five Undertow shots at High), with a slightly
smoother wound glow. **Still open:** its own reprojected history, and a quarter-resolution tier for min-spec
(RTX 3060 projection ~7.4 ms on Day High).

### Striations, billows and the wound skin (M2-RND-01, criterion 2)
Aimed at review-sweep-G's "uniform khaki lit tone" and "regular striations". Report:
`docs/kb/qa/gpu/2026-10-23-m2-rnd-01-start.md`, "Billows and striations".
- **Striations** (`undertow_striation`, common include, so the Low shells follow). One low-frequency noise sample in
  the frame that turns with the eyewall bends the helix phase by up to `shape.striation_warp` turns (0.35) and
  flattens it by up to `striation_vary` (0.6), over `striation_warp_scale_m` (4.5 km). The body reads its baked
  lattice (`UNDERTOW_BAKED_NOISE`, two channels in one fetch); the shells hash. Skipped where the wall envelope is 0.
- **Billows** (body only). On the cloud's eroding fringe, where the density is between 0 and 1 (the surface a view
  sees), a 1 km field (`cloud.billow_scale_m`) is folded into billow noise `|2n - 1|` and added **zero-mean** (its
  mean over the lattice is 0.33, measured) × `billow_weight` 0.8 × `4 d0 (1 - d0)`. They reshape the fringe
  without thinning coverage, and they leave the solid core and the outermost wisps alone.
  - **Sun-ward shading:** the same fold one `billow_shade_step_m` (300 m) toward the sun, minus here, removes
    optical depth × `billow_shade` (3). Each lump is lit on its sun side. Medium compiles it out
    (`UNDERTOW_BILLOW_SHADE 0`).
  - The envelope is not the surface: the wall's envelope reaches 1 about a kilometre before the eroded front the camera
    sees, so an envelope-weighted billow did nothing.
- **Wound skin refinement** (`wounds.skin_step` 0.25). The rents glow in a 900 m skin, and High's dense steps are
  several hundred metres long. So 1–3 steps landed in it depending on the jitter, and that variance was the
  rents' stipple: TAA averages it, FSR2 (High) keeps it (no reactive mask, see Gotchas). Inside the skin the
  step is at most `wound_skin_m × skin_step`.
  - **Step budget:** a refined step spends only `ds / dense stride` of the `march_steps` budget, with
    `UNDERTOW_SKIN_LOOP` (2×) iteration headroom. Counting it as a whole step ended rays before they crossed the
    wall, which showed as see-through holes on `undertow_horizon_dusk`.
- **Cost (RX 9070 XT, High 1440p, GPU median):** Day 2.28 → 2.56 ms, Eye 2.79 → 3.11 ms. Ultra Day 16.1 → 17.7 ms.
- **Sea wind streaks** (water `storm` group, `water_surface_body.gdshaderinc`): the lines meander across by up to
  3 streak widths and break into foam flecks along their length, with a softer profile. Before, they were hard,
  straight, parallel rails.

## Storm events (M2-RND-05)

The storm as an event, on top of the body. `UndertowEvents` (`game/vfx/undertow/undertow_events.gd`) is an internal
child of `UndertowStorm`; the storm calls `build()` on every rebuild and `update()` every frame. Tunables are in
undertow.json: `streamers`, `bolts`, `exposure_flash`, `rain`, `zone_shadow`, `reflection`, `unbinding` and `presets`,
with the per-tier counts in `quality`. Key frames: `docs/kb/qa/gpu/rnd05/`. Report and cost:
`docs/kb/qa/gpu/2026-10-24-rnd-05-undertow-events.md`. Art's sign-off: M2-ART-03.

### Torn rents
`undertow_wound()` (common include) now returns two more bands around each seam's open core:
- a **lip**, `wounds.lip_width` seam widths wide, where the cloud is torn. Its lit colour and the pooled held
  light are darkened by `lip_dark`, and it's a little denser;
- a wider **halo** (`halo_width`), where the light pouring out scatters in the cloud beside the rent
  (`halo_energy` × the seam glow, weighted by density).

The body, the Low shells and the sea use the same function, so every tier gets dark-edged rents.

**The drift is integrated.** The seams' drift down the wall, and the throat streaks' drift into the funnel, are
now `wound_drift_m` and `glow_drift_m`, integrated by `UndertowState` (not `speed × time` in the shader), so the
Letting can reverse them without the pattern jumping. Held, they equal the old `sink_m_s × t` exactly.

### Curtains of held light (streamers)
`UndertowMeshBuilder.streamers()` builds curtains anchored on the wall's outer face inside the wounds' height
window, spread by a golden-angle sequence. Each one:
- falls to the sea and bulges out from the face toward the foot (`reach_m`), like the spray;
- trails `twist_rad` sideways and widens toward the sea;
- faces outward.

`undertow_streamer.gdshader` turns them with the wall and slides a pattern of motes down them with the wounds'
drift (arc length in UV2). It's additive, near half only (as the outer spray), and fades a curtain seen edge-on.
Counts: Low 8, Medium 12, High 16, Ultra 24.

### Lightning bolts and the exposure flash
**Bolts.**
- At a strike (a site's flash crossing `bolts.threshold`), a scheduled flash shows a cloud-to-sea bolt with
  `bolts.chance`; `force_flash` always shows one.
- The stroke runs from the cloud base (`top_m`) over the site's wall angle down to the sea just beyond the wall.
  It's deterministic in (site, strike), with `quality.bolt_branches` forks.
- `undertow_bolt.gdshader` draws it as view-facing quads, never thinner than `min_px` pixels, at the site's
  flash level.
- **A bolt draws only on the camera's half of the storm.** The body can't occlude a transparent stroke, and one
  behind the wall would show through. For a strike in view, a cutscene calls
  `storm.force_flash(storm.site_facing(camera.global_position))`.

**The exposure flash.** At each strike, `UndertowStorm.world_environment`'s `tonemap_exposure` is multiplied by
`exposure_flash.gain` (2.0) for `frames` (2): the colour script's Ch8 lightning frames.
- Photosensitivity follows the battle flashes (battle_vfx.md): at least `min_interval_s` (0.5 s) apart, so at
  most two a second, under WCAG 2.3.1's three. A refused flash counts in `UndertowEvents.flashes_suppressed`.
- Under reduced motion the gain is `reduced_motion_gain` (1.33).
- `storm.exposure_flash = false` turns it off. Captures do that.

**The signal.** `lightning_struck(site, bolt)` fires at each strike, for audio (thunder) and cutscenes.

### Rain
`UndertowRain` is a set of curtains on the camera (`undertow_rain.gdshader`). The streaks:
- fall on the storm clock (never `TIME`), slanted by `slant`;
- are lit by the storm's ambient (dimmed by the zone shadow);
- flash with the lightning.

**How hard it rains.** Full within `rain.full_m` of the eye, nothing beyond `reach_m` (the outer bands), none
above `ceiling_m` over the sea (a camera above the storm stays dry), all times `intensity`.
`storm.rain_amount` overrides it (−1 = automatic).

**Cost.** Every layer is a full-screen blend (about 0.06 ms at 1440p), so light rain draws only the inner
layers. Layers per tier: 1, 2, 3, 3.

### The zone shadow
`zone_shadow_at()` gives how deep the zone marker (the storm node) is in the storm's shadow: the canopy
overhead, or the canopy or wall on the line to the sun, times intensity.
- The zone's key light and its Environment ambient are dimmed by `sun_dim` (0.75) and `ambient_dim` (0.45) at
  full shadow.
- The storm itself stays lit by the undimmed key (`UndertowEvents.sun_energy()`).
- A zone script that changes the key or the ambient is re-read the next frame, so the shadow never compounds.
- Both come back when the storm leaves the tree or is hidden. `storm.zone_shadow = false` turns it off.

### The storm in the reflection
The engine's sky reflection never sees the storm, so the water shader's storm group reflects it:
- **Medium and High:** the reflected ray's point at the storm's distance is projected to the screen, and the
  half-res body's own pixel there (compute or SubViewport `body_tex`, ready before the water draws) is the
  reflection. That includes the wounds and the lightning, which reflect as glints in the chop.
- **Off screen, on Low (shells) and on Ultra (full-res body, no texture):** an analytic impostor of the wall
  and the canopy ring, coloured from the storm's lighting. Its gains are matched to the body's measured
  on-screen colour; a naive albedo × key was several times too bright (a white band, found on the GPU).
- Where the storm is reflected, the sky reflection gives way to it. `reflection.strength` × intensity; it's
  cleared when the storm leaves.

### Chapter presets and the Letting
`storm.preset = "ch08_landfall"` (or `apply_preset(id)`) sets storm properties from undertow.json `presets`. Each
preset is a starting point from the colour script, awaiting Art (M2-ART-03):

| Preset | Chapter |
|---|---|
| `ch01_arrival` | Ch1, the storm out of a clear sky, far off |
| `ch08_seawall` | Ch8 16:00, the storm wall (the `undertow_day_ch08` reference) |
| `ch08_landfall` | Ch8 16:40, under the canopy's edge, near-night, heavy rain |
| `ch20_interior` | Ch20, inside the storm |
| `ch21_heart` | Ch21, phases 1–2, every wound open |
| `ch21_letting` | Ch21, phase 3 |

The zone still owns its light: key, fog and exposure, per color_script.md.

**`unbinding` (0..1) is the Letting.**
- Over its first half, the wounds' and the throat streaks' drift slows and reverses (sinking → rising, at
  `unbinding.rise_ratio`).
- Over its second half, `col_wound` and `col_held` lerp to `glimmer_lift` (colours `lift`), per colour script
  rule 1: the direction reverses, then the hue turns.
- The curtains follow (they share `col_held` and the drift).
- A cutscene tweens it over the countdown.

### Cost (RX 9070 XT, 2560×1440, GPU median over 300 frames, the storm's own by `gpu_bench --hide-storms`)

| Camera, High | Before | After | Of which rain |
|---|---:|---:|---:|
| Day (Ch8, 14 km, light rain) | 0.66 ms | **0.83 ms** | ≈ 0.10 ms (2 layers) |
| Eye (high angle, dry) | 0.76 ms | 0.80 ms | 0 |
| Night (light rain) | 0.68 ms | 0.79 ms | ≈ 0.06 ms (1 layer) |
| Horizon (dusk, dry) | 0.55 ms | 0.59 ms | 0 |
| Landfall (preset, full rain, under the canopy) | – | 0.84 ms | ≈ 0.17 ms (3 layers) |

- **Within the ~1 ms target at High** on every camera; about 2.5 ms projected on an RTX 3060.
- **Where the rest goes:** the curtains, bolts and reflection together add 0.03–0.06 ms.
- **Medium:** the Day frame rises 1.96 → 2.14 ms. **Ultra** (full-res body): 17.2 → 17.4 ms.
- **Low** (shells, 1 rain layer): Day 2.16 → 2.23 ms. See the finding in the report: Low's full-resolution
  shells cost more than High's 0.35-scale compute body.

### Still open
- **Rain on the sea:** no ripple rings.
- **No sky overcast:** the anvil darkening a zone's sky dome toward the storm isn't there. The storm itself is in
  the sky and in the reflection; the sky shader doesn't know it.
- **Ultra and Low** reflect the impostor, not the body.
- **Thunder:** `lightning_struck` is the hook, for Audio.
- **Per-chapter exposure flashes:** the gain is one value for now.

## Gotchas
- **Unshaded additive shaders write ALBEDO, not EMISSION (M2-RND-05).** With `unshaded` Godot outputs ALBEDO
  alone; EMISSION is dropped, so `blend_add` of EMISSION over a black ALBEDO drew nothing (the streamers and
  bolts were invisible until this was found).
- **UndertowEvents is a plain Node (M2-RND-05),** so it breaks the visibility chain: hiding the storm would leave
  the camera's rain drawing. `update()` gates on `storm.is_visible_in_tree()` and gives the zone its light back.
  `gpu_bench --hide-storms` measured 0.2 ms of "storm-free" frame until it did.
- **Rotate NORMAL with VERTEX** in a storm part that turns with the wall (the curtains): a stale normal made the
  edge-on fade hide the curtains facing the camera.
- **Compute body: four Godot 4.6 traps (M2-RND-01).**
  - A `.glsl` RDShaderFile expands one level of `#include` only, and is re-imported only when the `.glsl` itself
    changes. Hence the generated flat body, and the hash in each twin.
  - `RenderSceneData.get_cam_projection()` already carries the depth correction (reverse-Z, flipped Y). Applying
    `Projection.create_depth_correction()` again turns every ray around.
  - Set `Texture2DRD.texture_rd_rid` on the main thread (`set_deferred` from the render thread). Assigned on the
    render thread, the material kept sampling the placeholder.
  - Before freeing an RD texture, detach every Texture2DRD and material that uses it, or the material's uniform
    set fails ("Texture (binding: 1, index 0) is not a valid texture").
- **`capture_preset --mat-set` does not reach the half-res body (M2-RND-01).** The body renders in UndertowHalfRes's
  SubViewport, so a `--mat-set` uniform shows no change (albedo_gain=0.1 left the frame as it was). To try a body
  tunable, edit undertow.json for the run and restore it afterwards.
- **The half-res body (M2-RND-01) puts the body on visual layer 20 and clears that bit from the game camera's
  `cull_mask` every frame.** Don't use layer 20 for anything else in a scene with a storm.
- **Keep the node unrotated and unscaled.** The visuals are a top-level child placed at `storm_center()` in world axes. Its Y is irrelevant: see "Sea level".
- **Render priorities matter.** The lid must draw before the water (−1 < 0), and the body after the water. Anything transparent that should cover the storm (motes, rain near the lens, UI-like VFX) needs a priority above `render_priority.body` (2). The body ignores the transparent depth (`depth_test_disabled`, clipped against the *opaque* depth copy), so transparent things at lower priorities are painted over.
- **The lid hides transparent things below its height over the funnel** (lift + crest height, about 2–3 m): the ocean, as intended, but also any low transparent VFX placed on the storm's sea. Nothing gameplay-relevant lives there.
- **The ocean needs an opaque floor in deep water.** With nothing under it, the water's refraction reads the sky. The test scene places a navy floor at −200 m outside the storm footprint. The funnel goes to −260 m, so keep floors out of the footprint.
- **Water SSS at a low sun (finding for the water stream).** With the dusk sun at 5° *behind* the camera, `water_ocean`'s subsurface term painted saturated green bands across the open sea (rgb about 50/95/54). The test material sets `use_sss = false`. Water should look at the SSS view/sun geometry for grazing suns. I did not edit the water shader.
- **Captures hold the storm.** Each `undertow_*` shot's `setup` (tests/screenshots/shots.json, M1-RND-13) sets `Storm.playing = false`, so the clock stays at the mood's time, and names the mood (`"." : {"mood": ...}`); the rig no longer detects the capture. The scene's storm plays by default. Use the bench, or open the scene, to see it move. A held storm also holds its `jitter_phase` (the frame counter only advances with the clock), so captures keep a static dither pattern.
- **`temporal_jitter` needs temporal AA, and now checks for it (M1-RND-11).** UndertowStorm tells its state each frame whether the viewport accumulates (`use_taa`, or the FSR2 upscaler). Without that, `jitter_phase` is 0 (a static pattern), so a player who overrides High to FXAA gets a still dither instead of crawling grain.
- **How well the jitter integrates depends on the temporal method** (measured on the day shot's glow, RX 9070 XT, docs/kb/qa/gpu/2026-10-23-rnd-11.md). Under native TAA (Medium, Ultra) the dither integrates almost fully (high-frequency RMS 0.046 → 0.007). Under FSR2 (High) only partly (0.040 → 0.026): Godot 4.6 gives FSR2 no reactive mask for transparents, so it accumulates the storm body conservatively. For a storm close-up on High, a cutscene switches to TAA with FSR1 or bilinear scaling through the scoped override API (next item). Shifting the IGN pixel pattern per frame was tried and made FSR2 worse (0.030), so it was reverted.
- **Storm close-ups on High: push a scoped override at the cut (M1-RND-16).** `var h := GraphicsSettings.push_override(cutscene_node, {"aa": "taa", "scaling_mode": "fsr"})` at a camera cut (or behind a fade), and `GraphicsSettings.pop_override(h)` at the cut out; the override also pops itself when `cutscene_node` leaves the tree. The player's render scale and other settings stay; settings.cfg is never written. Overrides stack (last pushed wins, popping restores the one below; the last pop restores the viewport exactly). The storm is in `GraphicsSettings.VIEWPORT_STATE_GROUP`, so `on_viewport_state_changed()` re-gates `temporal_jitter` in the same frame as the push or pop. To compile the override's pipeline before the cut, spawn `ShaderPrewarm.spawn_with_state(scene_path, SceneRouter, GraphicsSettings.override_state({"aa": "taa", "scaling_mode": "fsr"}))` a few frames ahead, or push the override before the zone loads (the router's prewarm copies the live viewport). Details: graphics_settings.md, "Scoped overrides". **Measured (M1-RND-16, RX 9070 XT, `docs/kb/qa/gpu/2026-10-23-rnd-16-aa-override.md`):** `{"aa": "taa", "scaling_mode": "bilinear"}` brings the glow dither to 0.0062, 22 % under native TAA, and costs 0.40 ms *less* than FSR2. The 22 % is the unsharpened 0.77 upscale's blur, not better integration: with the jitter frozen, the same scaling already halves the static dither (0.0255 against native's 0.0509), and TAA removes 76 % of that against native's 84 % (control row, M1-RND-23). `"fsr"` gives 0.0123, +56 % over native and 0.30 ms less than FSR2. The cost column was measured with `gpu_bench --override` applying the same values as plain settings overrides, which give the same viewport state, **not through `push_override`**. The dither column did go through the push API (`capture_preset --push-override`). Prefer `bilinear` for storm close-ups; use `fsr` only when a sharp foreground needs the upscaler's sharpening. Ch1, Ch8 and Ch20-21 storm shots (M2 cinematics) use this.
- **Tier parameters are validated and clamped.** `tools/validate_data.py` (`undertow_quality_errors`) checks the tier ids, bodies, `march_steps` against each variant's compiled `UNDERTOW_MAX_STEPS`, `curl_reuse` 1–8, `temporal_jitter` bool, and the noise texture and slice count. At runtime `quality_plan` clamps `march_steps` to 0–128 and `curl_reuse` to 1–8 (the shader's hint ranges, tested).
- **Keep the noise lattice lossless with no mipmaps** (`undertow_noise3d.png.import`: `compress/mode=0`, `mipmaps/generate=false`). VRAM compression or mips would blur the lattice; the import is tested. Regenerate it with the PROVENANCE command if the hash ever changes (`tools/tests/test_undertow_noise.py` fails on a stale asset).
- **`spawn_wound` usage.** See "Palette note" above.

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
- **Lighting:** single scattering with a dual-lobe Henyey-Greenstein phase, sun transmittance from 1–3 sun-ward samples (envelope only on Medium, coarse noise above), ambient between `col_ambient_bottom` and `_top` with an occlusion term, and a **low-sun reach** (`sun_clear_height`, `sun_low_floor`): a low sun has crossed the outer bands first, so it gilds the upper storm while the lower wall stays dark slate. The albedo is a cool white. The mass reads as `storm_slate` through its own shadow, which is what lets its upper flanks catch the dusk gold (pillar 2: gorgeous and doomed).
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
storm.position = village_marker.position  # the point it approaches; keep the node unrotated/unscaled
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

A cutscene animates it by tweening these properties (`create_tween().tween_property(storm, "approach_distance_m", 4000.0, 12.0)`) and pausing or scrubbing the clock. The test rig (`undertow_test_rig.gd`) does what a zone does, driven by a mood table: key light, environment, approach, wounds, ambient, haze, sea-glow, a timed flash, and the camera aim. Under the screenshot capture it holds the clocks and uses FXAA, as the water rig does.

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
| Body | **3 lathe shells + canopy shell** (alpha-hash) | raymarch, 28 steps | raymarch, 44 steps | raymarch, 72 steps |
| Light samples | wrap-lit with a noise self-shadow | 1, envelope only | 2, coarse noise | 3, coarse noise |
| Curl turbulence | no | no | yes | yes |
| Cloud octaves | 3 (on the shell) | 3 | 4 + detail | 5 + detail |
| Wounds, lightning, striations, bands | yes (on the shells) | yes | yes | yes |
| Sea funnel, foam rings, throat glow, lid | yes (2 foam octaves) | yes (3) | yes (4) | yes (5) |
| Spray curtains | 1 | 2 | 2 | 2 |

**Low still reads as the Undertow** (`undertow_horizon_low`): the same silhouette, the helical vortex banding, the rain bands, the cyan rents and the inner flashes, on surfaces instead of in a volume. It loses depth (parallax between three walls instead of a mass), soft self-shadowing and the fine billows, and the shells show as plates at the silhouette. Preset → tier: low → low, medium → medium, high → high, ultra → ultra (`undertow.json quality`, tested against `graphics_presets.json`).

## Cost

> **"GPU" figures are estimates.** The only renderer here is lavapipe (Forward+ on the CPU, ADR 0009). Its cost per ALU op and per pixel is not a GPU's. Use the *ratios* between configurations to rank the parts, and replace the absolute figures with GPU-runner numbers (M1-QA-01 follow-up).

### Method (reproducible)
```bash
~/.cache/hymn/godot-4.6.3+ds-2/godot-render --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync \
  --resolution 960x540 res://game/levels/_tests/undertow/undertow_bench.tscn -- --camera=Cameras/Horizon
```
The same method as the water bench: CPU time of the Godot process per frame (from `/proc/self/stat`, so other load on the shared 4-core machine cannot inflate it). There are 10 configurations, 2 interleaved rounds, 3 warm-up plus 4 measured frames each, and the minimum is kept. 960×540 matches the shots.

COST_TABLE_PLACEHOLDER

## Honest assessment against "the most important visual in the game"

COST_ASSESSMENT_PLACEHOLDER

## Gotchas
- **Keep the node unrotated and unscaled.** The visuals are a top-level child placed at `storm_center()` in world axes.
- **Render priorities matter.** The lid must draw before the water (−1 < 0), and the body after the water. Anything transparent that should cover the storm (motes, rain near the lens, UI-like VFX) needs a priority above `render_priority.body` (2). The body ignores the transparent depth (`depth_test_disabled`, clipped against the *opaque* depth copy), so transparent things at lower priorities are painted over.
- **The lid hides transparent things below its height over the funnel** (lift + crest height, about 2–3 m): the ocean, as intended, but also any low transparent VFX placed on the storm's sea. Nothing gameplay-relevant lives there.
- **The ocean needs an opaque floor in deep water.** With nothing under it, the water's refraction reads the sky. The test scene places a navy floor at −200 m outside the storm footprint. The funnel goes to −260 m, so keep floors out of the footprint.
- **Water SSS at a low sun (finding for the water stream).** With the dusk sun at 5° *behind* the camera, `water_ocean`'s subsurface term painted saturated green bands across the open sea (rgb about 50/95/54). The test material sets `use_sss = false`. Water should look at the SSS view/sun geometry for grazing suns. I did not edit the water shader.
- **Captures hold the storm.** The rig sets `playing = false` and fixes the clock per mood. Use the bench, or open the scene, to see it move.
- **`spawn_wound` usage.** See "Palette note" above.

# Glimmer Motes and Night Sea-Glow (M1-RND-02)

Owner: Rendering. SPEC §8.2 item 3 and §7.1. The meaning rules come from [`art/color_script.md`](../art/color_script.md) (narrative light rules 1–3), [`art/README.md`](../art/README.md) convention 2, and bible §2. This page covers the API, the rules as implemented, every tunable, cost notes, and gotchas.

| Piece | Path |
|---|---|
| Component (Node3D) | `game/vfx/glimmer/glimmer_field.gd` (`class_name GlimmerField`) |
| State machine (pure, headless) | `game/vfx/glimmer/glimmer_state.gd` (`class_name GlimmerState`) |
| Tunables | `game/data/vfx/glimmer.json` |
| Particle process shader | `game/shaders/glimmer/glimmer_motes_process.gdshader` |
| Draw passes | `glimmer_motes_draw.gdshader` (direct), `glimmer_motes_reflect.gdshader` (still-water mirror); shared body `glimmer_motes_draw_body.gdshaderinc` |
| Sea-glow helper (for water) | `game/shaders/include/glimmer.gdshaderinc` → `hymn_sea_glow(...)` |
| Sea-glow overlay (any zone, today) | `game/shaders/glimmer/glimmer_sea_glow_overlay.gdshader` |
| Test scenes | `game/levels/_tests/glimmer/` (`glimmer_dusk`, `glimmer_night_held`, `glimmer_release`, driver `glimmer_test_stage.gd`) |
| Tests | `tests/unit/test_glimmer_state.gd`, `tests/unit/test_glimmer_field.gd` |
| Screenshot shots | `glimmer_dusk`, `glimmer_night_held`, `glimmer_release` in `tests/screenshots/shots.json` (960×540) |

## The meaning rules, as implemented

The player is never told these rules. They learn them, so every mote must obey them. Never use glimmer as generic sparkle (references.md, "must NOT do" item 10).

| Mode | Colour (palette) | Motion | Energy |
|---|---|---|---|
| `RELEASED` | `glimmer_lift` `#FFE9B8`, whitening to `glimmer_lift_hi` `#F4F8FF` late in life ("fades into the sky") | Slow vertical spiral up: rise 0.15–0.4 m/s, spiral radius 0.2–0.6 m, about 21 s per turn | `hymn_glimmer.a` (scene) or `modes.released.energy` |
| `HELD` | `glimmer_held` `#7FC6D9` | Sideways and down towards `sea_direction`: 0.05–0.2 m/s, 15–30° down bias, ±35° heading spread. Motes sink through `water_height_m`, slow down, and are absorbed (exp falloff with depth) | `hymn_glimmer.a` or `modes.held.energy` |
| `MACHINE` | `glimmer_bound` `#4FB3B0` | **None.** Velocity target is 0, no attractors, no breathing flicker. Its stillness is its wrongness | `hymn_glimmer.a` or `modes.machine.energy` |
| **Release** (held or machine → released) | Hue lerp in **Oklab** (a perceptual blend; cyan to gold doesn't go muddy) | Direction reverses with the hue, because the same blend factor drives velocity and colour | as above |

- **Release timing.** `release()` defaults to `release_duration_s` = **1.5 s**. The change travels outward from the release origin (the singer, the dancer, or the field itself) as a **wave**: each mote starts its own eased lerp after `release_wave.fraction` (0.4) × its rank, where rank is its distance from the origin over `radius_m` with 30% random jitter. So each mote's own lerp takes 0.9 s, and the whole field finishes in exactly 1.5 s. This is a deliberate reading of rule 1. The world "exhales" from the person outward, instead of every mote flipping in sync. Set `fraction` to 0 for a uniform 1.5 s lerp on every mote.
- **One hue per mote.** Core, halo, and tail all use the mote's single colour. The only blend is the sanctioned held → lift lerp.
- **Gathering around the living.** Attractors pull motes onto an orbit shell around a living node and swirl them about the vertical axis. A `half_height_m` > 0 makes the axis a segment, so motes wrap a standing figure. Released motes keep `keep_drift` (55%) of their rise inside the orbit, so around a dancer they climb in a helix. Bound motes ignore attractors.
- **Brightness variety.** Mote size follows a power law (`size_power` 3: many specks, a few large "lamps"). Brightness varies independently, 0.3–1.0. Uniform fireflies read as generic, and this variety is what keeps the field from looking like them.

## API

```gdscript
var field := GlimmerField.new()           # or instance it in a scene and set the exports
field.emission_shape = GlimmerField.EmissionShape.DISC
field.emission_extents_m = Vector3(5.0, 0.05, 0.0)   # disc: x = radius, y = half height
field.water_height_m = 0.0
field.mode = GlimmerState.Mode.HELD
add_child(field)                           # builds the GPUParticles3D child "Motes" in _ready

GlimmerField.set_scene_glimmer(Color("#FFE9B8"), 4.0)   # hymn_glimmer: a = colour-script energy
field.add_attractor(asha, 1.0, 0.7, GlimmerField.USE_DEFAULT, 0.8)   # strength, orbit r, swirl, half height
field.release(GlimmerField.USE_DEFAULT, asha)           # 1.5 s, the wave starts at Asha
field.release_finished.connect(_on_lifted)
GlimmerField.set_global_focus(rhen.global_position, 1.0)  # hymn_glimmer_focus: every field gathers here
field.set_quality(graphics_settings.preset_id)          # or field.apply_graphics_settings(gs)
```

### `GlimmerField` (Node3D)

| Member | Notes |
|---|---|
| `signal mode_changed(mode)`, `release_started(duration_s)`, `release_finished` | relayed from the state machine |
| `@export mode: GlimmerState.Mode` | setter `set_mode()`, which is immediate and cancels a release |
| `@export quality: String` | `"low"`…`"ultra"` (the GraphicsSettings preset ids); empty means `default_quality` |
| `@export emission_shape` (`BOX` / `DISC`), `emission_extents_m`, `emission_inner_radius_m`, `amount_multiplier` | emission volume in the field's local space; per-field density |
| `@export sea_direction`, `water_height_m`, `still_water_reflection` | seaward heading for held motes; absorption plane and mirror plane |
| `@export follow_scene_intensity` (default **true**), `intensity` | true: energy = `hymn_glimmer.a`. false: the per-mode JSON energy. `intensity` multiplies either |
| `@export follow_global_focus` (default true) | treat `hymn_glimmer_focus` as an extra attractor |
| `@export fill_light_energy`, `fill_light_offset_m` | optional OmniLight3D that follows the mote colour (0 means none) |
| `@export use_fixed_seed`, `fixed_seed`, `preprocess_s` | determinism; `preprocess_s` < 0 uses the JSON value (14 s, one full lifetime) |
| `set_mode(m)`, `get_mode()`, `release(duration_s = USE_DEFAULT, origin: Node3D = null) -> bool` | `release` returns false when already released |
| `is_releasing()`, `get_release_progress()`, `current_color()`, `release_origin()` | |
| `add_attractor(node, strength, radius_m, swirl, half_height_m) -> bool` | `USE_DEFAULT` (−1) takes the JSON default. Re-adding a node updates it. False if the node is null or the list is full (`attractor.max` = 8) |
| `remove_attractor(node)`, `clear_attractors()`, `get_attractor_count()`, `max_attractors()` | freed nodes are dropped automatically |
| `set_quality(id) -> bool`, `get_quality()`, `apply_graphics_settings(gs)`, `planned_amount()`, `reflection_active()` | |
| `refresh()` | re-apply after changing exports at runtime |
| `static set_scene_glimmer(tint, intensity)`, `set_global_focus(pos, radius_m)`, `clear_global_focus()` | write the project globals |
| `static_process_parameters()`, `dynamic_process_parameters()`, `draw_parameters()`, `reflect_parameters()`, `pack_attractors()` | **pure**: the exact uniform dictionaries pushed to the materials (unit-tested) |

### `GlimmerState` (RefCounted, no nodes)

`enum Mode { HELD, RELEASED, MACHINE }`, plus `set_mode()`, `release(duration_s)`, `advance(delta)`, `is_releasing()`, `release_progress()`, `shader_state()`, `blend_color()`, and `mode_from_name()` / `mode_name()`. `release_blend` (0 held, 1 released) and `machine_amount` (1 bound) are the field-wide values. `shader_state()` returns the transition endpoints and the linear progress, and the shader staggers them per mote. During a release, `mode` reads `RELEASED` from the first frame.

## Global uniforms

| Global | How glimmer uses it |
|---|---|
| `hymn_glimmer` | **a** = the colour script's mote emission energy for the frame (Ch2 2.5, Ch9 4.0, Ch21 6.0…). Motes use it when `follow_scene_intensity` is on. Sea-glow is **on whenever a > 0** (see below). **rgb** is a tint for other shaders. **Motes ignore it**, because their hue carries meaning |
| `hymn_glimmer_focus` | xyz = gather point, w = orbit radius in m (0 = off). Every field with `follow_global_focus` treats it as an attractor with strength `focus_strength` and half height `focus_half_height_m` |
| `hymn_wind_time` | the sea-glow clock (`hymn_sea_glow_global`). Motes use their own `flow_time_s`, which `GlimmerField` advances |

The default for `hymn_glimmer.a` in `project.godot` is **0**. A zone that never writes it gets **invisible motes** (with `follow_scene_intensity` on) **and no sea-glow**. That's intended (it is how `ending_dock` turns the dead off), but it is the first thing to check when "nothing shows".

## Night sea-glow (for the water stream)

The rule (color script rule 3): `sea_glow` `#1C6B78`, energy 0.04–0.15, ±25% slow noise with an 8–20 s period. It appears in every night frame and every post-sunset frame with open sea, and it is **exactly 0** in `ending_dock`. It is never dropped below 0.04 for performance.

```glsl
#include "res://game/shaders/include/globals.gdshaderinc"   // optional; enables *_global
#include "res://game/shaders/include/glimmer.gdshaderinc"   // includes common.gdshaderinc itself

// Pure form. Returns linear-light emission to ADD (to EMISSION, or to the water-column colour).
vec3 hymn_sea_glow(vec3 world_pos, float time_s, float energy, float column_m);
//   world_pos : world-space surface point (xz and the clock drive the noise)
//   time_s    : a pausable clock in seconds (hymn_wind_time or a cinematic uniform), not raw TIME
//   energy    : already gated: hymn_sea_glow_energy(zone_energy, hymn_glimmer.a)
//   column_m  : metres of water the view ray travels below the surface (0 = surface only);
//               a deep column glows up to 2x the surface value (1 - exp(-0.45 m^-1 * column))

// Gate and clamp: 0 if glimmer_intensity <= 0 or zone_energy <= 0, else clamp(zone_energy, 0.04, 0.15).
float hymn_sea_glow_energy(float zone_energy, float glimmer_intensity);

// Slow modulation alone, in [0.75, 1.25] (for water that wants to modulate something else too).
float hymn_sea_glow_modulation(vec3 world_pos, float time_s);

// Convenience (only when globals.gdshaderinc was included first): gate = hymn_glimmer.a, clock = hymn_wind_time.
vec3 hymn_sea_glow_global(vec3 world_pos, float zone_energy, float column_m);
```

- Also exported: the palette constants `HYMN_GLIMMER_LIFT`, `HYMN_GLIMMER_LIFT_HI`, `HYMN_GLIMMER_HELD`, `HYMN_GLIMMER_BOUND`, and `HYMN_SEA_GLOW_COLOR` (linear; tests check them against `palette.json`), plus `HYMN_SEA_GLOW_ENERGY_MIN` / `_MAX` / `_MOD_AMPLITUDE` / `_PERIOD_S` / `_PATCH_M`.
- **Multiply by transmission.** Light from below reaches the eye through `1 − F` (Fresnel). The overlay does this with Schlick, F0 = 0.02. Water should apply its own Fresnel to the returned value, so the glow sinks into the sky reflection near the horizon. Without it, the night sea reads as a lit teal floor. The first test frame proved this.
- **Zone energy** is the colour script's "Night sea-glow" value. Pass it as a material uniform (for example `uniform float sea_glow_energy : hint_range(0.0, 0.15) = 0.08;`).
- **Cost:** two 3D value-noise lookups (16 PCG3D hashes), one `exp`, and a `pow` for Fresnel per fragment. That's cheap for a full-screen sea surface, roughly 0.1–0.2 ms at 1440p on RTX 3060-class hardware (estimate).
- **Until water integrates it:** put `glimmer_sea_glow_overlay.gdshader` on a ShaderMaterial and set it as the `next_pass` of the sea material (the night test scenes do this). It is additive and unshaded, pulled 4 mm towards the camera to avoid z-fighting, and exposes `zone_energy` and `column_m`.

## Rendering design

- **Simulation:** `GPUParticles3D` with a custom particle shader, world-space (`local_coords = false`), `fixed_fps` 30, `preprocess` 14 s, lifetime 14 s. Motion is a target velocity that the actual velocity eases towards (`response_rate` 1.4 /s), giving the motes weight. The target is the mode drift plus divergence-free curl noise (`hymn_curl_fbm3`, one shared field sampled at the mote's position, so neighbours move together like a current rather than buzzing independently), plus attractors. Per-particle layout: see the header of `glimmer_motes_process.gdshader`.
- **Draw:** a 1×1 QuadMesh, billboarded in view space (`skip_vertex_transform`), additive and unshaded. Each mote has a gaussian core (2% at one core radius), a round inverse-square halo (quad half-size = 7 core radii), and a short tail: a gaussian streak along the screen-space velocity whose length is speed × `trail_time_s` (1.1 s), capped at 1.4 halo radii. A longer streak spreads the same light (alpha / (1 + 0.5 · trail)), so fast motes don't get brighter. Output is HDR (cores reach about 2–5) for Environment glow to bloom.
- **Soft particles:** both passes read `hint_depth_texture`. The direct pass fades over `soft_depth_m` (0.35 m) in front of opaque geometry. Without it, a mote sinking just under the sea surface leaves a hard horizontal cut where its camera-facing quad meets the water.
- **Still-water reflection** (second draw pass, `still_water_reflection` and tier `reflection`): mirrors each mote about `water_height_m`, multiplies by Schlick reflectance for that view ray, and draws it softer. Depth test is off (mirrored motes sit under the opaque water), so occlusion is done by hand: it compares the opaque depth with the point where the view ray meets the water plane, which means a figure in front of the water hides the reflection behind it.
- **Near-lens fade:** alpha is 0 nearer than 0.6 m and full from 2 m. Invisible motes (at the lens, fully absorbed, or unborn) collapse to zero area in the vertex shader, so they cost no fill.

## Tunables (`game/data/vfx/glimmer.json`)

| Section | Keys |
|---|---|
| `colors` | `released`, `released_hi`, `held`, `machine`: sRGB hex from palette.json (tested) |
| `release_duration_s`, `release_wave` | 1.5 s; wave `fraction` 0.4, `radius_m` 4, `jitter` 0.3 |
| `modes.released` | `energy` 3.0, `rise_min/max_mps` 0.15/0.4, `spiral_radius_min/max_m` 0.2/0.6, `spiral_rate_rad_s` 0.3, `curl_scale` 0.4, `hi_shift` 0.55 |
| `modes.held` | `energy` 1.5, `drift_min/max_mps` 0.05/0.2, `down_bias_min/max_deg` 15/30, `heading_spread_deg` 35, `curl_scale` 1.0 |
| `modes.machine` | `energy` 1.2 |
| `motion` | `curl_frequency` 0.35 /m, `curl_strength_mps` 0.05, `curl_evolve` 0.04, `response_rate` 1.4, `underwater_drag` 3, `underwater_absorb_per_m` 2.2 |
| `attractor` | `max` 8 (= `HYMN_GLIMMER_MAX_ATTRACTORS` in the shader, tested), `default_strength` 1, `default_radius_m` 0.7, `default_swirl` 1, `default_half_height_m` 0, `influence_scale` 3 (× radius), `pull_mps` 0.5, `swirl_mps` 0.45, `keep_drift` 0.55, `focus_strength` 0.8, `focus_half_height_m` 0.8 |
| `look` | `size_min/max_m` 0.012/0.045, `size_power` 3, `halo_scale` 7, `core_gain` 0.8, `halo_gain` 0.12, `halo_falloff` 0.6, `streak_gain` 0.25, `streak_width` 1.6, `trail_time_s` 1.1, `trail_max_ratio` 1.4, `breath_rate_hz` 0.18, `breath_depth` 0.22, `fade_in/out_fraction` 0.12/0.3, `reflection_gain` 1, `reflection_softness` 1.6, `brightness_min` 0.3, `brightness_power` 1.5, `near_fade_start/end_m` 0.6/2, `soft_depth_m` 0.35 |
| `emitter` | `amount` 450 (at High), `lifetime_s` 14, `preprocess_s` 14, `fixed_fps` 30, `aabb_margin_m` 6 |
| `fill_light` | `range_m` 6, `attenuation` 1.6 |
| `quality` | per tier: `amount_scale`, `trail_scale`, `curl_octaves`, `reflection` |

### Quality tiers

| Tier | Motes (×amount) | Trails | Curl octaves | Reflection |
|---|---|---|---|---|
| low | 0.35 (158) | off (round billboards) | 1 | off |
| medium | 0.6 (270) | 0.6× | 2 | on |
| high | 1.0 (450) | full | 2 | on |
| ultra | 1.5 (675) | full | 3 | on |

No tier removes the effect (a test asserts amount ≥ 1 and growing with tier). Changing the tier changes `GPUParticles3D.amount`, which **restarts the emitter**, so apply it behind the same fade as the graphics presets. The mapping from GraphicsSettings is the preset id itself: call `field.apply_graphics_settings(gs)` after each zone load.

## Cost notes (estimates, not measurements)

> CPU-render timings below come from Mesa lavapipe (ADR 0009). They are **not** GPU cost. GPU figures are arithmetic estimates (±50%) until the GPU runner exists.

- **Measured on lavapipe** (960×540, 30 frames, shared 4 vCPU, noisy): the dusk scene takes about 15–22 s without motes and about 27–28 s with 450 motes plus reflection. So the motes add roughly 0.2–0.4 s per CPU frame, almost all of it rasterising overlapping additive quads.
- **GPU estimate, High (450 motes + reflection, RTX 3060 at 1440p internal ~1971×1109):** the process shader does 2 curl octaves (6 analytic value-noise lookups, 48 PCG3D hashes), 2 Oklab conversions, and up to 9 attractor evaluations per mote, which is about 0.01–0.02 ms for 450 motes. Draw: about 900 quads, typically 20–60 px across at mid distance, so about 1–2 Mpx of additive fill with one depth fetch and a few `exp`. That's about **0.15–0.4 ms**. Ultra (675) is about 0.25–0.6 ms. Low (158, no reflection, no tail) is about 0.05–0.1 ms on a GTX 1060.
- **The risk is overdraw from big near motes.** The near-lens fade and zero-area collapse bound it, but a cutscene camera pushed into a dense field can still fill the screen with halos. If a shot hitches, lower `amount_multiplier` for that field first.
- **The sea-glow overlay** costs about 0.1–0.2 ms full-screen at 1440p (estimate). It is folded into the water shader once M1-RND-01 integrates it.
- **Fill light:** one shadowless omni per field, so use it only on hero fields.

## Determinism and captures

- Captures need `use_fixed_seed = true` and a fixed `fixed_seed`, a `preprocess` (default 14 s = one full lifetime, so the field is "full" on frame 1), `fixed_fps` (30), and the capture's `--fixed-fps 60`. The three shots are **bit-exact between runs of the same manifest** (RMSE 0.00000).
- **Order sensitivity (open).** The particle sim depends slightly on what the process rendered *before* the shot. Running `glimmer_dusk` alone versus after any other shot (even the 10-frame UI `boot_title`) shifts motes by sub-pixel amounts: RMSE 0.0018–0.0041, about half the 0.008 limit. The cause is not `fixed_fps` sub-stepping (it's identical at `fixed_fps` 0) and not volumetric-fog reprojection (the test scenes turn that off anyway). It is probably engine-global particle or frame time. **The baselines are approved from the full-manifest order** (what `tools/ci_local.sh` runs). New shots inserted *before* the glimmer shots may move them by up to about 0.004. Re-approve in that commit if they get close to the limit. Running `--shots glimmer_*` alone gives about 0.003 against these baselines, which is expected.
- Motes never read `TIME`. The flow clock is `GlimmerField.flow_time_s`, advanced in `_process`, so a paused tree pauses the current. The release progresses in `_process`, so `glimmer_release` at 45 settle frames (0.75 s at 60 fps) is exactly 50% through.
- `glimmer_test_stage.gd` writes the globals in `_ready` and **resets them in `_exit_tree`** (`hymn_glimmer.a` = 0, focus off), so later shots aren't affected.

## Gotchas

1. **`hymn_glimmer.a` defaults to 0**, which means no motes (when following the scene) and no sea-glow. See "Global uniforms".
2. **Quality changes restart the emitter** (the amount changes). Do it behind a fade.
3. **The reflection pass ignores depth** except against the water-plane hit, so tall geometry *reflected* in the water (by SSR) does not occlude mirrored motes. Use it on open still water (lagoons, flooded courts), not in cluttered harbours. Turn it off for rough water. When M1-RND-01's water has real planar or SSR reflections of transparents, drop it.
4. **Held motes under an opaque sea are hidden** once they sink. With a transparent or refractive water shader they'll be visible sinking and fading (absorption is already in the colour alpha), which is the intended look.
5. **`visibility_aabb`** is the emission extents plus a 6 m margin. A field whose motes are pulled far away by attractors, or rise higher than about 6 m, can be culled at the frame edge. Raise `aabb_margin_m` for tall shots.
6. **Attractor count is capped at 8** per field (uniform array size). The 9th `add_attractor` returns false.
7. **Shader globals:** the process shader includes `globals.gdshaderinc`. That's fine, because all six globals are registered in `project.godot`.
8. **Prewarm:** the materials are created in code, so they aren't in `game/data/settings/prewarm_materials.json` yet. A battle or dialogue transition that reveals a glimmer field for the first time may hitch while the pipelines compile. Follow-up: save the three materials as `.tres` under `game/vfx/glimmer/` and register them (the registry is Rendering-owned, M1-RND-06).
9. **Shared `/tmp` logs:** `tools/screenshots/capture.sh` writes `${TMPDIR:-/tmp}/hymn_capture.log`. With several worktrees capturing at once, set `TMPDIR` per worktree, or the logs interleave.

## Open items

- Integrate `hymn_sea_glow()` into the ocean shader (M1-RND-01, water stream) and retire the overlay in those zones.
- The dance for the dead: animate a moving attractor along the dancer's hand path (cinematics). The API supports it already: `add_attractor(hand_node, ...)` follows the node each frame.
- Real-GPU measurement of the cost table (M1-QA-01 runner).
- Art review: the gold reads as pale cream at dusk against a warm sky. That is per palette (`glimmer_lift` is a pale gold), but the Art Director may want the halo warmer than the core.

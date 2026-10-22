# Shader Conventions

These rules apply to every `.gdshader` and `.gdshaderinc` in the project. Rendering owns this folder, and other roles' shaders follow the same rules. Signature shaders are listed in SPEC §8.2, the renderer choice is in ADR 0002, and the graphics presets are described in `docs/kb/tech/graphics_settings.md`.

## Layout and naming

```
game/shaders/
  include/            shared .gdshaderinc only (no shader_type line)
    common.gdshaderinc   colour space, hashing, value noise, fBm, curl noise, quality tiers
    globals.gdshaderinc  project-wide global uniforms (see "Global uniforms")
  water/ glimmer/ storm/ character/ env/ vfx/ post/ sky/ ui/   one folder per domain
  test/               test-only shaders and materials (never referenced by game scenes)
```

- Files use `snake_case`, with the domain first and the stage last when it's not spatial. Examples: `water_ocean.gdshader`, `glimmer_motes_process.gdshader` (particles), `ui_dissolve_canvas.gdshader`, and `sky_painted.gdshader`.
- A quality variant appends its tier: `water_ocean_low.gdshader`. See "Quality tiers".
- Materials (`.tres`) sit next to the scene or asset that owns them. Shaders live here, and materials reference them.
- Include files with an absolute path, `#include "res://game/shaders/include/common.gdshaderinc"`, never a relative one.
- Every include has an include guard: `#ifndef HYMN_<NAME>_GDSHADERINC` / `#define ...` / `#endif`.

## Identifiers

| Kind | Rule | Example |
|---|---|---|
| Shared functions (includes) | `hymn_` prefix, `snake_case` | `hymn_fbm3`, `hymn_srgb_to_linear` |
| Shared macros and constants | `HYMN_` prefix, `UPPER_SNAKE` | `HYMN_QUALITY_HIGH`, `HYMN_TAU` |
| Global uniforms | `hymn_` prefix (one project namespace) | `hymn_wind`, `hymn_glimmer` |
| Material uniforms: textures | `tex_` prefix | `tex_albedo`, `tex_flow`, `tex_foam_mask` |
| Material uniforms: colours | `col_` prefix, with `source_color` | `col_shallow`, `col_glimmer_tint` |
| Material uniforms: scalars and vectors | plain `snake_case`, unit suffix where useful | `wave_height_m`, `foam_cutoff`, `noise_octaves` |
| Instance uniforms | `inst_` prefix | `inst_seed`, `inst_wetness` |
| Varyings | `v_` prefix | `v_world_pos` |
| Locals and shader-local functions | plain `snake_case`, no prefix | `shore_fade`, `sample_caustics` |

- Group the material uniforms with `group_uniforms <group>;` so the inspector stays readable. Give every tunable a `hint_range` and a default.
- Don't bury magic numbers. A tunable is a uniform with a hint. A true constant is a named `#define` or `const`, with a comment saying where it comes from (a paper, a standard, or a measurement).

## Colour

- Work in **linear** space everywhere. Albedo and colour textures use `source_color`, so Godot linearizes them. Data textures (normal, flow, masks) never do.
- Use `hymn_luminance` (Rec.709) for luma, `hymn_srgb_to_linear` and `hymn_linear_to_srgb` (exact IEC 61966-2-1) only when converting a value that arrives in sRGB, and the `hymn_*oklab*` pair for perceptual blends and grading. Per-zone tonemapping and LUT grading (SPEC §8.1) happen in post, not in surface shaders.

## Noise and randomness

- Use `common.gdshaderinc` and nothing else. No `sin()`-based hashes: they band and differ between GPUs. The hashes are PCG2D and PCG3D (integer-based and stable).
- `*_cell*` hashes take whole-number lattice coordinates. `hymn_hash12` and `hymn_hash33` take any float through its bits, for per-particle seeds and world positions.
- Value noise and fBm return values in [0, 1]. The `*_d` variants also return analytic derivatives.
- Curl noise (`hymn_curl_noise2`, `hymn_curl_noise3`, `hymn_curl_fbm3`) is divergence-free. Use it for glimmer motes (M1-RND-02), foam advection (M1-RND-01), and storm wisps (M1-RND-03).
- Drive animation from a time source the game controls (`hymn_wind_time`, or a uniform the cinematics system sets), not raw `TIME`, wherever a cutscene has to pause or scrub it.

## Global uniforms

These are declared in `include/globals.gdshaderinc` and **must be registered in `project.godot` under `[shader_globals]`** before any shader includes that file. On a GPU renderer, an unregistered `global uniform` is a compile error. The headless dummy renderer does **not** check this, so CI can't catch it.

| Name | Type | Meaning | Written by |
|---|---|---|---|
| `hymn_wind` | `vec4` | xyz = world direction × speed (m/s), w = gust strength 0–1 | weather / time-of-day system |
| `hymn_wind_time` | `float` | wind animation clock in seconds (pausable) | weather system |
| `hymn_time_of_day` | `float` | hours, 0 to 24; story scenes lock it (SPEC §8.1) | time-of-day system |
| `hymn_sun_direction` | `vec3` | normalized direction *towards* the sun or moon | time-of-day system |
| `hymn_glimmer` | `vec4` | rgb = linear tint, a = scene glimmer intensity | zone / cutscene |
| `hymn_glimmer_focus` | `vec4` | xyz = point where motes gather, w = radius in metres (0 = off) | battle / field / cutscene |

Write them from GDScript with `RenderingServer.global_shader_parameter_set(&"hymn_wind", value)`. Don't add a new global without updating this table and `project.godot` in the same commit.

## Quality tiers

Shaders can't read the graphics preset at runtime, so tiers are **compile-time variants**:

- `common.gdshaderinc` defines `HYMN_QUALITY_LOW` (0), `HYMN_QUALITY_MEDIUM` (1), `HYMN_QUALITY_HIGH` (2), and `HYMN_QUALITY_ULTRA` (3). `HYMN_QUALITY` defaults to HIGH.
- Branch with `#if HYMN_QUALITY >= HYMN_QUALITY_HIGH`. The include already caps fBm octaves (`HYMN_FBM_MAX_OCTAVES`: 8 at High and above, 4 below).
- A variant is a thin wrapper that keeps the body in an include:

```glsl
// water_ocean_low.gdshader
shader_type spatial;
render_mode cull_back;
#define HYMN_QUALITY HYMN_QUALITY_LOW
#include "res://game/shaders/water/water_ocean_body.gdshaderinc"
```

- Define `HYMN_QUALITY` **before** including `common.gdshaderinc`, directly or through the body include.
- Only add a variant when the cost difference has been measured. Most shaders need only the default. Map from preset to variant in `graphics_presets.json` when the first variant lands (a follow-up to M1-RND-05).
- Use a runtime uniform only for cheap, coherent branches, such as toggles that are the same across a draw.

## Shader-cache prewarm

Every material that can appear in a battle transition or a dialogue cut must be registered in `game/data/settings/prewarm_materials.json`, with `scenes: []` for any transition or a list of scene paths. Each quality variant is a separate pipeline and needs its own entry. `ShaderPrewarm` (`game/core/shader_prewarm.gd`) draws each one off-screen for `frames_to_render` frames during the `SceneRouter.prewarm_requested` transition and logs the max frame time against the 50 ms budget (SPEC §4.2).

## Testing

- Headless CI (dummy renderer) **does** run Godot's shader front end. Preprocessing, includes, parsing, and type and semantic checks all happen when a shader is first used (for example, `get_shader_uniform_list()`), not when `code` is assigned. Errors print `SHADER ERROR` and leave the shader with no uniforms.
- Headless does **not** run the GPU back end (SPIR-V generation, driver compile, pipeline creation) or check global-uniform registration. Those need the GPU runner (M1-QA-01).
- Every new include or shader gets a compile check in `tests/unit/`. `test_shader_prewarm.gd::test_common_include_compiles_in_every_shader_stage` is the pattern to copy: compile it, assert a known uniform exists, and assert the logger saw zero shader errors.

# Screenshot regression (SPEC §5.5, M1-QA-01, ADR 0009)

Godot renders real frames on the **CPU** here: Forward+ on Mesa **lavapipe** (Vulkan), on an Xvfb virtual display. No GPU is needed, so it runs in the cloud sandbox and on any stock Linux runner.

## One-time setup (cloud sandbox)

```bash
python3 tools/dev/fetch_godot.py        # Godot 4.6.3+ds-2 + sysroot (ADR 0008)
python3 tools/dev/fetch_render_deps.py  # + Mesa 26.2 lavapipe/llvmpipe, Xvfb, vulkaninfo: 88 pkgs, ~30 s
godot --headless --path . --import      # once per checkout (class cache)
```

This writes `~/.cache/hymn/godot-4.6.3+ds-2/godot-render`, a wrapper that sets `VK_DRIVER_FILES` (a lavapipe ICD patched to point into the sysroot), `__EGL_VENDOR_LIBRARY_DIRS`, `LIBGL_DRIVERS_PATH`, `GBM_BACKENDS_PATH`, `XKB_CONFIG_ROOT`, `XLOCALEDIR`, `FONTCONFIG_FILE`, `LP_NUM_THREADS` and `LP_NATIVE_VECTOR_WIDTH=256`. If `$DISPLAY` is unset, it also starts Xvfb (`HYMN_XVFB_SCREEN`, default `1920x1080x24`), using the host `Xvfb` when there is one and the sysroot copy otherwise. Every argument passes straight through to Godot.

## Everyday commands

```bash
tools/screenshots/capture.sh                       # every shot -> tests/screenshots/out/<id>.png
tools/screenshots/capture.sh --shots lighting_probe
python3 tools/screenshots/compare.py               # RMSE vs baselines; diffs in out/diff/<id>.png
python3 tools/screenshots/compare.py --update-baselines lighting_probe   # approve (after LOOKING at out/)
python3 tools/screenshots/compare.py --manifest-only                      # no rendering needed
tools/screenshots/capture.sh --driver opengl3      # Compatibility/llvmpipe (diagnosis only, see caveats)
```

`tools/ci_local.sh` runs capture and compare as its last step. It prints `SKIP` when the wrapper is missing (`capture.sh` exits 3). The wrapper is found at `$HYMN_GODOT_RENDER`, then `godot-render` on PATH, then the default cache path.

To run any scene by hand (to look at it, or to probe a feature):

```bash
~/.cache/hymn/godot-4.6.3+ds-2/godot-render --path . --audio-driver Dummy --fixed-fps 60 \
  res://tests/screenshots/capture.tscn -- --shots=<id> --out=/abs/dir
```

## Adding a shot

1. Add an entry to `tests/screenshots/shots.json`. Missing keys are filled from `defaults`:

   | Key | Meaning |
   |---|---|
   | `id` | output name (`out/<id>.png`, `baselines/<id>.png`) |
   | `scene` | `res://` path of the scene to instance |
   | `camera` | `"default"` (the scene's current camera) or a `Camera3D`/`Camera2D` path relative to the scene root, e.g. `"Cameras/Low"` |
   | `resolution` | `[w, h]`; the window is resized to this (max = Xvfb screen size) |
   | `settle_frames` | frames rendered before the grab (TAA, SDFGI, fog and auto-exposure need time) |
   | `seed` | passed to `seed()` before the scene is instanced |
   | `threshold_rmse` | max allowed linear-light RMSE vs. the baseline (0..1) |
   | `setup` | optional per-shot state pinned by the manifest (see [Per-shot setup](#per-shot-setup-m1-qa-04)) |
2. Run `tools/screenshots/capture.sh --shots <id>` and **open `tests/screenshots/out/<id>.png` yourself**. Check that it shows what you meant, not black, not the clear colour.
3. Approve it with `python3 tools/screenshots/compare.py --update-baselines <id>`, then commit `baselines/<id>.png` and `baselines/baselines.json`.
4. Keep baselines small: 1280×720 unless the shot is about resolution, and the whole folder well under 5 MB (ADR 0005). It is ~650 KB today.

A scene for capture must not depend on input, wall-clock time or unseeded randomness. Animated content is fine because `--fixed-fps 60` makes frame time deterministic.

## Per-shot setup (M1-QA-04)

A shot can pin state in the manifest, so a scene doesn't have to detect the capture (`CAPTURE_SCENE` checks, "which camera is current" moods) to hold it. `tests/screenshots/capture_setup.gd` (`CaptureSetup`) implements it:

```json
{
  "id": "water_shallows_storm",
  "scene": "res://game/levels/_tests/water/water_test.tscn",
  "camera": "Cameras/Shallows",
  "setup": {
    "globals":  {"hymn_wind_time": 40.0, "hymn_sun_direction": [0.2, 0.9, -0.3]},
    "nodes":    {"Sun": {"light_energy": 2.2, "light_color": "#FFE4CE"}, ".": {"start_time_s": 40.0}},
    "viewport": {"use_taa": false, "screen_space_aa": 1},
    "time_scale": 0
  }
}
```

| Key | What it sets | When |
|---|---|---|
| `globals` | RenderingServer global shader parameters. Each must be declared in `project.godot [shader_globals]`, which gives its type. | before the scene is instanced, again after its `_ready`, and twice every frame (see Hold order) |
| `nodes` | properties of nodes under the shot's scene root (`"."` is the root itself), including script `@export` vars | after the scene's `_ready`, and twice every frame |
| `viewport` | properties of the capture viewport, e.g. `use_taa`, `screen_space_aa` (1 = FXAA), `msaa_3d` | before the scene is instanced, and twice every frame |
| `time_scale` | `Engine.time_scale`. **0 is a fixed time:** delta-driven animation (AnimationPlayer, Tween, particles, `delta` in `_process`) and the shader `TIME` built-in stop at their first-frame values. Physics time stops too (bodies and `_physics_process` deltas are frozen) | for the whole shot |

- **Hold order.** The capture node has `process_priority = 1 << 20`, so it re-applies `globals`, `nodes` and `viewport` after every node in the scene has run `_process`. The SceneTree then runs its Tweens and timers (and physics and AnimationPlayers in their own callback modes can write too), so the setup applies them **again on `RenderingServer.frame_pre_draw`**, after all of those and just before the frame is drawn (M1-QA-06). For each held node it also flushes the pending transform notifications of the node and its subtree (`Node3D.force_update_transform`), because the SceneTree would otherwise only push a held transform to the renderer next frame, after that frame's Tweens wrote over it again. So a rig that writes the same global each frame (the water and Undertow rigs write `hymn_wind_time`), a Tween or an animation can't override the manifest. Frame-counting rigs keep counting, and only what the setup names is pinned. The hook is connected only while a shot with a non-empty `setup` runs.
- **Values** are JSON, converted to the target's current type: numbers become int, float or bool (enums are ints); `[x, y(, z, w)]` becomes Vector2/3/4(i), Quaternion or Color; `"#rrggbb"` becomes a Color; `"res://..."` loads a Resource for an Object property. Nothing else is converted: a value for a Transform3D, Basis, Rect2, Plane or AABB property fails the shot's type check (set its components instead, e.g. `position` and `rotation`), and Array and Dictionary properties take the JSON value as it is.
- **Errors fail the shot:** an unknown key, missing node, misspelt property, undeclared global, or a value that doesn't fit the type. `compare.py --manifest-only` checks the keys, and `tests/unit/test_capture_setup.gd` validates every setup in `shots.json`.
- **Restore.** When the shot ends, node, viewport and time-scale values return to what they were. Globals return to their `project.godot` default, **not** to the value the previous scene left, because Godot refuses to read a global's live value outside the editor. **Rule: a capture scene must not rely on a global shader parameter inherited from an earlier shot.** Set what it needs in `_ready` (the rigs do), or name it in `setup.globals`. Otherwise its frame depends on which shots a `HYMN_SHOTS` subset happens to run before it.
- **A shot without `setup` runs exactly as before.** The 58 baselines are untouched, and `water_shallows` re-rendered byte-identical through the new code path.
- **Measured** on `water_shallows` (2026-10-23): `"globals": {"hymn_wind_time": 40.0}` gives RMSE **0.0** against the rig's own capture hold (start_time_s = 40), which shows the manifest can stand in for the `CAPTURE_SCENE` hold. `80.0` gives 0.079, so the hold beats the rig's per-frame write. `"nodes": {"Sun": {"visible": false}}` gives 0.28. With `"time_scale": 0`, a `TIME` probe reads 0.016 s after 60 frames, against 1.0 s at scale 1.
- **Migrating a rig** off its capture detection belongs to the rig's owner. Move the held values (clock, TAA → FXAA, mood) into each shot's `setup`, delete the `CAPTURE_SCENE` branch, and confirm the shot still compares at RMSE 0.0 before re-approving anything. Candidates: `water_test_rig.gd`, `undertow_test_rig.gd`, `haluna_mood.gd`, whose camera → mood switch could become `nodes` overrides of an exported `mood`.

## Comparison

- Both PNGs are decoded with `tools/screenshots/pngio.py` (numpy + zlib, no Pillow), converted from sRGB to **linear** light, and compared by RMSE over RGB. Alpha is ignored.
- A size mismatch, a missing capture or a missing baseline all **fail**.
- `out/diff/<id>.png` shows the baseline at 35% brightness with per-pixel error in red. An error of 1/8 of full scale saturates the red.
- Measured sensitivity on `lighting_probe`: the same machine and settings give **0.00000** (bit-exact across runs). The residual TAA wobble between 20 and 60 settle frames is 0.002 to 0.005. Raising the sun's energy by 10% gives **0.0128**, and swapping Forward+ for Compatibility gives 0.24. Hence the thresholds: **0.008** for 3D shots and **0.004** for UI-only shots.

## Timings (this sandbox: 4 vCPU, warm shader cache)

| Shot | Resolution | Frames | Time |
|---|---|---|---|
| `boot_title` (UI) | 1920×1080 | 10 | ~0.4 s |
| `lighting_probe` | 1280×720 | 30 | ~11 s |
| `lighting_probe_low` | 1280×720 | 30 | ~8 s |
| Whole `capture.sh` (3 shots) | | | ~21 s wall |
| Whole `tools/ci_local.sh` | | | ~35 s |

- 3D costs about **0.26 s/frame at 720p** with shadows, SSR, SSAO and glow. With SDFGI and volumetric fog it rises to about 0.55 s/frame, and those effects need **≥ 20 settle frames** to converge (RMSE vs. 60 frames: 0.037 at 10 frames, 0.0025 at 20, 0.0011 at 30).
- On a **cold** shader cache (fresh `user://`), the first 3D shot takes ~25 s while lavapipe compiles the pipelines.

## Renderer caveats

- **Forward+ on lavapipe is the reference.** Godot reports `Vulkan 1.4.354 - Forward+ - llvmpipe (LLVM 22.1.8, 256 bits)`. Confirmed working: directional shadows, the clustered omni light, SSR, SSAO, glow, ProceduralSky ambient and reflections, TAA, SDFGI, and volumetric fog.
- It is **not** a GPU. Use it to catch regressions, not to judge final quality: precision, filtering and driver quirks can differ from NVIDIA/AMD. Judge fidelity and performance (1440p60 / 1080p30 targets) on real hardware.
- **Compatibility (`--driver opengl3`, llvmpipe GL 4.6) also works**, about 2× faster, but it drops SSR, SSAO, TAA, SDFGI and volumetrics and uses a different colour pipeline. Never approve Forward+ baselines from it. It exists only to tell "my scene is broken" apart from "Vulkan is broken".
- Baselines are tied to the stack named in `baselines/baselines.json` (Godot distro build, Mesa 26.2.4, LLVM 22). A different Mesa or the official Godot build may shift pixels slightly, so the CI `screenshots` job is `continue-on-error` until baselines approved on that runner exist.
- `LP_NATIVE_VECTOR_WIDTH=256` pins llvmpipe's SIMD width so AVX-512 hosts rasterise like AVX2 hosts.
- `--headless` still draws nothing. `capture.tscn` refuses to run under it (exit 2).

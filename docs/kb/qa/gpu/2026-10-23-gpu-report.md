# GPU performance report, 2026-10-23 (M1-QA-01 follow-up)

> **Status: PARTIAL.** The main sweep (every test scene × 4 presets × 2 resolutions) and the Undertow Horizon breakdown are complete and valid. Still pending: the Undertow **Eye** breakdown, the **water** breakdown, and the **screenshot drift** run (step 3). They stopped because the PC's display went to sleep after 60 min idle (23:06 local), and Vulkan cannot create a swapchain without a display (`swap_chain_resize`, `rendering_device_driver_vulkan.cpp:3369`). Someone needs to wake the display at the machine. See "Harness gotchas".

These are the first **real GPU** numbers for the project. Everything in `graphics_settings.md`, `water.md`, `undertow.md`, `glimmer.md` and `character_shading.md` was estimated from lavapipe.

## Hardware and software

| | |
|---|---|
| GPU | **AMD Radeon RX 9070 XT**, 16 GB VRAM (RDNA 4) |
| Driver | AMD Adrenalin 26.6.1 (32.0.31019.2002), Vulkan 1.4.349 |
| CPU / RAM | Intel Core i9-12900K (16 cores), 32 GB |
| OS | Windows 10 Home 22H2 (10.0.19045), 64-bit |
| Display | 3440×1440 primary; the bench uses a borderless window at the origin |
| Engine | Godot **4.6.3-stable official** win64 (`7d41c59c4`), SHA512 matches `SHA512-SUMS.txt` from godot-builds |
| Project | `claude/new-session-mj8c3c` @ `4363fc2`, Forward+ / Vulkan |

**This is not a SPEC §4.2 reference card.** The RX 9070 XT is roughly 2.3–2.8× an RTX 3060 and 4.2–5.0× a GTX 1060 in raster workloads. Those factors are my estimates from public benchmarks, not measured here. The verdicts below project through those ranges, and they're conservative: PASS means it passes even at the slow end, FAIL means it fails even at the fast end. ALU-bound shaders (the Undertow raymarch) may scale *worse* than raster on older cards, because the 1060 has about a tenth of the 9070 XT's shader throughput. **Re-measure on a real RTX 3060 / GTX 1060 before signing off §4.2.**

## Method

- Harness: `tools/gpu_bench/gpu_bench.gd` + `.tscn`, driven entirely by the command line (options in the script header). Full sweep: `GODOT=<godot> tools/gpu_bench/run_sweep.sh <out.csv>`. Tables: `python tools/gpu_bench/summarize.py <out.csv>`.
- One Godot process per scene/camera, windowed (never `--headless`), `--disable-vsync`, `Engine.max_fps = 0`.
- Per configuration, the preset is applied through `GraphicsSettings.set_preset()` + `apply_current(viewport, environment)`. The matching tier is applied to every `WaterSurface`, `UndertowStorm`, `GlimmerField`, and to the character materials via `CharacterShaderTiers.apply_to_tree`, because those maps aren't in `graphics_presets.json` yet.
- Warm-up: **120 frames and at least 3 s** after every change (async pipeline compiles; frames take about 1 ms here, so 120 frames alone is only about 0.1 s). Then **300 sampled frames**, reading `RenderingServer.viewport_get_measured_render_time_gpu()` and `_cpu()` (with `viewport_set_measure_render_time` on).
- Reported: median and p99 (nearest rank). p99 sits within 1–10% of the median everywhere, so there were no compile hitches in the sampling window.
- The test rigs run **animated** (they only freeze their clocks under `capture.tscn`).
- "Internal" is the 3D render size: output × `scaling_3d_scale` (Low and High 0.77, Medium 0.85, Ultra 1.0).
- CPU ms is the **render-thread** submission time for the viewport. It never exceeded 0.37 ms p99. These test scenes are GPU-bound, so CPU cost is a non-issue at this scale.
- Scenes: the four water cameras, the three Undertow cameras (HorizonLow is skipped because the rig forces Low there), the three glimmer scenes, three vegetation cameras, three character_shading cameras (Compare is skipped because it holds a duplicated Low bust), three base-body cameras, `field_shot_court` (a bonus, the closest thing to a zone), and `battle_sandbox`. **There is no `haluna_mood` scene** in `game/levels/_tests/` on this branch.

## Headline

1. **The Undertow's raymarched body is the only thing that misses budget, and it misses badly.** At High and 1440p it costs **25.9 ms (Horizon), 28.3 ms (Eye) and 35.7 ms (Night) on a 9070 XT**, which projects to **about 60–100 ms on an RTX 3060** against a 16.7 ms frame. Ultra at 1440p Night measures **106 ms** on this card (9 fps). Medium also fails on both reference tiers. **Low (shells) passes everywhere.**
2. **Everything else is cheap.** No other scene goes above **2.0 ms at High 1440p or 3.3 ms at Ultra 1440p** on this card, which projects to at most about 5.6 ms (High) on an RTX 3060. Caveat: these are isolated feature test scenes, not a dressed zone. The "Base" row in `graphics_settings.md` (5–7 ms) still has to be measured on a real vertical-slice zone (M2).
3. **Bug: SSR roughness quality does nothing.** In 4.6.3, `RenderingServer.environment_set_ssr_roughness_quality` is deprecated and logs *"has been deprecated and no longer does anything"* at `graphics_settings.gd:213` on every apply. The `ssr_roughness_quality` setting (Low/Medium/High/Ultra) is therefore a no-op. `test_planned_engine_api_names_exist_in_this_godot` passes because the method still exists. Remove the setting, or replace it with whatever 4.6 offers (owner: Rendering, M1-RND-05).

## Worst case per preset (RX 9070 XT, GPU median ms)

| Preset | 1920×1080 worst (all) | 1920×1080 worst non-storm | 2560×1440 worst (all) | 2560×1440 worst non-storm |
|---|---:|---:|---:|---:|
| Low | 1.33 (undertow Eye) | 0.69 (water Lagoon) | 2.26 (undertow Eye) | 1.12 (water Lagoon) |
| Medium | 8.53 (undertow Night) | 1.08 (water Lagoon) | 14.87 (undertow Night) | 1.73 (water Lagoon) |
| High | 20.48 (undertow Night) | 1.30 (char SkinEye) | **35.66** (undertow Night) | 1.99 (water Lagoon) |
| Ultra | 60.12 (undertow Night) | 2.08 (water Lagoon) | **105.97** (undertow Night) | 3.28 (water Lagoon) |

## Undertow cost by tier and feature (Horizon camera; Eye pending)

The column is the GraphicsSettings preset (environment, shadows, render scale). The row picks the storm tier, as in `UndertowBench.CONFIGS`. The value is GPU median ms; the parenthesised value is the delta against "no storm" in the same column.

| Config | Low preset 1080p | High preset 1080p | Low preset 1440p | High preset 1440p |
|---|---:|---:|---:|---:|
| no storm | 0.42 | 0.64 | 0.60 | 1.08 |
| low (shells) | 1.03 (+0.61) | 1.30 (+0.66) | 1.71 (+1.11) | 2.18 (+1.10) |
| medium | 5.06 (+4.64) | 5.31 (+4.66) | 8.50 (+7.90) | 9.01 (+7.93) |
| high | 14.96 (+14.54) | 15.16 (+14.52) | 25.31 (+24.71) | 25.81 (+24.73) |
| ultra | 27.15 (+26.73) | 27.54 (+26.90) | 46.49 (+45.89) | 46.67 (+45.59) |
| high - body | 0.42 (+0.00) | 0.67 (+0.03) | 0.63 (+0.03) | 1.11 (+0.03) |
| high - sea | 14.90 (+14.48) | 15.22 (+14.58) | 25.29 (+24.69) | 25.68 (+24.60) |
| high - spray | 14.91 (+14.50) | 15.22 (+14.58) | 25.30 (+24.70) | 25.73 (+24.65) |
| high - wounds | 14.91 (+14.50) | 15.21 (+14.57) | 25.30 (+24.70) | 25.82 (+24.73) |
| high, 22 steps | 7.54 (+7.12) | 7.78 (+7.14) | 12.76 (+12.16) | 13.20 (+12.12) |

- **The body is the whole cost.** Hiding it ("high - body") brings the frame back to the no-storm figure. Sea, lid, spray curtains and wounds are each within ±0.1 ms, so they are free.
- **Cost is linear in march steps:** 22 steps costs 51% of 44 (7.78 vs 15.16 ms at 1080p). Each dense step costs about **0.33 ms at 1478×831 internal** on this card.
- **The storm cost doesn't depend on the preset.** The storm delta is the same under the Low and High presets at the same output size (both use 0.77 render scale), so shadows, SSR, GI and fog don't interact with it.
- **Ultra is about 1.8× High, and High about 2.9× Medium.** That's close to the lavapipe *ratios* in `undertow.md` (+60–70% and 2.7×). Lavapipe ranked the features correctly but underestimated the absolute cost: undertow.md projected the raymarched tiers at "5–15× over" a 2–3 ms slot, and High on an RTX 3060 at 1440p is about **20–35× over**.
- **The resolution scaling is almost ideal.** 1080p to 1440p is 1.78× the pixels and 1.70× the cost, so the half-/quarter-resolution body that undertow.md proposes for M2 should cut cost by roughly 4× / 16×.

## Top 3 costs to fix

1. **Undertow raymarched body, High/Ultra (blocker for §4.2).** 25.9–35.7 ms at High 1440p on a 9070 XT, about 60–100 ms on an RTX 3060. To fit **≤ 2–3 ms on an RTX 3060** it needs to be about **1 ms on this card**: a 25–35× cut. The M2 plan in undertow.md (render at quarter resolution with temporal reprojection, about 16×; baked 3D noise in place of hash fBm; early-out on opacity) is the right direction. Measure each step with `gpu_bench --variants=undertow`.
2. **The Undertow Medium tier can't serve as a fallback.** 8.5 ms (1080p) and 14.9 ms (1440p) at Night on this card, so about 36–43 ms on a GTX 1060 at 1080p and about 34–42 ms on an RTX 3060 at 1440p. Until (1) lands, ship the storm as **shells (Low tier) on every preset**, with raymarched tiers opt-in for capture or trailers. Shells cost 1.1 ms at 1440p here, about 2.5–3 ms on a 3060.
3. *(Provisional, pending the water breakdown.)* **Water-heavy views are the heaviest non-storm content.** Lagoon is 1.99 ms at High 1440p and 3.28 ms at Ultra 1440p (about 4.6–5.6 ms and 7.5–9.2 ms on an RTX 3060), with Ultra +65% over High. It fits the budget alone, but it's the biggest line item a coastal zone will add. Re-ranked once the `--variants=water` run shows how much is the water shader itself (SSR, refraction, caustics).

## Budget verdicts (all scenes)

Projected = measured median × the factor range under "Hardware". The budget is 16.7 ms for High (60 fps) and 33.3 ms for Low (the 30 fps floor of the §4.2 minimum tier).

| Scene | Camera | High 1440p on RTX 3060 (60 fps): 9070 XT ms -> projected ms -> verdict | Low 1080p on GTX 1060 (30 fps floor): 9070 XT ms -> projected ms -> verdict |
|---|---|---|---|
| water | Cameras/Shallows | 1.84 -> 4.2-5.2 -> **PASS** | 0.64 -> 2.7-3.2 -> **PASS** |
| water | Cameras/Lagoon | 1.99 -> 4.6-5.6 -> **PASS** | 0.69 -> 2.9-3.4 -> **PASS** |
| water | Cameras/Horizon | 1.58 -> 3.6-4.4 -> **PASS** | 0.55 -> 2.3-2.7 -> **PASS** |
| water | Cameras/Night | 1.81 -> 4.2-5.1 -> **PASS** | 0.66 -> 2.8-3.3 -> **PASS** |
| undertow | Cameras/Horizon | 25.86 -> 59.5-72.4 -> **FAIL** | 1.02 -> 4.3-5.1 -> **PASS** |
| undertow | Cameras/Eye | 28.32 -> 65.1-79.3 -> **FAIL** | 1.33 -> 5.6-6.6 -> **PASS** |
| undertow | Cameras/Night | 35.66 -> 82.0-99.8 -> **FAIL** | 1.17 -> 4.9-5.9 -> **PASS** |
| glimmer_dusk | ShotCamera | 1.19 -> 2.7-3.3 -> **PASS** | 0.29 -> 1.2-1.5 -> **PASS** |
| glimmer_night_held | ShotCamera | 1.23 -> 2.8-3.5 -> **PASS** | 0.36 -> 1.5-1.8 -> **PASS** |
| glimmer_release | ShotCamera | 1.23 -> 2.8-3.4 -> **PASS** | 0.37 -> 1.5-1.8 -> **PASS** |
| vegetation | Cameras/Backlit | 1.30 -> 3.0-3.6 -> **PASS** | 0.39 -> 1.7-2.0 -> **PASS** |
| vegetation | Cameras/FrangipaniClose | 1.74 -> 4.0-4.9 -> **PASS** | 0.59 -> 2.5-3.0 -> **PASS** |
| vegetation | Cameras/Wide | 1.60 -> 3.7-4.5 -> **PASS** | 0.52 -> 2.2-2.6 -> **PASS** |
| character_shading | Cameras/SkinEye | 1.98 -> 4.6-5.6 -> **PASS** | 0.63 -> 2.7-3.2 -> **PASS** |
| character_shading | Cameras/HairBack | 1.58 -> 3.6-4.4 -> **PASS** | 0.48 -> 2.0-2.4 -> **PASS** |
| character_shading | Cameras/Cloth | 1.65 -> 3.8-4.6 -> **PASS** | 0.49 -> 2.1-2.5 -> **PASS** |
| characters | Slender/Cameras/Front | 0.97 -> 2.2-2.7 -> **PASS** | 0.24 -> 1.0-1.2 -> **PASS** |
| characters | Slender/Cameras/Face | 0.96 -> 2.2-2.7 -> **PASS** | 0.24 -> 1.0-1.2 -> **PASS** |
| characters | Heavy/Cameras/ThreeQuarter | 0.98 -> 2.2-2.7 -> **PASS** | 0.23 -> 1.0-1.1 -> **PASS** |
| field_court | default | 1.11 -> 2.6-3.1 -> **PASS** | 0.29 -> 1.2-1.4 -> **PASS** |
| battle_sandbox | default | 0.88 -> 2.0-2.5 -> **PASS** | 0.30 -> 1.2-1.5 -> **PASS** |

Scenes that miss budget: **undertow (Horizon, Eye, Night) at High 1440p on the recommended tier**. All three also miss at Medium. Every other scene passes both checks with a wide margin. Low on a GTX 1060 holds even 60 fps everywhere (worst: undertow Eye, about 5.6–6.6 ms projected).

## Screenshot drift (GPU vs. lavapipe baselines)

**Pending.** Blocked by the display sleeping. The runner is ready: `GODOT=<godot> tools/gpu_bench/capture_gpu.sh <out_dir>` (one process per shot, like `capture.sh`), then `python tools/screenshots/compare.py --out <out_dir>`. Baselines are not touched.

## Harness gotchas

- **The display must be awake.** On Windows, Godot's window needs a live display for the Vulkan swapchain. After the monitor's idle timeout (60 min here), every process logs `swap_chain_resize ... ERR_CANT_CREATE` and reports **0.00 ms GPU at about 16 ms frames**. Four rows of the Undertow Eye breakdown were lost this way and dropped from the CSV. `summarize.py` discards `gpu_median_ms == 0` rows. Hold the display on *before* a long run (power settings, or `SetThreadExecutionState(ES_CONTINUOUS|ES_DISPLAY_REQUIRED)`). That keeps a display awake but cannot wake one that is already off.
- Very low GPU load (about 1 ms frames) can leave a GPU at partial clocks, so the light scenes' absolute numbers may read slightly high. That doesn't change any verdict.

## Full table (RX 9070 XT)

Raw data, one row per measurement (scene, camera, variant, preset, output and internal resolution, GPU/CPU/frame median, p99 and mean): [`2026-10-23-gpu-bench.csv`](2026-10-23-gpu-bench.csv).

| Scene | Camera | Preset | Res | Internal | GPU med | GPU p99 | CPU med | CPU p99 |
|---|---|---|---|---|---:|---:|---:|---:|
| water | Cameras/Shallows | low | 1920x1080 | 1478x832 | 0.64 | 0.69 | 0.10 | 0.20 |
| water | Cameras/Shallows | medium | 1920x1080 | 1632x918 | 1.00 | 1.06 | 0.11 | 0.21 |
| water | Cameras/Shallows | high | 1920x1080 | 1478x832 | 1.11 | 1.17 | 0.11 | 0.23 |
| water | Cameras/Shallows | ultra | 1920x1080 | 1920x1080 | 1.88 | 1.97 | 0.10 | 0.21 |
| water | Cameras/Shallows | low | 2560x1440 | 1971x1109 | 1.07 | 1.18 | 0.10 | 0.20 |
| water | Cameras/Shallows | medium | 2560x1440 | 2176x1224 | 1.59 | 1.74 | 0.10 | 0.22 |
| water | Cameras/Shallows | high | 2560x1440 | 1971x1109 | 1.84 | 1.96 | 0.12 | 0.25 |
| water | Cameras/Shallows | ultra | 2560x1440 | 2560x1440 | 2.77 | 3.04 | 0.11 | 0.26 |
| water | Cameras/Lagoon | low | 1920x1080 | 1478x832 | 0.69 | 0.73 | 0.10 | 0.19 |
| water | Cameras/Lagoon | medium | 1920x1080 | 1632x918 | 1.08 | 1.13 | 0.10 | 0.20 |
| water | Cameras/Lagoon | high | 1920x1080 | 1478x832 | 1.23 | 1.27 | 0.11 | 0.22 |
| water | Cameras/Lagoon | ultra | 1920x1080 | 1920x1080 | 2.08 | 2.14 | 0.10 | 0.22 |
| water | Cameras/Lagoon | low | 2560x1440 | 1971x1109 | 1.12 | 1.22 | 0.10 | 0.20 |
| water | Cameras/Lagoon | medium | 2560x1440 | 2176x1224 | 1.73 | 1.84 | 0.10 | 0.22 |
| water | Cameras/Lagoon | high | 2560x1440 | 1971x1109 | 1.99 | 2.09 | 0.12 | 0.23 |
| water | Cameras/Lagoon | ultra | 2560x1440 | 2560x1440 | 3.28 | 3.33 | 0.10 | 0.20 |
| water | Cameras/Horizon | low | 1920x1080 | 1478x832 | 0.55 | 0.58 | 0.09 | 0.17 |
| water | Cameras/Horizon | medium | 1920x1080 | 1632x918 | 0.85 | 0.89 | 0.09 | 0.18 |
| water | Cameras/Horizon | high | 1920x1080 | 1478x832 | 0.97 | 1.01 | 0.10 | 0.21 |
| water | Cameras/Horizon | ultra | 1920x1080 | 1920x1080 | 1.48 | 1.53 | 0.09 | 0.19 |
| water | Cameras/Horizon | low | 2560x1440 | 1971x1109 | 0.88 | 0.97 | 0.09 | 0.17 |
| water | Cameras/Horizon | medium | 2560x1440 | 2176x1224 | 1.36 | 1.47 | 0.10 | 0.20 |
| water | Cameras/Horizon | high | 2560x1440 | 1971x1109 | 1.58 | 1.68 | 0.10 | 0.22 |
| water | Cameras/Horizon | ultra | 2560x1440 | 2560x1440 | 2.27 | 2.39 | 0.09 | 0.18 |
| water | Cameras/Night | low | 1920x1080 | 1478x832 | 0.66 | 0.71 | 0.10 | 0.19 |
| water | Cameras/Night | medium | 1920x1080 | 1632x918 | 1.00 | 1.05 | 0.11 | 0.20 |
| water | Cameras/Night | high | 1920x1080 | 1478x832 | 1.10 | 1.15 | 0.12 | 0.23 |
| water | Cameras/Night | ultra | 1920x1080 | 1920x1080 | 1.75 | 1.79 | 0.11 | 0.21 |
| water | Cameras/Night | low | 2560x1440 | 1971x1109 | 1.08 | 1.20 | 0.10 | 0.20 |
| water | Cameras/Night | medium | 2560x1440 | 2176x1224 | 1.63 | 1.76 | 0.11 | 0.22 |
| water | Cameras/Night | high | 2560x1440 | 1971x1109 | 1.81 | 1.92 | 0.12 | 0.25 |
| water | Cameras/Night | ultra | 2560x1440 | 2560x1440 | 2.75 | 2.93 | 0.11 | 0.21 |
| undertow | Cameras/Horizon | low | 1920x1080 | 1478x832 | 1.02 | 1.07 | 0.08 | 0.16 |
| undertow | Cameras/Horizon | medium | 1920x1080 | 1632x918 | 6.14 | 6.19 | 0.08 | 0.16 |
| undertow | Cameras/Horizon | high | 1920x1080 | 1478x832 | 15.18 | 15.31 | 0.10 | 0.25 |
| undertow | Cameras/Horizon | ultra | 1920x1080 | 1920x1080 | 43.73 | 43.95 | 0.12 | 0.26 |
| undertow | Cameras/Horizon | low | 2560x1440 | 1971x1109 | 1.70 | 1.80 | 0.08 | 0.16 |
| undertow | Cameras/Horizon | medium | 2560x1440 | 2176x1224 | 10.47 | 10.54 | 0.09 | 0.34 |
| undertow | Cameras/Horizon | high | 2560x1440 | 1971x1109 | 25.86 | 26.03 | 0.12 | 0.28 |
| undertow | Cameras/Horizon | ultra | 2560x1440 | 2560x1440 | 76.15 | 76.55 | 0.14 | 0.33 |
| undertow | Cameras/Eye | low | 1920x1080 | 1478x832 | 1.33 | 1.37 | 0.07 | 0.17 |
| undertow | Cameras/Eye | medium | 1920x1080 | 1632x918 | 7.20 | 7.26 | 0.08 | 0.21 |
| undertow | Cameras/Eye | high | 1920x1080 | 1478x832 | 16.76 | 16.92 | 0.10 | 0.34 |
| undertow | Cameras/Eye | ultra | 1920x1080 | 1920x1080 | 46.49 | 46.81 | 0.11 | 0.29 |
| undertow | Cameras/Eye | low | 2560x1440 | 1971x1109 | 2.26 | 2.35 | 0.07 | 0.15 |
| undertow | Cameras/Eye | medium | 2560x1440 | 2176x1224 | 12.33 | 12.42 | 0.09 | 0.23 |
| undertow | Cameras/Eye | high | 2560x1440 | 1971x1109 | 28.32 | 28.46 | 0.12 | 0.31 |
| undertow | Cameras/Eye | ultra | 2560x1440 | 2560x1440 | 80.61 | 80.91 | 0.14 | 0.31 |
| undertow | Cameras/Night | low | 1920x1080 | 1478x832 | 1.17 | 1.21 | 0.08 | 0.17 |
| undertow | Cameras/Night | medium | 1920x1080 | 1632x918 | 8.53 | 8.60 | 0.09 | 0.29 |
| undertow | Cameras/Night | high | 1920x1080 | 1478x832 | 20.48 | 20.55 | 0.12 | 0.35 |
| undertow | Cameras/Night | ultra | 1920x1080 | 1920x1080 | 60.12 | 60.34 | 0.13 | 0.25 |
| undertow | Cameras/Night | low | 2560x1440 | 1971x1109 | 2.00 | 2.11 | 0.08 | 0.16 |
| undertow | Cameras/Night | medium | 2560x1440 | 2176x1224 | 14.87 | 14.94 | 0.13 | 0.37 |
| undertow | Cameras/Night | high | 2560x1440 | 1971x1109 | 35.66 | 35.75 | 0.14 | 0.36 |
| undertow | Cameras/Night | ultra | 2560x1440 | 2560x1440 | 105.97 | 106.22 | 0.17 | 0.36 |
| glimmer_dusk | ShotCamera | low | 1920x1080 | 1478x832 | 0.29 | 0.33 | 0.14 | 0.20 |
| glimmer_dusk | ShotCamera | medium | 1920x1080 | 1632x918 | 0.61 | 0.65 | 0.12 | 0.23 |
| glimmer_dusk | ShotCamera | high | 1920x1080 | 1478x832 | 0.74 | 0.78 | 0.13 | 0.24 |
| glimmer_dusk | ShotCamera | ultra | 1920x1080 | 1920x1080 | 1.09 | 1.14 | 0.13 | 0.23 |
| glimmer_dusk | ShotCamera | low | 2560x1440 | 1971x1109 | 0.48 | 0.59 | 0.09 | 0.18 |
| glimmer_dusk | ShotCamera | medium | 2560x1440 | 2176x1224 | 0.91 | 1.02 | 0.12 | 0.24 |
| glimmer_dusk | ShotCamera | high | 2560x1440 | 1971x1109 | 1.19 | 1.30 | 0.13 | 0.25 |
| glimmer_dusk | ShotCamera | ultra | 2560x1440 | 2560x1440 | 1.52 | 1.67 | 0.12 | 0.24 |
| glimmer_night_held | ShotCamera | low | 1920x1080 | 1478x832 | 0.36 | 0.40 | 0.09 | 0.22 |
| glimmer_night_held | ShotCamera | medium | 1920x1080 | 1632x918 | 0.67 | 0.71 | 0.12 | 0.23 |
| glimmer_night_held | ShotCamera | high | 1920x1080 | 1478x832 | 0.76 | 0.81 | 0.13 | 0.26 |
| glimmer_night_held | ShotCamera | ultra | 1920x1080 | 1920x1080 | 1.17 | 1.21 | 0.12 | 0.23 |
| glimmer_night_held | ShotCamera | low | 2560x1440 | 1971x1109 | 0.54 | 0.65 | 0.09 | 0.19 |
| glimmer_night_held | ShotCamera | medium | 2560x1440 | 2176x1224 | 1.03 | 1.14 | 0.12 | 0.24 |
| glimmer_night_held | ShotCamera | high | 2560x1440 | 1971x1109 | 1.23 | 1.34 | 0.13 | 0.25 |
| glimmer_night_held | ShotCamera | ultra | 2560x1440 | 2560x1440 | 1.64 | 1.76 | 0.12 | 0.24 |
| glimmer_release | ShotCamera | low | 1920x1080 | 1478x832 | 0.37 | 0.40 | 0.09 | 0.22 |
| glimmer_release | ShotCamera | medium | 1920x1080 | 1632x918 | 0.66 | 0.70 | 0.12 | 0.23 |
| glimmer_release | ShotCamera | high | 1920x1080 | 1478x832 | 0.76 | 0.80 | 0.13 | 0.25 |
| glimmer_release | ShotCamera | ultra | 1920x1080 | 1920x1080 | 1.16 | 1.22 | 0.12 | 0.24 |
| glimmer_release | ShotCamera | low | 2560x1440 | 1971x1109 | 0.53 | 0.64 | 0.09 | 0.19 |
| glimmer_release | ShotCamera | medium | 2560x1440 | 2176x1224 | 1.00 | 1.10 | 0.12 | 0.23 |
| glimmer_release | ShotCamera | high | 2560x1440 | 1971x1109 | 1.23 | 1.33 | 0.14 | 0.27 |
| glimmer_release | ShotCamera | ultra | 2560x1440 | 2560x1440 | 1.61 | 1.73 | 0.12 | 0.24 |
| vegetation | Cameras/Backlit | low | 1920x1080 | 1478x832 | 0.39 | 0.43 | 0.09 | 0.18 |
| vegetation | Cameras/Backlit | medium | 1920x1080 | 1632x918 | 0.64 | 0.68 | 0.10 | 0.21 |
| vegetation | Cameras/Backlit | high | 1920x1080 | 1478x832 | 0.85 | 0.89 | 0.11 | 0.21 |
| vegetation | Cameras/Backlit | ultra | 1920x1080 | 1920x1080 | 1.29 | 1.34 | 0.11 | 0.22 |
| vegetation | Cameras/Backlit | low | 2560x1440 | 1971x1109 | 0.56 | 0.66 | 0.09 | 0.20 |
| vegetation | Cameras/Backlit | medium | 2560x1440 | 2176x1224 | 0.94 | 1.05 | 0.10 | 0.21 |
| vegetation | Cameras/Backlit | high | 2560x1440 | 1971x1109 | 1.30 | 1.40 | 0.12 | 0.23 |
| vegetation | Cameras/Backlit | ultra | 2560x1440 | 2560x1440 | 1.73 | 1.84 | 0.11 | 0.21 |
| vegetation | Cameras/FrangipaniClose | low | 1920x1080 | 1478x832 | 0.59 | 0.63 | 0.10 | 0.19 |
| vegetation | Cameras/FrangipaniClose | medium | 1920x1080 | 1632x918 | 0.96 | 1.01 | 0.10 | 0.20 |
| vegetation | Cameras/FrangipaniClose | high | 1920x1080 | 1478x832 | 1.15 | 1.20 | 0.12 | 0.22 |
| vegetation | Cameras/FrangipaniClose | ultra | 1920x1080 | 1920x1080 | 1.98 | 2.03 | 0.11 | 0.22 |
| vegetation | Cameras/FrangipaniClose | low | 2560x1440 | 1971x1109 | 0.92 | 1.02 | 0.09 | 0.18 |
| vegetation | Cameras/FrangipaniClose | medium | 2560x1440 | 2176x1224 | 1.45 | 1.57 | 0.10 | 0.22 |
| vegetation | Cameras/FrangipaniClose | high | 2560x1440 | 1971x1109 | 1.74 | 1.85 | 0.12 | 0.24 |
| vegetation | Cameras/FrangipaniClose | ultra | 2560x1440 | 2560x1440 | 2.72 | 2.83 | 0.11 | 0.21 |
| vegetation | Cameras/Wide | low | 1920x1080 | 1478x832 | 0.52 | 0.56 | 0.10 | 0.20 |
| vegetation | Cameras/Wide | medium | 1920x1080 | 1632x918 | 0.83 | 0.87 | 0.11 | 0.22 |
| vegetation | Cameras/Wide | high | 1920x1080 | 1478x832 | 1.01 | 1.06 | 0.12 | 0.22 |
| vegetation | Cameras/Wide | ultra | 1920x1080 | 1920x1080 | 1.56 | 1.61 | 0.12 | 0.23 |
| vegetation | Cameras/Wide | low | 2560x1440 | 1971x1109 | 0.85 | 0.95 | 0.10 | 0.20 |
| vegetation | Cameras/Wide | medium | 2560x1440 | 2176x1224 | 1.28 | 1.39 | 0.11 | 0.22 |
| vegetation | Cameras/Wide | high | 2560x1440 | 1971x1109 | 1.60 | 1.71 | 0.12 | 0.24 |
| vegetation | Cameras/Wide | ultra | 2560x1440 | 2560x1440 | 2.20 | 2.31 | 0.12 | 0.22 |
| character_shading | Cameras/SkinEye | low | 1920x1080 | 1478x832 | 0.63 | 0.67 | 0.12 | 0.24 |
| character_shading | Cameras/SkinEye | medium | 1920x1080 | 1632x918 | 0.86 | 0.91 | 0.12 | 0.25 |
| character_shading | Cameras/SkinEye | high | 1920x1080 | 1478x832 | 1.30 | 1.34 | 0.14 | 0.27 |
| character_shading | Cameras/SkinEye | ultra | 1920x1080 | 1920x1080 | 1.92 | 1.96 | 0.13 | 0.27 |
| character_shading | Cameras/SkinEye | low | 2560x1440 | 1971x1109 | 0.79 | 0.88 | 0.12 | 0.24 |
| character_shading | Cameras/SkinEye | medium | 2560x1440 | 2176x1224 | 1.33 | 1.43 | 0.13 | 0.24 |
| character_shading | Cameras/SkinEye | high | 2560x1440 | 1971x1109 | 1.98 | 2.08 | 0.14 | 0.28 |
| character_shading | Cameras/SkinEye | ultra | 2560x1440 | 2560x1440 | 2.75 | 2.85 | 0.13 | 0.25 |
| character_shading | Cameras/HairBack | low | 1920x1080 | 1478x832 | 0.48 | 0.51 | 0.12 | 0.24 |
| character_shading | Cameras/HairBack | medium | 1920x1080 | 1632x918 | 0.74 | 0.78 | 0.13 | 0.27 |
| character_shading | Cameras/HairBack | high | 1920x1080 | 1478x832 | 1.05 | 1.09 | 0.15 | 0.28 |
| character_shading | Cameras/HairBack | ultra | 1920x1080 | 1920x1080 | 1.43 | 1.48 | 0.14 | 0.28 |
| character_shading | Cameras/HairBack | low | 2560x1440 | 1971x1109 | 0.68 | 0.77 | 0.12 | 0.25 |
| character_shading | Cameras/HairBack | medium | 2560x1440 | 2176x1224 | 1.14 | 1.24 | 0.14 | 0.27 |
| character_shading | Cameras/HairBack | high | 2560x1440 | 1971x1109 | 1.58 | 1.68 | 0.15 | 0.29 |
| character_shading | Cameras/HairBack | ultra | 2560x1440 | 2560x1440 | 2.04 | 2.14 | 0.14 | 0.27 |
| character_shading | Cameras/Cloth | low | 1920x1080 | 1478x832 | 0.49 | 0.53 | 0.12 | 0.23 |
| character_shading | Cameras/Cloth | medium | 1920x1080 | 1632x918 | 0.81 | 0.86 | 0.13 | 0.25 |
| character_shading | Cameras/Cloth | high | 1920x1080 | 1478x832 | 1.04 | 1.08 | 0.15 | 0.28 |
| character_shading | Cameras/Cloth | ultra | 1920x1080 | 1920x1080 | 1.41 | 1.46 | 0.14 | 0.27 |
| character_shading | Cameras/Cloth | low | 2560x1440 | 1971x1109 | 0.77 | 0.85 | 0.12 | 0.24 |
| character_shading | Cameras/Cloth | medium | 2560x1440 | 2176x1224 | 1.26 | 1.36 | 0.13 | 0.27 |
| character_shading | Cameras/Cloth | high | 2560x1440 | 1971x1109 | 1.65 | 1.75 | 0.15 | 0.29 |
| character_shading | Cameras/Cloth | ultra | 2560x1440 | 2560x1440 | 2.13 | 2.23 | 0.14 | 0.27 |
| characters | Slender/Cameras/Front | low | 1920x1080 | 1478x832 | 0.24 | 0.27 | 0.12 | 0.19 |
| characters | Slender/Cameras/Front | medium | 1920x1080 | 1632x918 | 0.35 | 0.39 | 0.08 | 0.16 |
| characters | Slender/Cameras/Front | high | 1920x1080 | 1478x832 | 0.55 | 0.59 | 0.09 | 0.18 |
| characters | Slender/Cameras/Front | ultra | 1920x1080 | 1920x1080 | 0.53 | 0.57 | 0.09 | 0.17 |
| characters | Slender/Cameras/Front | low | 2560x1440 | 1971x1109 | 0.38 | 0.46 | 0.07 | 0.15 |
| characters | Slender/Cameras/Front | medium | 2560x1440 | 2176x1224 | 0.63 | 0.72 | 0.08 | 0.17 |
| characters | Slender/Cameras/Front | high | 2560x1440 | 1971x1109 | 0.97 | 1.06 | 0.10 | 0.19 |
| characters | Slender/Cameras/Front | ultra | 2560x1440 | 2560x1440 | 0.92 | 1.02 | 0.09 | 0.18 |
| characters | Slender/Cameras/Face | low | 1920x1080 | 1478x832 | 0.24 | 0.27 | 0.12 | 0.16 |
| characters | Slender/Cameras/Face | medium | 1920x1080 | 1632x918 | 0.36 | 0.40 | 0.08 | 0.17 |
| characters | Slender/Cameras/Face | high | 1920x1080 | 1478x832 | 0.54 | 0.58 | 0.09 | 0.18 |
| characters | Slender/Cameras/Face | ultra | 1920x1080 | 1920x1080 | 0.52 | 0.56 | 0.09 | 0.18 |
| characters | Slender/Cameras/Face | low | 2560x1440 | 1971x1109 | 0.38 | 0.45 | 0.07 | 0.14 |
| characters | Slender/Cameras/Face | medium | 2560x1440 | 2176x1224 | 0.63 | 0.73 | 0.08 | 0.16 |
| characters | Slender/Cameras/Face | high | 2560x1440 | 1971x1109 | 0.96 | 1.05 | 0.10 | 0.19 |
| characters | Slender/Cameras/Face | ultra | 2560x1440 | 2560x1440 | 0.93 | 1.02 | 0.09 | 0.18 |
| characters | Heavy/Cameras/ThreeQuarter | low | 1920x1080 | 1478x832 | 0.23 | 0.26 | 0.12 | 0.19 |
| characters | Heavy/Cameras/ThreeQuarter | medium | 1920x1080 | 1632x918 | 0.36 | 0.39 | 0.08 | 0.15 |
| characters | Heavy/Cameras/ThreeQuarter | high | 1920x1080 | 1478x832 | 0.56 | 0.59 | 0.09 | 0.19 |
| characters | Heavy/Cameras/ThreeQuarter | ultra | 1920x1080 | 1920x1080 | 0.56 | 0.59 | 0.09 | 0.18 |
| characters | Heavy/Cameras/ThreeQuarter | low | 2560x1440 | 1971x1109 | 0.38 | 0.46 | 0.07 | 0.16 |
| characters | Heavy/Cameras/ThreeQuarter | medium | 2560x1440 | 2176x1224 | 0.63 | 0.73 | 0.08 | 0.17 |
| characters | Heavy/Cameras/ThreeQuarter | high | 2560x1440 | 1971x1109 | 0.98 | 1.06 | 0.10 | 0.19 |
| characters | Heavy/Cameras/ThreeQuarter | ultra | 2560x1440 | 2560x1440 | 0.94 | 1.04 | 0.09 | 0.18 |
| field_court | default | low | 1920x1080 | 1478x832 | 0.29 | 0.32 | 0.18 | 0.24 |
| field_court | default | medium | 1920x1080 | 1632x918 | 0.44 | 0.48 | 0.12 | 0.14 |
| field_court | default | high | 1920x1080 | 1478x832 | 0.65 | 0.69 | 0.13 | 0.15 |
| field_court | default | ultra | 1920x1080 | 1920x1080 | 0.80 | 0.84 | 0.13 | 0.23 |
| field_court | default | low | 2560x1440 | 1971x1109 | 0.46 | 0.52 | 0.12 | 0.17 |
| field_court | default | medium | 2560x1440 | 2176x1224 | 0.73 | 0.82 | 0.12 | 0.15 |
| field_court | default | high | 2560x1440 | 1971x1109 | 1.11 | 1.20 | 0.13 | 0.23 |
| field_court | default | ultra | 2560x1440 | 2560x1440 | 1.20 | 1.29 | 0.13 | 0.23 |
| battle_sandbox | default | low | 1920x1080 | 1478x832 | 0.30 | 0.33 | 0.23 | 0.33 |
| battle_sandbox | default | medium | 1920x1080 | 1632x918 | 0.42 | 0.46 | 0.17 | 0.34 |
| battle_sandbox | default | high | 1920x1080 | 1478x832 | 0.55 | 0.59 | 0.18 | 0.34 |
| battle_sandbox | default | ultra | 1920x1080 | 1920x1080 | 0.61 | 0.66 | 0.17 | 0.35 |
| battle_sandbox | default | low | 2560x1440 | 1971x1109 | 0.48 | 0.54 | 0.17 | 0.34 |
| battle_sandbox | default | medium | 2560x1440 | 2176x1224 | 0.66 | 0.75 | 0.17 | 0.35 |
| battle_sandbox | default | high | 2560x1440 | 1971x1109 | 0.88 | 0.97 | 0.18 | 0.37 |
| battle_sandbox | default | ultra | 2560x1440 | 2560x1440 | 0.86 | 0.95 | 0.17 | 0.34 |


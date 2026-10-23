# GPU performance report, 2026-10-23 (M1-QA-01 follow-up)

> **Status: complete.** Main sweep (every test scene × 4 presets × 2 resolutions), Undertow breakdown (Horizon and Eye), water breakdown, and the screenshot drift run against the lavapipe baselines (baselines untouched).

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

## Undertow cost by tier and feature

### Horizon camera

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

### Eye camera

| Config | Low preset 1080p | High preset 1080p | Low preset 1440p | High preset 1440p |
|---|---:|---:|---:|---:|
| no storm | 0.48 | 0.81 | 0.79 | 1.37 |
| low (shells) | 1.29 (+0.81) | 1.58 (+0.77) | 2.25 (+1.46) | 2.75 (+1.38) |
| medium | 5.86 (+5.38) | 6.15 (+5.34) | 10.01 (+9.22) | 10.58 (+9.21) |
| high | 16.31 (+15.83) | 16.54 (+15.73) | 28.14 (+27.35) | 28.53 (+27.16) |
| ultra | 28.57 (+28.09) | 28.92 (+28.11) | 49.62 (+48.83) | 49.48 (+48.11) |
| high - body | 0.64 (+0.16) | 0.92 (+0.11) | 1.04 (+0.25) | 1.52 (+0.16) |
| high - sea | 16.13 (+15.65) | 16.45 (+15.64) | 27.98 (+27.19) | 28.15 (+26.78) |
| high - spray | 16.26 (+15.78) | 16.55 (+15.74) | 28.07 (+27.28) | 28.42 (+27.06) |
| high - wounds | 16.18 (+15.70) | 16.57 (+15.76) | 28.06 (+27.27) | 28.34 (+26.97) |
| high, 22 steps | 8.78 (+8.30) | 9.15 (+8.33) | 15.28 (+14.50) | 15.68 (+14.31) |

- **The body is the whole cost.** Hiding it ("high - body") brings the frame back to within 0.25 ms of the no-storm figure (Eye: sea, lid and spray together are about 0.1–0.25 ms). Sea, spray curtains and wounds each move the frame by under 0.4 ms, which is noise at these frame times.
- **Cost is linear in march steps:** 22 steps costs 51–55% of 44 (Horizon 7.78 vs 15.16 ms at 1080p; Eye 9.15 vs 16.54). Each dense step costs about **0.33 ms at 1478×831 internal** on this card.
- **The storm cost doesn't depend on the preset.** The storm delta is the same under the Low and High presets at the same output size (both use 0.77 render scale), so shadows, SSR, GI and fog don't interact with it.
- **Ultra is about 1.8× High, and High about 2.9× Medium.** That's close to the lavapipe *ratios* in `undertow.md` (+60–70% and 2.7×). Lavapipe ranked the features correctly but underestimated the absolute cost: undertow.md projected the raymarched tiers at "5–15× over" a 2–3 ms slot, and High on an RTX 3060 at 1440p is about **20–35× over**.
- **The resolution scaling is almost ideal.** 1080p to 1440p is 1.78× the pixels and 1.70× the cost, so the half-/quarter-resolution body that undertow.md proposes for M2 should cut cost by roughly 4× / 16×.

## Top 3 costs to fix

1. **Undertow raymarched body, High/Ultra (blocker for §4.2).** 25.9–35.7 ms at High 1440p on a 9070 XT, about 60–100 ms on an RTX 3060. To fit **≤ 2–3 ms on an RTX 3060** it needs to be about **1 ms on this card**: a 25–35× cut. The M2 plan in undertow.md (render at quarter resolution with temporal reprojection, about 16×; baked 3D noise in place of hash fBm; early-out on opacity) is the right direction. Measure each step with `gpu_bench --variants=undertow`.
2. **The Undertow Medium tier can't serve as a fallback.** 8.5 ms (1080p) and 14.9 ms (1440p) at Night on this card, so about 36–43 ms on a GTX 1060 at 1080p and about 34–42 ms on an RTX 3060 at 1440p. Until (1) lands, ship the storm as **shells (Low tier) on every preset**, with raymarched tiers opt-in for capture or trailers. Shells cost 1.1 ms at 1440p here, about 2.5–3 ms on a 3060.
3. **The Undertow's Low-tier shells sit at the top of their slot.** The fallback in (2) costs +1.1 ms (Horizon) and +1.4 ms (Eye) at 1440p on this card, about **2.5–3.9 ms on an RTX 3060**, against the 2–3 ms a storm shot can afford (undertow.md). It's fine at 1080p on a GTX 1060 (+0.6–0.8 ms here, about 2.5–4 ms there, inside a 33 ms frame). At High 1440p, trim shell overdraw (fewer wall fractions or a tighter alpha cut) if a storm view also carries water and characters.

Water is **not** in the top 3. See the next section: it matches its estimate.

## Water cost by tier and feature (Lagoon camera)

Same layout as the Undertow tables, with the delta against "no water" in the same column (`WaterBench.CONFIGS`; "high - X" turns one optional term off on the High tier).

| Config | Low preset 1080p | High preset 1080p | Low preset 1440p | High preset 1440p |
|---|---:|---:|---:|---:|
| no water | 0.46 | 0.74 | 0.71 | 1.19 |
| low | 0.69 (+0.24) | 1.01 (+0.27) | 1.14 (+0.43) | 1.63 (+0.43) |
| medium | 0.82 (+0.36) | 1.13 (+0.39) | 1.34 (+0.64) | 1.83 (+0.64) |
| high | 0.93 (+0.47) | 1.24 (+0.50) | 1.51 (+0.80) | 2.01 (+0.82) |
| ultra | 1.15 (+0.69) | 1.45 (+0.71) | 1.86 (+1.15) | 2.37 (+1.18) |
| high - ssr | 0.83 (+0.37) | 1.15 (+0.41) | 1.36 (+0.66) | 1.85 (+0.66) |
| high - caustics | 0.84 (+0.38) | 1.16 (+0.42) | 1.38 (+0.68) | 1.88 (+0.68) |
| high - foam | 0.83 (+0.37) | 1.15 (+0.41) | 1.36 (+0.65) | 1.86 (+0.67) |
| high - refraction | 0.93 (+0.47) | 1.25 (+0.51) | 1.52 (+0.82) | 2.02 (+0.83) |
| high - detail normals | 0.86 (+0.40) | 1.18 (+0.44) | 1.42 (+0.71) | 1.91 (+0.72) |
| high - sss | 0.93 (+0.47) | 1.24 (+0.50) | 1.51 (+0.81) | 2.01 (+0.82) |
| high - all optional | 0.59 (+0.14) | 0.92 (+0.18) | 0.96 (+0.26) | 1.47 (+0.27) |

- **Water High at 1440p: +0.82 ms here, about 1.9–2.3 ms on an RTX 3060.** That's at the top of water.md's 1.0–2.0 ms estimate (made at the same 0.77 internal scale), so the estimate holds. Water Low at 1080p on a GTX 1060: +0.24 ms here, about 1.0–1.2 ms there (estimate 0.4–0.9).
- Per term at High 1440p: SSR, caustics and foam about 0.15 ms each; detail normals about 0.1 ms. Refraction and SSS cost nothing measurable (refraction's screen copy is part of the base). The base (all optional terms off) is +0.27 ms, about a third of the High cost. Lavapipe put it at half.
- The jump from High to Ultra in the whole-scene tables (Lagoon 1.99 → 3.28 ms) is mostly the **Ultra preset's native resolution** (1.0 vs 0.77 render scale) plus its heavier SSR, GI and fog. The water Ultra tier itself adds only +0.36 ms over High.

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

Captured on the RX 9070 XT with the official build: `GODOT=<godot> tools/gpu_bench/capture_gpu.sh <out_dir>` (one process per shot, like `capture.sh`, `--fixed-fps 60`), then `python tools/screenshots/compare.py --out <out_dir>`. **Baselines were not modified** (`git status tests/` clean before and after). **41 of 43 shots pass; 2 exceed their limit.** Neither looks wrong on the GPU.

| Shot | RMSE | Limit | Result |
|---|---:|---:|---|
| boot_title | 0.00009 | 0.004 | pass |
| lighting_probe | 0.00258 | 0.008 | pass |
| lighting_probe_low | 0.00306 | 0.008 | pass |
| glimmer_dusk | 0.00137 | 0.008 | pass |
| glimmer_night_held | 0.00020 | 0.008 | pass |
| glimmer_release | 0.00028 | 0.008 | pass |
| battle_hud_preview | 0.00138 | 0.008 | pass |
| battle_swap_menu | 0.00138 | 0.008 | pass |
| battle_victory | 0.00121 | 0.008 | pass |
| base_body_slender_front | 0.00071 | 0.008 | pass |
| base_body_slender_q34 | 0.00083 | 0.008 | pass |
| base_body_slender_side | 0.00111 | 0.008 | pass |
| base_body_slender_face | 0.00102 | 0.008 | pass |
| base_body_slender_posed | 0.00083 | 0.008 | pass |
| base_body_athletic_front | 0.00072 | 0.008 | pass |
| base_body_athletic_q34 | 0.00081 | 0.008 | pass |
| base_body_athletic_side | 0.00099 | 0.008 | pass |
| base_body_heavy_front | 0.00072 | 0.008 | pass |
| base_body_heavy_q34 | 0.00074 | 0.008 | pass |
| base_body_heavy_side | 0.00069 | 0.008 | pass |
| veg_backlit_fronds | 0.01356 | 0.018 | pass (75% of limit) |
| veg_frangipani_close | 0.01575 | 0.018 | pass (88% of limit) |
| **veg_beach_wide** | **0.01903** | 0.018 | **fail** |
| water_shallows | 0.00222 | 0.008 | pass |
| water_lagoon | 0.00214 | 0.008 | pass |
| water_horizon | 0.00230 | 0.008 | pass |
| water_night | 0.00031 | 0.008 | pass |
| field_lane_fixed | 0.00116 | 0.008 | pass |
| field_court_pan | 0.00344 | 0.008 | pass |
| field_causeway_dolly | 0.00496 | 0.008 | pass |
| battle_statuses | 0.00137 | 0.008 | pass |
| save_shrine_field | 0.00122 | 0.008 | pass |
| save_menu | 0.00097 | 0.008 | pass |
| save_menu_overwrite | 0.00058 | 0.008 | pass |
| swatch_card | 0.00112 | 0.004 | pass |
| undertow_horizon_dusk | 0.00071 | 0.008 | pass |
| undertow_eye | 0.00081 | 0.008 | pass |
| undertow_night | 0.00075 | 0.008 | pass |
| **undertow_horizon_low** | **0.01202** | 0.008 | **fail** |
| char_skin_eye_closeup | 0.00198 | 0.008 | pass |
| char_hair_backlit | 0.00165 | 0.008 | pass |
| char_cloth_gold | 0.00185 | 0.008 | pass |
| char_low_compare | 0.00242 | 0.008 | pass |

Findings (I inspected the GPU PNG, the baseline and the diff for each failure):

- **`undertow_horizon_low` (0.012):** the error is confined to the **alpha-cut edges of the Low-tier shells**, where the hash noise crosses `alpha cut`. A last-bit difference in the GPU's float hash flips pixels on either side of the cutoff. The image is visually identical, and the GPU edges are if anything slightly cleaner. Not a GPU bug. Alpha-tested noise edges simply aren't stable across rasterizers.
- **`veg_beach_wide` (0.019) and the other vegetation shots (75–88% of a limit already loosened to 0.018):** the error is on **foliage alpha edges and the dappled palm shadow edges** (shadow filtering). It's visually identical. The vegetation limit is already the loosest in the manifest because of this.
- Everything else, including the raymarched storm shots, SDFGI/fog lighting probes, water and skin, is **under 0.005**. Lavapipe is a good proxy for the GPU look here.
- **Recommendation:** keep the lavapipe baselines as the CI reference (the job is already `continue-on-error`). If a GPU runner becomes a gate, approve a **separate GPU baseline set** rather than raising the shared limits. Never re-approve lavapipe baselines from GPU captures.
- Most interesting PNGs (on the measuring PC, not committed): `C:\Users\Aaron\hymn_shots_gpu\undertow_horizon_low.png`, `C:\Users\Aaron\hymn_shots_gpu\diff\undertow_horizon_low.png`, `C:\Users\Aaron\hymn_shots_gpu\veg_beach_wide.png`, `C:\Users\Aaron\hymn_shots_gpu\diff\veg_beach_wide.png`, `C:\Users\Aaron\hymn_shots_gpu\undertow_night.png` (the 106 ms-at-Ultra view, matching lavapipe at 0.00075).

## Harness gotchas

- **The monitor must stay on.** On Windows, Godot's window needs a live display for the Vulkan swapchain. When the monitor was switched off mid-run, every process logged `swap_chain_resize ... ERR_CANT_CREATE` (`rendering_device_driver_vulkan.cpp:3369`) and reported **0.00 ms GPU at about 16 ms frames**. Four rows were lost this way, dropped from the CSV, and re-measured once the monitor was back on. `summarize.py` discards `gpu_median_ms == 0` rows. For unattended runs, keep the monitor on (and the idle display timeout off), or fit an HDMI/DP dummy plug.
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


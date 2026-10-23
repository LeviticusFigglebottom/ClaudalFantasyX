# M1-RND-10: Undertow High-tier performance (2026-10-23)

**Result: target met.** The Undertow test scene at **High, 2560×1440** now takes **3.95 / 5.35 / 5.04 ms** of GPU time per frame (Horizon / Eye / Night; p99 4.04 / 5.46 / 5.14) on the RX 9070 XT, against a target of **≤ 6.0 ms**. It was 25.80 / 28.35 / 35.72 ms, so it's **5.3–7.1× faster**. Medium is 3.6–4.0× cheaper, Ultra 5.9–6.3× cheaper, and Low is unchanged (±0.01 ms). The look keeps its character and the wound seams stay where they were, but the billow layout changed. The three raymarched lavapipe shots need re-approval (see "Screenshot drift").

Hardware, driver, engine and the projection factors are as in [`2026-10-23-gpu-report.md`](2026-10-23-gpu-report.md): AMD RX 9070 XT, Adrenalin 26.6.1, Vulkan 1.4.349, official Godot 4.6.3-stable, Windows 10. 6.0 ms here projects to about 13.8–16.8 ms on an RTX 3060 at the report's 2.3–2.8× factor. Note that this is now a texture-fetch-heavy shader rather than an integer-ALU one, so scaling to older cards should be *better* than for the old hash version, not worse. That's still to be confirmed on a real 3060.

## Method

- `tools/gpu_bench/run_undertow.sh <csv> <label>` runs `gpu_bench.tscn` on `undertow_test.tscn` for the Horizon, Eye and Night cameras × Low/Medium/High/Ultra × 1080p/1440p. GraphicsSettings applies the preset, and `UndertowStorm.set_quality(preset)` sets the tier. 120 frames and at least 3 s of warm-up, then 300 sampled frames (lever sweeps: 2 s and 200 frames). The storm runs animated, with GPU time from `viewport_get_measured_render_time_gpu`.
- Look checks, both deterministic:
  1. The screenshot rig (`tools/gpu_bench/capture_gpu.sh`: capture.tscn, FXAA, held clock, 960×540) for the 4 storm shots, diffed with `tools/gpu_bench/diff_shots.py` (the same linear-light RMSE as `compare.py`).
  2. The real in-game path: `gpu_bench --hold-storm --warmup-s=0 --png-dir=…` at High 1440p (FSR2 temporal AA). The storm clock is frozen, but its jitter frame advances, so TAA integrates it. Run-to-run repeatability of this mode is RMSE ≤ 0.00003.
- "Before" renders come from a git worktree of the pre-change commit, using the same harness.
- Raw rows: [`2026-10-23-rnd-10-bench.csv`](2026-10-23-rnd-10-bench.csv). Labels: `before`, `after` (full sweeps), `d_baked`, `d2`, `c1`, `c2_N`, `t_<steps>_<reuse>` (lever runs at High 1440p).

## Where the time went (before)

Each dense march step at High evaluated about 22 hashed value-noise lookups: two curl warps (3 analytic-gradient lookups each), two 4-octave fBm plus 2 detail lookups, 3 wound lookups, and 2 light samples × 2. That's about 180 PCG3D hashes, each with six 32-bit integer multiplies, for 44 steps a pixel. A profile with features removed, taken after lever (d), at High 1440p (Horizon / Eye / Night): wounds 0.4 / 1.15 / 0.5 ms, sun light samples 0.25 / 0.7 / 0.3 ms, curl warp 1.1 / 1.0 / 1.8 ms. The rest is fBm, the envelope and step overhead.

## Per lever (cumulative, High preset, 2560×1440, GPU median ms)

| # | Lever | Horizon | Eye | Night | Look vs. previous row (capture rig RMSE, Eye / Dusk / Night) |
|---|---|---:|---:|---:|---|
| 0 | Before (hash noise, 44 steps) | 25.80 | 28.35 | 35.72 | – |
| 1 | **(d) Baked 3D noise** for the cloud fields (fBm, detail, curl, light samples); wounds keep hashing | 5.66 | 7.22 | 7.45 | 0.066 / 0.031 / 0.048 (new billow layout, same character; seams in place) |
| 1′ | *(rejected)* (d) with the wounds baked too | 5.40 | 6.45 | 7.11 | 0.085 / 0.069 / **0.172** (the rents moved and spread into broad glow patches at Night) |
| 2 | **(c) Wound noise only where the cloud has density** (a rent only thins cloud, and empty steps are skipped anyway) | 5.43 | 6.63 | 7.13 | **0.00000** (bit-identical) |
| 3 | **(c) `curl_reuse` = 2**: one curl warp per 2 dense steps, refreshed after any empty stride | 5.01 | 6.52 | 6.37 | 0.008 / 0.006 / 0.013 |
| 4 | **(b) `temporal_jitter`**: per-frame R1 rotation of the step offset (TAA/FSR2 integrates it) | 4.99 | 6.52 | 6.36 | none in the held capture; integrates in game |
| 5 | **(b) `march_steps` 44 → 32** (affordable because of 4) | **3.92** | **5.29** | **5.01** | 0.014 / 0.014 / 0.027 (FXAA capture; the in-game TAA path is below) |
| | Final sweep (300 frames) | 3.95 | 5.35 | 5.04 | |

Options measured for row 5 (all with `curl_reuse` 2 and temporal jitter): 44 steps 4.99 / 6.52 / 6.36; 36 steps 4.27 / 5.69 / 5.48; **32 steps 3.92 / 5.29 / 5.01 (chosen: about 12% margin on Eye)**; 28 steps 3.57 / 4.88 / 4.59; 36 steps with `curl_reuse` 3 4.08 / 5.47 / 5.22. `curl_reuse` 3 at 44 steps gave 4.76 / 6.22 / 6.04 with twice the drift of 2.

**(a) Half/quarter-resolution body: not implemented.** It isn't needed to hit the target, and in Godot 4.6 it means either a SubViewport pass, where the body loses the main view's opaque depth (occlusion by islands, ships and characters would need a separate depth-aware composite), or a CompositorEffect, which means porting the shader and its includes to a raw GLSL compute shader. Resolution scaling measured as nearly ideal (1080p → 1440p: 1.78× pixels, 1.70× cost), so it remains the lever for more headroom, for example a 1060-class card at Medium, or close approaches where the storm fills the screen.

## Every tier, before → after (GPU median ms; p99 within 3% of the median everywhere)

| Preset (tier) | Res | Horizon | Eye | Night |
|---|---|---|---|---|
| Low (shells) | 1080p | 1.01 → 1.01 | 1.32 → 1.32 | 1.17 → 1.17 |
| Medium | 1080p | 6.07 → 1.70 | 7.20 → 2.34 | 8.54 → 2.14 |
| High | 1080p | 15.07 → 2.27 | 16.75 → 3.12 | 20.50 → 2.89 |
| Ultra | 1080p | 43.48 → 7.42 | 46.47 → 9.32 | 60.21 → 9.63 |
| Low (shells) | 1440p | 1.69 → 1.70 | 2.25 → 2.25 | 1.99 → 1.99 |
| Medium | 1440p | 10.42 → 2.90 | 12.34 → 4.00 | 14.86 → 3.74 |
| **High** | **1440p** | **25.80 → 3.95** | **28.35 → 5.35** | **35.72 → 5.04** |
| Ultra | 1440p | 76.09 → 12.92 | 80.71 → 16.22 | 106.36 → 16.82 |

The frame without the storm is 0.6–1.4 ms of each figure. CPU (render-thread) time is unchanged at about 0.1–0.2 ms.

## Tier parameters (data, validated)

`game/data/vfx/undertow.json`:
- `quality.<tier>.curl_reuse` (int, 1–8, default 1);
- `quality.<tier>.temporal_jitter` (bool, default false);
- `quality.high.march_steps` 44 → 32;
- a new `noise` section (`texture`, `texels`).

Final values: Medium `temporal_jitter`; High 32 steps, `curl_reuse` 2, `temporal_jitter`; Ultra `curl_reuse` 2, `temporal_jitter`, with its 72 steps kept. Low is unchanged. Tests:
- `test_tier_perf_params_parse_and_validate`: `curl_reuse` within the shader's range; `march_steps` ≤ each variant's compiled `UNDERTOW_MAX_STEPS`; temporal jitter only on tiers whose preset's AA is temporal (TAA or FSR2).
- `test_jitter_phase_advances_only_with_the_clock`.
- `test_noise_lattice_matches_its_data`: the 64³ RGBA8 texture, no mipmaps.
- The storm binds the texture and pushes `curl_reuse`.
- `tools/tests/test_undertow_noise.py`: the bake equals a scalar PCG3D reference written from the shader, the atlas order, and the committed PNG is current, < 5 MB, and imported lossless with no mipmaps.

Suite: 669 GDScript tests, 0 failed; Python discovery OK; `validate_data` 0 errors; gdlint and gdformat clean.

## Look: before vs. after

**In game (High preset, FSR2, 2560×1440, held clock, 180 frames)**, before → after:

| View | RMSE | max abs (8-bit) | pixels > 8 levels |
|---|---:|---:|---:|
| Eye | 0.06713 | 186 | 53.1% |
| Horizon | 0.03271 | 232 | 24.6% |
| Night | 0.04968 | 241 | 21.6% |

Almost all of this is lever (d): the same views with baked noise alone differ from "before" by 0.066 / 0.031 / 0.048 in the capture rig, and the step and jitter levers add 0.014–0.027 on top in the static FXAA capture, less under TAA.

What changed, by eye:
- **Same:** the wound seams and pockets (same places and shapes), the lightning, the funnel, the throat, the banding, the overall mass, colour and silhouette.
- **Different:** the billow layout. The large-scale cloud noise now comes from a 64-cell periodic lattice, so the same storm has differently placed lumps of the same size and softness.
- **Better:** the static IGN dither is less visible in the glow areas, because the jitter now integrates over frames.

No banding or tiling is visible at these scales. The lattice period is 147 km for the base octave and 18 km for the finest, and the warp and flow hide it.

## Screenshot drift (for Lead re-approval on lavapipe)

GPU capture-rig shots, before → after, plus the effect on the committed lavapipe baselines (**not modified**; `git status tests/` is clean):

| Shot | GPU before → after RMSE | vs. lavapipe baseline (limit 0.008) | Needs re-approval |
|---|---:|---|---|
| `undertow_horizon_dusk` | 0.03237 | 0.00071 → **0.03239** | **yes** |
| `undertow_eye` | 0.06647 | 0.00081 → **0.06650** | **yes** |
| `undertow_night` | 0.05036 | 0.00075 → **0.05039** | **yes** |
| `undertow_horizon_low` | **0.00000** | 0.01202 → 0.01202 (the existing GPU-vs-lavapipe alpha-edge drift from the GPU report, unchanged) | no |

No other shot in `tests/screenshots/shots.json` draws the raymarched body.

## Ghosting check in motion (follow-up, same day)

**Result: no ghosting or smearing from `temporal_jitter` or `curl_reuse`, so no fix is needed.**

**Setup.** `tools/gpu_bench/ghost_check.tscn` runs a deterministic sequence on `undertow_test.tscn`:
- Horizon camera, High preset (FSR2 temporal), 2560×1440.
- The camera **pans at 30°/s** (about 14 px per frame).
- An opaque ship-sized box (110×70×20 m at 450 m) crosses in front of the storm body.
- The storm runs at its **fastest API settings**: `rotation_rad_s` 0.12 and `time_scale` 8, so the eyewall turns about 55°/s.
- A lightning flash is forced at frame 20.
- Every quantity steps by a fixed amount per frame, and the water clock is frozen.

**Runs.** 90 history frames at the start pose, then 48 moving frames; frames 8, 16, 24, 32, 40 and 47 are saved.
- **final:** RND-10 High as shipped (32 steps, `curl_reuse` 2, jitter).
- **static:** the temporal levers off (44 steps, `curl_reuse` 1, no jitter).
- **At rest:** each config's frames held still for 64 frames at the same pose, so TAA settles.
- **Reference:** 48 steps, `curl_reuse` 1, jitter on, held for 128 frames: the common ground truth.

Stats come from `python tools/gpu_bench/ghost_stats.py <dir>`. Each value is linear-light RMSE against the reference, as full frame / storm (above the horizon) / a band around the silhouette that extends 200 px past its trailing, disoccluded edge. Means over the 6 frames:

| | In motion | At rest (same poses) | Motion adds |
|---|---|---|---|
| **final** | 0.0161 / 0.0142 / 0.0383 | 0.0157 / 0.0141 / 0.0396 | +0.0004 / +0.0001 / −0.0013 |
| static | 0.0114 / 0.0101 / 0.0287 | 0.0121 / 0.0107 / 0.0341 | −0.0007 / −0.0006 / −0.0054 |

Per frame, final in motion: 0.0148–0.0178 full and 0.0343–0.0407 in the band, with no trend toward the end of the pan and no spike after the flash.

- **Motion doesn't add error for either config**, and in particular none around the silhouette. A ghost would show up as moving error above at-rest error in the band. Crops of the band (moving vs. at rest, both configs, frame 40) show clean box edges with no trail. The only visible difference is that the per-frame jitter grain integrates slightly less in motion.
- The final config's constant offset from the reference (about 0.016 vs about 0.012 full frame) exists equally at rest. It's the bias of 32 steps plus curl reuse against 48 steps, the same drift reported above. It isn't a temporal artefact.
- **The azimuthal streaks at the fastest animation are the cloud's real shape**, not TAA smear. The converged reference, which has no motion history, shows the same streaks. At `time_scale` 8, the differential rotation winds the noise within one flow cycle. That's a look question for cutscenes that push the clock, not a rendering bug.
- Engine note: the storm is transparent and writes no motion vectors, so TAA reprojects it by camera motion only. That holds up at storm distance (above), but anything close to the camera that drives fast storm motion relative to the view could still smear. It's untested here because the API has nothing faster.

## Files

- `game/shaders/undertow/undertow_body.gdshaderinc`: baked lattice lookup, fBm and curl; wound-after-density; `curl_reuse`; `jitter_phase`. `undertow_common.gdshaderinc` is untouched, so the Low tier, sea and spray are byte-for-byte as before.
- `game/vfx/undertow/undertow_state.gd`: tier keys, `frame`, `jitter_phase()`, `noise_texture_path()`, the `noise_texels` uniform. `game/vfx/undertow/undertow_storm.gd`: binds `noise_tex`.
- `game/data/vfx/undertow.json`: tier parameters and the `noise` section.
- `assets_src/vfx/undertow/bake_noise3d.py` → `assets/vfx/undertow/undertow_noise3d.png` (+ `.import`, a PROVENANCE row, and an ownership row).
- Tests: `tests/unit/test_undertow_storm.gd`, `tests/unit/test_undertow_shaders.gd`, `tools/tests/test_undertow_noise.py`.
- Tools: `tools/gpu_bench/gpu_bench.gd` (`--png-dir`, `--hold-storm`), `run_undertow.sh`, `diff_shots.py`, `ghost_check.gd/.tscn`, `ghost_stats.py`.
- Docs: `docs/kb/tech/undertow.md` (tiers, measured cost, gotchas).

## Follow-ups

1. Lead: re-approve `undertow_horizon_dusk`, `undertow_eye` and `undertow_night` on lavapipe.
2. Confirm the projection on a real RTX 3060 / GTX 1060. The shader is now fetch-bound, which older cards handle relatively better than integer multiplies.
3. If more headroom is wanted, add the half-resolution body (lever a), with a depth-aware composite.
4. ~~Watch the storm in motion for TAA ghosting~~: done. No ghosting (see "Ghosting check in motion").

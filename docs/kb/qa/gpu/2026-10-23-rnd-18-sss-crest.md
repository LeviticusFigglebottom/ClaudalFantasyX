# M1-RND-18: SSS crest patches from high cameras, measured on the GPU (2026-10-23)

Machine: RX 9070 XT, Godot 4.6.3. Branch `gpu/rnd-18-sss-crest`.

**Probe.** `game/levels/_tests/swatches/water_look_probe.tscn -- --look=lagoon_clear --camera=survey` (ch02_noon, sun
74° at 3.2, exposure 0.65).
- The control run used `col_sss` #000000, made by a temporary edit to `water_looks.json` that was reverted at once
  (as Art did; the probe's swatches folder is Art-owned).
- The probe needs its `--out` folder to exist. Without it, it errors and hangs.
- Metrics: `tools/gpu_bench/sss_probe_metrics.py <on.png> <off.png>`. Deep water is y < 290, foam (OkL > 0.85)
  excluded.

## Change (`game/shaders/water/water_surface_body.gdshaderinc`, every ocean and river tier)

```
view_steep = |view.y| (world)
view_high  = smoothstep(sss_view_height_lo_m 10, sss_view_height_hi_m 25, view_dist * view_steep)
view_keep  = 1 - smoothstep(sss_view_fade_lo 0.10, sss_view_fade_hi 0.28, view_steep) * view_high
crest SSS  *= view_keep
col_deep   *= 1 + scatter_view_lift 1.5 * (1 - view_keep)      (the deep end of the in-scatter only)
```

- `view_dist × view_steep` is the camera's height above the water it is looking at. Gating on it leaves low cameras
  untouched: a 5.5 m camera sees its near water steeply too.
- The lift goes on `col_deep` only. Lifting all of the in-scatter put the 4–15 m band at ΔE 0.105 against
  `reef_blue`.

## Survey results (deep water)

| | Before (SSS on) | SSS off | After | Goal |
|---|---:|---:|---:|---|
| Deep pixels where SSS adds ΔE_ok > 0.05 | 22.5 % | 0 | **0.0004 %** | ≤ 5 % |
| … > 0.03 | 27.5 % | 0 | **0.06 %** | ≤ 10 % |
| Max added | 0.174 | 0 | **0.050** | ≤ 0.08 |
| OkL p90 − p10 | 0.166 | – | **0.075** | ≤ 0.14 |
| > 15 m band median | `#15586E` (0.046) | `#134D69` (0.081) | **`#15627A` (0.019)** | ≤ 0.07 to `#106776` |
| 4–15 m band median | `#17808C` (0.066) | `#16808B` | `#17808C` (0.066) | ≤ 0.07 to `reef_blue` |

The "before" and "SSS off" columns are this GPU's runs. They match Art's lavapipe numbers (27.5 / 22.5 / 0.174 /
0.166 / `#15586E`, and `#134E69` off).

On the way there:
- The first thresholds (0.26 / 0.53) left 14.7 % and 11.1 %: the upper deep rows only look 20–30° down.
- 0.14 / 0.36 got to 4.4 % and 2.1 %.

## Other shots (GPU capture rig, before → after RMSE)

| Shot | RMSE |
|---|---:|
| water_shallows, water_lagoon, water_horizon, water_night | **0.00000** |
| haluna_h01_village_from_sea, haluna_h04_dock | **0.00000** |
| undertow_horizon_dusk / eye / night / horizon_low | ≤ 0.0004 (measured before the height gate, which can only lower it) |

The lagoon mid-ground pale-turquoise share is unchanged, since the image is identical. **No lavapipe baseline drifts**,
except in high-camera views, and no shot in the manifest has one.

## Checks

- **Run:** the Godot tests filtered to `water` (uniform coverage on every tier, plus a compile check); the tools
  unittest; validate_data; taskboard.
- **Skipped:** the full Godot suite (outside the diff) and the other shots (they can't change).

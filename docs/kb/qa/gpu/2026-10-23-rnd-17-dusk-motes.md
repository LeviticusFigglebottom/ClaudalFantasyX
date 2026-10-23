# M1-RND-17: dusk released motes, gold and rising, measured on the GPU (2026-10-23)

Machine: RX 9070 XT, Godot 4.6.3. Branch `gpu/rnd-17-dusk-motes`. Captures come from `tests/screenshots/capture.tscn`
at 960×540 with scene defaults. Metrics use `tools/screenshots/mote_metrics.py`, the M1-ART-05 method. On the
committed lavapipe baseline it reproduces the sign-off: hues 87° / 175° / 136°, |Δab| 0.039 / 0.023 / 0.021,
coverage 17.0 %, median streak 37°, 33 % of streaks within 30°.

## Changes

1. **Streak axis.** `glimmer_motes_process.gdshader` now writes a second smoothed velocity into `CUSTOM.xyz`: the same
   target minus the released spiral's tangential term. The share that survives attractors, the bound state and
   underwater drag is tracked too. The draw pass orients the streak along that.
   - `VELOCITY`, and so the spiral itself (radius, rate 1.0, rise), is unchanged.
   - The streak sits on the rise and curl drift only.
2. **Gold halo for released motes** (`glimmer_motes_draw_body.gdshaderinc`; look data in glimmer.json):
   - `halo_chroma_min` 0.22 puts a floor under the halo's Oklab chroma, C ≥ 0.22 × L.
   - It sits at hue `halo_hue_deg` 83° (`glimmer_lift`), whatever the core has whitened to (the lift_hi white
     switched the old warm test off).
   - Within `halo_hue_band_deg` 8° of the horizon in view elevation, the hue moves to `halo_hue_horizon_deg` 55°.
   - The floor is weighted by the mote's released share, which the process pass now writes to `CUSTOM.w`.
   - The streak takes the halo colour. The core stays pale.
3. **Checks.**
   - palette_check gained the kinds `mote_halo` and `mote_streaks`, and an `advisory` flag (warn instead of fail).
   - Both `glimmer_dusk` targets are in palette_checks.json as advisory, until the shot is re-approved.
   - Tests: `tools/tests/test_mote_metrics.py`, with synthetic comets, gold-over-grey, the baseline sign-off values,
     and advisory behaviour.

## Results (`glimmer_dusk`, GPU)

| Target | Before | After | Goal |
|---|---:|---:|---|
| Upper sky Δab hue | 87° | **76°** | 75–95 ✔ |
| Upper sky \|Δab\| | 0.039 | **0.060** | ≥ 0.06 ✔ |
| Horizon Δab hue | 175° | 139° | 75–95 ✘ |
| Horizon \|Δab\| | 0.023 | 0.024 | ≥ 0.04 ✘ |
| Horizon chroma under the halo / background | 0.029 / 0.042 | **0.044 / 0.043** | ≥ ✔ |
| Mirror Δab hue | 136° | 102° | 75–95 ✘ |
| Mirror \|Δab\| | 0.021 | 0.031 | ≥ 0.04 ✘ |
| Mirror chroma under the halo / background | 0.029 / 0.036 | **0.045 / 0.036** | ≥ ✔ |
| Core median chroma | 0.018 | 0.031 | ≤ 0.03 allowed |
| Coverage (rel > 0.10) | 17.1 % | 16.3 % | ≤ 18 % ✔ |
| Streak median angle | 37.5° | **5.7°** | ≤ 25 ✔ |
| Streaks within 30° | 31 % | **84 %** | ≥ 70 ✔ |
| Streaks beyond 60° | 12 % | **3 %** | ≤ 5 ✔ |
| Heads-down | 8.5 % (this script) | 6.0 % | ≤ 2 (the sign-off counted 3/96 on the baseline; this count runs higher) |

What was tried for the horizon:
- Floors of 0.08, 0.15, 0.22, 0.25 and 0.28.
- Halo hues of 83°, 75°, 65° and 58°.
- Moving energy from core to halo. That fixed the hue but put coverage at 22–23 %.

**Why the horizon misses.** The horizon background is a red-peach: Oklab a 0.037, b 0.024, hue 33°. Light added to
it moves Δab toward the added light's hue only if the light's a/L at least matches the sky's (0.056). At 83° that
takes C/L ≥ 0.46, which is out of gamut.

Lower halo hues help the horizon and the mirror but pull the upper sky below 75°. The elevation band separates the
two, but in the horizon band the inner-halo pixels (rel 0.6–2) are mostly the **pale cores' falloff**, and the task
says not to tint the cores. Hitting 75–95° there needs one of:
- (a) a core warmed toward sun-gold near the horizon only;
- (b) the target measured on the halo light alone (rel 0.6–2 minus the core's share);
- (c) a slightly larger halo near the horizon, within the 18 % coverage.

The Art Director should choose.

## Nothing else moves (GPU capture, before → after RMSE)

| Shot | RMSE |
|---|---:|
| glimmer_night_held | 0.00004 |
| glimmer_bound | 0.00011 |
| save_shrine_field | 0.00001 |
| glimmer_dusk | 0.01470 (intended) |
| glimmer_release | 0.01396 (its gold half, intended) |

The water shots can't change: no water shader or water data was touched. The held halo hue (~217°) and the bound
core (193–205°) aren't affected, because the floor is gated by the released share.

**Lavapipe baselines that will drift:** `glimmer_dusk` and `glimmer_release`. Look at both before re-approving them.

## Checks

- **Run:** gdlint and gdformat (game/vfx/glimmer); the Godot tests filtered to `glimmer` (35/0); tools unittest for
  `test_mote_metrics` and `test_palette_check` (16 OK); `palette_check` on the baselines (21 ok, the two new
  advisory checks warn); validate_data; taskboard.
- **Skipped:** the full Godot suite (outside the diff) and the other shots (they can't change; listed above).

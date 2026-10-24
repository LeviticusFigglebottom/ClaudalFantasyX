# M2-RND-05: the Undertow's storm events, chapter presets and the Art package (2026-10-24)

Machine: RX 9070 XT, Godot 4.6.3. Branch `gpu/m2-rnd-05-undertow-events`, cut from the integration branch at 54425e2.
Design: docs/kb/tech/undertow.md, "Storm events". Key frames: `docs/kb/qa/gpu/rnd05/`. Art's sign-off: M2-ART-03.

## What each criterion got

| Criterion | Done | Where |
|---|---|---|
| Wounds as real torn rents | Dark torn lip, halo of poured-out light, a little thicker at the edge; every tier | `undertow_wound()`, `wounds.lip_*` / `halo_*` |
| Storm-scale mote streamers | Curtains of held light hanging from the rents down the wall's outer face to the sea, motes sliding down them | `UndertowMeshBuilder.streamers()`, `undertow_streamer.gdshader` |
| The storm in the sky and in reflections | The sea reflects the storm's own pixels (Medium, High), or an impostor (off screen, Low, Ultra); the sky reflection gives way to it | water shader storm group, `UndertowEvents.reflection_parameters()` |
| Shadowing the zone | Key light and ambient dim under the canopy or with the storm toward the sun; the storm stays lit by the undimmed key | `UndertowEvents.zone_shadow_at()` |
| Rain | Camera curtains, by distance to the eye, dry above the cloud base, layers by tier and strength | `UndertowRain`, `undertow_rain.gdshader` |
| Lightning bolts plus an exposure flash | Cloud-to-sea bolts with forks on the camera's half; 2.0× exposure for 2 frames, photosensitivity-capped; `lightning_struck` signal | `UndertowEvents`, `undertow_bolt.gdshader` |
| Per-chapter presets, the Ch21 turn to rising gold | Six presets; `unbinding` reverses the drift, then lerps to `glimmer_lift` | undertow.json `presets`, `UndertowState.unbinding` |
| Art confirms `spawn_wound` usage | Filed as **M2-ART-03**, with key frames and six questions | `docs/kb/tasks/M2/M2-ART-03-undertow-events-signoff.md` |
| Storm's own cost ≤ ~1 ms at High 1440p | **0.59–0.84 ms** on every camera | below |

## Cost (2560×1440, GPU median over 300 frames, `gpu_bench --hide-storms` by difference)

| Camera | Preset | Before: frame / hidden / storm | After: frame / hidden / storm |
|---|---|---|---|
| Day (Ch8, 14 km) | High | 1.87 / 1.21 / 0.66 ms | 2.05 / 1.22 / **0.83 ms** |
| Eye | High | 2.22 / 1.46 / 0.76 ms | 2.26 / 1.46 / **0.80 ms** |
| Night | High | 1.85 / 1.17 / 0.68 ms | 1.96 / 1.17 / **0.79 ms** |
| Horizon | High | 1.66 / 1.11 / 0.55 ms | 1.70 / 1.11 / **0.59 ms** |
| Day, `ch08_landfall` (full rain) | High | – | 2.06 / 1.22 / **0.84 ms** |
| Day | Low | 2.16 / 0.80 / 1.36 ms | 2.23 / 0.80 / 1.43 ms |
| Day | Medium | 1.96 / 1.04 / 0.92 ms | 2.14 / 1.04 / 1.10 ms |
| Day | Ultra | 17.22 / 1.27 / 15.95 ms | 17.44 / 1.27 / 16.17 ms |

- **Rain is most of the increase.** Each layer is a full-screen blend, about 0.06 ms at 1440p. Light rain draws
  only the inner layers (Day: 2 at amount 0.2; Night: 1).
- **The other parts are small:** the curtains, bolts and reflection add 0.03–0.06 ms together.
- **The rents:** no measurable cost.
- **RTX 3060 projection (×3):** about 2.5 ms on High. The target was ~3 ms.
- **The first measurement was wrong:** the hidden frame was 0.2 ms slower than the base, because the rain kept
  drawing with the storm hidden. `UndertowEvents` is a plain Node and breaks the visibility chain. It now gates on
  the storm's visibility, and the hidden frames match the base to 0.01 ms.

## Screenshots

**Drift** (GPU, linear RMSE against this branch's base):

| Shot | Capture rig | High preset |
|---|---:|---:|
| `undertow_horizon_dusk` | 0.0115 | 0.0091 |
| `undertow_eye` | 0.0068 | 0.0048 |
| `undertow_night` | 0.0219 | 0.0180 |
| `undertow_horizon_low` | 0.0204 | – |
| `undertow_day_ch08` (pending since RND-09) | – | 0.0089 |
| `haluna_h01_village_from_sea` (water shader; no storm) | 0.0 | – |

- **The four `undertow_*` baselines drift by design.** The rents, the curtains, the sea's reflection and the
  rain all change them, so the Lead re-approves them on lavapipe.
- **Scenes without a storm are unchanged.** The water shader's new branch is off at `storm_reflect` 0.
- **Three new pending shots** in `docs/kb/qa/gpu/2026-10-24-rnd-05-pending-shots.json`: `undertow_strike_ch08`,
  `undertow_landfall_ch08` and `undertow_letting_ch21`.
  - Each repeats exactly on the GPU (RMSE 0.0).
  - Each holds the clocks and FXAA like the other storm shots, and turns the exposure flash off.
  - `undertow_strike_ch08` uses the test rig's new `strike` mood: the day mood, with its flash on the site facing
    the camera.

## How it was tuned (GPU)

- **Reflection.** The first impostor painted a hard white band on the sea. Its colours (albedo × key) were several
  times the storm's measured on-screen colour (dusk lower wall about 0.04 linear).
  - The fix reflects the half-res body's own pixel where the reflected ray meets the storm. That's exact, and it
    includes the wounds and lightning, which glint in the chop.
  - The impostor is kept as a fallback, with gains matched to the measured colour.
- **Rents.** The first halo (6 widths, 0.35) turned the seams into bigger smears. Now the halo is 3.5 widths at
  0.12, and the lip is 3 widths at 0.8, darkening the held glow as well as the lit cloud.
- **Streamers.**
  - As 5 km radial ribbons they read as arcs across the sky. Now they're curtains down the outer face, faded when
    seen edge-on.
  - They were invisible at first: an unshaded shader writing EMISSION draws nothing (see the undertow.md gotchas).
  - A stale normal hid the facing curtains.
- **Bolts.**
  - The day mood's forced site was on the near half but off-frame. `site_facing()` picks the site in view.
  - A strike fired before the capture made its camera current, so it went unbuilt. A stroke is now built on any
    frame of its strike.
  - Raised top and shorter sea reach make the strokes near-vertical.
- **Landfall.** At 6 km the camera stood inside the eyewall, which is 9.2 km at the sea. The preset is now
  10 km: under the canopy's edge.

## Findings

1. **Low's storm costs more than High's.** Low draws the full-resolution shells: 1.36 ms on the Day camera at
   1440p before this task. High draws the 0.35-scale compute body: 0.66 ms. That's an RX 9070 XT measurement, and
   on a GTX 1060 (Low's target) the ratio may differ. Worth a Low pass, maybe half-res shells or fewer of them.
   Not filed as a task yet; the Lead decides.
2. **The sky dome never sees the storm.** There's no overcast toward it; the zones' `env_sky_cumulus` doesn't know
   the storm. The storm draws in the sky itself and in the sea's reflection, so this is a nice-to-have.
3. **Ultra has no half-res texture to reflect** (its body is full resolution), so it reflects the impostor.

## Checks

- **Run:**
  - gdlint and gdformat on every touched script.
  - The Godot `undertow` filter: 51 run, 0 failed, 11 of them new in `test_undertow_events.gd`.
  - `tools/rendering/gen_undertow_compute.py`, whose outputs are committed and checked by its test.
  - validate_data, `taskboard --check` and the tools unittests.
  - The 4 undertow shots, `undertow_day_ch08` and `haluna_h01` on the GPU, with the capture rig and High.
- See the task notes for the full-suite run.

---
id: M1-RND-18
title: SSS crest patches from high noon cameras (fade the crest term with view elevation)
role: rendering
status: todo
owner_session: ""
depends_on: [M1-RND-08]
milestone: M1
request-from: "character"
---
## Goal
M1-RND-08's view-dependent wrap (`toward_light`) fixed the noon crests as the *low* cameras see them. Art approves `water_lagoon`, `water_horizon`, `haluna_h01` and `haluna_h04` (M1-ART-05). The finding M1-ART-04 actually made, though, was from the probe's **40 m survey camera**, and from there the patches are still there.

`toward_light` = ½ − ½·(V·L) is only 0 when the sun is straight behind the viewer. With a 74° sun and a camera looking 39° down, it stays at roughly 0.2–0.4, so every crest of the 62 m swell lights up as a pale-teal sheet over the deep water.

Zones with high cameras are coming: Ch18 from the Kite, overworld establishing shots, Haluna H01-style cranes. The colour script's water-looks finding asked for this term to "fade with view elevation".

## Measured (M1-ART-05, lavapipe, 960×540)
Setup:
- Look: `water_look_probe.tscn -- --look=lagoon_clear --camera=survey`, which is the `ch02_noon` light: sun 74° at 3.2, exposure 0.65.
- Control: the same run with a temporary look whose `sss` is `#000000`. Art added it to water_looks.json for the run only and reverted it.
- Deep water: y < 290, above the reef lip; foam with OkL > 0.85 is excluded.

| | SSS on (today) | SSS off |
|---|---|---|
| Deep-water pixels where SSS adds ΔE_ok > 0.03 | **27.5 %** | 0 |
| … where it adds ΔE_ok > 0.05 | **22.5 %** | 0 |
| Max ΔE_ok added | 0.174 | 0 |
| Lightness added, p90 | +0.096 OkL | 0 |
| OkL p90 − p10 | 0.166 | 0.128 |
| > 15 m band median | `#15586E`, ΔE_ok **0.046** to `deep_teal_shadow` "+1" `#106776` (passes ≤ 0.07; ART-04 measured `#186D7B`, 0.020) | `#134E69`, ΔE_ok **0.078** (fails) |

So SSS supplies some of the lift the deep band needs, but it supplies it as patches. The fix must spread or fade it, not just delete it.

## Acceptance criteria
- [ ] **The crest term fades with view elevation.** Weight the crest term by the steepness of the view ray, e.g. `1 − smoothstep(sss_view_fade_lo, sss_view_fade_hi, abs(VIEW_world.y))`. Grazing views (the low cameras) keep their SSS. Views looking down more than about 25–30° lose most of it. Expose both thresholds as material parameters with defaults in the shader, not magic numbers in zone scenes. Apply it on every tier.
- [ ] **Survey view (the probe run above):**
  - the share of deep-water pixels where SSS adds ΔE_ok > 0.05 is **≤ 5 %**, and the share above 0.03 is **≤ 10 %**;
  - the max added is **≤ 0.08**;
  - OkL p90 − p10 over deep water is **≤ 0.14**.
- [ ] **The deep band still passes.** The > 15 m survey band median stays within **ΔE_ok ≤ 0.07** of `deep_teal_shadow` "+1" (colour script, "Water looks", pass criteria). If the fade pushes it past 0.07, as SSS off does at 0.078, make up the lift with an even term (e.g. `scatter_energy` or the deep colour's view-angle response), never with patches. Report the band hex.
- [ ] **Low cameras unchanged.** `water_shallows`, `water_lagoon`, `water_horizon`, `haluna_h01_village_from_sea` and `haluna_h04_dock` stay within RMSE **0.004** of their current baselines, or are re-approved with each image opened. In `water_lagoon`'s mid-ground (x 0–960, y 195–300), the pale-turquoise share (OkL > 0.72, C < 0.10, hue 170–230°) stays **≤ 13 %** (today 12.2 %; before RND-08, 29.5 %).
- [ ] **Undertow unaffected.** No Undertow shot changes by more than RMSE 0.002. `storm_ocean_material.tres` has SSS off today; the scene owner decides whether to turn it back on.
- [ ] **Docs.** water.md documents the new parameters (the subsurface row, and the "Sun behind the camera" gotcha), and the colour script's "Two findings for Rendering" first bullet can then be closed by Art.
- [ ] Back to **review** with **character** (Art Director) as the reviewer. Art re-runs the probe pair and records the numbers in color_script.md, "Art sign-off".

## Notes
- Probe command (needs a real renderer, ADR 0009):
  ```
  ~/.cache/hymn/godot-4.6.3+ds-2/godot-render --path . --audio-driver Dummy --fixed-fps 60 res://game/levels/_tests/swatches/water_look_probe.tscn -- --look=lagoon_clear --camera=survey --out=<dir>
  ```
  Set your own `XDG_DATA_HOME`.
- An optional probe flag, `--sss=#hex`, would make the control run possible without editing water_looks.json.

## Review log

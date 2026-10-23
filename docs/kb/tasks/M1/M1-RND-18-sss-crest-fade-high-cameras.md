---
id: M1-RND-18
title: SSS crest patches from high noon cameras (fade the crest term with view elevation)
role: rendering
status: review
reviewer: character
owner_session: "session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-18-sss-crest)"
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

## Notes (PC GPU session, branch gpu/rnd-18-sss-crest)

Report: `docs/kb/qa/gpu/2026-10-23-rnd-18-sss-crest.md`. The GPU probe pair reproduces Art's "before" exactly:
27.5 % / 22.5 % / max 0.174 / spread 0.166 / band `#15586E`.

- **Fade.** The crest term is weighted by `1 − smoothstep(sss_view_fade_lo, hi, |view.y|) × smoothstep(height_lo,
  height_hi, camera height above the point)`, with 0.10 / 0.28 and 10 / 25 m. All are material parameters with
  shader defaults, applied on every tier.
  - The height gate is needed because a 5.5 m camera sees its own near water steeply. Steepness alone moved
    `water_lagoon` and `haluna_h01` past RMSE 0.004.
- **Even lift.** `col_deep` gains `scatter_view_lift` 1.5 × the same fade. Lifting the whole in-scatter instead
  pushed the 4–15 m band to ΔE 0.105 against `reef_blue`, so only the deep end is lifted.
- **Survey, after:**
  - Deep pixels where SSS adds ΔE > 0.05: **0.0004 %** (≤ 5). Over 0.03: **0.06 %** (≤ 10).
  - Max added **0.050** (≤ 0.08).
  - OkL p90 − p10 **0.075** (≤ 0.14).
  - > 15 m band `#15627A`, **ΔE_ok 0.019** to `#106776` (≤ 0.07).
  - 4–15 m band `#17808C`, unchanged, at 0.066 to `reef_blue`.
- **Low cameras.** `water_shallows`, `water_lagoon`, `water_horizon`, `water_night`, `haluna_h01` and `haluna_h04` are
  **bit-identical** (RMSE 0.00000) on the GPU capture rig, so the lagoon's pale-turquoise share is unchanged.
- **Undertow.** Every shot ≤ RMSE 0.0004, measured before the height gate, which can only reduce it.
- **Docs.** water.md has the subsurface row and a new gotcha. Art can close the colour script's first "Two findings
  for Rendering" bullet.
- **Reviewer:** character (Art Director), who re-runs the probe pair.

### Follow-up S1 (branch `gpu/rnd-18-20-followups`)
- The `col_deep` lift is multiplied by `lift_gate = use_sss ? clamp(sss_strength / 1.4, 0, 1) : 0`, where 1.4 is the
  default `sss_strength` the lift was tuned at (`SSS_LIFT_TUNED_STRENGTH`). So the storm sea (`use_sss` off) gets no
  lift, and a weaker SSS gets less. Tested (`test_deep_lift_is_gated_by_sss`).
- GPU before → after (capture_preset High, storm held): the 4 water shots are 0.0000. Of the Undertow shots, eye is
  0.0004 and the other three are 0.0000. No current shot sees the storm sea from the lift's 10–25 m heights; the Ch18
  Kite will.
- S2 and S3 are not done (they weren't in the Lead's follow-up).

## Review log
- 2026-10-23 character (review-sweep-N, fresh reviewer, Art Director): **approve with should-fixes.** No blockers.
  - **What I read:** this task, `docs/kb/qa/gpu/2026-10-23-rnd-18-sss-crest.md`, water.md's subsurface row and gotcha, and `git diff cede626^1 cede626` (water_surface_body.gdshaderinc, test_water_surface.gd, sss_probe_metrics.py).
  - **Checks:** lavapipe shots via ci_local (HYMN_SHOTS): `water_shallows` 0.00000, `water_lagoon` 0.00000, `water_horizon` 0.00507, `water_night` 0.00306, `haluna_h01` 0.00189, `haluna_h04` 0.00000. The 0.00507 and 0.00306 are the drift that was already there before these merges, the same values recorded in handoff integration-1 and M1-RND-13. So the low shots are bit-identical on lavapipe too, and the lagoon's pale-turquoise share is unchanged. Godot tests 1174/0. I did not re-run the probe pair, which needs a real renderer (ADR 0009). I accept the GPU pair: its "before" reproduces Art's lavapipe numbers exactly.
  - **What passes:**
    - The survey targets clear with margin: 0.0004 % over ΔE 0.05, 0.06 % over 0.03, max 0.050, spread 0.075.
    - The > 15 m band improved to `#15627A` (ΔE 0.019).
    - The height gate is the right call: steepness alone would have moved the 5.5 m shots.
    - The parameters are material uniforms with shader defaults, on every tier (tested).
  - **Should-fix:**
    - **S1: the even lift is not gated by `use_sss`** (water_surface_body.gdshaderinc:551). `scatter_view_lift` makes up for crest SSS, but it also lifts `col_deep` up to 2.5× on materials that have SSS off. `storm_ocean_material.tres:17` is one, and it will be seen from the Ch18 Kite. Multiply the lift by `float(use_sss)`, ideally by `sss_strength` too, so a murky or storm sea seen from above doesn't brighten.
    - **S2:** the fade thresholds are much steeper than the task's suggestion: 0.10 / 0.28 (about 6–16°) against "lose most past 25–30°". That's fine with the height gate, but note in water.md that from a 10–25 m crane the near water already loses its crests, so the H01-style crane shots coming in M2 are judged with that in mind.
    - **S3:** add the probe's `--sss=#hex` flag (the task's Notes suggest it), so the control run no longer needs a temporary edit to Art-owned water_looks.json.
  - **Closing:** Art can tick the colour script's first "Two findings for Rendering" bullet. Close after S1, or file S1 against the Undertow owner.

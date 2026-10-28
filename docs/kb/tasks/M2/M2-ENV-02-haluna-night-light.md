---
id: M2-ENV-02
title: Haluna at night (H10) for the slice's dock scene
role: environment
status: done
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-ENV-01]
reviewer: environment
milestone: M2
request-from: cinematics
---
## Goal
Request from the m2-slice track (M2-FP-15). B11 plays on Haluna's dock at night: H10 in docs/kb/art/environments/haluna.md, with oil lamps in the windows, sea-glow at 0.12 and stars (color_script.md `ch03` night). The playable zone instances the mood scene, so it needs a night lighting state it can switch to: a sun or moon, the sky, the sea-glow value and window lamps.

## Acceptance criteria
- [x] A night variant the zone can select by data (a second Environment and light rig, or a switch on the mood scene) with no edit to the noon baselines.
- [x] Window lamps and sea-glow per the colour script; the dock reads at H10's framing.
- [x] A screenshot shot for H10 at night (lavapipe baseline), with the cost noted.

## Notes
- 2026-10-24 m2-slice, **done, for review by environment** (Rendering for the sky shader and the foliage fix). The Lead assigned it to this track (queue top-up, item b).
  - **The night switch:** `HalunaMood.mood` (`day`/`night`, settable before or after `_ready`) switches to `ch02_night`:
    - the sun off, and a `Moon` light (`#9DB4D9`, 0.25, 38° at azimuth 200);
    - `haluna_night_environment.tres` with the new `game/shaders/environment/env_sky_night.gdshader` (gradient, hashed stars, the moon disc; stars and disc in the visible pass only), exposure 1.1;
    - sea-glow 0.12 with the `night_sea` look (deep `#061A2B`, absorption ×1.0, caustics 0.25) on a copy of the sea material;
    - the glimmer gate open, and the oil lamps shown.
  - **The lamps:** the dresser places one lantern (OmniLight3D 1.3, range 7, no shadow; emissive glass) under each house's front eave, from `haluna_layout.json` `night_lamps`. 38 lamps, none drawn from the scatter RNG. The zone's collision ignores them (the `night_lamp_flame` rule).
  - **The zone:** `HalunaZone.set_night` now asks for the world's night mood instead of dimming the noon sun. It keeps two dock lanterns from first_playable.json. test_haluna_night checks the moon, the sea-glow and the lamps.
  - **Foliage bug fix (Environment's `vegetation_foliage_body.gdshaderinc`):** the translucency shadow floor applied to omni and spot lights too, whose ATTENUATION carries distance falloff. Every lamp therefore lit all the saltgrass at 35% from any distance (the beach glowed orange). The floor now applies to directional lights only.
  - **Shot:** `haluna_h10_dock_night` with a lavapipe baseline. Its foreground sea is `#003B4C` (colour script `#003845`) and its sky `#091B36`. Cost on lavapipe: 27.2 s for 24 frames, in the noon shots' 20.6–36.1 s band. **GPU cost:** the PC session should measure 38 unshadowed omni lights plus the night sky on the 9070 XT.
  - **Noon:** the five noon shots pass against their committed baselines. Four are byte-identical. H01 differs by RMSE 0.00027 (589 px of palms and grass) from before the change, and sits at 0.0019 against its 0.008 limit. No noon baseline was re-approved.
  - **Not done:** `lut_ch04_wake` (the colour script's night grade) doesn't exist yet, so night has no LUT. haluna.md's "stars, sea-glow 0.12" are met, but the dock isn't built to hero quality (M2-ENV-03-adjacent).

## Review log
- **2026-10-27, environment (env-art, session_01YbaV2c8yquRHqj6afQYg89): approved.**
  - **Check run:** `--filter=haluna_night` is 9 run, 0 failed.
  - **Viewed:** H10 at night, re-approved today with the density pass's palms (lead/gate-render-env-art-ab58f89).
    The moon, the sea-glow 0.12 and the eave lanterns read, and the noon shots are untouched.
  - **Follow-up, not a blocker:** `lut_ch04_wake` still doesn't exist, so the night has no LUT. The zone_lut grades
    can make it when the Lead asks. Done.

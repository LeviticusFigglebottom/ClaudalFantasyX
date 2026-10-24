# Handoff — environment — 2026-10-24 #2

Session: m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC), branch `claude/m2-slice`. Task: M2-ENV-02, Haluna at night (H10), Lead-assigned to this track.

## Done
- `HalunaMood.mood` switches to the colour script's `ch02_night`:
  - the moon (`#9DB4D9`, 0.25, 38°), a star sky (`env_sky_night.gdshader`, new), exposure 1.1;
  - sea-glow 0.12 with the `night_sea` look (on a copy of the material);
  - the glimmer gate open, and oil lanterns under the 38 house eaves (layout `night_lamps`; the dresser places them without using the RNG).
- B11's `HalunaZone.set_night` uses it, so the FP-15 stand-in is gone.
- Fixed the foliage translucency floor: it leaked every omni light into all foliage at any distance. It's now directional-only.
- New shot `haluna_h10_dock_night` with a lavapipe baseline. The noon five pass; four are byte-identical, and H01 differs by RMSE 0.00027.

## In progress
- Nothing. M2-ENV-02 is in review (environment; Rendering for the sky shader and foliage fix).

## Exact next step
- PC GPU session: measure the night's cost (38 unshadowed omnis plus the star sky) at H10 on the 9070 XT.
- When Art makes `lut_ch04_wake`, set it as the night environment's `adjustment_color_correction`.
- This track: wire M2-UI-04's field menu into Haluna, then the slice playthrough pass.

## Known issues
- No night LUT yet (see above).

## Files touched
- game/shaders/environment/env_sky_night.gdshader (new); game/shaders/vegetation/vegetation_foliage_body.gdshaderinc (the floor fix)
- game/levels/ch02/haluna/: haluna_night_environment.tres (new), haluna_mood.gd, haluna_dresser.gd, haluna_dressing.tscn, haluna_layout.json, haluna_zone.gd, haluna.tscn (piece rule), README.md
- game/levels/_tests/haluna_mood/haluna_mood.tscn (H10 camera), README.md
- game/data/flow/first_playable.json (night block)
- tests/unit/test_haluna_night_mood.gd (new), test_environment_shaders.gd; tests/integration/test_haluna_night.gd
- tests/screenshots/shots.json, baselines/haluna_h10_dock_night.png, baselines.json

## Gates
- lint and format; validate_data; taskboard --check.
- The full Godot suite: 1363 run, all green after the camera-count update.
- Tools unittest: 488 OK.
- `HYMN_SHOTS`: the six haluna shots, with all five noon shots passing against their committed baselines.

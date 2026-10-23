---
id: M1-ENV-03
title: Vegetation follow-ups (review-sweep-B)
role: environment
status: todo
owner_session: ""
depends_on: [M1-ENV-02, M1-ENV-01]
milestone: M1
request-from: "rendering"
---
## Goal
Rendering-side findings on vegetation, scheduled after the mood test (which uses the vegetation) merges.

## Acceptance criteria
- [ ] translucency_shadow_floor no longer lets plants under eaves glow
- [ ] Capture under FXAA (as water does) and restore threshold 0.008
- [ ] LOD fade (no palm pop against sky)
- [ ] Overdraw measured (debug_draw OVERDRAW capture) with a budget
- [ ] Assets tagged PLACEHOLDER until Art Director sign-off
- [ ] Wind flutter cap noted for GPU TAA motion test

## Notes
-

## Review log
- 2026-10-23 rendering (review-sweep-N, fresh reviewer): **changes needed.** The LOD cross-fade produces see-through trunks in the shots, and the report puts the drift down to the AA swap.
  - **What I read:** this task, `docs/kb/qa/gpu/2026-10-23-env-03-vegetation.md`, vegetation.md:83 and :123, and `git diff 40aa118^1 40aa118` (vegetation_plant.gd, vegetation_test.gd, the foliage body, shots.json, test_vegetation_plant.gd, eave_glow and lod_pop).
  - **Checks:** lavapipe:
    - `veg_backlit_fronds` 0.02440, `veg_frangipani_close` 0.02966, `veg_beach_wide` **0.04471**, `haluna_h02` 0.01212 and `haluna_h03` 0.01163: all FAIL at the new 0.008 threshold;
    - `h01` 0.00189, `h04` 0.00000 and `h07` 0.00075 pass;
    - Godot 1174/0, gdlint and gdformat clean.
  - **What I viewed:** all five failing shots against their baselines, with 3× crops of veg_beach_wide's palms (x 330–620) and h02's top-right palm.
  - **Blockers:**
    - **B1: palms in a fade band render with translucent, ghost trunks** (vegetation_plant.gd:136-146).
      - In `veg_beach_wide` the trunks at x ≈ 395 and x ≈ 490 are pale see-through bands under solid crowns. A palm that the baseline doesn't show at all now appears at x ≈ 380–420.
      - In Godot 4.6, `VISIBILITY_RANGE_FADE_SELF` fades through the alpha-blended path, not a dither (the comment at :27-30 assumes a dither that TAA smooths). So opaque trunks go half-transparent across the whole 6 m band, while alpha-scissor fronds stay solid. Any palm 45–51 m or 120–126 m from a still camera will show this, under any AA.
      - Your own `lod_pop` measure says the 45 m switch is invisible (0.84/255 mean). So fade **only the last LOD's end** (400 m against the sky), and keep the hard switch with hysteresis at 45 m and 120 m.
      - Then re-capture, and re-check what in `veg_beach_wide` is the AA swap and what is the fade.
    - **B2: the drift is attributed to the wrong cause.** The report says veg_beach_wide's 0.044 is "TAA → FXAA". It's partly B1. Re-measure after B1, before anyone re-approves.
  - **Should-fix:**
    - **S1: `shelter` is a float with a sentinel** (:38, :43-48). `shelter == SHELTER_AUTO` is a float equality check, and any value in (-1, 0) silently does nothing. Use an enum (AUTO / OPEN / SHELTERED) plus a separate weight, or clamp.
    - **S2: the shelter probe** (:59-64, :79-84):
      - The ray has no collision mask, so a CharacterBody or prop standing by a plant at `_ready` flags it as sheltered. Use a static-world layer mask.
      - `sun_direction()` takes the first visible DirectionalLight3D in the scene, not `hymn_sun_direction`. A moon, or a character key light, could win.
      - The result is computed once, so a time-of-day change never updates it. Note that in vegetation.md, or re-probe on sun changes.
    - **S3: the auto-probe is untested.** test_vegetation_plant.gd:63 only covers a manual `shelter = 1`. Add a test with a StaticBody3D roof above a plant, and one with no roof.
    - **S4: `tests/unit/test_vegetation_plant.gd.uid` isn't committed.** The import step generates it as untracked; the other 91 unit-test `.uid` files are tracked.
    - **S5:** the shelter only works with collision on buildings, and the Haluna kit has none, so the eave fix does nothing in the only real zone. Request collision on the kit from Environment, or file it on M1-ENV-05.
  - **What passes:**
    - The FXAA capture swap mirrors water_test_rig and restores the viewport on exit. The backlit and frangipani diffs look like AA edge changes only, with no content change.
    - The overdraw budget is recorded, and the PLACEHOLDER list exists.
    - The flutter cap is noted with the RND-15 ghosting measure.
  - **Baselines:**
    - **Reject** `veg_beach_wide`, `haluna_h02_tidewall_lane` and `haluna_h03_lintel_gull` (B1).
    - **Hold** `veg_backlit_fronds` and `veg_frangipani_close`. They look right (AA only), but re-approve them in the same commit as the B1 fix, so the 0.008 threshold is set against final images.

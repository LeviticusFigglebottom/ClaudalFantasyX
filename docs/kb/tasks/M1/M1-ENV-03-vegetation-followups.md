---
id: M1-ENV-03
title: Vegetation follow-ups (review-sweep-B)
role: environment
status: done
reviewer: rendering
owner_session: "session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/env-03-vegetation-v2; routed by the Lead)"
depends_on: [M1-ENV-02, M1-ENV-01]
milestone: M1
request-from: "rendering"
---
## Goal
Rendering-side findings on vegetation, scheduled after the mood test (which uses the vegetation) merges.

## Acceptance criteria
- [x] translucency_shadow_floor no longer lets plants under eaves glow
- [x] Capture under FXAA (as water does) and restore threshold 0.008
- [x] LOD fade (no palm pop against sky): the final 400 m cut only (v2)
- [x] Overdraw measured (debug_draw OVERDRAW capture) with a budget
- [x] Assets tagged PLACEHOLDER until Art Director sign-off
- [x] Wind flutter cap noted for GPU TAA motion test

## Notes
PC GPU session (Lead-routed; branch `gpu/env-03-vegetation`). Report: `docs/kb/qa/gpu/2026-10-23-env-03-vegetation.md`.
- **Eaves.** The instance uniform `inst_translucency_shelter` turns the through-shadow floor off. `VegetationPlant`
  sets it automatically: a crown-height ray toward the sun that hits a collider means sheltered. It can also be set
  by hand. GPU bench: the glow under a roof (mean 0.013, p99 0.23 linear luminance) is removed. Needs collision on
  buildings; the Haluna kit has none yet.
- **FXAA capture.** The vegetation test swaps TAA for FXAA under capture.tscn, as the water does, and the three veg
  shots are back at the default 0.008 threshold. On this GPU, two shot orders differ by RMSE ≤ 0.0001.
- **LOD fade.** A 6 m cross-fade with `VISIBILITY_RANGE_FADE_SELF` and overlapping fade bands; the last LOD fades out
  at 400 m. +0.04 ms. Tested.
- **Overdraw.** Measured in layers per pixel; the budget is in vegetation.md (wide ≤ 2.5 mean / p99 ≤ 12, close-up
  ≤ 5 / 14).
- **PLACEHOLDER.** `docs/kb/art/environments/vegetation_placeholders.md` lists the assets pending Art sign-off.
- **Flutter cap.** 0.02 m at 3.5 Hz, recorded in vegetation.md with the RND-15 ghosting measure.
- **Drift:**
  - `veg_backlit_fronds`, `veg_frangipani_close` and `veg_beach_wide`: TAA → FXAA, RMSE 0.022–0.044 on the GPU.
  - `haluna_h02_tidewall_lane` and `haluna_h03_lintel_gull`: 0.012, a palm in a fade band.
  - Not overwritten. Environment and Art re-approve.

### v2 (review-sweep-N fixes, branch `gpu/env-03-vegetation-v2`)
Report section: "v2" in `docs/kb/qa/gpu/2026-10-23-env-03-vegetation.md`.
- **B1 (ghost trunks):** only the last LOD fades, out at 400 m (`VISIBILITY_RANGE_FADE_SELF`, end margin =
  `lod_fade_m`). The 45 m and 120 m switches are hard again, with the `lod_margin_m` hysteresis. Tested.
- **B2 (drift attribution):** re-measured on the GPU. With the AA swap disabled, v2 renders the three `veg_*` shots
  identically to the base (RMSE 0.0000), so their drift is purely TAA → FXAA. `haluna_h03` no longer drifts.
  `haluna_h02` 0.0124 is one palm at the 120 m switch, drawn now and missing in the base (see the report).
- **S1:** `shelter` is `enum Shelter { AUTO, OPEN, SHELTERED }`.
- **S2:**
  - The ray has a `shelter_mask` (physics layers, default 1).
  - The sun comes from the `hymn_sun_direction` global through the new `ShaderGlobals`
    (`game/core/shader_globals.gd`). It keeps a CPU copy of what was written, because `global_shader_parameter_get`
    is editor-only.
  - The four writers (the vegetation, water, Undertow and Haluna mood test rigs) now go through
    `ShaderGlobals.set_value`. The Haluna rig line is a one-line cross-role edit.
- **Tests:** an auto-detect test (a box roof on layer 1 shelters; off the mask, or under a low side sun, it doesn't).
  The `.uid` is committed.

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
- 2026-10-23 lead: the code merge was REVERTED on the integration branch (e97dd41 / 9a57a8c) because the review-sweep-N blockers broke lavapipe shots. The reports and notes are kept. The PC reworks it on its gpu/ branch: rebase on the integration branch, fix the blockers, and resubmit.
- 2026-10-24 review-sweep-O (rendering): **approve with fixes.** The sweep-N blockers are fixed. B1: only the last LOD fades now, so the 45 m and 120 m switches are hard again and no trunk goes translucent. B2: the drift is re-attributed, and the Lead lavapipe-checked the merge as ci33 (b1997e1, baselines re-approved in c940d77). S1-S4 are done.
  - **What I read:** `git show 4ca20cc`: vegetation_plant.gd, the new game/core/shader_globals.gd, the four rig writers, vegetation_test.gd and test_vegetation_plant.gd (plus its `.uid`).
  - **Checks:** Godot `--filter=vegetation` 10/0 failed. gdlint and gdformat are clean on the tree. I ran no shots, because the Lead's ci33 covered this merge.
  - **Should-fixes, filed as M1-ENV-09:**
    1. **The hysteresis gap at the last switch** (vegetation_plant.gd `_apply_lod`). The fading last LOD gets a begin margin of 0, while LOD1's end margin stays at `lod_margin_m` (2 m) as hysteresis. Approaching through 118-120 m, neither LOD draws. Receding through 120-122 m, both draw. That is the same family as the h02 palm "the old hysteresis failed to draw".
    2. **ShaderGlobals goes stale.** vegetation_test.gd:54-57 restores the sun through RenderingServer directly, so `ShaderGlobals.get_value` keeps returning the test's sun. Its fallback is `Vector3.UP`, not the project default.
    3. **The probe runs once.** A time-of-day change doesn't re-probe, and vegetation.md doesn't say so.
    4. **Check the AUTO shelter against first-playable's Haluna collision** once that branch merges (sweep-N S5).

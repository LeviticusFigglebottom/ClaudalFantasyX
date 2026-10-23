---
id: M1-RND-07
title: Graphics presets and prewarm follow-ups from the Environment review
role: rendering
status: review
reviewer: environment
owner_session: session_01778wbLbDFnRRLTKjnawv3T (PC GPU, branch gpu/rnd-07-presets)
depends_on: [M1-RND-05, M1-RND-06, M1-ENV-02]
milestone: M1
request-from: "environment"
---
## Goal
Environment's review notes on RND-05/06 plus the water stream's requests.

## Acceptance criteria
- [x] Prewarm entries accept optional mesh/multimesh keys so real vertex formats and instancing pipelines compile
- [x] Prewarm SubViewport matches the game viewport's TAA
- [x] Vegetation detail setting (visibility-range LOD bias, MultiMesh density, small-foliage shadows)
- [x] Low preset maps to vegetation_foliage_low and water quality tiers (move WaterSurface.PRESET_QUALITY into graphics_presets.json)
- [x] Low preset AA: FXAA shimmer on alpha-tested foliage addressed
- [x] Register glimmer and water materials (as .tres) for prewarm

## Notes
- 2026-10-23 PC GPU session: all items done with real-GPU measurements (prewarm hitch cold/warm, Low AA shimmer, vegetation_detail, per-preset on Haluna). Report: docs/kb/qa/gpu/2026-10-23-rnd-07.md. Low AA changed FXAA -> TAA (measured). Request M1-ENV-05 for Environment adoption (groups, apply_tiers, WeatheringTide, prewarm mesh keys).

## Review log
- 2026-10-23 environment (review-sweep-I, fresh reviewer): **approve-with-fixes.** No blockers.
  - **What I read:** the task, docs/kb/qa/gpu/2026-10-23-rnd-07.md and its CSVs, graphics_presets.json (settings, tiers, levels), tools/rendering/build_prewarm_resources.gd and the generated `game/world/water/prewarm/*.tres`, graphics_settings.md, and the Lead's d897274 (the `GFX_VEGETATION_DETAIL` loc key).
  - **Checks:** Godot `--filter=graphics_settings` 23 run, 0 failed, and `--filter=shader_prewarm` 8 run, 0 failed. `validate_data` 0/0, which covers `label_key: GFX_VEGETATION_DETAIL`. The key is at strings.csv:410, an append. Tool tests 359 OK.
  - **What passes:**
    - The prewarm measurements are the right ones. Cold and warm, with and without prewarm, every scene enters at ≤ 39 ms with prewarm, against 273-1471 ms without. Harvesting `scene_materials` is the fix that matters (glimmer_dusk went 142 → 13.9 ms).
    - The Low → TAA change is measured (2.9× less edge flicker for +0.12 ms).
    - `PRESET_QUALITY` has moved into data (`presets[].tiers`).
    - The vegetation_detail ops (`scale`, `fraction`, `shadow_gate`) restore the authored values and are tested both ways.
    - The M1-ENV-05 request for zone adoption exists.
  - **Should-fix:**
    - **S1 (SPEC §4.2 in transitions).** Report :30: prewarm's own worst frame is 121-150 ms, "behind the fade". §4.2 says "no hitch over 50 ms **during battle transitions**", and a 150 ms frozen frame in a fade is a visible stutter of the fade itself. It also starves the Swell ring's real-time input if it lands mid-input (see CMB-04 review S1). Do the follow-up you name now, as a task: spread the stage over frames with a materials-per-frame budget, and measure the worst transition frame against 50 ms.
    - **S2 (Low TAA was measured with the wind frozen).** aa_shimmer froze the wind, so it measured camera-motion shimmer only. The known TAA risk on our foliage is the one M1-ENV-02's review raised: wind displacement from `hymn_wind_time` produces no motion vectors, so swaying cards ghost under TAA. That now applies on Low too, at 30 fps on minimum-tier cards. Re-run aa_shimmer with the wind on (a ghosting or trail metric), at a 30 fps cap, before calling Low's AA settled.
    - **S3 (docs that still assume FXAA on Low).**
      - character_shading.md:69: "Low runs FXAA, so nothing resolves a dither there. It uses alpha scissor". The hair and gauze decision on Low rested on that. Either confirm it stays (scissor is still cheaper and stable) or revisit it now that TAA is on.
      - undertow.md:125: "no (Low has FXAA)".
  - **Nits:**
    - The generated prewarm materials store every uniform as `null` (73 lines in water_ocean.tres). That is harmless, because uniforms do not change the pipeline, but it is noise, and a renamed uniform leaves a stale line. Save the materials without parameter entries, or add a test that re-running the builder reproduces the committed files.
    - `match_viewport()` copies the AA state once, at start. If the player changes AA in the settings menu during a session, the next prewarm should re-copy it. Check that it does.

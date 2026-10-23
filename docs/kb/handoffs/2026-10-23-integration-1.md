# Handoff: multi-role integration (environment, rendering, ui), 2026-10-23 #1

Session: worktree-agent-aa764c62452184711. Branch `worktree-agent-aa764c62452184711`, **not pushed**.

## Done
- **M1-ENV-05 → review (rendering).** The vegetation is tagged with the `vegetation_detail` groups (plants,
  vines as `small_foliage`, grass scatters). `WeatheringTide` takes its tier from `presets[].tiers.weathering`
  and drives the sea, which publishes `hymn_water_level` (haluna_mood `Water`). `env_weathering_body` and
  `env_ground` read the global. The prewarm entries gained kit meshes, the playable zone scene, and
  `frangipani_bark` and `beach_vine`.
- **M1-ENV-06 → review (architect).** The First Playable session's `game/levels/ch02/haluna` (M2-FP-02)
  already satisfies it. One deliberate departure: the shrine stays in the mood scene, which the zone
  instances. It can't go straight to `done` because the taskboard requires a Review log entry.
- **M1-RND-13 → review (qa).** The water, undertow and haluna_mood rigs dropped their `CAPTURE_SCENE` holds.
  The 13 shots declare the holds in their `setup` instead: `hymn_wind_time`, FXAA, `mood`, and
  `Storm.playing = false` for the undertow shots.
- **M1-RND-16 → review (environment).** Added `GraphicsSettings.push_override` / `pop_override` /
  `override_state`, `ShaderPrewarm.viewport_state` / `spawn_with_state`, and the Undertow listener
  (`VIEWPORT_STATE_GROUP`). It is documented in graphics_settings.md and undertow.md.
- **M1-UI-09 → review (architect).** Added `AutosaveToast` (game/ui/toast/), installed by boot.gd, with the
  loc key `AUTOSAVE_SKIPPED_TOAST` and the timings in game/data/ui/toast.json.

## Gates (this worktree, own XDG_DATA_HOME)
- validate_data 0/0, tools unit tests OK, taskboard --check OK, gdlint and gdformat clean, import clean,
  and the 60-frame boot smoke test has no errors.
- Godot tests: **1024 run, 0 failed** (full suite), and the log check is clean.
- Shots: water_* (4), undertow_* (4), haluna_* (5) and veg_* (3) were captured before and after the change,
  and all 16 are **byte-identical**. The pre-existing baseline drift on this machine is unchanged and passes
  (water_horizon 0.00507, water_night 0.00306, undertow ≤ 0.00031, the rest 0.0). Nothing was re-approved.

## In progress
- Nothing local.

## Exact next step
1. **Lead:** merge this branch with `origin/claude/first-playable`. `game/data/loc/strings.csv` conflicts
   (both sides appended at the end); resolve it with `tools/dev/merge_union.py` and keep both rows. boot.gd
   and graphics_settings.md auto-merge.
2. After M1-ARC-15 is in, the per-zone `apply_tiers` and `WeatheringTide.quality` are applied by
   `GraphicsRuntime.apply_scene`. Cutscenes can pass `GraphicsRuntime.settings()` as `base` to
   `push_override`.
3. **PC GPU session:** M1-RND-16 criterion 5. Measure the storm close-up dither crop on High with
   `{"aa": "taa", "scaling_mode": "fsr"}` against native TAA (target within 10 %), plus the cost, as in
   docs/kb/qa/gpu/2026-10-23-rnd-11.md.

## Known issues
- A settings-menu apply during an active override writes over it, and the last pop restores the
  pre-override snapshot. Menus aren't reachable in cutscenes today (graphics_settings.md, caveat).
- The `env_ground` prewarm still draws on a quad, because the terrain is generated.
- The first night Environment zone must call `GlimmerField.set_scene_sea_glow` itself (ENV-05 note).
- The toast wording is UI's first pass, so Narrative may want to reword it.

## Files touched
- game/core/{graphics_settings.gd, shader_prewarm.gd, boot.gd}, game/data/settings/{graphics_presets.json, prewarm_materials.json}
- game/vfx/undertow/undertow_storm.gd, game/levels/_tests/undertow/{undertow_test_rig.gd, undertow_test.tscn}
- game/levels/_tests/water/water_test_rig.gd
- game/levels/_tests/haluna_mood/{haluna_mood.gd, haluna_mood.tscn, weathering_tide.gd, haluna_dresser.gd, haluna_layout.json, README.md}
- game/levels/_tests/vegetation/{vegetation_plant.gd, vegetation_scatter.gd, vegetation_test.tscn}
- game/shaders/environment/{env_weathering_body.gdshaderinc, env_ground.gdshader}
- game/ui/toast/autosave_toast.gd (new), game/data/ui/toast.json (new), game/data/loc/strings.csv (appended)
- tests/screenshots/shots.json; tests/unit/{test_graphics_override, test_vegetation_groups, test_autosave_toast}.gd (new), test_environment_shaders.gd
- docs/kb/tech/{graphics_settings, undertow, water}.md, docs/kb/qa/screenshots.md, the five task files

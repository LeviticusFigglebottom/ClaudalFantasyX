# Handoff — environment — 2026-10-24 #seawall-breach (M3-ENV-04B)

## Done
- **M3-ENV-04B, the Seawall falls** is at `review` (reviewer: rendering). Worktree branch
  `worktree-agent-a84a551e4f82edd5e` (not pushed; the Lead merges). Design: `docs/kb/art/environments/corrow.md` §7.
- Kit (job `corrow_kit`, new modules `cw_breach.py`, `cw_fallen.py`): `seawall_breach_a/b`, `seawall_breach_end_w`,
  `seawall_breach_end_e`, `lowtown_rubble`, `watcher_head_fallen`, `watcher_head_cracked`, `fisher_stair_broken`,
  `liss_hoist_cut`, and a second Watcher carving `watcher_head_b` (`cw_common.CARVING_B`). LOD chains, budgets,
  vertex-colour weathering, material `cw_laterite_broken` (by script), 11 PROVENANCE rows, `.glb.import` files on
  the corrow post-import script. `verify_blender_builds --job corrow_kit`: 44 identical. All M3-ENV-04 outputs
  are byte-identical (the first carving's constants are the old literals in the same arithmetic).
- Preview: `CorrowPreview` phases `fallen` (`ch08_after`, `corrow_fallen_environment.tres`) and `ch09` (night mood:
  Moon, `corrow_ch09_environment.tres`, `lut_ch09_ebbing`, sea-glow 0.15, slack water at +0.1 m); both show the
  layout's `states.fallen`, built on first use, the replaced pieces hidden, restored on the way back. Cameras C10
  (fallen, from the bay) and C11 (ch09, from the stair foot's lane).
- `env_sky_night.gdshader`: optional `moon_lit_fraction` / `moon_lit_angle_deg` / `moon_earthshine` (default full
  moon: the branch is skipped, Haluna's night is unchanged).
- Baseline `corrow_c10_breach_fallen` registered (the one allowed). `corrow_c01_wall_head` and
  `corrow_c08_watcher_profile` re-capture at rmse 0.00000.
- Task file: status review, notes, swap-in note for m2-slice.

## In progress
- Nothing.

## Exact next step
- Rendering reviews M3-ENV-04B (Review log in the task file): the `ch08_after` frame (no colour-script row yet)
  and the `ch09` ambient (0.7 instead of the script's 0.3 fill). Then the Lead merges the swap-in note into
  `docs/kb/handoffs/live/env-art.md` (not edited here, per instructions).

## Known issues
- The fallen heads' faces read weakly in the flat `ch08_after` light (low relief needs raking light).
- At 30 m the laterite block map reads small, like brick (the M3-ENV-04 texture, unchanged).
- Preview breach takes the stair's middle: in Ch9 the stair climbs 12 steps then breaks (flagged for Narrative in
  the task file).
- `watcher_head_b` is not in the intact preview row (it would change C01/C08); the zone can alternate it.
- The M3-ENV-04 `watcher_head` back sweeps 2π - 0.52 rad, so it laps over the inside of the face (hidden, but
  about 1,000 wasted triangles and a possible z-fight at the face edges). Left as is: fixing it changes the
  approved baselines. The broken heads use the exact sweep.
- Pre-existing, not from this branch: `haluna_h10_dock_night` re-captures at rmse 0.00545 with or without the
  sky-shader change (checked both ways); still under its 0.008 limit.

## Gates
- Run: `gdlint game tests`, `gdformat -l 120 --check game tests`, `validate_data`, `taskboard --check`,
  `unittest tools.tests.test_corrow_kit tools.tests.test_post_import tools.tests.test_release_excludes_tests`,
  `verify_blender_builds --job corrow_kit`, Godot `--import` (corrow glb caches deleted first), Godot tests
  `--filter=corrow` (8) and `--filter=post_import` (19), screenshots `corrow_c01`, `corrow_c08`, `corrow_c10`
  and `haluna_h10_dock_night` (the only other shot using the touched night-sky shader).
- Skipped: the coverage step (no `game/battle/` or `game/progression/` change), the full manifest (Lead's).

## Files touched
- New: `assets_src/environments/kits/corrow/cw_breach.py`, `cw_fallen.py`; 10 `.glb` + `.glb.import` in
  `assets/environments/kits/corrow/`, `materials/cw_laterite_broken.tres`; `game/levels/_tests/corrow_kit/`
  `corrow_fallen_environment.tres`, `corrow_ch09_environment.tres`, `lut_ch09_ebbing.png(.import)`;
  `tests/screenshots/baselines/corrow_c10_breach_fallen.png`; this handoff.
- Edited: `cw_common.py` (FaceCarving), `cw_watchers.py` (head carving/base/sweep options), `cw_wall.py` (bent
  flag), `cw_materials.py`, `cw_zone_lut.py` (`--frame ch09`), `cw_preview_layout.py` (states), `build.py`,
  `kit_manifest.json`, `corrow_layout.json`, `corrow_preview.gd/.tscn`, `corrow_preview_shots.json`, README,
  `game/shaders/environment/env_sky_night.gdshader`, `tests/unit/test_corrow_preview.gd`,
  `tools/tests/test_corrow_kit.py`, `tests/screenshots/shots.json` + `baselines/baselines.json` (appended),
  `assets/PROVENANCE.md` (appended), `docs/kb/art/environments/corrow.md` (§7 + revision),
  `docs/kb/tasks/M3/M3-ENV-04B-seawall-breach.md`.

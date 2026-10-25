# Handoff — environment — 2026-10-24 #seawall (M3-ENV-04)

## Done
- **M3-ENV-04 Ch8 the Seawall** is at `review` (reviewer: rendering). Branch `worktree-agent-a37e7e1f20c6506a9`
  (not pushed; the Lead merges).
- Design notes first: `docs/kb/art/environments/corrow.md` (committed before any geometry, revised after the
  preview: the wall is concave to the sea at R = 300 m, so the far Watchers turn their faces round the curve).
- Kit `assets_src/environments/kits/corrow/` (11 pieces, LOD chains, budgets in each module): `seawall_curve`,
  `wall_apron`, `watcher_head`, `watcher_relief`, `fisher_stair`, `liss_hoist`, `lowtown_ground`,
  `lowtown_house_a/b`, `coilspire_headland`, `corrow_far`. The Watchers' face is one displacement function,
  `cw_common.watcher_face` (closed lids, humming mouth, breaking-wave crown). Maps `laterite_blocks` (6 × 1 m,
  dry-laid) and `laterite`; 17 materials; LUT `lut_ch08_storm`.
- Blender job `corrow_kit` (threads 4): `verify_blender_builds --job corrow_kit` → 33 identical.
- Import kind `corrow_kit` (json + post-import script, added to both KINDS lists and docs/kb/tech/asset_import.md).
- Preview `game/levels/_tests/corrow_kit/` (rig `CorrowPreview`: phases `front` = ch08, `surge` = ch08_surge
  with the sea at +1.8 m flooding the low town; the beacon light). Seven views; baselines
  `corrow_c01_wall_head` and `corrow_c08_watcher_profile` approved (re-capture rmse 0.00000).
- Follow-up filed: **M3-ENV-04B** (the breach / wall-falls state, the cut hoist, the Ch9 night pass).
- Ownership row, PROVENANCE rows (33), swap-in note for m2-slice in the task file.

## In progress
- Nothing.

## Exact next step
- Rendering reviews M3-ENV-04 (append to its Review log). Then env-art takes M3-ENV-04B, or the Lead merges the
  swap-in note into `docs/kb/handoffs/live/env-art.md` (not edited here, per instructions).

## Known issues
- All 148 heads share one carving; a second head variant would help the long row in C03.
- The volumetric spray haze is disabled in the preview environment on lavapipe (it doubled capture time and
  veiled the sky warm); the rig still writes the colour script's density for GPU tiers.
- The storm wall is Rendering's `UndertowStorm`; the preview's storm is a static `env_sky_low_sun` sky. The Sun
  must keep `sky_mode` 0 (light and sky), or that sky goes uniformly tan.
- Pre-existing, not from this branch: `tools/tests/test_tamsule_bell_kit.py` `test_lut` fails (its regenerated
  LUT differs from the committed one; no tamsule or Haluna LUT file is touched here).

## Files touched
- New: `assets_src/environments/kits/corrow/**`, `assets/environments/kits/corrow/**`,
  `game/levels/_tests/corrow_kit/**`, `game/core/import/corrow_kit_post_import.gd`, `game/data/import/corrow_kit.json`,
  `tools/tests/test_corrow_kit.py`, `tests/unit/test_corrow_preview.gd`, `docs/kb/art/environments/corrow.md`,
  `docs/kb/tasks/M3/M3-ENV-04B-seawall-breach.md`, the two baselines.
- Appended / small edits: `tools/dev/blender_builds.json` (job), `assets/PROVENANCE.md`, `docs/kb/ownership.md`,
  `tests/screenshots/shots.json` + `baselines/baselines.json`, `tests/unit/test_post_import.gd`,
  `tools/tests/test_post_import.py`, `docs/kb/tech/asset_import.md`, `docs/kb/tasks/M3/M3-ENV-04-seawall.md`.

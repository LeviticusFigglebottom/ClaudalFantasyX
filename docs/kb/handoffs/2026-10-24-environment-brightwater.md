# Handoff — environment — 2026-10-24 #brightwater (M3-ENV-08)

## Done
- **M3-ENV-08 Ch4 Brightwater Crossing** is at `review` (reviewer: rendering). Branch
  `worktree-agent-ad1cc767434d06b24` (not pushed; the Lead merges).
- Design notes first: `docs/kb/art/environments/brightwater_ferry.md` (committed 5c57ae3e before any geometry;
  revised after the preview: the moon is a waning crescent low in the east, see its Revisions).
  references.md gained the coastal-trader row (words only).
- Kit `assets_src/environments/kits/brightwater_ferry/` (11 pieces, LOD chains, budgets in each module): the ferry
  *Kind Weather* (`ferry_hull`, `ferry_rig`, `ferry_deckhouse`, `ferry_awning`, `ferry_cargo`, `ferry_skiff`),
  `passenger_bundles`, `ferry_lantern`, and the drowned (`derelict_hulk_a`, `derelict_hulk_b`, `reef_awash`).
  One parametric plank-built hull (`bf_common.HullForm`, `hull_sides`, `deck_planks`, `bulwark`) builds the ferry
  and every derelict, with `arena_derelict_deck`'s plank/seam/thickness proportions (tested): they read as kin.
  27 materials by script; grade LUT `lut_ch04_crossing` (`bf_zone_lut.py`: `ch04_wake` with the sea's teal spared).
- Blender job `brightwater_ferry_kit` (threads 4): `verify_blender_builds --job brightwater_ferry_kit` → 40 identical.
- Import kind `brightwater_ferry_kit` (json + post-import script, both KINDS lists, docs/kb/tech/asset_import.md);
  `.glb.import` files point at it (`bf_import_settings.py`); the LUT's `.import` is a 3D texture.
- Preview `game/levels/_tests/brightwater_ferry_kit/` (rig `BrightwaterFerryPreview`: HalunaMood's night mood at
  the `ch04` values; nine deck lanterns from the layout, every light `light_volumetric_fog_energy` = 0). Seven
  views; baselines `brightwater_b02_awning` and `brightwater_b03_rail_drowned` (re-capture rmse 0.00000).
- Tests: `tools/tests/test_brightwater_ferry_kit.py` (22), `tests/unit/test_brightwater_preview.gd` (5).
- Follow-up filed: **M3-ENV-08B** (the *Seventh Terrace*: one hero ship for Ch1's mooring and the Ch4 derelict).
- Ownership row, PROVENANCE rows (40), swap-in note for m2-slice in the task file.

## In progress
- Nothing.

## Exact next step
- Rendering reviews M3-ENV-08 (append to its Review log); please also add the colour script's `ch04_derelict`
  sub-frame (beat sheet §9) so M3-ENV-08B has a daylight grade. The Lead merges the task file's swap-in note into
  `docs/kb/handoffs/live/env-art.md` (not edited here, per instructions).

## Known issues
- At a deck's eye height the far night sea mirrors the sky; the sea-glow only reads looking down. The drowned
  therefore stand on the crescent's glade (moon east, 88°) rather than "against the glowing sea".
- `ch04_wake` (M3-ENV-06's grade) turns a whole-frame sea navy-grey; this zone uses `lut_ch04_crossing`. If
  Rendering wants one Ch4 grade, the teal spare could move into `zone_lut.py`'s `ch04_wake` (it would change the
  arena's baseline, so it was not done here).
- B05: the deckhouse's fore wall reads as dark boards where the door lantern cannot reach. B04 (from the sea) is a
  backlit silhouette: it reads as night, not as detail.
- Python files exceed 120 columns in places (as the other kits' do); no Python formatter gate exists.

## Files touched
- `docs/kb/art/environments/brightwater_ferry.md`, `docs/kb/art/references.md` (one row)
- `assets_src/environments/kits/brightwater_ferry/*.py`, `assets/environments/kits/brightwater_ferry/**`
- `game/data/import/brightwater_ferry_kit.json`, `game/core/import/brightwater_ferry_kit_post_import.gd(.uid)`
- `game/levels/_tests/brightwater_ferry_kit/**`
- `tests/unit/test_brightwater_preview.gd`, `tests/unit/test_post_import.gd` (KINDS),
  `tools/tests/test_brightwater_ferry_kit.py`, `tools/tests/test_post_import.py` (KINDS)
- `tests/screenshots/shots.json`, `tests/screenshots/baselines/{baselines.json, brightwater_b02_awning.png,
  brightwater_b03_rail_drowned.png}`
- `tools/dev/blender_builds.json` (job appended), `assets/PROVENANCE.md` (rows appended),
  `docs/kb/ownership.md` (row), `docs/kb/tech/asset_import.md` (row)
- `docs/kb/tasks/M3/M3-ENV-08-brightwater-ferry.md`, `docs/kb/tasks/M3/M3-ENV-08B-seventh-terrace.md`

# Handoff — environment — 2026-10-24 #env-art-10 (M3-ENV-10, Coilspire temple)

## Done
- **M3-ENV-10 Ch8 Coilspire temple** is at `review` (reviewer: rendering). Worktree branch
  `worktree-agent-a6fa746c7f37087e8` (not pushed; the Lead merges).
- Design notes first: `docs/kb/art/environments/coilspire.md` (commit 2dc3b399, before any geometry; revised after
  the preview, see its Revisions) and a references.md §2 row (coastal fire-towers, copper still-houses).
- Kit `assets_src/environments/kits/coilspire/` (12 pieces): `coilspire_shell`, `coilspire_flues`,
  `coilspire_tiers`, `beacon_basket`, `keepers_hut`, `flue_key`, `flue_key_wheel`, `tier_brazier`,
  `coilspire_ground`, `headland_path`, `scrub_clump_a/b`. It *is* Corrow's skyline `coilspire_headland` up close:
  `cs_common` reads the far piece's radius law, coils, cage and headland noise from `cw_far` (read-only), and the
  tests check the two match. 16 materials (`cs_materials.py`, Haluna writers loaded by path as
  `haluna_materials`; copper on the Tamsule `env_bronze`), no new maps; interior LUT `cs_zone_lut.py`.
- Blender job `coilspire_kit` (threads 4), import kind `coilspire_kit` (json, post-import, both KINDS lists,
  asset_import.md row), PROVENANCE rows, ownership row.
- Preview `game/levels/_tests/coilspire_kit/` (8 views, two phases, Corrow's kit as a backdrop dresser);
  baselines `coilspire_k01_headland_path`, `coilspire_k03_well` (approved with `compare.py --update-baselines`
  from `tools/screenshots/capture.sh --shots` output; rmse 0).
- Tests: `tools/tests/test_coilspire_kit.py` (24), `tests/unit/test_coilspire_preview.gd` (5).

## In progress
- Nothing.

## Exact next step
- Rendering reviews M3-ENV-10 (task file Review log). The Lead merges the branch and moves the swap-in note (task
  file) into `docs/kb/handoffs/live/env-art.md`.

## Known issues
- K07 (the long lens to Corrow) is hazy and dull: Corrow's environment and flat inland apron.
- Slit light shafts barely read without GI; scrub and far rock are simple; the hut interior is minimal.
- Liss's mark behind tier 3's key (188 deg) is a decal for m2-slice / VFX; the wall-gate (W07) is Corrow's zone.
- Gotchas: cw_far's coils run to +42 m (y = 3 + t (H - 7)), not +39; the spire base is +39.285 m (int arrays
  into `headland_height` truncate the noise's 0.53 offset: pass floats); `env_weathering` tints multiply in
  linear light (a `#A2968E` tint is a third of the map); env_bronze patina at ~50 % coverage reads as camouflage
  (set VC.G high, `cs_common.patina`); a D-landing covering more than half the circle blocks the well's axis.

## Files touched
- New: `assets_src/environments/kits/coilspire/**`, `assets/environments/kits/coilspire/**`,
  `game/levels/_tests/coilspire_kit/**`, `game/data/import/coilspire_kit.json`,
  `game/core/import/coilspire_kit_post_import.gd(.uid)`, `tools/tests/test_coilspire_kit.py`,
  `tests/unit/test_coilspire_preview.gd(.uid)`, `docs/kb/art/environments/coilspire.md`, two baselines, this file.
- Appended: `assets/PROVENANCE.md`, `docs/kb/ownership.md`, `docs/kb/art/references.md`, `docs/kb/tech/asset_import.md`,
  `tools/dev/blender_builds.json`, `tests/screenshots/shots.json`, `tests/screenshots/baselines/baselines.json`,
  `tests/unit/test_post_import.gd`, `tools/tests/test_post_import.py`; the task file.

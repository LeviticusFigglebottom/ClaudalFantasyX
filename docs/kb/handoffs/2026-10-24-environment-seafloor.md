# Handoff — environment — 2026-10-24 #12 (M3-ENV-05, Oruvel Underway)

## Done
- **M3-ENV-05 → review (reviewer: rendering).** Ch1's drowned tower and its sea floor, `ch01/oruvel_underway`.
  - Design notes `docs/kb/art/environments/oruvel_underway.md` (committed before any geometry, revised after the
    preview): the podium-and-tower layout with Lit Age floors counted from the street (F9 = the gallery at the
    terrace, so "nobody goes below the ninth floor" is literal), the dive's sub-frames (open / interior / deep, the
    08:45 sun), downwelling, kit, materials, U01–U14 shots.
  - Kit `assets_src/environments/kits/oruvel_underway/` (30 pieces, `silt` and `coral` maps, 25 materials, import
    kind `oruvel_underway_kit`, Blender job `oruvel_underway_kit` with threads 4: 60 files byte-identical).
  - Preview `game/levels/_tests/oruvel_underway_kit/` on the existing `UnderwaterRig`; 7 views viewed on lavapipe
    and iterated; baselines `ou_u04_lamp_gallery` and `ou_u12_terrace` approved (only those two), stable twice.
  - Tests: `tools/tests/test_oruvel_underway_kit.py` (18), `tests/unit/test_oruvel_underway_preview.gd` (6).
  - Request filed: **M3-RND-24** (downwelling and a per-area light scale on the rig; the preview fakes both).
  - Swap-in note for m2-slice: in the task file (scene, anchors, collision, lighting).

## In progress
- Nothing. Not pushed (worktree branch only, per the Lead's instruction).

## Exact next step
- Rendering reviews M3-ENV-05 (the two baselines and the notes' read). The Lead merges the branch and folds the
  swap-in note into `docs/kb/handoffs/live/env-art.md` (I did not edit it).

## Known issues
- The rig's lantern halo is a warm haze over much of the frame whenever the lamp is within ~2.5 m of the lens
  (U06, U07): the post's single-scatter halo, as designed; in play the camera sits further back.
- Coral boulders read as lumpy masses more than brain coral at game distance; the coral curtain reads as rags from
  afar; hulls seen from the terrace are dark ellipses against the dark TIR.
- `tools/tests/test_tamsule_bell_kit.GeneratedTextTests.test_lut` fails in this worktree (a PNG byte mismatch in a
  file this task does not touch); not investigated, flagged for the Tamsule kit's owner.
- The kit has no `-col` proxies (collision is m2-slice's, notes in the swap-in note).

## Files touched
- `docs/kb/art/environments/oruvel_underway.md` (new), `docs/kb/tasks/M3/M3-ENV-05-lamp-diver-seafloor.md`,
  `docs/kb/tasks/M3/M3-RND-24-underwater-downwelling-area-light.md` (new), this handoff.
- `assets_src/environments/kits/oruvel_underway/**` (new), `assets/environments/kits/oruvel_underway/**` (new).
- `game/data/import/oruvel_underway_kit.json`, `game/core/import/oruvel_underway_kit_post_import.gd` (new).
- `game/levels/_tests/oruvel_underway_kit/**` (new).
- `tests/unit/test_oruvel_underway_preview.gd` (new), `tests/unit/test_post_import.gd` (KINDS),
  `tools/tests/test_oruvel_underway_kit.py` (new), `tools/tests/test_post_import.py` (KINDS).
- Shared, append-only: `assets/PROVENANCE.md` (60 rows), `docs/kb/ownership.md` (one row),
  `tools/dev/blender_builds.json` (one job), `tests/screenshots/shots.json` (two shots),
  `tests/screenshots/baselines/` (two PNGs + `baselines.json` via compare.py), `docs/kb/tech/asset_import.md` (one row).

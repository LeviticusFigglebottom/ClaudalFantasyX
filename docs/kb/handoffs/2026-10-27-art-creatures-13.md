# Handoff — art (creatures) — 2026-10-27 #13

## Done
- M3-CRE-622, the Mangrove Drowner silhouette redesign, finished from the interrupted WIP (cc81201a) and set to
  `review` (reviewer: art).
  - Roots in four lopsided bundles: each root converges late onto its cluster's heading, so no top view is a
    sunburst (`CLUSTERS`, `ROOTS`, `CONVERGE`).
  - The risen stance is three planted pairs, steered by rolling each leg's plane (`RISEN_ROLL`): 1+3, 5+6 and 7+9,
    with the bank's trails alongside 7+9. Leg bends are capped at 55 degrees.
  - Every clip stays on the water: rest geometry is flattened onto y 0, and `grounded_clips` re-keys every frame
    (roots curl up; the mass and the aerial roots lift). The KO keels over on the trunk's foot edge instead of
    sinking. The drowner is removed from GroundedClipsTest's allow-list.
- Measured: 14,700 triangles (body 13,881, stump 819), 53 bones. The lowest vertex is +0.002 m in every clip
  (+0.003 m in cast and idle_b).
- Sheet: two model notes appended (on the water; clusters in plan).
- Gates:
  - Blender verify: 3 identical.
  - `tools.tests.test_creatures` and `tools.tests.test_blender_builds`: OK (40 tests).
  - `validate_data`: 0 errors. The one warning (a haluna kit GLB) is pre-existing and unrelated.
  - `taskboard --check`: OK.
  - gdlint and gdformat: clean.
  - Godot import, then `--filter=creature`: 42 run, 1 failed, the known test_creature_portraits missing-PNG red.

## In progress
- Nothing. The commits are not pushed.

## Exact next step
- The art review of M3-CRE-622 needs a PC render of `creature_mangrove_drowner` and `_risen`, which this
  environment cannot do.
- The flat-silhouette sheet (before vs after; rooted, KO end, phase_change 1.2 s, risen) is in this session's scratch:
  `M3-CRE-622b/final_sheet.png` (and `final_sheet_shaded.png`). It is not committed.

## Known issues
- **Residual spider risk:**
  - The risen front view is still a dark dome on roots splayed both ways. It reads more crab or tick than spider.
  - The rooted top view keeps a few short pale spokes at the centre (limb stubs, and the high roots' bleached
    shoulders).
- The risen lean is still 48 degrees, kept as the reviewer approved it. The sheet's silhouette text says "about 30".
  Amend one or the other after the render.
- The sheet's risen text names "a back cluster". As built, the back roots 5 and 6 plant front-left under the lean,
  because the 48-degree tip carries their attachments forward. The appended model note describes this.

## Files touched
- `assets_src/creatures/mangrove_drowner/build_mangrove_drowner.py`
- `assets/creatures/mangrove_drowner/mangrove_drowner.glb`
- `tools/tests/test_creatures.py` (the allow-list entry is removed)
- `docs/kb/tasks/M3/M3-CRE-622-drowner-polish.md`
- `docs/kb/art/creatures/act2/mangrove_drowner.md` (appended)
- `docs/kb/handoffs/2026-10-27-art-creatures-13.md`

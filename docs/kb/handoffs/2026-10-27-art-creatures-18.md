# Handoff — art (creatures track) — 2026-10-27 #18

Hesk, the Cord-Keeper, Asha's Holy Vowbound (bound Ch12), as a creature model (M3-CRE-643). Branch
`worktree-agent-adff7ba4a64aa18db`, launched by the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY). This
resumed a WIP build script committed before a container restart (715885cc). Not pushed: the Lead merges it. Nhoa
(M3-CRE-642) and Ethren (M3-CRE-644) were built in parallel and append to the same shared files (creatures.json,
blender_builds.json, PROVENANCE.md, shots.json, portraits.json, the import list). Every edit here is an append at the
end of its block, or an alphabetical insert in the import list.

## Done
- **M3-CRE-643, to review (art).** The details and measured numbers are in
  docs/kb/tasks/M3/M3-CRE-643-hesk-vowbound-model.md and the sheet's "As built" section.
  - The build script finished: the KO settles instead of sinking, and the open wings cup forward with drooping cords,
    so the full span is 4.2 m and every frame keeps inside the default camera's right safe edge.
  - assets/creatures/hesk/ (GLB 1.58 MB, 13,602 triangles, 25 bones, 13 clips, six slots). The Blender job
    `creature_hesk` (verify: 7 identical), the import rule, PROVENANCE rows (their own commit).
  - game/creatures/hesk/hesk_battle.tscn and the creatures.json row `hesk` (`vowbound` true, `vowbound_pending`
    "M3-CRE-643", stand_in with height 2.4 and radius 0.6).
  - tools/validate_creatures.py accepts `vowbound_pending` (the coordinator's shared key, Nhoa's semantics), with a
    test in tools/tests/test_creatures.py.
  - Tests: tests/unit/test_creature_hesk_vowbound.gd (6), tests/integration/test_hesk_summon_path.gd (2).
  - Review shot `creature_hesk` (no baseline) and the portrait manifest row `hesk` (no PNG).

## In progress
- Nothing. The model has not been rendered (no rendering in this environment).

## Exact next step
1. The Lead merges this branch. For `vowbound_pending`, keep Nhoa's validator version (same key and semantics).
   Mine also has a test, `test_a_vowbound_modelled_ahead_of_its_row_says_so`; keep whichever test survives.
2. PC render: `creature_hesk` and her portrait (it joins the PNG bake).
3. Combat adds her vowbound.json row, skills and `VOWBOUND_HESK`. Then creatures.json gets `clip_by_skill` (cleanse →
   `cast`, Pass-Cord → `special`) and drops `vowbound_pending`.
4. Art reviews on the render: whether the knots read as the light (mask 1.0 vs 0.2 on the cord), the cords' white
   against the slate body, and the keth readable at the review distance.

## Known issues
- `test_creature_portraits.gd::test_every_manifest_creature_exists_with_a_provenance_row` is red for the portraits the
  PC has not baked: 20 PNGs now, Hesk's included. Nothing else fails.
- The KO's falling wings pass 4.35 m for about 0.2 s. Every path from the mantled wings to flat sweeps the arm
  through the horizontal. They lie at 3.83 m.
- The summon shot puts her feet under the HUD's bottom band, as it does Kahre's.

## Gates run
- `python3 tools/dev/verify_blender_builds.py --job creature_hesk`: ok, 7 identical.
- `python3 -m unittest tools.tests.test_creatures tools.tests.test_blender_builds`: 43 OK (GroundedClipsTest includes
  Hesk with no allow-list entry).
- `python3 tools/validate_data.py`: 0 errors (1 pre-existing warning: shrine_offering.glb).
  `python3 tools/taskboard.py --check`: ok.
- `gdlint game tests`, `gdformat -l 120 --check game tests`: clean.
- `godot --headless --path . --import`, then `run_tests.tscn` with XDG_DATA_HOME in the scratchpad:
  `--filter=creature` 60 run, 1 failed (portraits, above); `--filter=vowbound` 68 run, 0 failed; `--filter=hesk`
  8 run, 0 failed.
- Not run: screenshots and portraits (no rendering here); the coverage step (nothing under game/battle/ or
  game/progression/ changed).

## Files touched
- assets_src/creatures/hesk/build_hesk.py, assets_src/creatures/hesk/materials.json
- assets/creatures/hesk/hesk.glb, hesk.glb.import, materials/{bundle,cord,eye,head,plumage,ruff}.tres (new)
- assets/PROVENANCE.md (7 rows appended)
- tools/dev/blender_builds.json (the `creature_hesk` job appended), game/data/import/creatures.json (the folder)
- game/creatures/hesk/hesk_battle.tscn (new), game/data/creatures/creatures.json (the `hesk` row appended)
- tools/validate_creatures.py, tools/tests/test_creatures.py (`vowbound_pending`)
- tests/unit/test_creature_hesk_vowbound.gd, tests/integration/test_hesk_summon_path.gd (+ .uid, new)
- game/levels/_tests/creatures/shots/creature_hesk.tscn (new), tests/screenshots/shots.json (one entry appended)
- tools/portraits/portraits.json (one row appended)
- docs/kb/art/creatures/vowbound/hesk.md, docs/kb/tasks/M3/M3-CRE-643-hesk-vowbound-model.md, this handoff

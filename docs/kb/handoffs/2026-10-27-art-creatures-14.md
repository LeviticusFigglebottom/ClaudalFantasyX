# Handoff — art (creatures track) — 2026-10-27 #14

Ilun, Asha's Vowbound, as a creature model (M3-CRE-638). Branch `worktree-agent-a9ff131d70b099e46`, launched by the
creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY), branched from `claude/creatures`. Not pushed: the Lead merges
it and takes this task file over the claim already on `claude/creatures`.

## Done
- **M3-CRE-638, to review (art).** The details and measured numbers are in
  docs/kb/tasks/M3/M3-CRE-638-ilun-vowbound-model.md.
  - Design sheet docs/kb/art/creatures/vowbound/ilun.md (the first Vowbound sheet).
  - assets_src/creatures/ilun/ (build and materials) → assets/creatures/ilun/ (GLB 1.29 MB, 13,655 triangles,
    16 bones, 13 clips; seven material slots).
  - The Blender job `creature_ilun` (verify: 8 identical), the import rule, PROVENANCE rows.
  - game/creatures/ilun/ilun_battle.tscn and the creatures.json row `ilun` with `"vowbound": true`.
  - `CreatureModels.stand_in_overrides` now gives a Vowbound's stand-in its creature scene (the row with that id and
    `vowbound` true), so `BattleStage.stand_in_spec(&"ilun")` shows the model with no change to UI's or
    battle-presentation's files. tools/validate_creatures.py checks `vowbound`.
  - Tests: tests/unit/test_creature_ilun_vowbound.gd (4), a validator test in tools/tests/test_creatures.py.
  - Review shot `creature_ilun` and its stage scene (no baseline).

## In progress
- Nothing. The model has not been rendered (this environment may not render).

## Exact next step
1. The Lead merges this branch and runs the PC render for `creature_ilun`, `battle_vowbound_out`,
   `battle_choreo_summon` and `battle_choreo_vowbound_rise` (the three battle shots now show the model instead of the
   capsule, so their baselines move).
2. On that render, art reviews the points in the task's "For the first PC render" note: the net against the body,
   the spectral read (deep core, pale margins), the mantle from the default camera, the float on the summon frame.
3. Battle-presentation picks up the request in the task: choreo.json entry and summon entry clip `rise`, dismiss
   clip `dismiss`.
4. Menus picks up the request in the task: test_creature_portraits skips `vowbound` rows (Ilun has no bestiary page).

## Known issues
- `test_creature_portraits.gd::test_every_manifest_creature_exists_with_a_provenance_row` was already red for the
  portraits the PC has not baked; it now also names `ilun` ("has a portrait in the manifest"). The portrait row was
  skipped on purpose (the bestiary covers foes only); the fix is menus' (the request in the task).
- `tools.tests.test_screenshots` is red on `creature_wakefin_body` (no baseline, pre-existing); `creature_ilun` has
  no baseline either, by the brief, until the PC renders it.
- He is opaque (the creature shader has no alpha); true translucency is a follow-up decision after the render (a
  `creature_spectral` shader would need a per-slot shader in common/write_materials.py, which reruns every creature
  job).

## Gates run
- `python3 tools/dev/verify_blender_builds.py --job creature_ilun`: ok, 8 identical.
- `python3 -m unittest tools.tests.test_creatures tools.tests.test_blender_builds`: 41 tests OK (GroundedClipsTest
  includes Ilun with no allow-list entry).
- `python3 tools/validate_data.py`: 0 errors (1 pre-existing warning: shrine_offering.glb). `python3
  tools/taskboard.py --check`: ok.
- `gdlint game tests`, `gdformat -l 120 --check game tests`: clean.
- `godot --headless --path . --import`, then `run_tests.tscn` with XDG_DATA_HOME in the scratchpad:
  `--filter=creature` 46 run, 1 failed (test_creature_portraits, above); `--filter=vowbound` 54 run, 0 failed;
  `--filter=battle_stage` matches no file, so `--filter=battle` was run instead: 720 run, 0 failed.
- Not run: screenshots and portraits (no rendering in this environment); the coverage step (nothing under
  game/battle/ or game/progression/ changed).

## Files touched
- docs/kb/art/creatures/vowbound/ilun.md (new), docs/kb/art/creatures/pipeline.md (§5, a Vowbound note)
- assets_src/creatures/ilun/build_ilun.py, assets_src/creatures/ilun/materials.json (new)
- assets/creatures/ilun/ilun.glb, ilun.glb.import, materials/{body,cord,crest,eye,glass,membrane,net}.tres (new)
- assets/PROVENANCE.md (8 rows appended)
- tools/dev/blender_builds.json (the `creature_ilun` job appended), game/data/import/creatures.json (the folder)
- game/creatures/ilun/ilun_battle.tscn (new), game/creatures/creature_models.gd, game/data/creatures/creatures.json
- tools/validate_creatures.py, tools/tests/test_creatures.py
- tests/unit/test_creature_ilun_vowbound.gd (+ .uid, new)
- game/levels/_tests/creatures/shots/creature_ilun.tscn (new), tests/screenshots/shots.json (one entry appended)
- docs/kb/tasks/M3/M3-CRE-638-ilun-vowbound-model.md, this handoff

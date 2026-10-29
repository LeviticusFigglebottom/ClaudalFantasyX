# Handoff — art (creatures track) — 2026-10-27 #15

Kahre, Asha's Lightning Vowbound, as a creature model (M3-CRE-640). Worktree `agent-aff95178e46e68414`, launched by
the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY), branched from `claude/creatures`. Not pushed: the Lead
merges it (the claim is already on `claude/creatures`). Virel (M3-CRE-641) was built in parallel by another agent and
appends to the same shared files (creatures.json, blender_builds.json, PROVENANCE, shots.json, portraits.json,
game/data/import/creatures.json); every edit here is an append, so the merge is a matter of keeping both blocks.

## Done
- **M3-CRE-640, to review (art).** Details and measured numbers: docs/kb/tasks/M3/M3-CRE-640-kahre-vowbound-model.md.
  - Design sheet docs/kb/art/creatures/vowbound/kahre.md, with the framing check.
  - assets_src/creatures/kahre/ (build and materials) → assets/creatures/kahre/ (GLB 1.37 MB, 14,080 triangles,
    22 bones, 13 clips; seven slots).
  - The build solves every planted foot onto the water at every frame (`solve_legs`), so every clip's lowest vertex
    is 0.000 m, with no allow-list entry.
  - The Blender job `creature_kahre` (verify: 8 identical), the import rule, PROVENANCE rows.
  - game/creatures/kahre/kahre_battle.tscn and the creatures.json row `kahre` (`"vowbound": true`, stand_in yaw −90,
    **height 3.3, radius 0.75**). tools/validate_creatures.py now accepts `height` and `radius` in `stand_in`.
  - Tests: tests/unit/test_creature_kahre_vowbound.gd (4), tests/integration/test_kahre_summon_path.gd (2), a
    validator test in tools/tests/test_creatures.py.
  - Review shot `creature_kahre` and its stage scene (no baseline); portrait manifest row `kahre` (not baked).
  - pipeline.md: the `height`/`radius` keys and the default-camera framing rule for the Vowbound slot.

## In progress
- Nothing. The model has not been rendered (this environment may not render).

## Exact next step
1. The Lead merges this branch (append-only conflicts with Virel's branch: keep both rows or jobs) and runs the PC
   render for `creature_kahre` and the portrait bake for `kahre.png`.
2. Art reviews the render against the task's notes: the hide must read dark stone, not teal (lower `GLOW` in the
   build if it does); the anvil must read as iron on the side view; the mane and the struck star at 1.2.
3. Battle-presentation: the M3-CRE-638 clip request covers Kahre too (`rise`, `dismiss`), and
   `summon_cinematic.first_call_flags` has no `kahre` entry (story names the seen-flag if he should get the
   cinematic).

## Known issues
- `test_creature_portraits.gd::test_every_manifest_creature_exists_with_a_provenance_row` is red for the PNGs the PC
  has not baked (pre-existing); the `kahre` row adds `kahre.png` to that list.
- The default camera's top margin is passed by the raised head in `cast` and one frame of the Last Strike's rear;
  harmless during an action (the director plays the lead shot), noted in the sheet.
- A planted foot can slide up to about 8 mm sideways in the idle (the body's slight roll; the solve holds it in the
  leg's plane only). Not visible at battle distance.
- `tests/integration/test_ilun_summon_path.gd.uid` appeared untracked after the import (the Lead's file); left alone.

## Gates run
- `python3 tools/dev/verify_blender_builds.py --job creature_kahre`: ok, 8 identical.
- `python3 -m unittest tools.tests.test_creatures tools.tests.test_blender_builds`: 42 tests OK.
- `python3 tools/validate_data.py`: 0 errors (1 pre-existing warning: shrine_offering.glb).
  `python3 tools/taskboard.py --check`: ok.
- `gdlint game tests`, `gdformat -l 120 --check game tests`: clean.
- `godot --headless --path . --import`, then `run_tests.tscn` with XDG_DATA_HOME in the scratchpad: `--filter=kahre`
  6 run, 0 failed; `--filter=creature` 50 run, 1 failed (test_creature_portraits, above); `--filter=vowbound` 58 run,
  0 failed; `--filter=battle` 720 run, 0 failed.
- Not run: screenshots and portraits (no rendering here); the coverage step (nothing under game/battle/ or
  game/progression/ changed).

## Files touched
- docs/kb/art/creatures/vowbound/kahre.md (new), docs/kb/art/creatures/pipeline.md (a note appended)
- assets_src/creatures/kahre/build_kahre.py, assets_src/creatures/kahre/materials.json (new)
- assets/creatures/kahre/kahre.glb, kahre.glb.import, materials/{anvil,beak,body,eye,hammer,mane,strike}.tres (new)
- assets/PROVENANCE.md (8 rows appended)
- tools/dev/blender_builds.json (the `creature_kahre` job appended), game/data/import/creatures.json (the folder)
- game/creatures/kahre/kahre_battle.tscn (new), game/data/creatures/creatures.json (the `kahre` row appended)
- tools/validate_creatures.py, tools/tests/test_creatures.py
- tests/unit/test_creature_kahre_vowbound.gd, tests/integration/test_kahre_summon_path.gd (+ .uid, new)
- game/levels/_tests/creatures/shots/creature_kahre.tscn (new), tests/screenshots/shots.json, tools/portraits/portraits.json
  (one entry appended each)
- docs/kb/tasks/M3/M3-CRE-640-kahre-vowbound-model.md, this handoff

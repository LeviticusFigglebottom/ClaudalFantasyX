# Handoff — art (creatures track) — 2026-10-27 #17

Nhoa, the Rootlight, Asha's Ice Vowbound, as a creature model (M3-CRE-642). Branch `worktree-agent-a68ca47506828c52d`,
launched by the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY) and branched from `claude/creatures`. Not
pushed: the Lead merges it. A container restart interrupted the first agent after its WIP build script (554f5fbd).
This session ran that script, judged it sound, refined the folded poses and finished the task. Hesk (M3-CRE-643) and
Ethren (M3-CRE-644) were built in parallel on other branches and append to the same shared files.

## Done
- **M3-CRE-642 is in review (art).** The details and measured numbers are in
  docs/kb/tasks/M3/M3-CRE-642-nhoa-vowbound-model.md.
  - The design sheet docs/kb/art/creatures/vowbound/nhoa.md is marked built, with an "As built" section.
  - assets_src/creatures/nhoa/ (build and materials) builds assets/creatures/nhoa/: 14,820 triangles, 1,623 skinned
    mote beads, 28 bones, 13 clips and five slots.
  - The Blender job `creature_nhoa` (verify: 6 identical), the import rule and the PROVENANCE rows.
  - game/creatures/nhoa/nhoa_battle.tscn and the creatures.json row `nhoa`, with `"vowbound": true`, its own
    height and radius, and `vowbound_pending` (a new validate_creatures.py key: her vowbound.json row is Combat's).
  - Tests: tests/unit/test_creature_nhoa_vowbound.gd (5) and tests/integration/test_nhoa_summon_path.gd (2).
  - The review shot `creature_nhoa` (no baseline) and the portrait manifest row `nhoa` (no PNG).
  - pipeline.md notes `vowbound_pending` and the summon shot's bottom safe line.

## In progress
- Nothing. The model has not been rendered.

## Exact next step
1. The Lead merges this branch (all appends, plus the import list's alphabetical insert, and one validator change in
   validate_creatures.py and tools/tests/test_creatures.py). The Lead then runs the PC render for `creature_nhoa` and
   the portrait bake.
2. On that render, art reviews the task's "For the first PC render" points: whether the beads read as a figure or as
   noise, the dark body between them, the antler tips, the unlit shell, and the cold read through colour alone.
3. Combat adds her vowbound.json row (skills, the copy skill, `farewell_tide`). In the same change, creatures drops
   `vowbound_pending`, adds `clip_by_skill` and points the summon-path test at her own row.
4. Battle-presentation adds `first_call_flags.nhoa` and the `rise` / `dismiss` entry clips. Rendering and battle-vfx
   sanction and build Farewell-Tide's rising column; the task gives the strand positions at the contact.

## Known issues
- `test_creature_portraits.gd::test_every_manifest_creature_exists_with_a_provenance_row` is red for the portraits
  the PC has not baked, now including Nhoa's. Nothing else fails.
- On the summon shot the lower 0.45 m of her strands sit under the HUD's bottom band, as Kahre's feet do. Her top
  touches the top edge only on hit_b's peak and Farewell-Tide, and neither plays on that shot. On the default camera
  every frame is inside.

## Gates run
- `python3 tools/dev/verify_blender_builds.py --job creature_nhoa`: ok, 6 identical.
- `python3 -m unittest tools.tests.test_creatures tools.tests.test_blender_builds`: 43 tests OK. GroundedClipsTest
  includes Nhoa with no allow-list entry.
- `python3 tools/validate_data.py`: 0 errors, with 1 pre-existing warning (shrine_offering.glb).
- `python3 tools/taskboard.py --check`: ok.
- `gdlint game tests` and `gdformat -l 120 --check game tests`: clean.
- `godot --headless --path . --import`, then `run_tests.tscn` with XDG_DATA_HOME in the scratchpad:
  - `--filter=creature`: 59 run, 1 failed (test_creature_portraits, above).
  - `--filter=vowbound`: 67 run, 0 failed.
  - `--filter=nhoa`: 7 run, 0 failed.
- Not run:
  - screenshots and portraits (no rendering here);
  - the coverage step (nothing under game/battle/ or game/progression/ changed);
  - `--filter=battle` (outside the requested gate; only creatures.json data and the validator changed).

## Files touched
- docs/kb/art/creatures/vowbound/nhoa.md (as built), docs/kb/art/creatures/pipeline.md (one note)
- assets_src/creatures/nhoa/build_nhoa.py (the bow refined), assets_src/creatures/nhoa/materials.json
- assets/creatures/nhoa/nhoa.glb, nhoa.glb.import, materials/{antler,body,eye,motes,shell}.tres (new)
- assets/PROVENANCE.md (6 rows appended)
- tools/dev/blender_builds.json (the `creature_nhoa` job appended), game/data/import/creatures.json (the folder)
- game/creatures/nhoa/nhoa_battle.tscn (new), game/data/creatures/creatures.json (the `nhoa` row appended)
- tools/validate_creatures.py and tools/tests/test_creatures.py (`vowbound_pending`)
- tests/unit/test_creature_nhoa_vowbound.gd and tests/integration/test_nhoa_summon_path.gd (+ .uid, new)
- game/levels/_tests/creatures/shots/creature_nhoa.tscn (new), tests/screenshots/shots.json (one entry appended)
- tools/portraits/portraits.json (one row appended)
- docs/kb/tasks/M3/M3-CRE-642-nhoa-vowbound-model.md, this handoff

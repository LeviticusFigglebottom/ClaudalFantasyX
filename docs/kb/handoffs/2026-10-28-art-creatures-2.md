# Handoff: creatures track (art), 2026-10-28 #2: the six Vowbound held forms (worktree agent)

This is a worktree branch, launched by the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY). It is not pushed.
The Lead merges it and records the claim.

## Done
- **M3-CRE-647**, ready for review (art). The details are in docs/kb/tasks/M3/M3-CRE-647-vowbound-held-forms.md.
  - `write_materials.py` writes a `materials_held/` set from an optional `held` block: glimmer_bound becomes
    glimmer_held at the same energy, steady. All six Vowbound have the block.
  - Each of the six builds has a `release` clip of 3.3–3.5 s. It opens, holds, then lifts the form up and back, ending
    at peace. The six GLBs were rebuilt, and every other clip is unchanged.
  - Six `<id>_held_battle.tscn` scenes, each the same GLB with `CreatureActor.material_dir`.
  - Six `<id>_held` rows in creatures.json: KO `release`, a `release` phase with `hold`, yaw 90.
  - A new phase key, `hold`, in the actor and the validator.
  - Tests: the Godot unit test `test_creature_vowbound_held.gd`, and `release` added to each Vowbound test.
  - Six review shots and six portrait manifest rows, none rendered.
  - Docs: pipeline.md §5, act3_roster.md, and each sheet's "As built: the held form".
- **Verify:** all 53 creature jobs that use `assets_src/creatures/common/**` are byte-identical, including the six
  rebuilt Vowbound jobs and their `materials_held/` outputs.
- **Gates:** both unittest suites (test_creatures, test_blender_builds), validate_data, taskboard --check, gdlint and
  gdformat pass. On Godot, `--filter=vowbound` passes (83 run). `--filter=creature` has 1 failure, the known
  test_creature_portraits missing-PNG one, which now also lists the six `_held` PNGs.

## In progress
- Nothing.

## Exact next step
1. Merge the branch.
2. RENDER-REQUEST on the PC: `creature_{ilun,kahre,virel,hesk,nhoa,ethren}_held`, plus the six `_held` portraits.
3. In the renders, check:
   - the held light reads cool cyan (`#7FC6D9`), not the ally's teal;
   - the idle pose frames like the ally's.
4. Combat and the chapter designer add the Ch20 enemies.json rows (`model` = the held scene).
5. Battle VFX adds the held-to-lift hue lerp and the rising motes at the release.

## Known issues
- The release's light change (to glimmer_lift) is not in the model or the actor. It belongs to presentation and VFX.
- Nhoa's strands are short, so her rising motes read as an upturned hem more than a column. The VFX column carries
  the rise.
- The preview strips came from a numpy/PIL skinner reading the GLBs. Nothing was rendered in Godot.

## Files touched
- `assets_src/creatures/common/write_materials.py`
- `assets_src/creatures/{ilun,kahre,virel,hesk,nhoa,ethren}/{materials.json,build_<id>.py}`
- `assets/creatures/<id>/<id>.glb`, `assets/creatures/<id>/materials_held/*.tres` (the six ids)
- `assets/PROVENANCE.md`, `tools/dev/blender_builds.json`
- `game/creatures/creature_actor.gd`, `game/creatures/<id>/<id>_held_battle.tscn`
- `game/data/creatures/creatures.json`
- `tools/validate_creatures.py`, `tools/tests/test_creatures.py`
- `tests/unit/test_creature_vowbound_held.gd`, `tests/unit/test_creature_<id>_vowbound.gd`
- `game/levels/_tests/creatures/shots/creature_<id>_held.tscn`, `tests/screenshots/shots.json`,
  `tools/portraits/portraits.json`
- `docs/kb/art/creatures/pipeline.md`, `docs/kb/art/creatures/act3_roster.md`,
  `docs/kb/art/creatures/vowbound/*.md`, the task file, this handoff

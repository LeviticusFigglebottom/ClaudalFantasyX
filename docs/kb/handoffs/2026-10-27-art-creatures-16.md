# Handoff — art (creatures track) — 2026-10-27 #16

Virel, the Kite-Serpent, Asha's Fire Vowbound, as a creature model (M3-CRE-641). Branch
`worktree-agent-ab22a89553400c234`, launched by the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY), branched
from `claude/creatures`. Not pushed: the Lead merges it. Kahre (M3-CRE-640) was built in parallel on another branch
and appends to the same shared files (creatures.json, blender_builds.json, PROVENANCE.md, shots.json,
portraits.json); every edit here is an append at the end of its block, so the merge is a plain both-sides append.

## Done
- **M3-CRE-641, to review (art).** The details and measured numbers are in
  docs/kb/tasks/M3/M3-CRE-641-virel-vowbound-model.md.
  - Design sheet docs/kb/art/creatures/vowbound/virel.md.
  - assets_src/creatures/virel/ (build and materials) → assets/creatures/virel/ (GLB 1.05 MB, 12,158 triangles,
    16 bones, 13 clips; five material slots).
  - The Blender job `creature_virel` (verify: 6 identical), the import rule, PROVENANCE rows.
  - game/creatures/virel/virel_battle.tscn and the creatures.json row `virel` with `"vowbound": true`; CreatureModels
    attaches it with no code change (M3-CRE-638's hook).
  - Tests: tests/unit/test_creature_virel_vowbound.gd (4), tests/integration/test_virel_summon_path.gd (2).
  - Review shot `creature_virel` (no baseline) and the portrait manifest row `virel` (no PNG).

## In progress
- Nothing. The model has not been rendered (this environment may not render).

## Exact next step
1. The Lead merges this branch (after or before Kahre's: both append) and runs the PC render for `creature_virel` and
   the portrait bake (her PNG joins the 17 already requested).
2. On that render, art reviews the points in the task's "For the first PC render" note: the seams against the cloth,
   the lit-through cloth, the frame, the key on the summon frame, and whether the still teal seams read as fire held
   still.
3. UI picks up the request in the task: a `stand_ins.virel` row in battle_sandbox.json (height 2.6) so the damage
   numbers and VFX anchors sit on her.
4. Battle-presentation picks up the requests in the task: `first_call_flags.virel` (her B16 first-call cinematic),
   and the `rise` / `dismiss` entry clips (as for Ilun, M3-CRE-639).
5. Battle-vfx: Kite Flare's and Flare Line's fire is the effect's (her form stays `glimmer_bound`); the task gives
   Flare Line's line end points at the contact.

## Known issues
- `test_creature_portraits.gd::test_every_manifest_creature_exists_with_a_provenance_row` is red for the portraits the
  PC has not baked: 18 PNGs now (the 17 known and Virel's). Nothing else fails.
- Flare Line's release touches the default camera's right safe edge for a frame (−0.002 of the screen, under 3 px);
  everything else is inside it (the task has the margins).
- `tests/integration/test_ilun_summon_path.gd.uid` appeared untracked after the import (the Lead's commit a785a613
  added the test without it). Not mine; left uncommitted.

## Gates run
- `python3 tools/dev/verify_blender_builds.py --job creature_virel`: ok, 6 identical.
- `python3 -m unittest tools.tests.test_creatures tools.tests.test_blender_builds`: 41 tests OK (GroundedClipsTest
  includes Virel with no allow-list entry).
- `python3 tools/validate_data.py`: 0 errors (1 pre-existing warning: shrine_offering.glb). `python3
  tools/taskboard.py --check`: ok.
- `gdlint game tests`, `gdformat -l 120 --check game tests`: clean.
- `godot --headless --path . --import`, then `run_tests.tscn` with XDG_DATA_HOME in the scratchpad:
  `--filter=creature` 50 run, 1 failed (test_creature_portraits, above); `--filter=vowbound` 58 run, 0 failed;
  `--filter=virel` 6 run, 0 failed; `--filter=battle` 720 run, 0 failed.
- Not run: screenshots and portraits (no rendering in this environment); the coverage step (nothing under
  game/battle/ or game/progression/ changed).

## Files touched
- docs/kb/art/creatures/vowbound/virel.md (new)
- assets_src/creatures/virel/build_virel.py, assets_src/creatures/virel/materials.json (new)
- assets/creatures/virel/virel.glb, virel.glb.import, materials/{cord,key,sail,seam,spar}.tres (new)
- assets/PROVENANCE.md (6 rows appended)
- tools/dev/blender_builds.json (the `creature_virel` job appended), game/data/import/creatures.json (the folder)
- game/creatures/virel/virel_battle.tscn (new), game/data/creatures/creatures.json (the `virel` row appended)
- tests/unit/test_creature_virel_vowbound.gd, tests/integration/test_virel_summon_path.gd (+ .uid, new)
- game/levels/_tests/creatures/shots/creature_virel.tscn (new), tests/screenshots/shots.json (one entry appended)
- tools/portraits/portraits.json (one row appended)
- docs/kb/tasks/M3/M3-CRE-641-virel-vowbound-model.md, this handoff

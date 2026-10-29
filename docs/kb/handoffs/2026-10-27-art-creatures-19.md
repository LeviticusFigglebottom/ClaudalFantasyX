# Handoff — art (creatures track) — 2026-10-27 #19

Ethren, the Level Saint, Asha's Glimmer Vowbound (bound Ch13), as a creature model (M3-CRE-644). Branch
`worktree-agent-a6fd4ee605a76cf01`, launched by the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY), branched
from `claude/creatures` at ec4a3bbd. Not pushed: the Lead merges it. Nhoa (M3-CRE-642) and Hesk (M3-CRE-643) were
built in parallel and append to the same shared files; every edit here is an append at the end of its block (the
import list insert is alphabetical), so the merges are both-sides appends.

## Done
- **M3-CRE-644, to review (art).** Details and numbers in docs/kb/tasks/M3/M3-CRE-644-ethren-vowbound-model.md; the
  as-built design in docs/kb/art/creatures/vowbound/ethren.md ("As built").
  - assets_src/creatures/ethren/ (build, materials) → assets/creatures/ethren/ (14,406 triangles, 27 bones, 13 clips,
    GLB 1.53 MB, seven slots; the veil its own mesh on its own bone).
  - Blender job `creature_ethren` (8 identical), import rule folder, PROVENANCE rows.
  - game/creatures/ethren/ethren_battle.tscn; the creatures.json row `ethren` with `vowbound` true and
    `vowbound_pending` "M3-CRE-644"; tools/validate_creatures.py's minimal `vowbound_pending` rule and its test (the
    Lead keeps Nhoa's implementation on merge; same key and semantics).
  - Tests: tests/unit/test_creature_ethren_vowbound.gd (6), tests/integration/test_ethren_summon_path.gd (2).
  - Review shot `creature_ethren` (no baseline) and portrait row `ethren` (no PNG).

## In progress
- Nothing. The model has not been rendered (no rendering in this environment).

## Exact next step
1. The Lead merges this branch (keeping one `vowbound_pending` implementation in validate_creatures.py and
   test_creatures.py), then the PC renders `creature_ethren` and bakes his portrait.
2. Art reviews on that render the points in the task's Notes (lacquer gloss, seams as inner light, the halo's
   crescent from the default camera, the veil, the ring) and measures the gold on the summon frame with the palette
   tool (numpy estimate 1.35% max).
3. Combat writes his vowbound.json row; then drop `vowbound_pending` and add `clip_by_skill`.

## Known issues
- `test_creature_portraits.gd::test_every_manifest_creature_exists_with_a_provenance_row` is red for the 20 portraits
  the PC has not baked (the 19 known and Ethren's). Nothing else fails.
- The summon shot puts his lower robe under the HUD's bottom band, as for Kahre (grounded-height figures).
- `rise`'s start and `dismiss`'s end are 0.005 of the screen inside the default camera's right safe edge.

## Gates run
- `verify_blender_builds.py --job creature_ethren`: ok, 8 identical.
- `python3 -m unittest tools.tests.test_creatures tools.tests.test_blender_builds`: 43 OK.
- `validate_data.py`: 0 errors (1 pre-existing warning, shrine_offering.glb). `taskboard.py --check`: ok.
- `gdlint game tests`, `gdformat -l 120 --check game tests`: clean.
- `godot --headless --path . --import`, then run_tests.tscn (XDG_DATA_HOME in the scratchpad): `--filter=creature` 60
  run, 1 failed (portraits, above); `--filter=vowbound` 68 run, 0 failed; `--filter=ethren` 8 run, 0 failed.
- Not run: screenshots, portraits, renders (not allowed here); coverage (nothing under game/battle/ or
  game/progression/ changed).

## Files touched
- docs/kb/art/creatures/vowbound/ethren.md, docs/kb/tasks/M3/M3-CRE-644-ethren-vowbound-model.md, this handoff
- assets_src/creatures/ethren/build_ethren.py, materials.json (new)
- assets/creatures/ethren/ethren.glb, ethren.glb.import, materials/{gold,halo,lacquer,lacquer_red,ring,seam,veil}.tres
- assets/PROVENANCE.md (8 rows appended), tools/dev/blender_builds.json (job appended), game/data/import/creatures.json
- game/creatures/ethren/ethren_battle.tscn, game/data/creatures/creatures.json (row appended)
- tools/validate_creatures.py, tools/tests/test_creatures.py (`vowbound_pending`)
- tests/unit/test_creature_ethren_vowbound.gd, tests/integration/test_ethren_summon_path.gd (+ .uid)
- game/levels/_tests/creatures/shots/creature_ethren.tscn, tests/screenshots/shots.json, tools/portraits/portraits.json

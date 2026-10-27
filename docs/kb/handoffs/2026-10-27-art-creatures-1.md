# Handoff — character (creatures) — 2026-10-27 #1

Worktree agent `worktree-agent-a914f3f68a1829757`, launched by the creatures Lead session for M3-CRE-621. Not pushed:
the Lead merges this branch and records it in `docs/kb/handoffs/live/creatures.md`.

## Done
- M3-CRE-621: the Mangrove Drowner (Act II, Ch10 boss) built from its sheet through the creature pipeline: build
  script and materials, the Blender job (identical on rebuild), PROVENANCE rows, the import rule, the battle scene,
  the creatures.json row (phase `uprooted` with `hide_after: ["Stump"]`, `idle_risen` and the risen strikes),
  a unit test, and two review shots viewed and approved. Task file
  `docs/kb/tasks/M3/M3-CRE-621-mangrove-drowner.md` (status review, reviewer art).

## In progress
Nothing.

## Exact next step
Art review of `creature_mangrove_drowner` and `creature_mangrove_drowner_risen` against the sheet (rule 1:
judge whether the six-legged risen stance reads as a root cage, not a spider). Then the next Act II boss build
from M3-CRE-620's sheets (the Lamp Engine, Ch11).

## Known issues
- No enemies.json row: no Act II encounter exists. The encounter designers add it, with `model` and a phase
  `uprooted` at 50% HP.
- The snagged motes and the drag's telegraph are VFX (not requested yet); the break part needs a charge skill.
- The core reads a little smooth and glassy under the noon review light.

## Files touched
assets_src/creatures/mangrove_drowner/**, assets/creatures/mangrove_drowner/**, game/creatures/mangrove_drowner/**,
game/data/creatures/creatures.json, game/data/import/creatures.json, tools/dev/blender_builds.json,
assets/PROVENANCE.md, tests/unit/test_creature_actor.gd, tests/screenshots/shots.json,
tests/screenshots/baselines/{baselines.json,creature_mangrove_drowner.png,creature_mangrove_drowner_risen.png},
game/levels/_tests/creatures/shots/creature_mangrove_drowner{,_risen}.tscn, docs/kb/art/creatures/act2/README.md,
docs/kb/tasks/M3/M3-CRE-621-mangrove-drowner.md.

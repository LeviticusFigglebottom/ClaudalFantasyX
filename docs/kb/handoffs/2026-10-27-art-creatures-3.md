# Handoff — character (creatures) — 2026-10-27 #2

Worktree agent `worktree-agent-af5577379119314f8`, launched by the creatures Lead session for M3-CRE-623. Not pushed:
the Lead merges this branch and records it in `docs/kb/handoffs/live/creatures.md`.

## Done
- M3-CRE-623: the Lamp Engine (Act II, Ch11 boss) built from its sheet through the creature pipeline: build script
  and materials, the Blender job (identical on rebuild), PROVENANCE rows, the import rule, the battle scene, the
  creatures.json row (phase `opened`: `phase_change`, `idle_opened` and the open strikes), a unit test, and two
  review shots added to the manifest. No render in this environment (human directive): the model was checked
  numerically from the GLB (bounds per clip, feet, peak times, lamp clearances, core visibility closed and open,
  colours against the palette). The numbers are in `docs/kb/tasks/M3/M3-CRE-623-lamp-engine.md` (status review,
  reviewer art).

## In progress
Nothing.

## Exact next step
On the PC runner: capture `creature_lamp_engine` and `creature_lamp_engine_opened`
(`HYMN_SHOTS=creature_lamp_engine,creature_lamp_engine_opened`), view them against the sheet, and add their
baselines; check the portrait on the default lights. Then art review.

## Known issues
- No enemies.json row: no Act II encounter exists. The encounter designers add it, with `model` and a phase `opened`
  at 50% HP.
- Break parts (the three rings) need a charge skill and per-ring whole/broken meshes; not wired.
- The cast's lamps brightening in sequence, the KO's core going dark and its `glimmer_lift` motes are VFX.
- The KO starts from the open pose (a boss falls in phase 2); a KO in phase 1 opens the rings in the 0.12 s blend.
- The creature kit exports every clip one frame late (GLB times = authored + 1/30 s), for every creature. Not
  changed here (a kit change rebuilds every creature).

## Files touched
assets_src/creatures/lamp_engine/**, assets/creatures/lamp_engine/**, game/creatures/lamp_engine/**,
game/data/creatures/creatures.json, game/data/import/creatures.json, tools/dev/blender_builds.json,
assets/PROVENANCE.md, tests/unit/test_creature_actor.gd, tests/screenshots/shots.json,
game/levels/_tests/creatures/shots/creature_lamp_engine{,_opened}.tscn, docs/kb/art/creatures/act2/README.md,
docs/kb/tasks/M3/M3-CRE-623-lamp-engine.md, this handoff.

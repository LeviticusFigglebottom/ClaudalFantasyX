# Handoff: creatures track (art), 2026-10-27, Act II regulars and variants (worktree agent)

Branch `worktree-agent-aac484d16edeb5a00`, launched by the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY).
Not pushed. The Lead merges it and records the claim.

## Done
- **M3-CRE-628, three Act II regulars and four variants built**, to review (art). The numbers are in
  docs/kb/tasks/M3/M3-CRE-628-act2-regulars-ch12-16-and-variants.md.
  - `ridge_lynx`: 6,988 triangles and 27 bones. Its legs are posed by a planar two-bone solve. The pounce has its
    contact at 0.7 s, and the KO limps two steps and lies down on its side.
  - `cord_moth`: 4,144 triangles and 12 bones, hovering at 1.25 m. Its knot rows are seeded, abstract groups on raised
    cord strips (the `knot` slot). The cast tips it up toward the party with its wings open.
  - `glass_skate`: 2,624 triangles and 14 bones, a flat disc with eyes on turrets and a glossy pale back. It has its
    own `hit_b`.
  - The variants:
    - `root_crab`: the reef crab's new `LEG_KNEE`/`LEG_FOOT`, bark and lichen, and a knot of roots;
    - `fen_leech`: new sail leech parameters, ribbon-flat and 2.74 m long;
    - `scree_crawler`: new slag tortoise parameters, faceted scree and a tufted skin;
    - `rim_crawler`: a palette variant, chalk with black joints and dimmer wounds.
- For each creature: the Blender job, materials, PROVENANCE rows (their own commit), the import rule, the
  `.glb.import` script line, the battle scene, the creatures.json row (no enemies.json rows, no phases), and the shot
  entry (no baseline).
- One unit test per regular and one for the variants, all in tests/unit/test_creature_actor.gd.
- **Verify.** Every new job is identical, and so is every touched base job: reef_crab, wallcrab, wreck_crab,
  sail_leech and slag_tortoise. The tide crawler's build is untouched.

## In progress
- Nothing. The seven shots wait for the PC.

## Exact next step
1. Merge the branch, then RENDER-REQUEST the seven shots on the PC: `creature_ridge_lynx`, `creature_cord_moth`,
   `creature_glass_skate`, `creature_root_crab`, `creature_fen_leech`, `creature_scree_crawler` and
   `creature_rim_crawler`.
2. View them, approve the baselines, and fill the task's Review log. The task's "For the first PC render" list says
   what to judge, in particular whether the moth's knot rows and the skate's nearly clear back read at battle
   distance.

## Known issues
- Inherited from the bases' unchanged clips:
  - the reef crab's and tide crawler's leg tips and claws dip under the floor (most in the KO);
  - the slag tortoise's claws sit 4.5 cm under the floor at rest;
  - the reef crab's weak-point crack glows faintly (an emission mask of 0.16 at most), and the root crab inherits it.
- The glass skate is 0.16 m tall, so its encounter row needs a low battle `height`.
- VFX not modelled, by the sheets: the lynx's breath steam and the snow from its yowl, the skate's sand cloud, and the
  wounds' `glimmer_held` motes.

## Files touched
- **New:**
  - `assets_src/creatures/{ridge_lynx,cord_moth,glass_skate,root_crab,fen_leech,scree_crawler,rim_crawler}/`;
  - `assets/creatures/<same seven>/`;
  - `game/creatures/<same seven>/<id>_battle.tscn`;
  - `game/levels/_tests/creatures/shots/creature_<same seven>.tscn`;
  - `docs/kb/tasks/M3/M3-CRE-628-act2-regulars-ch12-16-and-variants.md`.
- **Base builds (parameters, outputs unchanged):**
  - `assets_src/creatures/reef_crab/build_reef_crab.py`;
  - `assets_src/creatures/sail_leech/build_sail_leech.py`;
  - `assets_src/creatures/slag_tortoise/build_slag_tortoise.py`.
- **Shared:**
  - `assets/PROVENANCE.md` (24 rows);
  - `tools/dev/blender_builds.json` (7 jobs);
  - `game/data/import/creatures.json` (7 folders);
  - `game/data/creatures/creatures.json` (7 rows);
  - `tests/screenshots/shots.json` (7 shots);
  - `tests/unit/test_creature_actor.gd` (4 tests);
  - `docs/kb/art/creatures/act2/README.md` (7 rows and a paragraph).

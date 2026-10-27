# Handoff: creatures track (art), 2026-10-27, the Avalanche Ram (worktree agent)

Branch `worktree-agent-a1f335e70d81fd58f`, launched by the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY).
Not pushed. The Lead merges it and records the claim.

## Done
- **M3-CRE-624, the Avalanche Ram built**, to review (art):
  - `assets_src/creatures/avalanche_ram/`: 15,179 triangles (budget 16k) and 38 bones.
  - Clips: idle, attack (contact 0.75 s), cast (0.9 s), hit (peak 0.10 s) and ko (kneel, then lie down).
  - The materials, the Blender job (verify: 5 identical), PROVENANCE rows, the import rule, the battle scene, the
    creatures.json row and a unit test.
  - Shot `creature_avalanche_ram` in the manifest, with no baseline.
  - The act2 README and the task file.
- Checked without renders:
  - each clip measured from the GLB (skinned at every baked frame): nothing below y 0, hooves at y 0 at the clips'
    ends, the head at 2.86 m (top 3.08 m) and each clip's peak time;
  - vertex colours against palette.json;
  - a PIL silhouette sketch in the scratchpad, used only to judge proportions (not an engine render, not committed).

## In progress
- Nothing. The shot waits for the PC.

## Exact next step
1. RENDER-REQUEST `creature_avalanche_ram` on the PC once this branch is merged. View it, approve the baseline, and
   fill the task's Review log.
2. Judge the notes in the task file on the render: the chest front's smoothness, the raised fore's woolly upper leg
   and the muzzle's length.

## Known issues
- The KO lowers `body` (0.5 m), not `root`. tools/tests' grounded-KO check reads the root; the real check is the
  GLB measurement (nothing below y 0).
- VFX not modelled, by the sheet: breath steam, the bellow's snow (the field hazard), ice cracking off on a hit, and
  `glimmer_held` shed from the partings.

## Files touched
assets_src/creatures/avalanche_ram/{build_avalanche_ram.py,materials.json}, assets/creatures/avalanche_ram/**,
assets/PROVENANCE.md (5 rows), tools/dev/blender_builds.json (one job), game/data/import/creatures.json (one folder),
game/data/creatures/creatures.json (one row), game/creatures/avalanche_ram/avalanche_ram_battle.tscn,
game/levels/_tests/creatures/shots/creature_avalanche_ram.tscn, tests/screenshots/shots.json (one shot),
tests/unit/test_creature_actor.gd (one test), docs/kb/art/creatures/act2/README.md,
docs/kb/tasks/M3/M3-CRE-624-avalanche-ram.md.

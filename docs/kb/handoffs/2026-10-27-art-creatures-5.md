# Handoff: creatures track (art), 2026-10-27, the Wakefin (worktree agent)

Branch `worktree-agent-a1b527f817c65c013`, launched by the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY).
Not pushed. The Lead merges it and records the claim.

## Done
- **M3-CRE-626, the Wakefin built**, to review (art):
  - `assets_src/creatures/wakefin/`: 11,128 triangles (budget 14k) and 20 bones.
  - The waterline is at y 0. The spine axis (the root) sits at y −0.38, so the blade's root meets the water.
  - Clips: idle (the circle, in place), attack (the breach and sweep, contact 0.8 s), cast (the dive, contact 1.5 s),
    hit (peak 0.10 s) and ko (it rolls belly-up and floats at the surface).
  - The materials (`body`, `seam`, `fin`, `eye`), the Blender job (verify: 5 identical), PROVENANCE rows (their own
    commit), the import rule, the battle scene, the creatures.json row (yaw 60, dark portrait rim 2.8 and kick 1.8),
    and a unit test.
  - Shot `creature_wakefin` in the manifest, with no baseline.
  - The act2 README row and paragraph, and the task file with the measured table.
- Checked without renders:
  - each clip measured from the GLB (skinned at every baked frame): bounds, the blade's top, peak times, and the KO's
    end at −0.46..+0.79;
  - vertex colours against palette.json: nothing below the albedo floor;
  - a PIL silhouette sketch in the scratchpad, used only to judge proportions (not an engine render, not committed).

## In progress
- Nothing. The shot waits for the PC.

## Exact next step
1. RENDER-REQUEST `creature_wakefin` on the PC once this branch is merged. View it, approve the baseline, and fill
   the task's Review log.
2. Judge the task file's "For the first PC render" notes, in particular whether the stage floor cuts the body
   cleanly at the blade's root, and the portrait (the submerged body is in frame).

## Known issues
- The body is below y 0 by design. An arena without an opaque water plane at y 0 would show it; the Ch15 barge arena
  needs one.
- VFX not modelled, by the sheet: the sea-glow wake and its brightening (the attack's telegraph), the dive's dark
  water and surfacing ring, the wake fading on the KO, and `glimmer_held` motes from the wounds.

## Files touched
assets_src/creatures/wakefin/{build_wakefin.py,materials.json}, assets/creatures/wakefin/**, assets/PROVENANCE.md (5
rows), tools/dev/blender_builds.json (one job), game/data/import/creatures.json (one folder),
game/data/creatures/creatures.json (one row), game/creatures/wakefin/wakefin_battle.tscn,
game/levels/_tests/creatures/shots/creature_wakefin.tscn, tests/screenshots/shots.json (one shot),
tests/unit/test_creature_actor.gd (one test), docs/kb/art/creatures/act2/README.md,
docs/kb/tasks/M3/M3-CRE-626-wakefin.md.

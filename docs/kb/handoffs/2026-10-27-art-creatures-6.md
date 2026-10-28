# Handoff: creatures track (art), 2026-10-27, four Act II regulars (worktree agent)

Branch `worktree-agent-a754445358ec40463`, launched by the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY).
Not pushed. The Lead merges it and records the claim.

## Done
- **M3-CRE-627, four Act II regulars built** (review: art). One commit per creature, then the PROVENANCE rows, then
  the docs. Every creature has its materials, Blender job, import-rule folder, battle scene, creatures.json row, unit
  test and shot entry (no baseline):
  - **tannin archer** (Ch10): 4,464 triangles, 10 bones. It lies on a mangrove root; contacts 0.55 and 0.9 s.
  - **gallery ray** (Ch11, a flier): 4,104 triangles, 12 bones, hover 1.4 m; contacts 0.6 and 0.9 s. The KO drops the
    root by the hover.
  - **rime urchin** (Ch11): 8,822 triangles, 10 bones (eight spine sectors); contacts 0.5 and 0.8 s.
  - **conduit crawler** (Ch11, a Lit Age construct): 4,752 triangles, 18 bones, its light `glimmer_bound` (steady);
    contacts 0.45 and 1.0 s.
- `verify_blender_builds.py --job creature_<id>` is identical for all four.
- The act2 README has four rows and a paragraph, and the task file has the measured tables (per clip: bounds, peaks,
  feet and KO ends, colours against the palette).
- Checked without renders, by GLB skinning at every frame and PIL silhouette sketches in the scratchpad (not
  committed).

## In progress
- Nothing. The shots wait for the PC.

## Exact next step
1. Once this branch is merged, RENDER-REQUEST `creature_tannin_archer`, `creature_gallery_ray`, `creature_rime_urchin`
   and `creature_conduit_crawler` on the PC. View them, approve the baselines, and fill the task's Review log.
2. Art settles the two palette-limit notes in the task file (`spawn_wound` on non-spawn weak points, as every sheet
   asks; `foam_white` in the urchin's rime).

## Known issues
- CreatureStage doesn't apply `hover`, so the ray's shot shows it at its origin with the floor through the disc, as
  with the other fliers' shots.
- The crawler's light dimming on the KO isn't modelled (the shader's emission is static). That needs VFX or an actor
  fade.
- VFX not modelled, by the sheets: the archer's jet, the ray pool's flare, the urchin's frost bloom and its rime
  melting.

## Files touched
- `assets_src/creatures/{tannin_archer,gallery_ray,rime_urchin,conduit_crawler}/{build_<id>.py,materials.json}`
- `assets/creatures/<id>/**` (the GLB, its `.import` and the materials)
- `assets/PROVENANCE.md` (17 rows)
- `tools/dev/blender_builds.json` (four jobs)
- `game/data/import/creatures.json` (four folders)
- `game/data/creatures/creatures.json` (four rows)
- `game/creatures/<id>/<id>_battle.tscn`
- `game/levels/_tests/creatures/shots/creature_<id>.tscn`
- `tests/screenshots/shots.json` (four entries)
- `tests/unit/test_creature_actor.gd` (a shared check, four tests)
- `docs/kb/art/creatures/act2/README.md`
- `docs/kb/tasks/M3/M3-CRE-627-act2-regulars-ch10-11.md`
- this handoff

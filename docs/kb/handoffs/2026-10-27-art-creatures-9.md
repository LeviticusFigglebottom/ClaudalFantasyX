# Handoff: creatures track (art), 2026-10-27, every creature on the floor (worktree agent)

Branch `worktree-agent-acecbace78996e4ba`, launched by the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY).
Not pushed. The Lead merges it and records the claim. (Named -9: `2026-10-27-art-creatures-8.md` is M3-CRE-631's.)

## Done
- **M3-CRE-632**, to review (art). The before/after table, the allow-list and the shot list are in
  docs/kb/tasks/M3/M3-CRE-632-ground-every-creature.md.
  - `common/grounding.py` gains a root limb, weighted turn axes, per-clip limbs, a mesh list and (already there) a
    floor for fliers; the M3-CRE-631 GLBs rebuild identical.
  - 19 GLBs rebuilt: scuttler, Cinder Matron, shoal skipper, raid hound, Drownbell, bottle hermit, vein sparker, spawn
    polyp, wall polyp, tower limpet, glassfry, lamp engine, oil slug, spar-wraith, flue moth, ashwing, gull harrier,
    stormgull, squall wing. Every one is at or above −0.005 m in every clip (fliers with their hover).
  - `GroundedClipsTest` covers every creature in creatures.json less `ALLOW` (hullgnaw, lantern eel, Mangrove
    Drowner, Undertow's Reach, Wakefin, tannin archer, each citing its sheet), fliers with their hover. About 8 s.
  - Verify: all 42 creature jobs identical.

## In progress
- Nothing. The renders wait for the PC.

## Exact next step
1. Merge the branch.
2. RENDER-REQUEST on the PC for the shots listed in the task file (19 creature shots plus the Drownbell's extras and
   the `battle_choreo_*` shots).
3. View them, re-approve the baselines, and fill the task's Review log.

## Known issues
- The oil slug rests 5 cm above the floor (not under it, so the test passes); see the task's "Found, not fixed".
- The spar-wraith's deck-anchored shrouds sit at −0.004 m at rest (inside the tolerance).

## Files touched
- assets_src/creatures/common/grounding.py
- assets_src/creatures/{scuttler,cinder_matron,shoal_skipper,raid_hound,drownbell,bottle_hermit,vein_sparker,
  spawn_polyp,wall_polyp,tower_limpet,glassfry,lamp_engine,oil_slug,spar_wraith,flue_moth,ashwing,gull_harrier,
  stormgull,squall_wing}/build_*.py and their assets/creatures/<id>/<id>.glb
- tools/tests/test_creatures.py, docs/kb/art/creatures/pipeline.md, assets/PROVENANCE.md
- docs/kb/tasks/M3/M3-CRE-632-ground-every-creature.md, this handoff

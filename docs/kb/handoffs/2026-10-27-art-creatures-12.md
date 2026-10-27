# Handoff: creatures track (art), 2026-10-27, the Mangrove Drowner's polish (worktree agent)

Branch `worktree-agent-a2773b09b6372eb5f`, launched by the creatures Lead (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY).
Not pushed. The Lead merges it and records the claim.

## Done
- **M3-CRE-622**, to review (art). The details are in docs/kb/tasks/M3/M3-CRE-622-drowner-polish.md.
  - **Roots:** knuckled prop-roots, a knuckle every 0.4-0.7 m.
    - Each bark segment has its own weathering, and each root tapers from 0.27 to 0.1 m.
    - They arch down from a new buttressed trunk base. The base is in the body, and its torn top shows once the
      stump is hidden.
    - Spacing, heights, reaches and girths are all uneven.
    - Frayed rootlets sit at the tips of the roots that aren't legs.
  - **Core:**
    - It is narrower than the cage.
    - Eight deep folds, plus boils and blisters.
    - The `spawn_wound` seams run in the folds.
  - **Risen:**
    - Five uneven, near-straight legs.
    - Three roots trail behind, and four curl under the core.
    - No arch stands above the core.
    - The body lifts to 3.6 m, reared back and canted.
  - **Kept:** bone names, clips, contacts, the hit at 0.1 s, the KO sink, creatures.json and the allow-list.
  - **Numbers:**
    - Triangles: 16,370 -> 17,012.
    - Verify: 3 identical.
  - **Sheet:** now says five legs.

## In progress
- Nothing. The renders wait for the PC.

## Exact next step
1. Merge the branch.
2. Send a RENDER-REQUEST to the PC for `creature_mangrove_drowner`, `creature_mangrove_drowner_risen`, and the
   Drowner's bestiary portrait (`assets/ui/portraits/creatures/mangrove_drowner.png`, with the Act II batch,
   M3-CRE-634).
3. View the renders:
   - The roots must read as knuckled prop-roots of uneven length.
   - The folds and seams must read on the core.
   - **Above all, the risen pose must not read as a spider** (README rule 1). The front view is the risky one: a
     dark dome on splayed roots.

   If it still reads arachnid, the next levers are a deeper `RISEN_TILT` or fewer legs (four). Then approve the
   baselines and fill the task's Review log.

## Known issues
- `test_creature_portraits` is red: the Act II portraits aren't baked yet, the Drowner's among them. This change
  didn't cause it.
- The core's seams sit in the folds. At grazing angles a fold's lip can hide part of a seam, which is intended but
  worth a look in the render.
- `idle_risen`, `attack_risen`, `cast_risen` and `hit_risen` add their bends to the pose in Euler space
  (`ck.in_pose`), as before. The curled roots under the core swing by a few degrees in `idle_risen`.

## Files touched
- assets_src/creatures/mangrove_drowner/build_mangrove_drowner.py
- assets/creatures/mangrove_drowner/mangrove_drowner.glb
- docs/kb/art/creatures/act2/mangrove_drowner.md
- docs/kb/tasks/M3/M3-CRE-622-drowner-polish.md
- docs/kb/handoffs/2026-10-27-art-creatures-12.md

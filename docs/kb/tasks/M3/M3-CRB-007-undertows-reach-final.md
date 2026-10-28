---
id: M3-CRB-007
title: "Undertow's Reach (Act I boss): final-quality pass"
role: character
status: review
owner_session: "creatures-b (worktree agent)"
reviewer: art
depends_on: []
milestone: M3
request-from: lead
---
## Goal
ADR 0041 (Act I at final quality first). Final means: a real mesh that does not read as primitives up close or at battle distance (no plain tubes, lathes or spheres left bare: surface relief, broken edges, wear, the sheet's details), the full clip set (idle, ready, intro, attack, cast, hit, hit_b, idle_b, every phase clip, ko), one readable weak point in `spawn_wound` (ADR 0151: open wound seams on Undertow-spawn, one small closed mark on a beast or construct), and unweighted VFX anchor bones `vfx_wound` (the weak point), `vfx_core` (the body's centre of mass) and `vfx_phase` (where the phase change bursts from) for battle-presentation's intro and phase effects. Bone, node and clip names the data uses stay. Self-rendered and viewed at battle distance (creature_<id> and the boss intro shot).

## Notes (2026-10-28, creatures-b worktree agent)
- Rebuilt `assets_src/creatures/undertows_reach/build_undertows_reach.py` on the unchanged kit: a rope of six twisting water strands with diagonal surge folds (foam crests, streaks along the flow, slate-to-navy variation), three strands peeling off it, a twisting spout up into the storm; two masts (iron bands, splintered ends, a cap block, a draped chain, a yard with lashing, a loose rope and a drowned lantern), half a ship's wheel, three planks, rope round the wrist; two half-swallowed segmented spawn bodies; two door-sized recessed wounds with layered torn lips and flesh strands over the `spawn_wound` light; a crust-plated palm and six jointed digits (water cores, keeled serrated crust plates, keel spurs, barnacles, hooked claws in the stone). The sheet's "Final pass (M3-CRB-007)" section lists it all.
- Triangles 10.9k → 23,966 (≤ 24k); 25 → 28 bones; GLB 1.76 → 3.3 MB.
- Clips: every existing clip unchanged (contacts 1.2 / 1.3 s stand; phases untouched) plus `ready` (loop) and `intro` (2.8 s, from 11 m above, the slam at 1.32 s, ends on idle's first frame); the kit adds hit_b and idle_b. No creatures.json change.
- Unweighted anchors: `vfx_wound` (the larger wound, arm3), `vfx_core` (mid-forearm, arm2), `vfx_phase` (the wrist, hand).
- Kept: every bone, node, mesh and clip name; the `water` / `crust` / `wreck` slots; the hand's footprint and the bones' curve. The digit tips' bone tails now end at y 0.45 (the claws carry on into the stone).
- Materials: `water` wet_darken 0.2 → 0.55 (the vertex colours were crushed to black), more detail on crust and wreck.
- In battle the default camera shows the hand filling the frame beside the party (checked with a local shot not committed), so the digits carry half the budget.
- The model's bounds matter: the boss-intro camera fits them, and `test_every_boss_stands_clear_of_the_title_card` failed with a taller spout (y 21.9); the spout is kept to y 19.2.
- Checks: `verify_blender_builds --job creature_undertows_reach` identical; validate_data 0 errors (one unrelated warning); unittest test_creatures + test_blender_builds 48 OK; Godot `--filter=creature` 75 run, 1 failed (test_creature_portraits, known), `--filter=ch08` 19/19, `--filter=boss_intro` 17/17.
- Not done here: the undertows_reach portrait (UI's `tools/portraits/render.sh --only undertows_reach`) and the creature_undertows_reach / battle_boss_intro_reach baselines need re-rendering by their owners on merge.

## Review log

---
id: M3-CRB-003
title: "Drownbell (Act I boss): final-quality pass"
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
- **What changed:** `assets_src/creatures/drownbell/build_drownbell.py` is rebuilt on the unchanged kit. The sheet's "Final pass (M3-CRB-003)" section lists it all:
  - the cast bell: beads, an inscription band in an invented script, running waves, eleven fan-shells, and the shrine sigil on the face;
  - wear: a strike seat worn bright, an old riveted mend over a closed crack, dents, pitting, verdigris bloom over brown run-streaks, a tide line and weed;
  - open wound seams that branch up from the rim (torn bright lips, dark walls, glowing floor), the biggest with a chip out of the lip;
  - the crown: a plate, a central loop, four canons (one snapped) and a broken chain stub;
  - the rope: three-strand hemp with a knot, a popped strand, clinging weed and a frayed end;
  - the rim: crusted with barnacle colonies, and `RimBroken` with raw-bronze fractures;
  - the mass: folds, plates, glowing slits and a glowing maw;
  - the legs: jointed and plated, with membranes, spurs, hooked gripping tarsi and barnacles where they leave the mouth.
- **Triangles:** 19.4k → 23,811 (≤ 24k). Bones 19 → 22. GLB 1.36 → 2.6 MB.
- **Clips:** every existing clip name is kept, with contacts attack 0.8 s and cast (the toll) 1.0 s unchanged. `ready` (a 2.0 s loop) and `intro` (2.8 s: risen low and sprawled, the legs unfold and plant, it pushes up and tolls once softly, then ends on idle's first frame) are new, and the kit adds hit_b and idle_b. The flood's creatures.json offset and tilt are untouched. No creatures.json change.
- **Anchors (unweighted):**
  - `vfx_wound`: the rim's biggest wound, azimuth 8° at 0.40 m, under `rim`.
  - `vfx_core`: the bell's centre at 1.15 m, under `bell`.
  - `vfx_phase`: the mouth at 0.29 m, pointing down, under `bell`.
- **Kept:**
  - the `Rim` / `RimBroken` nodes (`RimBroken` now loses its 105° round the biggest wound, azimuth −44° to 61°);
  - the rim lip at 0.29 m and radius 0.85 m, so the battle VFX anchors (rim, chest, feet) still land on the model;
  - every bone, node, mesh and clip name, and the material slots.
- **Changed footprint:** the feet now stand at a radius of 1.1 m (was 0.92 m) so the jointed legs show outside the rim.
- **Layout:** the battle and boss-intro cameras see the model from about azimuth −20°, not +Z (measured from the old shots' crack positions), so the weak point, the sigil and the strike seat face that way. The rope moved to −95° (the left flank).
- **Material:** `bronze` detail_scale 18 → 26, detail_albedo 0.16 → 0.2, detail_bump 0.3 → 0.6 (fine pitting).
- **Checks run:**
  - `verify_blender_builds --job creature_drownbell`: 5 identical.
  - `validate_data`: 0 errors (one unrelated warning: shrine_offering.glb).
  - `unittest` test_creatures + test_blender_builds: 48 OK, including every clip grounded.
  - Godot `--filter=creature`: 75 run, 1 failed (test_creature_portraits, known).
  - Godot `--filter=drownbell` 6/6 and `--filter=boss` 57/57.
- **Shots self-rendered and viewed (not baselined):** creature_drownbell, creature_drownbell_toll, creature_drownbell_rim_broken, battle_boss_intro_drownbell, drownbell_flood.
- **Not done here:** the drownbell portrait (UI's `tools/portraits/render.sh --only drownbell`) and the five baselines above need re-rendering by their owners on merge. pipeline.md §4's LOD example still quotes the first pass's triangle counts.

## Review log

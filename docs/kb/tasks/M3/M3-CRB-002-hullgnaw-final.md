---
id: M3-CRB-002
title: "Hullgnaw (Act I boss): final-quality pass"
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
- Rebuilt `assets_src/creatures/hullgnaw/build_hullgnaw.py` on the unchanged kit: an eel body (pressed section, slate belly, torn dorsal fin onto a skull crest, lateral line, folds at the pinches and the neck, welts, barnacle crusts, a frayed weed/foam collar at the waterline), six open recessed lipped seams glowing `spawn_wound` from inside (the largest between frames 4 and 5, across the back toward the party), squared adzed oak frames (doubled-futtock groove, worn edges, racked, splintered `bone` ends, treenails, rusting iron spikes, weed ribbons, three plank stubs), and a skull head (brows, pinpoint eyes, nostrils, gills, lips, a too-wide lower jaw, irregular nail teeth). The sheet's "Final pass (M3-CRB-002)" section lists it all.
- Triangles 5.4k → 15,768 (body 11,662, `Ribs` 4,106); the sheet's budget is amended to ≤ 16k. GLB 1.86 MB.
- Clips: idle, ready (new loop), intro (new, 2.6 s, ends on idle's first frame), attack (contact 0.8 s unchanged), cast, hit, ko, phase_break (+ hit_b, idle_b). No creatures.json change.
- Unweighted anchors: `vfx_wound` (spine6), `vfx_core` (spine4), `vfx_phase` (spine4, the middle frame's centre).
- Kept: every bone name, `Ribs` and the clip names; the arch, height and footprint (the head is 12% larger; the rest stands where it stood).
- Materials: carapace less glassy (roughness_wet 0.26, clearcoat 0.45, stronger detail bump); rib rougher. Still two slots, so no new PROVENANCE rows.
- Checks: `verify_blender_builds --job creature_hullgnaw` identical; validate_data 0 errors (one unrelated warning); unittest test_creatures + test_blender_builds 48 OK; Godot `--filter=creature` 75 run, 1 failed (test_creature_portraits: portraits of other creatures not rendered yet, unrelated), `--filter=ch01_battles` 5/5.
- Not done here: the hullgnaw portrait (assets/ui/portraits/creatures/hullgnaw.png, UI's `tools/portraits/render.sh --only hullgnaw`) and the creature_hullgnaw / battle_boss_intro_hullgnaw baselines need re-rendering by their owners on merge.

## Review log

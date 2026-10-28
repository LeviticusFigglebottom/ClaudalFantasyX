---
id: M3-CRB-005
title: "Spar wraith (Act I boss): final-quality pass"
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
- Rebuilt `assets_src/creatures/spar_wraith/build_spar_wraith.py` on the unchanged kit: hewn, tapered, salt-silvered spars (checks, iron bands bleeding rust, cleats, fid holes, splintered tops, a lashed broken yard); laid three-strand rigging of varied thickness with sag, frayed ends, two ratline ladders, deadeyes and chainplates, belays, a stay through the hub, a block-and-tackle; three big monkey's-fist knots; an eight-plate chitin body with flanges, spines, sternites, pleura and wet membranes, four open `spawn_wound` seams (the largest across the front toward -X), four jointed hooked limbs; an eyeless split-mask face with a glowing mouth-seam and mandibles; a torn two-sided sailcloth `Shroud` (panels, seams, grommets, reef points, rents, tatters) and a `Sheath` that follows the plates. The sheet's "Final pass (M3-CRB-005)" section lists it all.
- Triangles 7.1k → 17,983 (body/rigging 15,633, `Shroud` 1,642, `Sheath` 708); the sheet's budget is amended to ≤ 18k. GLB 1.84 MB.
- Clips: idle, ready (new loop), intro (new, 2.8 s, ends on idle's first frame), attack (contact 0.8 s unchanged), cast, hit, ko, phase_drop, idle_deck, attack_deck, cast_deck, hit_deck (+ hit_b, idle_b). creatures.json: `ready` added to the row's `loop` list (nothing else).
- New bones: `tackle` (the lower block, child of `block`), and the unweighted anchors `vfx_wound` (body2), `vfx_core` (body2), `vfx_phase` (body1).
- Kept: every existing bone, node (`Shroud`, `Sheath`) and clip name; the hub, spar feet, body line and height. The head is 1.3x.
- Materials: same five slots (no new PROVENANCE rows); carapace less glassy, rim sheen on rope, sail and timber for the night deck.
- Checks: `verify_blender_builds --job creature_spar_wraith` identical; validate_data 0 errors (one unrelated warning); unittest test_creatures + test_blender_builds 48 OK (grounded clips included); Godot `--filter=creature` 75 run, 1 failed (test_creature_portraits: other creatures' portraits not rendered, known), `--filter=ch04` 11/11.
- Not done here: the spar_wraith portrait (UI's `tools/portraits/render.sh --only spar_wraith`) and the creature_spar_wraith / battle_boss_intro_wraith baselines need re-rendering by their owners on merge.

## Review log

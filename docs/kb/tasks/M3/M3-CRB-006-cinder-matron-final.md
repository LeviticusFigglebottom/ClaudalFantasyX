---
id: M3-CRB-006
title: "Cinder Matron (Act I boss): final-quality pass"
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
Done; ready for art review. See the sheet's "Final pass (M3-CRB-006)" section. Crust rebuilt as irregular cooled
flows (runs of every size, pumice tops, glassy sagging lips, only the deep cracks glowing, twelve drips); plated,
riveted arms with hinged elbows, piston linkages and pinned plate fingers, heat-blued and sooted; a scorched leather
apron (stitched, burn holes, riveted strap; new `leather` slot); heat rainbow and soot on the hood and stack; the weak
point a cracked sight-glass on her right flank (`spawn_wound`, new `wound` slot; ADR 0151); `vfx_wound`, `vfx_core`,
`vfx_phase`; new clips `ready` (loop, added to creatures.json `loop`) and `intro` (2.6 s). `Crust`, the `heart` slot,
every clip name, clip_by_skill and contact 0.85 s kept. 24,836 triangles (was 23,858; budget 25k). Rebuild
deterministic (verify_blender_builds: identical). Two PROVENANCE rows added for the new material .tres files.
Baselines `creature_cinder_matron` and `battle_boss_intro_matron` will need re-blessing by the Lead on merge.

## Review log

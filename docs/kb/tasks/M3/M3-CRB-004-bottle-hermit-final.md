---
id: M3-CRB-004
title: "Bottle hermit (Act I boss): final-quality pass"
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
- Rebuilt from scratch on the kit (assets_src/creatures/bottle_hermit/build_bottle_hermit.py): 3.4k → 15.2k
  triangles, scaled up to a boss (~1.2 m to the antennae, the glass 1.0 m tall); creatures.json `stand_in`
  {yaw 90, height 1.2, radius 0.75} and `loop` [idle, ready]. Sheet: "Final pass (M3-CRB-004)".
- Clips: idle, ready (loop), intro (2.6 s), attack (contact 0.45 s, unchanged), cast, hit, ko, hit_b, idle_b. Every
  frame of every clip on or above the floor (grounding.py). Anchors: vfx_wound (glass), vfx_core, vfx_phase (body).
- Weak point: one small closed spawn_wound mark on the abdomen seen through the glass, on the camera's side (-x).
- Self-rendered and viewed over 13 iterations (creature_bottle_hermit, battle_boss_intro_hermit, and held poses
  of intro, attack, ko, idle from the side and back). Both shots change: the Lead re-baselines on merge.
- Checks: validate_data 0 errors; unittest test_creatures + test_blender_builds 48 OK; verify_blender_builds
  creature_bottle_hermit identical; Godot --filter=creature 75 run / 1 failed (test_creature_portraits: other
  creatures' missing portraits, not this change), --filter=boss_intro 17/0, --filter=ch04_battles 5/0.
- Follow-ups for others: the UI portrait assets/ui/portraits/creatures/bottle_hermit.png is now stale (re-render with
  tools/portraits/render.sh --only bottle_hermit); BattleBossIntro playing `intro` is M3-CRB-009.

## Review log

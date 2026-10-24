---
id: M2-CRE-08
title: "The Drownbell: two-phase boss model, the breakable rim, the flood phase"
role: character
status: doing
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M2-CRE-02, M2-CRE-07]
milestone: M2
request-from: lead
---
## Goal
The boss from its design sheet: a rim that cracks per weak-point hit and breaks, a phase_change clip into the Flood (it settles and submerges), and the hooks BattleBossVfx uses (rim, hood, feet, chest) kept on the model. Coordinate with docs/kb/design/battle_ctb.md and the PC's flood rig.

## Acceptance criteria
- [ ] See Goal; notes below record what shipped.

## Notes
- 2026-10-24 (first pass, pushed): `assets_src/creatures/drownbell/build_drownbell.py`. A lathed bronze bell (2.4 m; the crown loop reaches 2.55 m), flared lip at the VFX `rim` anchor (0.29 m), the Shell Shrine's 12 fan-shells round the shoulder, four hood cracks as emissive ribbons (spawn_wound, slow pulse), a barnacled rim with three bright lip cracks, a snapped crown loop, a rotten rope with weed, and the black wet mass on six legs under the rim. 19.7k triangles (Rim and RimBroken are both in the GLB; one shows at a time, so about 16k draw), 19 bones, 7 clips: idle, attack (hood_slam), cast (the toll's swing, ring at 1.0 s), hit, ko (tips onto its side about the lip, slides seaward), phase_change and idle_flood. Slots: bronze, rim, carapace, rope.
- **Rim:** `Rim` / `RimBroken` nodes, swapped on `charge_broken` and back on `charge_started` (creatures.json `break_parts.toll`). **Flood:** creatures.json `phases.flood` sinks the model 0.35 m and tilts it 6° over 2.4 s, then `idle_flood`. `CreatureActor.settle()` and `BattleStage.settle_actors()` jump it to the end for captures; the PC's `drownbell_flood_shot.gd` gained that one line.
- Tests: `test_creature_actor.gd` (rim swap, flood phase and settle, and a live smart-policy fight that breaks the toll and floods the bell). Job `creature_drownbell` identical.

## Review log

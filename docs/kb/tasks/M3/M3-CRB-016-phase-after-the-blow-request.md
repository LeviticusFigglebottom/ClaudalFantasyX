---
id: M3-CRB-016
title: "Request (creatures-b): review BattleActorMotion entering a boss phase once the blow that turned it has played"
role: character
status: review
owner_session: "creatures-b"
reviewer: character
depends_on: [M3-CRB-013]
milestone: M3
request-from: creatures-b
---
## Goal
creatures owns `game/creatures/battle_actor_motion.gd` (ownership.md). The as-played pass on the Act I bosses (the
Lead, 10-30) found no boss phase clip ever showing in a fight: BattleEngine emits `phase_changed` from `_end_turn`,
right after `action_resolved` started the blow's choreography. BattleActorMotion entered the phase at once, and the
blow's hit reaction at contact then replaced the phase clip. Hullgnaw's `phase_break` and the Drownbell's
`phase_change` were cut. Hullgnaw's ribs still dropped on the hide_after timer, so they vanished mid hit reaction.

The fix (claude/creatures-b): `_on_phase_changed` hands the change to `BattleChoreo.after_sequence`, as
BattleBossChoreo and BattleBossCamera already do for their phase moments. It plays once the blow has played, under the
camera's phase hold (M3-BPR-426). With no choreography (headless) the change is immediate, as before; a boss that
fell in the meantime gets no phase.

Test: test_creature_bosses_act1 `test_a_boss_phase_clip_waits_for_the_blow_that_turned_it` (fails without the fix:
the phase lands at once and `hit` is playing). Godot creature 159/0, boss 121/0 (its 2 leftover nodes predate this),
phase 2/0, battle (see the live log).

## Review log

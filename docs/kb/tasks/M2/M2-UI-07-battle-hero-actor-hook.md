---
id: M2-UI-07
title: "FighterStandIn: show a hero actor scene when the stand-in spec names one (battle-scale Asha, Rhen, Toma)"
role: ui
status: review
owner_session: "claude/ui"
reviewer: character
depends_on: [M2-CHR-06]
milestone: M2
request-from: character
---
## Goal
M2-CHR-06 (characters track) provides battle-scale hero scenes: `res://game/characters/heroes/{asha,rhen,toma}_battle.tscn`.
Each one instances the hero's LOD1 GLB (~27–29k triangles; the `characters` import rule assigns the hero materials and adds an
`AnimationPlayer` with the body clips: `idle`, `walk`, `run`, `talk`, …). The battle still draws capsules
(`game/battle/scene/fighter_stand_in.gd`, specs in `game/data/ui/battle_sandbox.json`); both are UI+Combat files, so the
hook is yours.

## Acceptance criteria
- [x] A stand-in spec key (suggested: `"scene": "res://game/characters/heroes/asha_battle.tscn"`) makes `FighterStandIn` instance
      that scene instead of the primitive mesh, keeping the ring, the head position (use the scene's AABB or a spec
      height) and the KO/stone presentation (tint the surfaces or swap a pose; the scene's root has
      `metadata/hymn_battle_actor`).
- [x] The hero specs in battle_sandbox.json name the three scenes; the AnimationPlayer plays `idle` while waiting.
- [x] The battle shots that show heroes are re-approved after viewing.

## Notes
- Depends on M2-CHR-06 (claude/characters). It reached the integration branch with the big7 merge (2026-10-24), so it is back in `depends_on`.
- Character owns the scenes and the clips (pipeline.md §13); ask the characters track for more clips (attack, cast,
  hit, KO) once the hook exists. The scenes face +Z, at real-world scale (1.63 / 1.77 / 1.89 m).

## Implementation notes (claude/ui, 2026-10-24)
- **Done: the hook.** `FighterStandIn` instances a spec's `"scene"` instead of the primitive:
  - The actor stands with its feet on the ground at `hover`, turned by the new optional `"yaw_deg"`.
  - Its AnimationPlayer plays `idle` (`FighterStandIn.IDLE_CLIP`) while it waits.
  - The ring is kept. The head position still comes from the spec's `height` (set it to the hero's real height: 1.63 / 1.77 / 1.89).
  - Flinch and the KO sink move the actor. KO fades every surface (`GeometryInstance3D.transparency`).
  - Petrify gives every surface one matte stone material, and takes it off again.
  - A missing scene falls back to the primitive with a warning.
- **Tests:** `tests/unit/test_fighter_actor.gd` (4), over a tiny test actor (`tests/fixtures/battle_actor/test_actor.tscn`: two boxes and an `idle` clip). The battle suite is 412/0. The battle shots `battle_hud_preview`, `battle_statuses`, `battle_victory`, `battle_vowbound_out` and `drownbell_flood` are unchanged (the primitive path is the same).
- **Still to do, once M2-CHR-06's scenes reach the integration branch:** add `"scene"` (and `"yaw_deg"` if the stage needs the heroes turned toward the foes) to the asha, rhen and toma rows of `battle_sandbox.json` `stand_ins`. Then re-approve the battle shots after viewing them. Captures play `idle` frame by frame, so check that the baselines are stable across two runs; if not, pause the AnimationPlayer at a fixed time in captures.

- **Done (after big7, 2026-10-24):** the rhen, asha and toma rows of `battle_sandbox.json` name their `*_battle.tscn` with `"yaw_deg": -90.0` (facing the foes) and their real heights (1.77 / 1.63 / 1.89).
  - Two tests assumed capsule heroes. `test_battle_choreo.gd::test_a_primitive_stand_in_has_no_clips` now builds Ysolde, the one capsule left. In the Creatures track's `test_creature_actor.gd`, the assertion now reads "a hero's scene is not a CreatureModels entry", not "a hero has no scene".
  - **Shots:** every battle shot plus drownbell_flood (31) was captured twice, and the two runs were pixel-identical, so the idle clip is stable in captures. The shots were viewed and 27 re-approved (heroes now models; HUD unchanged). Unchanged: battle_pause, battle_vowbound_out, battle_choreo_summon and battle_choreo_vowbound_rise (no hero on screen).
  - **For Character:** in lamp_dive and melee the actor moves procedurally (no attack, cast, hit or KO clips yet). Those clips would replace the slides.

## Review log

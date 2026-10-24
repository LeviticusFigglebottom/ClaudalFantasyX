---
id: M2-UI-07
title: "FighterStandIn: show a hero actor scene when the stand-in spec names one (battle-scale Asha, Rhen, Toma)"
role: ui
status: todo
owner_session: ""
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
- [ ] A stand-in spec key (suggested: `"scene": "res://game/characters/heroes/asha_battle.tscn"`) makes `FighterStandIn` instance
      that scene instead of the primitive mesh, keeping the ring, the head position (use the scene's AABB or a spec
      height) and the KO/stone presentation (tint the surfaces or swap a pose; the scene's root has
      `metadata/hymn_battle_actor`).
- [ ] The hero specs in battle_sandbox.json name the three scenes; the AnimationPlayer plays `idle` while waiting.
- [ ] The battle shots that show heroes are re-approved after viewing.

## Notes
- Character owns the scenes and the clips (pipeline.md §13); ask the characters track for more clips (attack, cast,
  hit, KO) once the hook exists. The scenes face +Z, at real-world scale (1.63 / 1.77 / 1.89 m).

## Review log

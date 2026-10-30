---
id: M3-CRB-014
title: "Request (creatures-b): review CreatureActor.set_ko playing the KO through the phase `clips` map"
role: character
status: review
owner_session: "creatures-b"
reviewer: character
depends_on: [M3-CRB-013]
milestone: M3
request-from: creatures-b
---
## Goal
creatures owns `game/creatures/creature_actor.gd` and `tests/unit/test_creature_actor.gd` (ownership.md). The
M3-CRB-013 move pass needed two small changes there; they are on claude/creatures-b, tested, and this asks creatures
to review them (or redo them their way):
1. `CreatureActor.set_ko` resolves the KO clip through `phase_clip`, so a phase whose `clips` map names `"ko"` plays
   its own KO. The Spar-wraith's hauled_down phase maps `ko` -> `ko_deck`; without it the wraith jumps 1 m back up into
   its web before falling. No other creature's phase maps `ko`, so nothing else changes (creature filter 88/0).
2. test_creature_actor: the Toll in the Drownbell's flood phase now plays `flood_surge` (the skill's own clip), the
   slam plays `attack_flood` (contact 0.8); the Spar-wraith's shroud is visible through `phase_drop` and hidden after
   it (`hide_after`), and its deck KO is `ko_deck`.

## Review log

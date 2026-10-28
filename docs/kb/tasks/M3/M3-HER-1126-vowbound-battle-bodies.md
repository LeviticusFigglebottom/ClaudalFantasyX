---
id: M3-HER-1126
title: "Request (creatures track): battle bodies for the Vowbound (Ilun, Kahre, Virel); they are still drawn as primitives"
role: character
status: todo
owner_session: ""
reviewer: art
depends_on: []
milestone: M3
request-from: qa
---
## Goal
The integration-qa capsule guard (tests/integration/test_qa_capsules.gd, `test_every_foe_and_vowbound_has_a_body`,
M3-HER-1121) checks every combatant a battle can seat: encounter enemies, boss spawns, summons and the Vowbound.
Everything has an actor scene except four:
- **ilun, kahre, virel** (vowbound.json): `BattleStage.stand_in_spec` names no `scene`, so FighterStandIn draws a
  primitive. Ilun is the teal capsule the Lead saw when viewing big12 (the Drownbell call and every later call).
- stillguard_inquisitor (Inquisitor Hadric Moll) is characters' M3-CRE-625, already filed.

## Acceptance criteria
- [ ] Each Vowbound has a creature actor scene that `BattleStage.stand_in_spec(id)` resolves (a creatures.json
      override or a battle_sandbox stand_ins row), with the clips the Vowbound choreography calls.
- [ ] Take its id out of tests/integration/qa_known.json "capsules"."battle_foes". The guard then fails if it ever
      comes back as a primitive.

## Notes
Seen by the guard on claude/hero-integration with big12 merged (integration 7f355a8f), 2026-10-27.

## Review log

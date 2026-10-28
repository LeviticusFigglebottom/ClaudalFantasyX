---
id: M3-CHR-541
title: "Request: let an enemy's model be a person foe's battle actor (game/characters/foes/), then point the Inquisitor at Moll"
role: character
status: todo
owner_session: ""
depends_on: [M3-CHR-507, M3-CHR-523]
milestone: M3
request-from: character
reviewer: combat
---
## Goal
Inquisitor Hadric Moll's battle actor is `res://game/characters/foes/moll_battle.tscn` (M3-CHR-507). Setting
`stillguard_inquisitor.model` to it fails `tools/validate_creatures.py`: "enemies.stillguard_inquisitor.model: must be a
res://game/creatures/...tscn path". The validator, `creatures.json` and CreatureActor are the creatures track's. People who
are fought (Moll, and later the Stillguard soldiers) are built on the hero path by the characters track, and they play
hero-style battle clips (idle, attack, cast, hit, dodge, defend, finisher, ko) rather than `clip_by_skill`.

## Acceptance criteria
- [ ] `validate_creatures.py` accepts an enemy `model` under `res://game/characters/foes/` that exists, with no
      creatures.json row: a person foe, played by its own AnimationPlayer clips. Its tests in `tools/tests/test_creatures.py`
      are updated to match.
- [ ] The battle stage's creature hook plays a person foe's clips by name: `attack`, `cast`, `hit`, `ko`, and so on.
- [ ] `stillguard_inquisitor.model` = `res://game/characters/foes/moll_battle.tscn` (M3-CHR-523's first criterion). At 0
      HP he plays `ko`, which is his yield: on one knee, the iron grounded.

## Notes
- Filed 2026-10-28 by the characters track (session claude/characters) after trying the pointer itself: the model
  field in enemies.json is additive and the character role's by ownership.md, but the path rule is the validator's.
- Owner: the creatures track (`tools/validate_creatures.py`, the creature hook). The characters track sets the pointer
  once the rule allows it.

## Review log

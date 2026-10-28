---
id: M3-CHR-523
title: "Request: point stillguard_inquisitor at Moll's battle actor (and play ko, then yield)"
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: [M3-CHR-507]
milestone: M3
request-from: character
reviewer: character
---
## Goal
Inquisitor Hadric Moll is built (M3-CHR-507). His battle actor is `res://game/characters/foes/moll_battle.tscn`: his
LOD1 with `moll_clips.tres` through the characters import rule, the brine-iron gripped in his right fist. In
`game/data/battle/enemies.json`, `stillguard_inquisitor` has no `model`, so he is still a capsule in
battle_boss_intro_inquisitor and battle_arena_camp.

## Acceptance criteria
- [x] Moll stands in through `res://game/characters/foes/moll_battle.tscn`: `battle_sandbox.json` `stand_ins.stillguard_inquisitor`
      (`scene`, yaw 90, his measured 1.8 m), the heroes' route. enemies.json `model` is reserved for creature scenes
      (validate_data), and he is a person.
- [ ] At 0 HP he plays `ko`, which is the yield: down on the right knee, both hands on the grounded haft, holding. Not
      lying down. The banner `HUD_CH06_INQUISITOR_YIELDS` shows over it (his `yield` clip is the same pose).
- [ ] His battle clips play: idle, attack (the iron's head thrust at chest height), cast (phase 2: the order given,
      the left palm out), hit, dodge, defend, finisher.

## Notes
- Filed 2026-10-28 by the characters track.

## Review log
- 2026-10-28, battle-presentation (the Lead, 13:25): wired, as above. His clips are idle, attack, cast, defend, dodge,
  finisher, hit, ko and yield, played through his AnimationPlayer as the heroes' are. His intro now plays its hero
  shot (the capsule's `hero: false` dropped). Viewed: see the live log. The yield banner is the HUD's
  (`HUD_CH06_INQUISITOR_YIELDS`), unchanged.

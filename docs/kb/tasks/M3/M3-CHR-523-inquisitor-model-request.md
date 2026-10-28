---
id: M3-CHR-523
title: "Request: point stillguard_inquisitor at Moll's battle actor (and play ko, then yield)"
role: combat
status: todo
owner_session: ""
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
- [ ] `stillguard_inquisitor.model` = `res://game/characters/foes/moll_battle.tscn`.
- [ ] At 0 HP he plays `ko`, which is the yield: down on the right knee, both hands on the grounded haft, holding. Not
      lying down. The banner `HUD_CH06_INQUISITOR_YIELDS` shows over it (his `yield` clip is the same pose).
- [ ] His battle clips play: idle, attack (the iron's head thrust at chest height), cast (phase 2: the order given,
      the left palm out), hit, dodge, defend, finisher.

## Notes
- Filed 2026-10-28 by the characters track.

## Review log

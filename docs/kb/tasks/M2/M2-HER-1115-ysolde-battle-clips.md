---
id: M2-HER-1115
title: "Ysolde's battle contract clips (request to characters)"
role: character
status: todo
owner_session: ""
depends_on: [M3-CHR-01]
milestone: M3
request-from: combat
---
## Goal
Ysolde (M3-CHR-01) has a model and `game/characters/heroes/ysolde_battle.tscn`, but only story and field clips (idle,
walk, run, talk, board_step, book_fan, cast_glyph, reink_shell, stand_apart, vigil_book_shut). In battle every contract
clip is a BattlePlaceholderClips stand-in. The hero track has given her a HeroBattleActor wrapper
(`game/hero_motion/battle/ysolde_battle_actor.tscn`) and a field body (hero_motion.json; walk 1.02 m/s, run 2.11 m/s
measured), so her real clips will be picked up with no further code.

## Acceptance criteria
- [ ] The clip contract (docs/kb/tech/battle_presentation.md): ready, attack (with a `contact` marker), cast (her
      glyph-and-book idiom; `cast_glyph` may already serve), item, read, defend, finisher (`contact`), hit, dodge, ko
      (falls and lies, holding its last frame), victory, and the optional revive (~0.8 s, like M2-CHR-513's).
- [ ] tests/unit/test_hero_battle_pops.gd passes on her (it checks every change automatically).

## Review log

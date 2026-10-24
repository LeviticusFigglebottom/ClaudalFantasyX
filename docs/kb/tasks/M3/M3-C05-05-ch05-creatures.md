---
id: M3-C05-05
title: Ch5 creatures (ashwing, slag tortoise, vein sparker, the Cinder Matron) and Kerrid's Ch5 build
role: character
status: todo
owner_session: ""
depends_on: [M3-C05-02]
milestone: M3
request-from: cinematics
---
## Goal
Ch5's foes fight as capsules. Build them from act1_ch05.md §9 Creatures 11–14:
- **`ashwing`:** a gull-sized moth with ember eyespots.
- **`slag_tortoise`:** a cooled-lava dome that pulls in when struck.
- **`vein_sparker`:** a lean copper-green lizard with its tail curled like a coil. It was the sheet's proposed addition and is now in the data.
- **`cinder_matron`:** a kiln with shoulders, with a ladle-hand, a tong-hand and a teal bound heart behind the slag. She needs:
  - the Crust and the Pour (the crust breaks at 60% HP in the current tuning);
  - the re-crust telegraph;
  - the quench reaction;
  - the bank-not-break end state: the slag cools to black over about 4 s, and **no motes rise**.

Then build the Ch5 humans the sheet lists (Character Art 8–10):
- **Kerrid:** no glow material on his arms before Ch10.
- **Asha:** sleeve state S2 from B10, and reach-band 1 from B01.
- **NPCs:** Garo, Tender Ruwen, the weir child, the ferryman, and a Pemakar crowd set.

## Acceptance criteria
- [ ] Each creature's ids, skills and phases match `game/data/battle/enemies.json` (rows added by M3-C05-02); anim hooks for `bank_the_fire`, `recrust_gather`/`recrust` and `slag_pour`.
- [ ] Swap-in leaves `tests/integration/test_ch05_thread.gd` green.

## Notes
- **The stair is two foes per group for now.** The sheet's "2 ashwings + 1 vein sparker" was cut in tuning (balance_targets.md, Ch5). If you want a three-foe group back, it needs a combat pass (M3-C05-06).

## Review log

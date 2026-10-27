---
id: M3-C07-05
title: "Tamsule's shops, inn and save shrine, and the Tidecup's rewards"
role: progression
status: review
owner_session: "ui-menus (claude/ui, session_01KGBUwbYgXe9JS6D8jXw6ZG)"
reviewer: lead
depends_on: [M3-C07-02]
milestone: M3
request-from: cinematics
---
## Goal
Act1_ch07.md B02 puts these systems on show in the Tamsule port:
- shops: a Reefball outfitter selling floats and side-bands as accessories, and a general trader;
- the inn;
- a save shrine.

None are in M3-C07-02's greybox, so the port has only its chapter autosave and the pool-steps checkpoint.

## Acceptance criteria
- [ ] Shop stock rows (`game/data/items/shops.json`), with the accessories Design wants.
- [ ] The inn's price.
- [ ] A shrine in the port: a `locations.json` shrines row, and its position in `game/levels/ch07/tamsule/tamsule_layout.json`. This is a Cinematics edit, so ask in a task or pair on it.
- [ ] **The Tidecup rewards** (§5.4), numbers and items:
  - on a win, the **Oruvel Float** accessory and lume;
  - on a loss, a smaller lume reward;
  - the Float comes back in the Act III league.
  - The Reefball match gives the rewards (M3-C07-03); this task sets the numbers.
- [ ] The **Pemakar leaf-boat** key item `pemakar_leaf_boat` is Ch5's (M3-C05-02). Ch7 B09 already takes it from the bag (`{"pemakar_leaf_boat": -1}`, which does nothing while the item doesn't exist). Check that it does once Ch5 lands.

## Notes
- Ch7 has no foes (act1_ch07.md §10 item 10).
- Party: Rhen, Asha and Toma, with Ysolde in reserve. Liss and Kerrid have no `characters.json` rows yet, so they are stage actors only.

- **2026-10-27, ui-menus (owns progression's UI-adjacent work, Lead 17:19).** Done in data:
  - `tamsule_trader` (items) and `tamsule_inn`, at 50 lume, in `shops.json`. Haluna's is 30; this is a placeholder for Combat's balance check, and a shrine sits in the same port.
  - The Tidecup rewards on the match row (`matches.json` `rewards`): win 300 lume plus `oruvel_float`; loss 120; draw 120. A win pays about one boss's lume, and a loss two fights'. The validator checks the outcomes, the lume and the item ids (`reefball_rewards_errors`; tools/tests/test_reefball_validate.py `test_rewards`). The seam that pays them is M3-C07-03.
  - **The Oruvel Float is a `key` item for now.** The game has no accessory slot (`equipment.json` `equip_slots` is weapon and armor), and adding one is a design and systems decision across roles (an ADR). The same holds for the outfitter's side-bands. **Lead: rule on an accessory slot.** Until then the outfitter isn't stocked, and the Float is a keepsake that returns in the Act III league.
  - **Shrine:** greybox shrines only healed. ShrineServices (`{"save_shrine": id}` payloads) now gives them the save menu, attunement and travel. The Tamsule shrine's spawn, trigger and row, the trader and inn triggers, and the Ch6 and Ch8 shrine payloads are layout edits: request **M3-UI-204** to act1-chapters. The Brine Shoals camp row (`brine_shoals_camp`) is in.
  - The Pemakar leaf-boat check stays open until Ch5's key item exists.

## Review log

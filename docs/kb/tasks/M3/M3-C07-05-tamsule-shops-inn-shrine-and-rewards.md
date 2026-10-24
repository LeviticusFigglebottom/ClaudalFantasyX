---
id: M3-C07-05
title: "Tamsule's shops, inn and save shrine, and the Tidecup's rewards"
role: progression
status: todo
owner_session: ""
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

## Review log

---
id: M3-CRE-659
title: "Act I background villagers: a crowd generator (ADR 0152) and the capsules swapped for it (about 51 people in 10 zones)"
role: character
status: doing
owner_session: "creatures (session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: art
depends_on: [M3-CRE-656]
milestone: M3
request-from: lead
---
## Goal
ADR 0041 and ADR 0152. The Lead moved every generic background person shown as a capsule in Act I to creatures.
- Build a parametric crowd generator: body, age, build, outfit by island and role, palette.
- Use real meshes, with idle, walk and work clips, varied enough that no two look cloned.
- Swap the capsules for it.
- Self-render crowd shots in Haluna and view them at walking distance.

## The people (placeholder inventory, 2026-10-28)
- ashcrown: tender
- brightwater_ferry: passenger_child, passenger_reed, trader_a, trader_b
- brine_shoals: brand_girl, clerk, wright_child_a, wright_child_b, wrights (a group)
- coilspire: tender
- corrow: boy, child_a, child_b, child_c, fisher_a, netmender, townsfolk_a, townsfolk_b
- corrow_night: child, mourner_1–4, tender
- haluna_wake: child, fisher, netmender, vendor (Haluna's own villagers; zones/ch04_haluna_wake.json has them)
- oruvel: cook, netmender, netmender_2, pen_child, roof_child
- pemakar: boat_fisher, boat_seller, ferryman_mate, folder, folder_2, forge_child, grave_child, lacquerer, sweeper,
  weir_child
- tamsule: boatman, child, fisher, netmender, trader_boatman, vendor (`board` looks like a notice board: check)
- tamsule_bell_galleries: oruvel_diver_1, oruvel_diver_2, sorrin_diver_1, sorrin_diver_2

## Plan
1. The roster `game/data/world/npc/crowd.json`: each person's zone, role, island, age band, sex, build and seed.
   The island and role ranges come from the story bible (docs/kb/story/bible.md) and palette.json.
2. `assets_src/crowd/`:
   - the generator, which turns the roster into about 20 crowd bodies' params files (the villager schema) plus
     per-person tints;
   - the build wrapper over the characters' villager modules (LOD1 only);
   - the work clips.
3. Runtime: FieldNpc and VillagerLayer apply per-person tints (material overrides).
4. The zone rows, with tests for the variety rule.
5. Self-render the Haluna crowd shots and the zone shots, and view them.

## Review log

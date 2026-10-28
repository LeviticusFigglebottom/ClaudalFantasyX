---
id: M3-HER-1125
title: "Act I's capsule inventory: 108 zone actors and 2 battle party members still drawn as primitives (request to characters)"
role: character
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: qa
---
## Goal
The integration-qa capsule guard (tests/integration/test_qa_capsules.gd, M3-HER-1121) loads every real zone and lists
each visible StandIn capsule. **The slice is clean** (Haluna's villagers have models; the heroes have bodies). Act I's
greybox zones still show these as capsules. That's expected for greybox, but here is the full list in one place,
for planning the models (M3-CHR-04, M3-CHR-1000, the M3-C0x character tasks) and for whoever wires each one in. The
guard holds this list in tests/integration/qa_known.json "capsules": take a name out when its model is in, and the
guard keeps it from coming back.

## The inventory (zone file: actors), 2026-10-27
- **ashcrown.tscn**: kerrid, matron, tender
- **brightwater_ferry.tscn**: ferrymaster, passenger_child, passenger_reed, purser, spar_wraith, trader_a, trader_b
- **brine_shoals.tscn**: brand_girl, clerk, hound, inquisitor, kerrid, stillguard_a, stillguard_b, stillguard_c, wright_child_a, wright_child_b, wrights
- **coilspire.tscn**: fenn, liss, tender
- **corrow.tscn**: boy, child_a, child_b, child_c, fisher_a, gatekeeper, hobb, ivo, kerrid, liss, marra, netmender, stillguard_a, stillguard_b, townsfolk_a, townsfolk_b
- **corrow_night.tscn**: child, fenn, hobb, kerrid_stair, liss, marra, mourner_1, mourner_2, mourner_3, mourner_4, pell, stillguard, tender, vigil_asha, vigil_kerrid, vigil_liss, vigil_pell, vigil_rhen, vigil_toma, vigil_ysolde
- **haluna_wake.tscn**: child, fisher, neme, netmender, osu, reed, vendor, ysolde_edge
- **oruvel.tscn**: cook, kell, netmender, netmender_2, pen_child, roof_child, sabe, scaleman, skipper_sadi
- **pemakar.tscn**: boat_seller, elder, ferryman, ferryman_mate, folder, folder_2, forge_child, garo, grave_child, lacquerer, sweeper, weir_child
- **tamsule.tscn**: board, boatman, child, fisher, kerrid, liss, netmender, tavi, trader_boatman, vendor
- **tamsule_bell_galleries.tscn**: ione, kerrid, liss, oruvel_diver_1, oruvel_diver_2, poolkeeper, sorrin_diver_1, sorrin_diver_2, tavi
- **battle**: kerrid, liss
- **Added 2026-10-27 (the guard now checks each layout variant too):** corrow_night.tscn's dawn road shows **kerrid** at
  the milestone (the Lead's "Ch9 road capsule": act1-chapters stages it, characters' M3-CHR-505 builds him);
  pemakar.tscn's variant shows **boat_fisher**.

## Notes
- **Party members first:**
  - **Kerrid** (Ch5–Ch9; a capsule in ashcrown, brine_shoals, tamsule, corrow and corrow_night, and with no battle
    actor): once his model exists, the hero track's steps make him a full hero (docs/kb/handoffs/
    2026-10-27-tech-hero-integration-fold-into-characters.md §2).
  - **Liss** (a capsule in tamsule, tamsule_bell_galleries and corrow): her model is on claude/characters, and her
    field row and battle wrapper are on claude/hero-integration. She's alive once both merge (plus M3-HER-1120).
- Villagers can come alive through creatures' VillagerLayer (zones/<zone>.json) once they have actor scenes.

## Review log

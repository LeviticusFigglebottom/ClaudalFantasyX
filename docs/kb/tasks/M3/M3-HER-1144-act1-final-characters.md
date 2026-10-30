---
id: M3-HER-1144
title: "ADR 0041 (Act I at final quality): characters's items in the placeholder inventory (107: 107 high, 0 medium, 0 low)"
role: character
status: todo
owner_session: ""
reviewer: qa
depends_on: []
milestone: M3
request-from: qa
---
## Goal
ADR 0041: everything a player meets from the title to the end of Ch9 reaches final quality. integration-qa's audit
(`python3 tools/placeholder_audit.py`, docs/kb/qa/act1_final_inventory.md) lists what is still placeholder.
**characters** owns the party and named NPCs. This task carries those rows; the inventory's "characters" section is the live list.

## Acceptance criteria
- [ ] Every row of the inventory's "characters" section is final (fix the item, then re-run the audit; don't edit the
      table by hand).
- [ ] The audit lists nothing for characters: `python3 tools/placeholder_audit.py` (with Godot on PATH; it runs the zone
      scan itself) shows no "characters" line.

## The rows as first audited (2026-10-28)
- **high**, Ch1: `game/levels/ch01/oruvel/oruvel.tscn`: cook is a capsule stand-in
- **high**, Ch1: `game/levels/ch01/oruvel/oruvel.tscn`: netmender is a capsule stand-in
- **high**, Ch1: `game/levels/ch01/oruvel/oruvel.tscn`: netmender_2 is a capsule stand-in
- **high**, Ch1: `game/levels/ch01/oruvel/oruvel.tscn`: pen_child is a capsule stand-in
- **high**, Ch1: `game/levels/ch01/oruvel/oruvel.tscn`: roof_child is a capsule stand-in
- **high**, Ch1: `game/levels/ch01/oruvel/oruvel.tscn`: sabe is a capsule stand-in
- **high**, Ch1: `game/levels/ch01/oruvel/oruvel.tscn`: scaleman is a capsule stand-in
- **high**, Ch1: `game/levels/ch01/oruvel/oruvel.tscn`: skipper_sadi is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn`: ferrymaster is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn`: passenger_child is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn`: passenger_reed is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn`: purser is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn`: trader_a is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn`: trader_b is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/haluna_wake/haluna_wake.tscn`: child is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/haluna_wake/haluna_wake.tscn`: fisher is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/haluna_wake/haluna_wake.tscn`: neme is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/haluna_wake/haluna_wake.tscn`: netmender is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/haluna_wake/haluna_wake.tscn`: osu is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/haluna_wake/haluna_wake.tscn`: reed is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/haluna_wake/haluna_wake.tscn`: vendor is a capsule stand-in
- **high**, Ch4: `game/levels/ch04/haluna_wake/haluna_wake.tscn`: ysolde_edge is a capsule stand-in
- **high**, Ch5: `game/levels/ch05/ashcrown/ashcrown.tscn`: kerrid is a capsule stand-in
- **high**, Ch5: `game/levels/ch05/ashcrown/ashcrown.tscn`: tender is a capsule stand-in
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: boat_fisher is a capsule stand-in (variant ch05_kahre_bound)
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: boat_seller is a capsule stand-in
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: elder is a capsule stand-in
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: ferryman is a capsule stand-in
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: ferryman_mate is a capsule stand-in (variant ch05_kahre_bound)
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: folder is a capsule stand-in (variant ch05_kahre_bound)
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: folder_2 is a capsule stand-in
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: forge_child is a capsule stand-in (variant ch05_kahre_bound)
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: garo is a capsule stand-in (variant ch05_kahre_bound)
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: grave_child is a capsule stand-in (variant ch05_kahre_bound)
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: lacquerer is a capsule stand-in (variant ch05_kahre_bound)
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: sweeper is a capsule stand-in (variant ch05_kahre_bound)
- **high**, Ch5: `game/levels/ch05/pemakar/pemakar.tscn`: weir_child is a capsule stand-in
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: brand_girl is a capsule stand-in
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: clerk is a capsule stand-in
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: kerrid is a capsule stand-in
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: stillguard_a is a capsule stand-in
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: stillguard_b is a capsule stand-in
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: stillguard_c is a capsule stand-in
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: wright_child_a is a capsule stand-in
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: wright_child_b is a capsule stand-in
- **high**, Ch6: `game/levels/ch06/brine_shoals/brine_shoals.tscn`: wrights is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule/tamsule.tscn`: board is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule/tamsule.tscn`: boatman is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule/tamsule.tscn`: child is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule/tamsule.tscn`: fisher is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule/tamsule.tscn`: kerrid is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule/tamsule.tscn`: liss is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule/tamsule.tscn`: netmender is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule/tamsule.tscn`: tavi is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule/tamsule.tscn`: trader_boatman is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule/tamsule.tscn`: vendor is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn`: ione is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn`: kerrid is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn`: liss is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn`: oruvel_diver_1 is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn`: oruvel_diver_2 is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn`: poolkeeper is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn`: sorrin_diver_1 is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn`: sorrin_diver_2 is a capsule stand-in
- **high**, Ch7: `game/levels/ch07/tamsule_bell_galleries/tamsule_bell_galleries.tscn`: tavi is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/coilspire/coilspire.tscn`: fenn is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/coilspire/coilspire.tscn`: liss is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/coilspire/coilspire.tscn`: tender is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: boy is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: child_a is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: child_b is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: child_c is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: fisher_a is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: gatekeeper is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: hobb is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: ivo is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: kerrid is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: liss is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: marra is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: netmender is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: stillguard_a is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: stillguard_b is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: townsfolk_a is a capsule stand-in
- **high**, Ch8: `game/levels/ch08/corrow/corrow.tscn`: townsfolk_b is a capsule stand-in
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: child is a capsule stand-in
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: fenn is a capsule stand-in
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: hobb is a capsule stand-in
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: kerrid is a capsule stand-in (variant ch09_pell_joined)
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: kerrid_stair is a capsule stand-in
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: liss is a capsule stand-in (variant ch09_pell_joined)
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: marra is a capsule stand-in
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: mourner_1 is a capsule stand-in
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: mourner_2 is a capsule stand-in
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: mourner_3 is a capsule stand-in
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: mourner_4 is a capsule stand-in
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: pell is a capsule stand-in (variant ch09_pell_joined)
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: stillguard is a capsule stand-in
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: tender is a capsule stand-in
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: vigil_asha is a capsule stand-in (variant ch09_pell_joined)
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: vigil_kerrid is a capsule stand-in (variant ch09_pell_joined)
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: vigil_liss is a capsule stand-in (variant ch09_pell_joined)
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: vigil_pell is a capsule stand-in (variant ch09_pell_joined)
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: vigil_rhen is a capsule stand-in (variant ch09_pell_joined)
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: vigil_toma is a capsule stand-in (variant ch09_pell_joined)
- **high**, Ch9: `game/levels/ch09/corrow_night/corrow_night.tscn`: vigil_ysolde is a capsule stand-in (variant ch09_pell_joined)
- **high**, all: `game/data/ui/battle_sandbox.json#kerrid`: party member kerrid has no battle actor (a capsule in battle)
- **high**, all: `game/data/ui/battle_sandbox.json#liss`: party member liss has no battle actor (a capsule in battle)

## Notes (integration-qa)
- 2026-10-29 ~23:40 integration-qa: **the audit lists nothing for this owner on lead/gate-big18** (full scan; 2 items
  in all, both env-art-b's). The owner can tick the boxes and send this to review (reviewer: qa).

## Review log

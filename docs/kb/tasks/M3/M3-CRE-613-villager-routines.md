---
id: M3-CRE-613
title: "Villagers alive: routines (work, chat pairs, glances, storm) and a one-node VillagerLayer that replaces the zone stand-ins"
role: character
status: doing
owner_session: "creatures (cloud session_01EbDaRQ5n7hpvwuRG6jEDQY, branch claude/creatures)"
reviewer: art
depends_on: [M3-CRE-610, M2-CHR-03]
milestone: M3
request-from: lead
---
## Goal
The human's playtest: "placeholder villagers", "parts look primitive". Haluna's villagers are still capsule
stand-ins on every branch, and FieldNpc only idles, talks and walks. Make Haluna (then every slice zone) feel
inhabited: villagers that work, chat in pairs, glance at the party and react to a storm, on the M2-CHR-03 bodies,
with the zone wiring reduced to one node for the zone owners (slice-polish, act1-chapters).

## Acceptance criteria
- [x] NpcLook head modifier (eased, no snap or overshoot, reach-limited) and FieldNpc attention priorities
- [x] Glances at a party that comes near; idle look-arounds
- [x] Chat pairs: face each other, take turns (never both), in bouts with quiet work between
- [x] Work: a work clip when the actor has one (requested, M3-CRE-614), the head on the work
- [x] Storm: per-villager reaction delay, hurry to shelter, brace and sky looks, walk home after
- [x] A talk ends when the player gets control back (no zone wiring)
- [x] VillagerLayer + game/data/world/npc/zones/ch02_haluna.json: all seven Haluna villagers placed
- [x] validate_npc (validate_data), tests (Godot and tools), review stage and four shots
- [ ] The zone owners add the node (slice-polish: haluna.tscn, GreyboxZone; act1-chapters: Act I zones)
- [ ] Work clips and hand props from characters (M3-CRE-614)

## Notes
- docs/kb/tech/field_npc.md "Routines" and "VillagerLayer".
- Haluna's ground under every route was probed against the zone's collision (Reed's chapel court is flat at
  2.70; the lane runs 2.16–2.21 along x).

## Review log

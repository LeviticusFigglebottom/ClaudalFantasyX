---
id: M3-CRE-656
title: "Villager runtime in the Act I greybox zones: VillagerLayer adopts a stage actor's villager model (Kell in Oruvel first)"
role: character
status: review
owner_session: "creatures (session_01EbDaRQ5n7hpvwuRG6jEDQY)"
reviewer: cinematics
depends_on: [M3-CRE-613]
milestone: M3
request-from: lead
---
## Goal
ADR 0041, the villager runtime half of the creatures scope. In the Act I greybox zones (Ch1, Ch4–Ch9), stage actors
stand as capsules until the characters track gives them bodies. A layout row's `model` (M2-FP-111) puts a villager
actor in its place, but GreyboxZone only loops its idle and breathing. Make such a villager alive like Haluna's
(glances, turning to talk, out-of-step idles, routines), with no change to the zones or their cutscenes.

## Done (2026-10-28)
- VillagerLayer: when a row's stand-in (a stage actor) holds GreyboxZone's `Model` and no FieldNpc yet, the layer
  wraps that very model in a FieldNpc inside the stage actor node (`_adopt_model`). Cutscenes still find the actor and
  its AnimationPlayer (HeroMotion.player_of searches down), and the micro-motion isn't doubled (add_micro_motion is
  idempotent).
- game/data/world/npc/zones/ch01_oruvel.json: Kell (`attach: child`, talk `Triggers/kell_stall`).
- Tests (tests/unit/test_villager_routines.gd):
  - test_a_greybox_actor_model_is_adopted_into_a_villager;
  - test_oruvels_kell_comes_alive_in_the_real_zone;
  - villager 27/0, ch01 14/0, field_npc 10/0.
- **Still needed: the zone has to add the layer.** GreyboxZone adds a WildlifeLayer for a location with data but no
  VillagerLayer. That is M3-CRE-657 (slice-polish's file).

## Next
As M3-CHR-100 and the chapter tasks give the Act I speakers and crowds bodies (layout `model`), add their rows to
`zones/<zone>.json` (attach child). The data is ours; the bodies and the layout rows are characters' and the chapters'.

## Review log

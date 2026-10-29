---
id: M3-CRE-657
title: "Request to slice-polish: GreyboxZone adds a VillagerLayer for a location with a villager zone file, as it does a WildlifeLayer"
role: cinematics
status: review
owner_session: "slice-polish (session_01F3vrUPLtDQMGSRrMHJtpz1)"
reviewer: creatures
depends_on: [M3-CRE-656]
milestone: M3
request-from: creatures
---
## Goal
ADR 0041. VillagerLayer can now bring a greybox stage actor's villager model alive (M3-CRE-656: Kell in Oruvel,
`game/data/world/npc/zones/ch01_oruvel.json`), but nothing in a greybox zone adds the layer.
`game/world/zone/greybox_zone.gd` (yours, M2-FP) already adds a WildlifeLayer (line ~252).

## Ask
In the same place, **after** `_build_stage()` has made the actors:

```gdscript
if FileAccess.file_exists(VillagerLayer.path_for(location_id)) and get_node_or_null(^"VillagerLayer") == null:
	VillagerLayer.wire(self, location_id)
```

(`wire` adds the node named `VillagerLayer`. Added after the zone is ready, it builds deferred and adopts the models.)
No layout or cutscene changes. Tests: tests/unit/test_villager_routines.gd
`test_oruvels_kell_comes_alive_in_the_real_zone` already wires the layer the same way on the real Oruvel.

## Update (creatures, 2026-10-28, after the Lead's rollout order)
- **Ready patch:** `docs/kb/handoffs/live/patches/m3-cre-657-greybox-villagers.patch` (`git apply`, 14 lines). It adds `_build_villagers()` to GreyboxZone, called at the top of `_ready()`, and does nothing for a location without a villager zone file.
  - **Why `_ready` and not `build()`:** `_ready` runs after every child's, so ZoneCast (M3-CIN-1217) has cast its villagers by then. Added in `build()`, the layer built first and the tender got two bodies.
- **What it does to ZoneCast's casts** (creatures' side, merged on claude/creatures):
  - A crowd row's person replaces the actor's `Cast`. ZoneCast dresses the generic folk as Haluna's villagers, and ADR 0152 says Haluna's faces stand for no other town.
  - A named villager's row adopts its `Cast` as it does a greybox `Model`.
  - `HeroMotion.player_of(actor)` finds the new body, so the cutscenes' `@anim` lines still play.
- **Trial on claude/creatures with the patch applied:**
  - villager 35/0;
  - qa_capsules: Pell only (Act II);
  - **test_zone_cast** (cinematics') fails on Tamsule's fisher and boatman. Its live check reads the actor's `Cast`, which the crowd person has replaced. Its owner should check `HeroMotion.player_of(actor)` plays `idle`, or pick an actor with no villager row. Apply both changes together.

## Review log

## Done (slice-polish, 2026-10-28)
- Applied `m3-cre-657-greybox-villagers.patch` on claude/m2-slice (GreyboxZone `_build_villagers()` in `_ready`).
- test_zone_cast reads the actor's body through `HeroMotion.player_of(actor)` (the Cast or the crowd person).
- Checks: zone_cast 3/0, ch01 21/0, zone_story 15/0; lint and format clean. The villager filter shows 3 failures
  and an abort identically with and without the patch (test_villager_routines on this tree, creatures').


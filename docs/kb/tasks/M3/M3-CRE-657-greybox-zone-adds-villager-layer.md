---
id: M3-CRE-657
title: "Request to slice-polish: GreyboxZone adds a VillagerLayer for a location with a villager zone file, as it does a WildlifeLayer"
role: cinematics
status: todo
owner_session: ""
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

## Review log

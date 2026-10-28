---
id: M3-CRE-658
title: "Request to act1-chapters: Brine Shoals' hound stands as the raid hound model (M3-HER-1142's row), one layout line"
role: narrative
status: todo
owner_session: ""
depends_on: [M3-CRE-655]
milestone: M3
request-from: creatures
---
## Goal
ADR 0041 inventory row (M3-HER-1142, creatures): `game/levels/ch06/brine_shoals/brine_shoals.tscn`, *hound is a
capsule stand-in*. The Order's shoal-hound has its real model, the raid hound the party fights in `ch06_inquisitor`.
As of 2026-10-28 a creature battle scene can stand on a greybox stage like a villager body (CreatureActor.play_clip
takes HeroMotion's blend; tests/unit/test_creature_vfx_anchors.gd `test_a_creature_plays_as_a_field_stage_model`).

## Ask (game/levels/ch06/**: yours)
In `game/levels/ch06/brine_shoals/brine_shoals_layout.json` `actors.hound`, add:

```json
"model": "res://game/creatures/raid_hound/raid_hound_battle.tscn"
```

Keep `at`. Turn its yaw if it should face the inquisitor: the model faces +Z, so yaw 180 faces −Z. That's the
whole change. The hound's polished body (M3-CRE-655) lands on the same scene path, so nothing else changes later.

## Note on the other row
*inquisitor is a capsule stand-in* is routed to creatures by the audit's name list, but it is **Inquisitor Hadric
Moll, a person**: the characters track's body (M3-CRE-625, M3-C06-06 item 3). Creatures has asked integration-qa to
route it to characters.

## Review log

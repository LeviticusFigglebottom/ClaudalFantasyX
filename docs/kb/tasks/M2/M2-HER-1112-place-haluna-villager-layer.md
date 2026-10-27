---
id: M2-HER-1112
title: "Put the VillagerLayer in Haluna so its villagers are never frozen (request to slice-polish)"
role: narrative
status: todo
owner_session: ""
depends_on: [M3-CRE-610]
milestone: M2
request-from: combat
---
## Goal
The human's playtest note: the villagers looked like placeholders and stood frozen. Creatures built the whole villager
motion layer (M3-CRE-610/613, on claude/creatures): FieldNpc on the hero motion layer (HeroLocomotion eased turns and
gait, HeroIdleMicro, NpcLook look-at), and a VillagerLayer that turns Haluna's stand-ins into those villagers from
`game/data/world/npc/zones/ch02_haluna.json`. **No zone places it yet**, so Haluna would still show the stand-ins
after creatures merges.

## Acceptance criteria
- [ ] Once claude/creatures is on the integration branch, haluna.tscn gets one node at its root (docs/kb/tech/field_npc.md
      "VillagerLayer"): a Node3D `VillagerLayer` with `script = villager_layer.gd`, `zone_id = &"ch02/haluna"`. Or the
      zone script adds it in code; that's the zone owner's choice.
- [ ] haluna and zone filters green; the Haluna field shots that show villagers re-captured, viewed, re-approved.
- [ ] `tests/unit/test_villager_snaps.gd` (hero track) still passes. It builds the layer itself, so it doesn't depend on
      the node.

## Notes
- Hero-integration ran the snap guards on a local trial merge (hero-integration + creatures, never pushed) on
  2026-10-27: all 7 Haluna villagers through their routines plus a visit (approach from behind the shoulder, talk,
  leave). Nobody snaps; turns ease at 110–200 deg/s. All 42 clip changes (idle, talk and walk pairs, at FieldNpc's
  blends) stay at half the pop limit or less.
- haluna.tscn is m2-slice's (slice-polish's) zone, so the hero track doesn't edit it.

## Review log

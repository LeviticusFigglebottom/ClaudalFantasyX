---
id: M3-HER-1117
title: "Villagers' feet on uneven ground: opt FieldNpc into HeroFootIK (request to creatures)"
role: character
status: todo
owner_session: ""
depends_on: [M2-HER-1116, M3-CRE-610]
milestone: M3
request-from: combat
---
## Goal
The heroes' field bodies now carry foot IK (HeroFootIK, M2-HER-1116). On a slope or a step one foot is lifted onto the
floor and the hips drop for the lower one; flat ground is left exactly as the clip made it. Haluna's villagers stand
and walk on the same terrain, and their rigs are the same DEF chain.

## Acceptance criteria
- [ ] In FieldNpc `_attach_actor()`, after `HeroMotion.add_micro_motion(actor, npc_id)`: `HeroMotion.add_foot_ik(actor)`.
      If the villager's stand-in body carries a collider, set the modifier's `exclude` to its RID.
- [ ] tests/unit/test_villager_snaps.gd (hero track) still passes; the npc_haluna_* shots re-rendered on the PC and
      viewed.

## Notes
- API: `HeroMotion.add_foot_ik(actor) -> HeroFootIK` (idempotent), `HeroFootIK.exclude: Array[RID]`. Tuning:
  game/data/hero_motion/foot_ik.json.

## Review log

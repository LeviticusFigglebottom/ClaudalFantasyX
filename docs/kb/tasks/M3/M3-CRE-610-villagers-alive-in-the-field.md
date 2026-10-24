---
id: M3-CRE-610
title: "Haluna's villagers alive in the field: idle loops, talk gestures, eased turn-to-face, ambient walk routes"
role: character
status: doing
owner_session: "creatures (cloud session_01CYks9e592YBEfygyTawcJD, branch claude/creatures)"
reviewer: art
depends_on: [M2-CHR-03, M2-HER-1101]
milestone: M3
request-from: lead
---
## Goal
The human's playtest note ("parts look primitive / placeholder"): villagers stand static or as stand-ins. Give the
villager actors (claude/characters' M2-CHR-03 models, idle/talk/walk clips) a field behaviour layer: idle loops
offset per villager, a talk gesture when spoken to, an eased turn to face the player (never snapping; reuse
hero-integration's HeroLocomotion turn and HeroIdleMicro, not a copy) and short ambient walk routes.

## Acceptance criteria
- [ ] FieldNpc (game/world/npc/): idle, talk-on-interact, eased face-the-player and back, walk routes with pauses
- [ ] Data-driven tuning (game/data/world/npc/), tests, a review scene and shot
- [ ] Handed to m2-slice (who places villagers in the zones) with a one-node integration note

## Notes
- Depends on hero-integration's game/hero_motion reaching the integration branch; built against it locally and
  landed after it merges.

## Review log

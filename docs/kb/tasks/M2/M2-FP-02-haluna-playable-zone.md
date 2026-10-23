---
id: M2-FP-02
title: Playable Haluna zone (player, collision, camera volumes, villagers, shrine, triggers)
role: environment
status: doing
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M1-ENV-01, M1-ARC-06]
milestone: M2
request-from: lead
---
## Goal
`game/levels/ch02/haluna/haluna.tscn`: the Environment-owned mood scene instanced (not edited) with a player, terrain and building collision, camera volumes, spawns, 3 talkable villagers, the save shrine, a scripted battle trigger and the causeway-head trigger, plus a CutsceneStage for Cutscene A.

## Acceptance criteria
- [ ] Rhen (placeholder) walks the beach, lanes and court with collision, under authored camera volumes.
- [ ] Spawns: Beach, Shrine, Village, BattleReturn, CausewayHead. `locations.json` row `ch02/haluna` points at the new scene and is playable.
- [ ] Three villagers with short bark scenes (the B03 "Cantor" fragments).
- [ ] Tests: the zone loads, the player stands on ground at every spawn, interactables fire their payloads.

## Review log

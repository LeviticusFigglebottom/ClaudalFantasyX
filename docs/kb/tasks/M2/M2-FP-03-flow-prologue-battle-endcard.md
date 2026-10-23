---
id: M2-FP-03
title: First-playable flow - prologue, New Game routing, battle hand-off and return, end card
role: architect
status: doing
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M1-ARC-06, M1-CMB-08]
milestone: M2
request-from: lead
---
## Goal
New Game → Prologue (Rhen's narration over the dead city) → Haluna beach; a field battle request that opens the CTB battle and returns to the field spawn; an end card after the Ch3 first verse that returns to the title.

## Acceptance criteria
- [ ] `locations.json` new_game goes to the prologue; the prologue hands off to `ch02/haluna` at Beach.
- [ ] `BattleRequest` + a field battle scene (instancing, not editing, the battle sandbox) that returns to the requesting location and spawn on victory or escape.
- [ ] End card scene with a loc-keyed message; accept returns to the title.
- [ ] Integration tests for each hand-off.

## Review log

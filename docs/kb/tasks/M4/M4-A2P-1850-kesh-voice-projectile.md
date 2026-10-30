---
id: M4-A2P-1850
title: "Request (creatures-b): Kesh's voices fly one shared pale orb that casts a shadow; let each voice's element read in flight"
role: combat
status: todo
owner_session: ""
reviewer: character
depends_on: [M4-A2P-061]
milestone: M4
request-from: creatures-b
---
## Goal
The agreed effects split (creatures-b's log, 15:00): battle-presentation owns the effect data, and creatures-b views
it on the bodies. Kesh's summon pass on big29 (ch12_avalanche_ram, every voice used; the sweep's impacts check found
no missing effect) shows:
1. **Every voice flies the same pale blue orb** (Ice, Holy, Glimmer, Water alike; Fire and Lightning too, by their
   frames). The element only reads on impact, where `voice_*` in effects.json are distinct. Kesh's whole kit is
   "which element is coming" (her element cycle, ADR 0204 §7; pillar 4: the player knows what's coming), so the
   projectile is the moment it should already read: the voice's own colour in flight (the swatches its impact uses).
2. **The orb casts a shadow** on the arena floor, a dark smear beside it that reads as a second, dark projectile.
   BattleVfx turns shadows off on its particles (battle_vfx.gd `cast_shadow = SHADOW_CASTING_SETTING_OFF`); the
   travelling orb doesn't seem to.
The bodies are fine: the orbs leave from her hands, and the impacts sit on the target's chest.

## Acceptance criteria
- [ ] Each Kesh voice's projectile carries its own element's colour.
- [ ] No travelling projectile casts a shadow.
- [ ] creatures-b re-views it on the next sweep (the review log below).

## Review log

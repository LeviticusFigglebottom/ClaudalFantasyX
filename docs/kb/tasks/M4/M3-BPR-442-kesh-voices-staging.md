---
id: M3-BPR-442
title: "Request: stage Kesh's six voices, The Seven and the cycle's next-element mark"
role: combat
status: todo
owner_session: ""
depends_on: [M4-A2P-025]
milestone: M4
request-from: cinematics
---
## Goal
To battle-presentation (with UI for the timeline mark). M4-A2P-025 lands Kesh's data and her cycle (BattleCycle):
- **Skills:** `voice_water`, `voice_lightning`, `voice_fire`, `voice_ice`, `voice_holy`, `voice_glimmer`, and the
  Swell finisher `the_seven`.
- **The Vowbound row:** `kesh` (caller Asha, `ch16_kesh_bound`).
- **The rule:** her `cycle` allows only this turn's voice, and the menu greys the others with
  `HUD_FAIL_OUT_OF_CYCLE`.
- **The telegraph:** each of her coming TurnEntries carries that turn's voice as `intent`.

## Acceptance criteria
- [ ] VFX map rows for the seven skills: kesh.md §4's clips (`voice_*`, `special`); the element colours are effects.json's.
- [ ] The timeline chip shows the element of `TurnEntry.intent` for a cycling combatant (UI). Pillar 4: the next voice
      is visible.
- [ ] The Seven's finisher staging (kesh.md §4: she rises 1 m on the column, all six at once, then a seventh note).
- [ ] The summon cinematic stays M4-A2P-061.

- Remove the `voice_glimmer` and `tide_gather` entries from tools/battle_vfx_coverage.py's INTENDED map once their
  effects land.

## Review log

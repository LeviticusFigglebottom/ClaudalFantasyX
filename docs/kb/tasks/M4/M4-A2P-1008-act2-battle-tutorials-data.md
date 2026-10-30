---
id: M4-A2P-1008
title: "Request: wire the Act II battle tutorials, and the mechanics they describe (combat data)"
role: progression
status: todo
owner_session: ""
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To act1-chapters' combat seat (`game/data/battle/encounters.json`, `enemies.json`, `skills.json`). This comes from the
Lead's Act II tip and tutorial clarity pass. **No Act II `TUT_*` key is referenced by any encounter, enemy or phase**
(no `prompt_key` or `turn_prompt_key`), so none shows. Story has rewritten them to match what's built, or the beat
sheets' design where nothing is built (commit on claude/act2-plan).

**One general issue first.** A `prompt_key` has no seen flag (`battle_boss_hud.gd:60`). On a random group (for example
`ch10_fen_roots`) it would show in every one of those fights. Act II's tutorials sit on random groups, so they need a
seen flag, or a placed one-off first fight as Act I does (`ch03_causeway_harrier`).

| # | Key | Where to raise it | Mechanic gap (if any) |
|---|---|---|---|
| A5 | `TUT_CH10_ROOTED` | the first `ch10_fen_roots` fight | — (text now matches Root Drag: two turns, two ranks) |
| A11 | `TUT_CH10_DRAIN` | the first `ch10_fen_leeches` fight | — |
| A3 | `TUT_DROWNER_ROOTS` | `ch10_mangrove_drowner` | **The two breakable root clusters aren't built** (`enemies.json:333`: no `parts`; act2_ch10 §5). The text keeps the design |
| A6 | `TUT_LAMP_ENGINE_CRAWLERS` | `ch11_lamp_engine`, at the first Lamps Turning | `crawler_mend` (`skills.json:295`) is instant; act2_ch11 §5 wants a telegraphed 2-turn repair (pillar 4) |
| A9 | new key (story will add the row): "Gallery rays rise out of reach after one turn and come down after the next. Strike them while they're low." | the first `ch11_vey_rays` fight | — |
| A12 | `TUT_CH12_UNRAVEL` | the first `ch12_pass_moths` fight | — |
| A4 | `TUT_RAM_FIELD` | `ch12_avalanche_ram` | **No scree field** (`field_rules`, `clears_field`); the text keeps the design (scree, not snow: act2_consistency P2) |
| A7 | `TUT_WAKEFIN_DARK` | `ch15_wakefin`, on its first Sound Dive | — (the darkness and sound mechanics aren't built; the text now teaches the telegraph) |
| A15 | `TUT_CH14_HOLD_STEPS` | `ch14_water_steps` | **The encounter isn't built** (act2_ch14 §5a) |
| A16 | `TUT_MALCOR_ENGINE` | `ch14_malcor_venn` | **Not built**: Malcor Venn, the flat-engine, Liss's Strip the Drum |
| A17 | `TUT_CH16_HOLD_LINE` | `ch16_storm_wakes` | **Not built** (act2_ch16 §5b) |
| A10 | new key: "Glass skates lie buried until each has struck once. Then they can be hit." | the first `ch16_rim_skates` fight | — |
| A14 | `TUT_CH10_LISTEN` | `ch10_fen_archers`, Pell's first turn | **Pell and Listen aren't built** (`characters.json`, `skills.json`; M3-C09-07) |
| A2 | `TUT_CH16_CYCLE` (now about Kesh) | Kesh's first call | **Kesh's Call appears in Ch16 as soon as `ch16_kesh_bound` is set**, though vowbound.md says "called from Act III" (`battle_vowbound_hud.gd:42-54`) |

Story has fixed `LORE_ABIDING_GUARD` (it said "three hooded figures"; act2_ch16 §5a has four guards plus the
Veil-First).

## Acceptance criteria
- [ ] Each built mechanic's tip shows once, at first meeting.
- [ ] Each mechanic gap built, or answered here with a reason.

## Review log

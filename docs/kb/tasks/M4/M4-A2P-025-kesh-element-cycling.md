---
id: M4-A2P-025
title: "Kesh: the element-cycling Vowbound, with each shift telegraphed on the timeline"
role: combat
status: review
owner_session: act1-chapters
depends_on: [M4-A2P-057]
reviewer: progression
milestone: M4
request-from: lead
---
## Goal
Kesh cycles through all six elements by phase. Add the cycling rule (data: an element per phase or per N turns), its timeline telegraph, her `vowbound.json` row (`ch16_kesh_bound`) and skills, and her Swell *The Seven*. The same rule serves her Act III fight.

## Acceptance criteria
- [ ] Engine rule and tests; her row and skills; pillar 4 (the next element is visible).
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch16, §4.6.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- **act1-chapters (the chapters combat seat, ADR 0205), 2026-10-30:**
  - **BattleCycle** (game/battle/battle_cycle.gd): a `cycle` row key (vowbound, characters or enemies) lists one skill
    per element, in order.
    - Only the current one may be used (FAIL_OUT_OF_CYCLE), and the AI skips the others. Skills outside the cycle
      stay free.
    - It moves on at the end of every own turn it acts.
    - The timeline gives each coming turn its voice as `TurnEntry.intent` (pillar 4). The menu greys the others with
      `HUD_FAIL_OUT_OF_CYCLE`.
    - The same rule serves Act III's enemy Kesh: an enemies.json `cycle`, which EnemyAI respects.
  - **Data, PROVISIONAL** (no Act II fight calls her; band her with Act III's suite):
    - Six `voice_*` skills in the pilgrimage's order: Water, Lightning, Fire, Ice, Holy, Glimmer.
    - Her Swell `the_seven`.
    - The `kesh` Vowbound row: caller Asha, bound flag `ch16_kesh_bound` (declared; the Ch16 flow sets it at C4).
    - The names in ch16.csv.
  - **Open (with kesh.md):** the voices have no multi-hit (fire's three hits) and no defence-ignoring lightning keys
    yet. Their notes say so.
  - **Validator:** a `cycle` must list distinct skills of the row's own.
  - **Tests:** tests/unit/test_battle_cycle.gd (5), plus battle_engine, timeline, vowbound, swell, boss, set_piece,
    sim, hud, parts and cover.
  - **Staging and the timeline mark:** M3-BPR-442.

## Review log

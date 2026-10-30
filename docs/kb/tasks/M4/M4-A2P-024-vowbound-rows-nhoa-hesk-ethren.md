---
id: M4-A2P-024
title: "Nhoa, Hesk and Ethren in vowbound.json: stats, skills, Swells, bind flags"
role: combat
status: review
owner_session: act1-chapters
depends_on: []
reviewer: progression
milestone: M4
request-from: lead
---
## Goal
The three models exist (`vowbound_pending`). Add their rows (caller Asha, `bound_flag` `ch11_nhoa_bound`, `ch12_hesk_bound`, `ch13_ethren_bound`), skills and Swells from vowbound.md (Nhoa copies the last enemy action; Hesk cleanses and mends; Ethren slows, stops and wards; finishers Farewell-Tide, Pass-Cord, Still Water), and their clip maps.

## Acceptance criteria
- [ ] Rows, skills, loc, tests; the summon-path tests drop `vowbound_pending`; the summon menu lists six.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §4.4.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- **act1-chapters (the chapters combat seat, ADR 0205), 2026-10-30:**
  - **Rows, PROVISIONAL** (caller Asha; banded once Asha can call them in Act II's boss suites):
    - `nhoa` (Ice, `ch11_nhoa_bound`): Silt Fall, Deep Well, Echo, Farewell-Tide.
    - `hesk` (Holy, `ch12_hesk_bound`): Knot-Light, Cord Lift, Mending, Pass-Cord.
    - `ethren` (Glimmer, `ch13_ethren_bound`): Level Hand, Hold the Hour, Lacquer Screen, Still Water.
  - **The echo:** "copies the last enemy action" is an engine rule, BattleEcho. A skill with `echo: true` resolves as
    BattleEngine.last_foe_skill's row, from her, at her own rank and cost, never copying a charge, summon, field or
    Swell. With nothing to echo yet it's refused (HUD_FAIL_NOTHING_TO_ECHO).
  - **Flags:** the bound flags and the first-call seen-flags are declared. choreo.json `first_call_flags` covers
    the four (Kesh too).
  - **Clip maps:** creatures.json `clip_by_skill`.
  - **Pending keys:**
    - Their creatures.json `vowbound_pending` keys are dropped, as validate_data asks once a row exists.
      tools/tests/test_creatures.py now tests that path on a table without Nhoa's row.
    - The rows carry `sfx_pending: M4-AUD-1010` until audio voices them. test_vowbound_sfx skips them until then and
      checks that the key names a task.
  - **Tests:** tests/unit/test_battle_echo.gd; vowbound, summon, creature and battle suites; tools vowbound,
    creatures, vfx_coverage.
  - **Requests:** M4-AUD-1010 (voices) and M3-BPR-443 (effects).

## Review log

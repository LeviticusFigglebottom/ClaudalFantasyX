---
id: M4-A2P-023
title: "A part only one hero breaks: Liss and the flat-engine"
role: combat
status: doing
owner_session: act1-chapters
depends_on: []
reviewer: character
milestone: M4
request-from: lead
---
## Goal
Malcor Venn's phase 1 ends when Liss breaks the flat-engine. Add the targeting rule (a part answerable by a named hero's skill, or a lent skill like Ch8's) and the charge skill M3-CRE-637's `break_parts` needs. The engine's slow pulse is an `entries` row (role `tide`) so the timeline shows it.

## Acceptance criteria
- [ ] Engine rule, skill rows, validator, tests; the flat-engine's `break_parts` validate.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch14; act2_roster's open question (plan default: a part, not its own combatant).
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- **act1-chapters (the chapters combat seat, ADR 0205), 2026-10-30: the engine is in.**
  - **The targeting rule:** enemies.json `answered_by: <hero>` with `answered_key` (BattleParts.may_strike). Only
    that hero may act on the foe. It's off everyone else's `living_foes_of` and target lists, so the sim and the
    menus follow. A group skill passes over it and is never refused.
  - **The phase:** phase rows take `when_down: <enemy id>`, so Venn's `boarded` comes on the engine's break or at
    50%, whichever is first.
  - **Validator:** `answered_by` must be a hero; `when_down` must be an enemy; `when_down` is in BOSS_PHASE_KEYS.
  - **Tests:** tests/unit/test_battle_answered_part.gd (3). battle_engine, boss, set_piece, sim, cover, parts,
    rooted and drain are all green.
  - **The plan default is kept: the flat-engine is its own combatant** with `answered_by: liss`, so the timeline shows
    it and its pulse. It doesn't need a lent skill: any of Liss's offensive skills breaks it.
  - **Still to do (data):**
    - The `malcor_venn` and `flat_engine` rows, `flat_pulse` (a `field_rules` Slow), and the tide `entries` row.
    - The suite.
    - These wait on the characters pipeline's Venn and story's beat sheet (M4-C14-01).
  - **The cursor readout:** added to M3-UI-1241.

## Review log

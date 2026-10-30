---
id: M4-A2P-020
title: "Rooted: a status that refuses the swap (the root crab's Root Drag)"
role: combat
status: review
owner_session: act1-chapters
depends_on: []
reviewer: progression
milestone: M4
request-from: lead
---
## Goal
act2_roster gives `root_crab` a skill that **roots** one hero: no swap while it lasts. Add the status (name it in our own words), its engine rule (the swap refusal with a reason key, like `locked_active`'s), its HUD glyph request, and set it on `root_drag`.

## Acceptance criteria
- [ ] Engine rule and tests in `tests/unit`; formulas.md only if a formula changes.
- [ ] Pillar 4: the swap row says why it is refused.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §4.6.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

- **act1-chapters (the chapters combat seat, ADR 0205), 2026-10-30:**
  - **A skill effect, not a status** (act2_plan §4.6 allows either). SPEC §6.8's status set, validate_data's
    CANON_STATUSES and the 21-glyph HUD test stay as they are, so no ADR is needed.
  - **The rule:** `root_turns` on a skill row sets `BattleCombatant.rooted_turns` (a longer hold wins). It counts down
    at the end of each own turn. While it's above 0, `BattleEngine.swap_refusal` returns `FAIL_ROOTED` for a living
    hero on the field. The swap help line says "… can't leave the line: held by the roots." (`HUD_SWAP_ROOTED`,
    ch10.csv).
  - **Data:** `root_drag` roots for 2 turns. `ch10_fen_roots` re-run at 1,000 seeds: naive 33.8, role 93.9, smart
    99.9, all in band.
  - **Tests:** tests/unit/test_battle_rooted.gd (4); battle_engine, hud and set_piece are green; validate_data checks
    `root_turns`. No formula changed.
  - **The HUD marker** is requested as M3-UI-1240.

## Review log

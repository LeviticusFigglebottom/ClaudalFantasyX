---
id: M1-CMB-02
title: Implement remaining statuses (Petrify, Berserk, Confuse, Doom, Zombie, Reflect, Provoke)
role: combat
status: review
owner_session: combat-stream-2
reviewer: progression
depends_on: [M1-CMB-00]
milestone: M1
request-from: ""
---
## Goal
Every status in statuses.json has implemented: true.

## Acceptance criteria
- [x] Each status has behaviour, a test, and a formulas.md entry where numeric
- [x] Timeline preview stays honest for any time-affecting status

## Notes
Delivered (rules: `docs/kb/design/formulas.md` § Statuses; engine API: `battle_ctb.md` § Rules and § Timeline API):
- All 21 statuses have `implemented: true`. The validator warning about `skills.challenge` is gone, and there are 2 new validator checks: Petrify must be −1, and Doom needs a countdown of at least 1.
- **Petrify** counts as KO (`is_alive()` false): timeline, targeting, outcome, XP, swap-in timing. **Berserk/Confuse** take control on either side: `run_enemy_turn()` plays the basic attack with seeded target picks, `perform()` refuses with `auto_turn`, and `is_party_turn()` is false. **Doom** counts own turns, lost turns included, with `TurnEntry.doom` on the timeline. **Zombie** inverts heal skills and Regen. **Reflect** bounces single-target magic deterministically to the lowest-HP unit on the other side, without chaining, and the preview follows the bounce. **Provoke** forces single-foe targets for AI and player (`forced_target()`; the engine rejects other targets as `provoked`).
- New constants `BERSERK_STR_RATIO` (3/2) and `CONFUSE_ALLY_PCT` (50) in `formulas.gd`, tested in `tests/unit/test_status_effects.gd` (39 tests) and `test_ctb_timeline.gd` (+6).
- Also delivered: `BattleEngine.preview_swap(out_id, in_id, count)` for the UI stream. It mutates nothing, follows the same rule as `swap()`, and is tested against both `preview()` after the swap and the turns actually played.
- Also delivered: ADR 0012 (hero `level` is one fixed constant).
For review (Progression): the Zombie rule ("revival KOs") and Petrify cures are waiting on items. Check that the cure and revive formulas fit when they land.

## Review log

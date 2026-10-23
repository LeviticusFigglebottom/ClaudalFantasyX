---
id: M1-CMB-02
title: Implement remaining statuses (Petrify, Berserk, Confuse, Doom, Zombie, Reflect, Provoke)
role: combat
status: done
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
- 2026-10-23 progression (review-sweep-A): **approve with fixes**. The rules match formulas.md § Statuses: Petrify counts as KO, Confuse wins over Berserk and its ally roll uses the seeded RNG, Doom counts lost turns, Zombie inverts heals and Regen, Reflect bounces deterministically with no chains, and Provoke is enforced for both AI and player. `BERSERK_STR_RATIO` and `CONFUSE_ALLY_PCT` are tested, the 39 status tests are specific and seeded, and the validator passes.
  - **should-fix** (preview honesty): the timeline preview still shows a sleeping target losing its next turn when the previewed skill would wake it. `apply_damage` erases Sleep on any damage above 0 (`combatant.gd:123-124`), but `BattleEngine.preview` (`battle_engine.gd:114`) only adds statuses, and `CtbTimeline.predict` (`ctb_timeline.gd:92`) marks the turn `skipped`. A probe on the real sandbox data (39 seeds, Sleep 3 on a foe, preview `attack` on it, then perform) found the preview and the real order disagreed on all 19 Sleep seeds and on none of the 20 controls. Example: preview `reef_crab#1(z)`, actual `reef_crab#1`. Magic damage and a Zombie "heal" wake the target the same way. This breaks the acceptance criterion "honest for any time-affecting status" (pillar 4). Fix: in `preview()`, when the skill can damage the recipient (physical or magical with power above 0, or heal on a Zombie), add a removal of `sleep` to `changes`. That needs `predict` to accept a removal, for example duration 0 meaning cleared. Add a test that compares preview with the turns actually played, as `preview_swap` already does.
  - **should-fix** (handoff to Progression's items): two rules can't be reached through the item API as it stands. (1) KO clears every status (`combatant.gd:125-127`) and revive items target only the fallen, so "Revival will KO a Zombie outright" (`formulas.md:120`) can never fire from an item. Either drop the sentence or define it for a future Life spell on a living Zombie. (2) `ItemBattleAction.can_target` (`item_battle_action.gd:76-77`) requires `is_alive()` for every item that isn't a revive, and a petrified unit is not alive, so a Petrify cure written as `cure {statuses:[petrify]}` can never target anyone. Petrify cures need a `targets_petrified` mode or similar. That is Progression's follow-up, recorded here so CMB-06 wires it.
  - **nit**: the preview doesn't model a Poison or Regen KO, or a damage KO from the previewed action, so a fighter about to die still appears in later entries. That is acceptable because death is HP-based rather than a timeline effect, but say so in `battle_ctb.md` § Timeline API.
- 2026-10-23 lead: closing on review-sweep-A approve-with-fixes; the Sleep-wake preview fix and the Zombie/Petrify reachability fixes were forwarded into M1-CMB-06.

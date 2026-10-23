---
id: M1-CMB-07
title: Engine item previews and sweep-C combat nits
role: combat
status: review
reviewer: ui
owner_session: "worktree-agent-a6210d9196b16c99a"
depends_on: [M1-UI-04]
milestone: M1
request-from: "ui"
---
## Goal
Follow-ups from M1-UI-04's handoff (docs/kb/handoffs/2026-10-23-ui-1.md) and CMB-06 sweep-C nits.

## Acceptance criteria
- [x] item_defeats_party (and the timeline preview) predict a Zombie's self-KO from a heal item, not only from revives
- [x] delays_taken resets when a unit rejoins the active party
- [x] Smart-policy balance bands get a ceiling
- [x] Tests for each; coverage of game/battle/ does not drop

## Notes
- 2026-10-23 combat (worktree-agent-a6210d9196b16c99a, branch `combat/M1-CMB-07-item-preview-followups`):
  - **AC1.** `BattleEngine.item_leaves_standing` / `item_downs` (static, Node-free) run the item's effects in order on a new `BattleCombatant.sim_copy()`. Items use no RNG, so the result is exact. `preview_item` sets FALLS from `item_downs`, so a heal that KOs a Zombie (ally or self) leaves the order. `item_defeats_party` now asks whether anyone in the active party stands after the item, which also fixes M1-UI-04 sweep E's group-revive false warning. A last foe felled first returns false.
  - **AC2.** `delays_taken` is 0 after a revive or a petrify cure. A swap-in takes a living leaver's count with its slot and starts at 0 for a fallen one (formulas.md § Time).
  - **AC3.** A win ceiling can't work (smart = 100.0%), so there is an ease ceiling instead: targets.json `mean_turns_min`, smart ≥ 16 (`sandbox_reef`) and ≥ 14.5 (`sandbox_reef_tier1`). It is checked in `sim.py` `in_band` and the Band column, and asserted at 200 seeds in test_sandbox_battle.gd. balance_targets.md has the rationale. The report was regenerated; every number is unchanged bit-for-bit.
  - **AC4.** tests/unit/test_battle_item_outcomes.gd (13), the integration ease-ceiling test, and tools/tests/test_balance_sim.py (6). Handoff: 2026-10-23-combat-1.

## Review log

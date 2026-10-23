---
id: M1-UI-04
title: economy.md refresh and self-revive warning
role: ui
status: review
reviewer: combat
owner_session: "worktree-agent-aa5733be52ed5e16a"
depends_on: [M1-CMB-06]
milestone: M1
request-from: "progression"
---
## Goal
Review-sweep-C follow-ups on CMB-06.

## Acceptance criteria
- [x] economy.md revive/petrify targeting rules updated to the merged behaviour
- [x] Item menu warns when a Zombie targets itself with a revive while it is the last one standing

## Notes
From review-sweep-C (see the source tasks' Review logs for file:line).

- 2026-10-23 ui (worktree-agent-aa5733be52ed5e16a): economy.md has a new § Targeting in battle, read from `battle_engine.gd` and `item_battle_action.gd`. The battle UI had no item menu, so this adds the **Items** command (item list, then target, then `use_item`) with the `preview_item` preview. `BattleEngine.item_defeats_party()` and `item_fells()` are Node-free, and `_resolve_item_on` now uses `item_fells`. When `item_defeats_party` is true, the help line is `HUD_HELP_ITEM_DEFEAT_FMT` alone, in the danger role, on hover and on the target. It warns and does not block. To stay under gdlint's 1000-line cap, the controller was split with no behaviour change (`BattleCaptureScript`, `BattleMenus` targeting rules, `BattleStage.lattice_for`). Tests: `tests/unit/test_battle_item_menu.gd`. Follow-up for Combat: a heal item that KOs a Zombie on itself while it is the last one standing is flagged as harm, but the KO is not predicted. See handoff 2026-10-23-ui-1.

## Review log

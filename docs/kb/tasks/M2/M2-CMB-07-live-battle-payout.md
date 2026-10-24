---
id: M2-CMB-07
title: Live battles pay out lume and drops (M2 blocker), with the victory panel listing them
role: combat
status: review
owner_session: worktree-agent-aa4303cb02313a538
reviewer: lead
depends_on: [M1-CMB-06, M1-PRG-02]
milestone: M2
request-from: "lead"
---
## Goal
M2 blocker. `BattleEngine.currency_award()` and `drop_awards()` are computed at victory, but only the balance simulator reads them: a live battle never pays, so the purse stays at 0 and the shop and inn (M2-UI-06) are unusable.

## Acceptance criteria
- [x] At a live victory (`persist_progress` on, no capture fixture) the engine's lume goes into the purse (`Wallet.earn`) and its drops into the bag (`Inventory.add`), through `PartyGoods` over `Game.state`, exactly once per battle. Escape and defeat pay nothing. Fixtures and tests never touch the save.
- [x] The victory panel lists the lume (and the purse after it) and one row per dropped item, through loc keys.
- [x] A starting purse from data, if the economy design needs one.
- [x] Tests: a won battle raises currency and inventory exactly as the engine computed; a save/load round trip keeps them.

## Notes (worktree-agent-aa4303cb02313a538)
- `BattleRewards.pay(engine, wallet, bag)` pays `currency_award()` through `Wallet.earn` and `drop_awards()` through `Inventory.add`, both wrapping `Game.state` in place; `award_victory` calls it once per victory and keeps the record in `BattleController.last_spoils`. Live only (`persist_progress` on, no fixture); tests and captures get `paid: false` and their save untouched.
- The panel: a "Lume +N lume / purse N lume" row, then one "<item> ×N" row per drop (roll order), "bag full, left behind" when a full stack kept some back. Loc keys `HUD_RESULT_LUME`, `_LUME_FMT`, `_PURSE_FMT`, `_DROP_FMT`, `_BAG_FULL`.
- **Live battles now wear the party's gear** (`BattleVitals.live_gear`, between the Lattice and the vitals, as architecture.md prescribed), and the engine's `currency_multiplier` comes from it, so Full Net pays double in play and bought pieces matter. The simulator already assumed gear.
- **Starting purse 100 lume** (`items.json` `rules.starting_currency`, read by `Game.new_game()`, validated 0..cap): B03 shows the shop before the first fight (B06). Rationale in economy.md § Starting purse.
- The `victory` capture fixture's foes carry lume and certain drops, so `battle_victory` shows the rows (baseline re-approved).
- Saves need no change: `currency` and `inventory` were already in the save (v6). A load keeps inventory counts as JSON floats (pre-existing; `Inventory.count` reads them as ints).
- Tests: `tests/unit/test_battle_rewards_payout.gd` (10), `tools/tests/test_starting_purse_validate.py` (4); `test_battle_controller.gd` counts fighter rows apart from spoils rows.

## Review log

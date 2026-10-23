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
- 2026-10-23 ui (review-sweep-F, fresh reviewer): **approve.** I read 64a618a and 75afc5c: battle_engine.gd `item_leaves_standing`/`item_downs`/`item_defeats_party`/`_standing_after`/`preview_item`/`_resolve_item_on`/`swap`, combatant.gd `sim_copy`, item_battle_action.gd `resolve_on`/`_apply`, sim.py, targets.json, balance_targets.md and formulas.md § Time. Checks: validate_data 0/0; `unittest discover -s tools/tests` 300 OK; taskboard --check rc 0; `dlgc --check` 0/0; gdlint and gdformat clean (test_balance_sim.py included). Godot (own `XDG_DATA_HOME`): `--filter=item` 60 run, 0 failed; `--filter=sandbox_battle` 7 run, 0 failed (the 200-seed ease-ceiling test included).
  - **AC1 is met.** The prediction replays `_without_delay(action).resolve_on` on a `sim_copy`, which is exactly what `_resolve_item_on` runs for a non-fell hit. `resolve_on` has no RNG (items are fixed numbers), so it is exact and deterministic. `sim_copy` copies every field `_apply` reads (hp/max, mp/max, statuses, affinities, equipment meta for wards, agility). The meta dict is shared by reference but only read. It is Node-free. `item_defeats_party` follows `_check_outcome`'s order (victory first) and counts revived allies. `preview_item` sets FALLS from `item_downs`.
  - **AC2 is met.** `delays_taken = 0` on revive and petrify cure (battle_engine.gd:389). A swap-in takes a living leaver's count, which matches `_swap_in_time` keeping the leaver's `next_time`, so a delayed slot keeps its diminishing returns. A fallen or stone leaver gives 0.
  - **AC3 is met.** `mean_turns_min` is in targets.json, sim.py `in_band` and Band column, and the integration test. The measured 17.9 (1000 seeds) and 18.1 (200) are above the 16 floor.
  - **AC4 is met.**
  - Nit: test_sandbox_battle.gd:17 `SIM_SMART_MIN_MEAN_TURNS := 16.0` duplicates targets.json. Read the floor from targets.json, so moving it with a tuning-log note can't leave the test behind. Also, a misspelt policy key in `mean_turns_min` is silently ignored (sim.py `turns_floor`). A one-line check that its keys are in `bands` would catch that.
  - Nit: formulas.md:58 says "so swapping can't launder diminishing returns". A high count protects the delayed unit, so the real reason is that the swap-in inherits the slot's delayed `next_time`, and a fresh count would let that slot be pushed again at full strength. Reword it. Also, this rule landed in 247304b (an M1-UI-04 commit) rather than with the engine change in 64a618a. Keep a rule and its code in one commit next time.
  - Nit: `item_defeats_party` (battle_engine.gd:281) predicts the item alone. The actor's end-of-turn Poison or Doom tick in `_end_turn` can still cause a defeat that is not predicted. Add one sentence to formulas.md or economy.md so the UI help line isn't read as a full guarantee.

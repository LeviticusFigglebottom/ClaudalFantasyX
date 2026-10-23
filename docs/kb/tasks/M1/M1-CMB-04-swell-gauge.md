---
id: M1-CMB-04
title: Swell gauge modes and Rhen's interactive Swell input
role: combat
status: review
owner_session: worktree-agent-af3aaf0993fbaba55
depends_on: [M1-CMB-01]
milestone: M1
request-from: ""
---
## Goal
SPEC §6.2: gauge fill modes plus one unique interactive input (Rhen).

## Acceptance criteria
- [x] At least 3 fill modes, data-driven, with numbers in formulas.md. There are four: Ballast (damage taken, rate 120), Wake (damage dealt, rate 50), Tether (an ally hurt, rate 60) and Salve (a healing item, flat 20). They live in `game/data/battle/swell.json`, and `check_swell` validates them (at least 3 modes, known triggers). The rules are in formulas.md § Swell, with `Formulas.swell_gain / swell_fill / swell_power` and their tests.
- [x] Rhen's input is short, cancelable, and distinct. The Lamp Ring (`SwellTimingRing`, drawn by `SwellRingView`) is 3 flares in at most 3.0 s, pressed at the brightest. Perfect, good and miss read by shape. It can be cancelled before the first grade, at no cost, back to the target pick.
- [x] Engine-side resolution is headless-testable (input result passed in). `BattleSwell.perform(technique, targets, {cancelled, grades})` goes through `BattleEngine.perform_row`, and it is tested on a fixture DB in `tests/unit/test_battle_swell.gd`.

## Notes
- **Reviewer: ui.** The HUD gauge placement and the ring panel are deviations 8 and 9 in tech/ui.md and want an art eye. The formulas.md § Swell change asks for a Progression look as well (formulas.md rule).
- **Engine:** `battle_engine.gd` was at 996 lines. The item rules moved to `BattleItemRules` (the engine keeps `item_*` wrappers), and the engine gained only `perform_row` and `apply_fixture`'s `swell`, ending at 951 lines. Gauges fill from `action_resolved`, so the core does not call Swell.
- **Controller:** `battle_controller.gd` was at 995 lines. Float feedback moved to `BattleFloats` and the victory rows to `BattleRewards`, both unchanged; it ends at 991 with the Swell flow.
- **Screenshots:** a new `battle_swell_ring` shot. `battle_hud_preview`, `battle_swap_menu` and `battle_statuses` were re-approved on purpose (Rhen's empty gauge under his name; rmse ≤ 0.0016 before re-approval). `battle_victory` is unchanged.
- **Gate:** `tools/ci_local.sh` with the five battle shots passes; coverage in game/battle is 99.79% (baseline 99.75%).
- **Follow-ups:** M2-CMB-01 (unlock rules, other heroes' inputs, Swell in the simulator), M2-ARC-01 (carry gauges and modes across battles and saves), M2-UI-01 (mode menu, timing assist).

## Review log

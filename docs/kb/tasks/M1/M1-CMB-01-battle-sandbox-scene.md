---
id: M1-CMB-01
title: CTB battle sandbox: 2 heroes vs 3 enemies with timeline preview and swap
role: combat
status: review
owner_session: ui-combat-stream-1
reviewer: progression
depends_on: [M1-CMB-00, M1-UI-01]
milestone: M1
request-from: ""
---
## Goal
SPEC §10.2 M1 exit criterion: a playable battle sandbox scene on top of the engine.

## Acceptance criteria
- [x] Scene game/battle/scene/battle_sandbox.tscn is reachable from the F-key debug menu (for now F9 on the boot screen, debug builds, until M1-ARC-02)
- [x] Timeline (right side) shows the next 16 turns; hovering a command previews the shift
- [x] Swap menu works on any party turn at no time cost
- [x] Target highlight ring shader (placeholder look is fine at M1)
- [x] Rhen + Asha vs sandbox_reef, reserves Toma + Ysolde

## Notes
Greybox visuals are acceptable; this proves tactical clarity (pillar 4).

Delivered (how it works: `docs/kb/tech/ui.md`, "Battle sandbox"):
- `battle_sandbox.tscn`: a greybox arena, primitive stand-ins (`battle_sandbox.json`), `ground_ring.gdshader`, a fixed camera, and the HUD.
- `BattleController`: the engine API and signals only. Previews follow hovered commands, skills and targets. Swap is free, Escape works, enemy turns are paced, damage numbers show, and there are victory, defeat and escape screens with retry.
- **Engine API added:** `BattleEngine.party_modifier: Callable`, run once on each party combatant after `_make_party_member`. The sandbox sets it to `LatticeProgress.apply_to`. Victory feeds `xp_awards()` into `award_battle()` and saves `Game.state.lattice`.
- Tests: `tests/unit/test_battle_controller.gd` (15 tests, simulated `ui_*` input on the real scene) and 4 new hook tests in `tests/unit/test_battle_engine.gd`.
- Capture states `player_preview`, `swap_menu` and `victory` (`game/battle/scene/shots/`). Baselines are in `tests/screenshots/baselines/`.
- Also done: the Combat review of M1-PRG-01 (approve with one fix: Shield Wall MP).

Follow-ups: `BattleEngine.preview_swap(out, in)`, so the Swap menu can move timeline chips (today the help line explains the effect). Defeat still means every *active* member is KO'd, and the sandbox makes that readable: the result screen lists fallen fighters.

## Review log

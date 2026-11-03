---
id: M3-CMB-04
title: "FAST-TRACK: after a won fight, KO'd party members return at 1 HP"
role: combat
status: review
owner_session: "combat-systems (claude/combat-systems)"
depends_on: []
milestone: M3
request-from: lead
reviewer: architect
---
## Goal
The human's playtest (2026-11-03): after a WON fight, KO'd party members come back at 1 HP instead of staying dead.

## Acceptance criteria
- [x] Rule in the headless core (BattleSpoils.returning_party), constant in Formulas + formulas.md + test_formulas together.
- [x] Applied where the party's vitals are sent back after a victory (BattleVitals.send_back); XP credit is unchanged (the fallen still earn none).
- [x] Tests: tests/unit/test_victory_rise.gd (win, scripted way out, escape, stone, send_back into the saved vitals) and test_formulas.

## Notes
- `BattleSpoils.returning_party` hands back risen COPIES; the engine's combatants stay as they ended, so the stage and the XP credit (alive at victory) are unchanged. `game/battle/scene/battle_vitals.gd` got a one-line hook (the scene glue is not this track's; noted in the live log).
- Petrify is not a KO (HP above 0): a stoned member stays stone, a carried status.

## Review log

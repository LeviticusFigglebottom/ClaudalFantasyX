---
id: M2-ARC-01
title: Carry Swell gauges and modes between battles and in saves
role: architect
status: todo
owner_session: ""
depends_on: [M1-CMB-04, M1-CMB-08]
milestone: M2
request-from: combat
---
## Goal
In M1-CMB-04, a Swell gauge lives only for one battle. It should follow the party like HP and MP do (M1-CMB-08), along with each hero's chosen mode and the unlocked modes.

## Acceptance criteria
- [ ] `BattleCombatant.swell` and `swell_mode` go out through `EventBus.battle_party_returned` and come back in through `Game.vitals_modifier()` (`BattleVitals`), after a victory or an escape. A defeat writes nothing back.
- [ ] `BattleSwell.unlocked` is saved and restored. Decide whether a save shrine's rest empties gauges; the combat default is that it does not.
- [ ] The save shape has its fields, with a version note in architecture.md "Saves" and tests.

## Notes
- Engine side: `BattleSwell.attach()` keeps a `swell_mode` that is already set, and `swell` is plain state on the combatant, so nothing in `game/battle/` needs to change.

## Review log

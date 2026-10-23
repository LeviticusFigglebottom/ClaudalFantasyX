---
id: M2-CMB-01
title: Swell mode unlocks through play, and the other heroes' Swell inputs
role: combat
status: todo
owner_session: ""
depends_on: [M1-CMB-04]
milestone: M2
request-from: ""
---
## Goal
SPEC §6.2 follow-up to M1-CMB-04: players unlock new fill modes through play, and every hero's Swell has its own short, cancelable input.

## Acceptance criteria
- [ ] Unlock rules are data in `game/data/battle/swell.json` (for example "take N hits in Ballast unlocks Tether"), counted by `BattleSwell` and calling `unlock_mode()`. The numbers go in formulas.md § Swell.
- [ ] At least one more input kind is Node-free and headless-testable like `SwellTimingRing`. Candidates from the character sheets: Asha's chant sequence, Liss's reel-stop, and Pell's call-and-response tiles. It is validated in `check_swell` (`SWELL_INPUT_KINDS`).
- [ ] The balance simulator can unleash techniques with a fixed input result (for example all `good`), and balance_report.md records the effect on the sandbox bands.

## Notes
- Rhen's ring, the four modes and their rates are in formulas.md § Swell. The engine takes only `{cancelled, grades}`, so a new input needs only its own grade table.

## Review log

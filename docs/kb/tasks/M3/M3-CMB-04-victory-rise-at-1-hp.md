---
id: M3-CMB-04
title: "FAST-TRACK: after a won fight, KO'd party members return at 1 HP"
role: combat
status: doing
owner_session: "combat-systems (claude/combat-systems)"
depends_on: []
milestone: M3
request-from: lead
reviewer: architect
---
## Goal
The human's playtest (2026-11-03): after a WON fight, KO'd party members come back at 1 HP instead of staying dead.

## Acceptance criteria
- [ ] Rule in the headless core (BattleSpoils.returning_party), constant in Formulas + formulas.md + test_formulas together.
- [ ] Applied where the party's vitals are sent back after a victory (BattleVitals.send_back); XP credit is unchanged (the fallen still earn none).
- [ ] Tests.

## Review log

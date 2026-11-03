---
id: M3-CMB-06
title: "FAST-TRACK: the solo Ch1 Hullgnaw is a little too hard (sim-tune it)"
role: combat
status: review
owner_session: "combat-systems (claude/combat-systems)"
depends_on: []
milestone: M3
request-from: lead
reviewer: lead
---
## Goal
The human's playtest (2026-11-03): the solo boss fight (Rhen alone, Ch1 Hullgnaw) is a little too hard. Tune it with the balance sim to a win rate that rewards basic play for a first-time player, keeping its pattern (Coil telegraph into Gnaw, the raft breaking at half HP, Kick Off) and drama.

## Acceptance criteria
- [x] New bands in targets.json + balance_targets.md; numbers logged in balance_report.md and the live log.
- [x] `sim.py --check` passes for the Ch1 suites.

## Notes
- HP 2000 → 1850, strength 3 → 2. 1000 seeds: naive 0.6 → 12.8%, role_answer 8.5 → 68.4%, smart 86.4 → 100% (mean 25.9 actions). The sweep is in balance_report.md (2026-11-03).

## Review log

---
id: M4-A2P-040
title: "Ossa Fen and Reedhollow dressed, lit and walkable at final quality, with a mangrove vegetation system"
role: environment
status: blocked
blocked-by: ADR 0203
owner_session: ""
depends_on: []
reviewer: rendering
milestone: M4
request-from: lead
---
## Goal
Place the built kit (M3-ENV-718, 733) in both zones per ossa_fen.md's swap map, add a procedural **mangrove** system (SPEC §7.4) with wind, reed beds, the clutch's shore, the farewell-tide's staging space, the grade and LUT, ambient wildlife hooks, and ten composed shots per zone (SPEC §8.4). Merge `e1db6170` (the `kirru_roost` fix) first.

## Acceptance criteria
- [ ] Dressing and collision JSON from generators; ≥10 shots per zone viewed; no seams; walkable tests green.
- [ ] Audit zero for both zones.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch10. Don't rebuild the kit.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Review log

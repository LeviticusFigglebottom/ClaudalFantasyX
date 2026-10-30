---
id: M4-A2P-084
title: "Act II scene changes within the hitch budget"
role: ui
status: blocked
blocked-by: ADR 0203
owner_session: ""
depends_on: []
reviewer: qa
milestone: M4
request-from: lead
---
## Goal
Every Act II zone entry, battle transition and cutscene cut within SPEC §4.2: ≤ 1 s per hidden frame, ≤ 3 s per zone entry, ≤ 50 ms visible; extend ResidentLoads and prewarm to Act II's zones and arenas.

## Acceptance criteria
- [ ] scene_loads.json covers Act II; measurements logged (real-GPU rows queue for the PC).
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). ADR 0042 §4, ADR 0203 condition 5.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Review log

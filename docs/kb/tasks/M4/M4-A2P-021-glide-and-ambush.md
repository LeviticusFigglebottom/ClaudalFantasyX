---
id: M4-A2P-021
title: "Glide and ambush: untargetable on alternate turns, and until it has acted once"
role: combat
status: blocked
blocked-by: ADR 0203
owner_session: ""
depends_on: []
reviewer: progression
milestone: M4
request-from: lead
---
## Goal
Two targeting rules for Act II's regulars: `gallery_ray` glides above the water line every other turn (untargetable then), and `glass_skate` is buried until it has acted once. Both must show on the timeline and in targeting (pillar 4).

## Acceptance criteria
- [ ] Enemy-row keys, engine rules and unit tests; the sim's policies skip untargetable foes.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §4.6. Phases already carry `untargetable`; this is per turn.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Review log

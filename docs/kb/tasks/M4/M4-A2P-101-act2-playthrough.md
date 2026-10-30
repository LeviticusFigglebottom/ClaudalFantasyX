---
id: M4-A2P-101
title: "The Act II headless playthrough: Ch9's end → Ch16's act break, with save and load at every shrine"
role: qa
status: blocked
blocked-by: ADR 0203
owner_session: ""
depends_on: [M4-A2P-016]
reviewer: lead
milestone: M4
request-from: lead
---
## Goal
The ADR 0203 condition 2 test for Act II: every chapter thread, every encounter entry, save and load at every save point, zero SCRIPT ERRORs.

## Acceptance criteria
- [ ] A test in `tests/integration/`; runs in the batch gate.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §5.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Review log

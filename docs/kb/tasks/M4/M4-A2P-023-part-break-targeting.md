---
id: M4-A2P-023
title: "A part only one hero breaks: Liss and the flat-engine"
role: combat
status: blocked
blocked-by: ADR 0203
owner_session: ""
depends_on: []
reviewer: character
milestone: M4
request-from: lead
---
## Goal
Malcor Venn's phase 1 ends when Liss breaks the flat-engine. Add the targeting rule (a part answerable by a named hero's skill, or a lent skill like Ch8's) and the charge skill M3-CRE-637's `break_parts` needs. The engine's slow pulse is an `entries` row (role `tide`) so the timeline shows it.

## Acceptance criteria
- [ ] Engine rule, skill rows, validator, tests; the flat-engine's `break_parts` validate.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch14; act2_roster's open question (plan default: a part, not its own combatant).
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Review log

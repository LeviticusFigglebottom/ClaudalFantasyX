---
id: M4-A2P-022
title: "Repairing adds: the conduit crawler restores the Lamp Engine's broken parts"
role: combat
status: blocked
blocked-by: ADR 0203
owner_session: ""
depends_on: [M4-A2P-024]
reviewer: character
milestone: M4
request-from: lead
---
## Goal
`conduit_crawler` repairs a broken part and ignores the party until the engine is struck (act2_roster). Add a `restores_part` skill effect, the crawler's enemy row and AI, and wire the Engine's ring break parts (M3-CRE-623's notes: a charge skill per ring and the ring meshes).

## Acceptance criteria
- [ ] Skill key, validator rule, tests; the Engine's `break_parts` validate.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch11.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Review log

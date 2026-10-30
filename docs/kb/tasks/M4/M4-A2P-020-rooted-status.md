---
id: M4-A2P-020
title: "Rooted: a status that refuses the swap (the root crab's Root Drag)"
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
act2_roster gives `root_crab` a skill that **roots** one hero: no swap while it lasts. Add the status (name it in our own words), its engine rule (the swap refusal with a reason key, like `locked_active`'s), its HUD glyph request, and set it on `root_drag`.

## Acceptance criteria
- [ ] Engine rule and tests in `tests/unit`; formulas.md only if a formula changes.
- [ ] Pillar 4: the swap row says why it is refused.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §4.6.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.

## Review log

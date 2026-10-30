---
id: M4-A2P-082
title: "The heresy in the menus, and the formation and summon menus at seven"
role: ui
status: doing
owner_session: "claude/ui (ui-menus)"
depends_on: [M4-A2P-031]
reviewer: progression
milestone: M4
request-from: lead
---
## Goal
From `ch14_declared_heretics`: Order shops refuse with a line, Order shrines go dark and refuse (plan default; Saltwright and Kirru places keep working), the party's title changes. Check the formation menu with seven heroes and the summon menu with seven Vowbound.

## Acceptance criteria
- [ ] Menus read the flag; tests; shots viewed.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §4.2, §4.1.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30 ui-menus: **dark shrines in.**
  - SaveShrine gains `order`. From `ch14_declared_heretics` (declared) an Order shrine's core and bound light go out.
  - Its prompt reads "Touch the dark shrine", and using it plays the `dark_shrine` bark ("The Order's light is out. It will not answer you.") and nothing else: no heal, no save.
  - test_save_shrine::test_an_order_shrine_goes_dark_for_heretics.
  - Next: Order shops refuse, the heretic subtitle and slot tag, shrine travel greying (needs `order` on locations.json shrine rows), and the seven-hero check once Pell has a battle row.
  - Zone authors set `order = true` on the Order's shrines (Ansedra, the Order temples).

## Review log

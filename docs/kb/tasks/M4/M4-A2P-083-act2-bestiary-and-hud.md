---
id: M4-A2P-083
title: "The Act II bestiary and the set-piece HUD bits"
role: ui
status: doing
owner_session: "claude/ui (ui-menus)"
depends_on: []
reviewer: combat
milestone: M4
request-from: lead
---
## Goal
Bestiary pages for every Act II foe and boss once their rows carry `model` (M3-UI-208), and the HUD for Act II's set pieces: the step-hold objective count, a broken part, the darkness fight's glow telegraphs, the rooted and untargetable glyphs.

## Acceptance criteria
- [ ] Pages and HUD elements; tests; shots viewed.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §4.5, §4.6.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30 ui-menus: rooted's HUD side is in. StatusGlyph draws `rooted` (a stake held by three roots and one curled round it; ailment polarity; viewed at 150 px and chip size), with `STATUS_ROOTED` and its description. Its engine rule, its statuses.json row and the Swap refusal's reason key are combat's (M4-A2P-020); the swap row already shows any refusal reason the engine gives. The rest (bestiary pages, the step-hold and part HUD) follows the combat rows.

## Review log

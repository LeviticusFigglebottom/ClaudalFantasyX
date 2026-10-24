---
id: M2-BPR-09
title: Battle targeting with the mouse (hover a fighter to aim, click to confirm), for the input-parity audit
role: combat
reviewer: ui
status: review
owner_session: battle-presentation (claude/battle-presentation)
depends_on: [M2-BPR-01]
milestone: M2
request-from: lead
---
## Goal
The UI track's input-parity audit (ADR 0036, M2-UI-26): every screen works with keyboard, mouse and controller. The
battle command menus already take mouse hover and click (MenuPage row signals); picking a target or the member to
swap out does not. Hovering a fighter that can be picked moves the cursor onto it; a left click confirms; right
click cancels (UiInput once it merges).

## Acceptance criteria
- [x] Hover and click pick a target (single target, group targets) and the member to swap out
- [x] Mouse picks go through the controller's public handle_input (the same actions the keyboard sends); battle_controller.gd unchanged
- [x] Only candidates react; elsewhere, and in any other state, the mouse does nothing
- [x] Tests

## Notes
- Lead queue 2026-10-24 (after big7).

- 2026-10-24 (track lead): BattleMousePick; 5 tests; battle filter 491/0. Reviewer: ui (the parity audit owner).

## Review log

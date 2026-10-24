---
id: M2-UI-04
title: A field menu that opens the bestiary and the out-of-battle Swell mode chooser; the target panel knows a Read foe
role: ui
status: doing
owner_session: "worktree-agent-a218779a0dea1229a"
depends_on: [M2-UI-01, M2-UI-02]
milestone: M2
request-from: "lead"
reviewer: combat
---
## Goal
M2-UI-01 and M2-UI-02 built the views, but nothing in play reaches them. `BestiaryMenu.open_in` has no caller outside tests and shots, and the out-of-battle mode chooser wasn't built because no party or Customize menu exists (`BattleSwellCarry.mode_rows` and `set_mode` are ready). No task covered either, so review-sweep-O filed this one.

## Acceptance criteria
- [ ] A field (pause or party) menu, opened from the field with a `ui_*` action, pauses the tree the way SaveMenu does, and reaches at least the bestiary (`BestiaryMenu.open_in`) and each hero's Swell fill mode (`BattleSwellCarry.mode_rows(cid)` and `set_mode`, rows with `name_key` and `desc_key`). Every string goes through a loc key.
- [ ] Once this menu exists, fix M2-FP-04's note: "Back, cancel: Escape" now does something in the field.
- [ ] **The target info panel** (M2-UI-02 follow-up): `BattleController._show_pick` passes `"revealed": false`, so a foe the party has already Read still says "HP unknown until Read". Take it from `bestiary.book.is_read(id)`, and test it.
- [ ] Screenshot fixtures for the new menu, viewed and approved.

## Review log

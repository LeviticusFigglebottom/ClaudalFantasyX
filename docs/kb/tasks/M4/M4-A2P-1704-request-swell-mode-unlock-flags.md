---
id: M4-A2P-1704
title: "Request (ui-menus): name the flags that unlock a new Swell fill mode, for the 'A New Swell' tip"
role: progression
status: todo
owner_session: ""
depends_on: []
reviewer: ui
milestone: M4
request-from: ui
---
## Goal
act2-plan's tutorials.md lists a field tip for a new Swell fill mode: "There's a new way to fill the Swell. Choose it
under Swell in the field menu." Its text is in (TIP_SWELL_MODE_TITLE and TIP_SWELL_MODE_BODY, ch16.csv). It is raised
by flag `<mode>_unlocked`, which Progression names. No such flag is declared in game/data/flags.tres yet.

## Ask
Declare the flag (or flags) that a new fill mode's unlock sets, and set it where the mode unlocks. Then tell ui-menus
which, and ui-menus adds the tip row (`on: flag`, `when: [<the flags>]`, seen flag `tut_swell_mode_seen`).

## Acceptance criteria
- [ ] The unlock flags are declared and set on unlock; ui-menus' tip row follows.

## Review log

---
id: M4-A2P-1701
title: "Act I first-hour UX from a fresh profile: the first battle's prompt, the menu, save and Where-to-next tips, once, on time, readable, skippable"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: qa
milestone: M4
request-from: lead
---
## Goal
New Game through Haluna on a fresh profile: each first-time teaching appears exactly once, at the right moment,
readable, and skippable.

## Acceptance criteria
- [x] The first battle's prompt (encounters.json `ch01_wickfry` `prompt_key` TUT_CH01_COMMANDS): on the help line
      when the first command menu opens, once per fight; the first cursor move gives the line back to the help.
- [x] The Where-to-next tip comes with Ch1's first objective (`ch01_started`), not Ch2's.
- [x] The menu tip comes after Ch1's first won fight (`ch01_wickfry_won`), not Ch2's. It is caught up when the field
      reloads after the fight, so it shows even though the flag was set in the battle scene.
- [x] The save tip: on the first shrine in reach (unchanged). The menu-save and Swell tips follow in turn.
- [x] A tip fades out when the player presses what it teaches (any {action} its body names).
- [x] tests: test_tutorial_tips 8/0 (three new), tools/tests/test_tutorial_tips (list `when`, `requires_any`).

## Notes
- 2026-10-30 ui-menus, found and fixed:
  1. **The menu tip never showed.** Its flag is set in the battle scene, where no field tip card listens, and the
     zone reloads after a scripted fight. The slice's `ch02_tideline_won` had the same gap. Flag tips are now
     caught up on the next field input.
  2. **The Where-to-next and menu tips waited for Ch2's slice flags.** New Game plays Act I (the prologue, then Ch1),
     so a chapter of play went untaught. `when` may now list flags and `requires_any` asks one of several, so both
     routes teach.
  3. **Tips couldn't be skipped**, and the menu tip came back after the menu closed. Pressing what a tip teaches now
     dismisses it.
- **Render viewed:** the menu tip at 130% (field_tip_card with the menu tip); whole and readable.

## Review log

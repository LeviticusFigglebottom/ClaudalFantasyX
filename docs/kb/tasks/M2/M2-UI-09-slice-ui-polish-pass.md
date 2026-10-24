---
id: M2-UI-09
title: Slice UI polish pass (an Accessibility page with text size, one Settings hub, consistent type and navigation)
role: ui
status: doing
owner_session: "claude/ui"
depends_on: [M1-UI-10, M2-UI-04]
milestone: M2
request-from: lead
---
## Goal
The Lead's queue item 4 for the slice review: the menus a player meets in the slice (field menu, bestiary, Read panel, Swell menus, Vowbound HUD, settings) should read as one system, work from keyboard and controller everywhere, and the text-size option that `UiSettings` has had since M1-UI-02 should be reachable and apply outside battle.

## Acceptance criteria
- [ ] An Accessibility page (reduced motion, text size, palette, timing assist) over `UiSettings`, built like the Graphics page; every change saves and applies at once.
- [ ] One Settings hub (Graphics, Accessibility) opened from the title's Settings row and from a new Settings row in the field menu.
- [ ] Text size, palette and reduced motion apply to the field menu, the bestiary, the settings pages and the title, not only the battle HUD.
- [ ] The audit's typography, spacing and navigation inconsistencies are fixed or listed with a reason.
- [ ] Loc keys for every string; tests; screenshots for the new pages (and the shots the fixes move, re-approved after viewing).

## Notes
- The shop and inn menus are m2-slice's (M2-UI-06 on claude/m2-slice); ideas for them are in docs/kb/handoffs/live/ui.md.

## Review log

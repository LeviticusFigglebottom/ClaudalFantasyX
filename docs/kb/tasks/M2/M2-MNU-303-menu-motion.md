---
id: M2-MNU-303
title: Menu motion polish: page transitions, cursor easing, focus sounds, Reduced motion
role: ui
status: doing
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-05]
milestone: M2
request-from: lead
---
## Goal
The playtest note "parts look primitive": the menus snap. Give the field menu's pages a short open and close transition, ease the cursor between rows, play audio's `ui_sfx` focus sounds, and honour Reduced motion everywhere (no slide, no ease: instant).

## Acceptance criteria
- [ ] Page transitions (open and close) on FieldSubmenu pages and the field menu; durations in data.
- [ ] Cursor easing on menu rows; instant under Reduced motion.
- [ ] Focus sounds through audio's `ui_sfx` hooks (no direct sound calls in pages beyond what the hooks expect).
- [ ] Captures and tests are deterministic (motion settles or is skipped in captures).
- [ ] Tests for both Reduced motion on and off.

## Review log

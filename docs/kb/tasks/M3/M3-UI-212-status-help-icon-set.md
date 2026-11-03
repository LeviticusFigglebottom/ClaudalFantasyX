---
id: M3-UI-212
title: "Request: use the battle status icon set in the status help (Read, status UI, tip, codex)"
role: ui
status: todo
owner_session: ""
depends_on: [M3-BPR-450]
milestone: M3
request-from: combat
---
## Goal
The human's playtest (11-03) item 3: ui-menus explains how to identify and remove each status. battle-presentation
made the on-body looks and one icon per status (M3-BPR-450); the help should show the same icon the player sees over
the fighter's head.

## What you get
- assets/vfx/battle/status_icons/<status id>.svg, 21 icons (128 px; tools/vfx/status_icons.py, re-run after a new
  status). Circle = beneficial, rounded square = harmful; a down-arrow tab = a "break" (a stat lowered).
- game/data/vfx/battle/status_looks.json `looks.<id>.reads_as`: a one-line English description of what the status
  looks like on the body (for your writers; not a loc string - make your own loc keys).

## Acceptance criteria
- [ ] The help panel, first-time tip and codex rows show each status's icon.
- [ ] Their text says what it looks like on the body (from reads_as) and how to remove it.

## Review log

---
id: M2-MNU-300
title: Field menu root shows the last save (place and time); the "Save at a shrine" tip
role: ui
status: doing
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-04]
milestone: M2
request-from: lead
---
## Goal
The Lead's design call (2026-10-24): the field menu gets **no** save row. Saving stays at save shrines plus the chapter autosaves (the pilgrimage pillar; shrines are rest points). Instead, the field menu's root shows where and when the game was last saved, and the tips carry a "Save at a shrine" hint.

## Acceptance criteria
- [ ] The root panel shows the last save's location name and time, read from the save system's public API (never a private field), or a "Not saved yet" line.
- [ ] A tip entry: saving happens at shrines.
- [ ] Loc keys for every string; layout values in `game/data/ui/field_menu.json`.
- [ ] Unit test; the field menu shot re-approved after viewing.

## Review log

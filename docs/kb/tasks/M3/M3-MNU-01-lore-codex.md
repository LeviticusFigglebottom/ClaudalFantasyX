---
id: M3-MNU-01
title: Lore codex (SPEC §6.11): entries and text records unlocked through play
role: ui
status: doing
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-03]
milestone: M3
request-from: lead
reviewer: narrative
---
## Goal
SPEC §6.11 asks for a lore codex that also unlocks text records found in the world. Build the data, the unlock path (story flags and field pickups), and a field-menu page, with Act I entries drawn only from the story bible (docs/kb/story/), reviewed by Narrative.

## Acceptance criteria
- [ ] game/data/codex/codex.json (validated): entries by category, each with title/body loc keys and an unlock rule (a declared flag, or a record found in the field).
- [ ] A field Interactable payload `{"record": id}` unlocks a text record and shows it; the save keeps what is unlocked.
- [ ] A Codex row in the field menu: categories, entries (locked ones shown as unknown), the text; keyboard, mouse and pad parity tests; UiSettings honoured; screenshot viewed.
- [ ] Act I entries in the story's own words (bible.md, glossary), no new canon; Narrative review.

## Notes

## Review log

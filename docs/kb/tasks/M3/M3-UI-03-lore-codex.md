---
id: M3-UI-03
title: A lore codex that also unlocks text records found in the world
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: []
milestone: M3
request-from: lead
---
## Goal
SPEC §6.11 asks for a lore codex that also unlocks text records found in the world. This task builds it on the systems that already exist (flags, Interactable payloads, FieldHud, MenuPage), with no new engine.

## Acceptance criteria
- [x] Data `game/data/lore/codex.json`: categories (World, Places, People, Records) and entries `{id, category, title_key, body_key, unlock}`; `unlock` is `{"flag": f}`, `{"record": true}` or `{"always": true}`. `validate_data.py` `check_codex` (categories known, flags declared, loc keys present, ids unique), with `tools/tests/test_codex.py`.
- [x] A small starter set: ten entries, two of them records, text in `game/data/loc/codex.csv` (registered in project.godot). Narrative is asked to review and extend them, and where to place the records (M3-NAR-01).
- [x] Field hook: an Interactable with payload `{"record": "<id>"}` marks the record found (`codex_<id>_found` through Game.set_flag) and `CodexNotice` (attached by FieldHud) shows "Record added to the Codex" and its title.
- [x] `CodexMenu` / `CodexModel` (game/ui/codex/): categories with counts, unlocked entries with "New", the text with a scrolling page; read state in one declared flag per entry (`codex_<id>_read`).
- [x] Field menu: a Codex row after Bestiary (eleven rows; panel and root one row pitch taller, still centred, rects multiples of 3).
- [x] Keyboard, pad and mouse parity (`tests/unit/test_codex.gd`, InputDriver).
- [x] Shots: new `field_menu_codex`; `field_menu` and `field_menu_swell_modes` re-approved for the eleventh row.

## Notes
- The records are not placed yet: game/levels/** belongs to m2-slice and Environment. M3-NAR-01 says where they go.
- docs/kb/tech/ui.md "Lore codex (M3-UI-03)" has the rules and why read state lives in per-entry flags.

## Review log

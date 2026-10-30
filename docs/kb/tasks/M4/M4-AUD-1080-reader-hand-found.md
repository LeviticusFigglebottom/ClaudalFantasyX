---
id: M4-AUD-1080
title: "Request (ui-menus): the document reader's sounds, a hand found and the mark"
role: audio
status: todo
owner_session: ""
depends_on: [M4-A2P-080]
milestone: M4
request-from: ui
---
## Goal
M4-A2P-080 added the document reader (DocumentReader, game/ui/codex/document_reader.gd). It is hooked in
`game/data/audio/ui_sfx.json` with existing rows so it is never silent:
- the page opens and closes on `ui_page`;
- the pane and line cursors use `ui_cursor`;
- a mark set, moved or cleared plays `ui_confirm`;
- a found hand (`hand_found`) borrows `ui_tip`.

Give the found hand its own row: the moment the player sees the same hand across the founders' ledger and the
Cantor roll (Ch13), quiet and certain, nothing triumphant. Optionally give the mark a softer pen-like row. Replace the
rows in the DocumentReader hook.

## Acceptance criteria
- [ ] New sfx rows reproducible from `assets_src/sfx/`, with PROVENANCE rows; the hook names them.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by ui-menus (claude/ui), 2026-10-30.

## Review log

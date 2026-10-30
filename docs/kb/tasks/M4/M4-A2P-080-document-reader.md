---
id: M4-A2P-080
title: "The document reader: the Lamp Archive's records side by side, and found records in the codex"
role: ui
status: doing
owner_session: "ui-menus (claude/ui)"
depends_on: []
reviewer: narrative
milestone: M4
request-from: lead
---
## Goal
A codex view that lays two or three records side by side and highlights the matching hand when the player asks; used for the Archive's ledgers and Cantor roll (Ch13) and later found records (Wenna's marks, Ama's keth).

## Acceptance criteria
- [ ] Control nodes and shaders (no raster mock-ups); input parity; tests; a shot viewed.
- [ ] ADR 0041 §3's final bar (no greybox, stand-in or placeholder the player can see or hear).

## Notes
- Filed by the act2-plan track (2026-10-30) from [act2_plan.md](../../plan/act2_plan.md). Plan §2 Ch13, §4.5.
- Blocked until the Lead tags `act1-complete` (ADR 0203); then `todo`.
- 2026-10-30 ui-menus: **the reader is in** (DocumentReaderModel, DocumentReader, game/data/ui/document_reader.json). It lays out one to three panes, one mark per pane. A hand is found when every one of its lines is marked: its lines turn gold, a gold rule draws on across the gaps (at once under Reduced motion), and the last hand sets the record's `flag`. The line under the panes counts the hands left. Input covers keys, pad and mouse (hover, click to mark, wheel, right-click Cancel). Tests: test_document_reader 7/0 (model, view, three-device parity, long-pane scroll); pseudo-locale at 100% and 130% fits. Shot scenes document_reader_three and document_reader_one (over a fixture record, game/levels/_tests/document_reader/) are viewed. They are **not in the manifest**: test_screenshots requires a baseline for every row, and baselines are the Lead's to bake (add both rows with their baselines). Sounds: a DocumentReader hook in ui_sfx.json on existing rows (the act1 audio audit asks every input-taking ui class for one); request M4-AUD-1080 for its own found-hand row.
  - `game/data/lore/records.json` ships empty. **Narrative** fills the Archive's ledgers, the Cantor roll and Corran's line (RECORD_<ID>_<NN> keys, hands, the Ch13 flag), and the scene opens the reader with `DocumentReader.open_in(host, DocumentReaderModel.new(DocumentReaderModel.row_of(&"<id>")))`.
  - The codex opens a record entry that names a `reader` row (codex.json `"reader": "<records.json id>"`) in the reader, single pane, and takes the input back when it closes (test_codex). Narrative adds the `reader` field to Wenna's marks, Ama's keth and the Archive set as their rows land.

## Review log

---
id: M5-A3P-1706
title: "Act III UI: the ledger page for Ch17 B05: held page-turns and a blank-page end (act3_ch17 §9 UI)"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
act3_ch17 §9: "the ledger reader (the document reader, M4-A2P-080, with held page-turns and a blank-page end)". The
document reader is a matching puzzle across panes, so the ledger gets a page of its own. The scene,
`ch17_the_ledger.dlg`, already writes each entry as a `#narration` line and turns each page with a held gate
(`<<event hold_input turn_page>>` … `hold_input_end`). The page shows what the script does.

## Acceptance criteria
- [x] **LedgerReader** (`game/ui/ledger/`) and **LedgerReaderModel**, Node-free. Layout and hooks are in
      `game/data/ui/ledger_reader.json`. `LedgerReader.mount(host, sequencer)`:
  - Each line whose id starts with `ch17_ledger_page_` is written on the open page, under "Dace Sallow's ledger".
    It still captions below, so the words are never only on the page. Rhen's and Liss's lines are not written.
  - A `turn_page` gate turns the page when it ends: the written page slides away and the next comes up blank.
    Other gates turn nothing.
  - Past the last entry nothing more is written, so Rhen's turns land on blank pages (ADR 0022 sweep-J).
  - It fades in at its first entry or turn, and out when the scene ends. It takes no input; the hold is
    CutsceneHoldGate's.
- [x] Sound: a ui_sfx row (`page_turned` → ui_page). The audio audit's UI section is 0.
- [x] **tests/unit/test_ledger_reader.gd (3/0):**
  - the model's blank-page end;
  - entries written and turned by the gate (not by another gate, not at the gate's start);
  - the page going at the scene's end;
  - the shipped script carrying the data's prefix and prompt.
- [x] **Shot `ledger_reader`** (pending_baseline): the second written page, rendered and viewed.

## Notes
- Mounting it in the B05 scene is the Ch17 staging's job (M5-A3P-1001). Request M5-A3P-1707 covers it.

## Review log

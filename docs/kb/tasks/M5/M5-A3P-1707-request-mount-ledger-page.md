---
id: M5-A3P-1707
title: "Request (staging): mount the ledger page in Ch17 B05 (LedgerReader.mount before ch17_the_ledger plays)"
role: cinematics
status: todo
owner_session: ""
depends_on: [M5-A3P-1706]
reviewer: ui
milestone: M5
request-from: ui
---
## Goal
B05's ledger page (M5-A3P-1706) is built and listens to the scene's own sequencer. The Ch17 staging (M5-A3P-1001)
needs to mount it when it plays `ch17_the_ledger`.

## Acceptance criteria
- [ ] Before `ch17_the_ledger` starts: `LedgerReader.mount(<the zone or cutscene host>, <its CutsceneSequencer>)`,
      the same sequencer the scene's CutsceneHoldGate is set up on. The page frees itself when the scene finishes.
- [ ] Nothing else is needed. The scene's `#narration` entries and `<<event hold_input turn_page>>` gates drive it as
      written. If the line ids or the prompt change, change `game/data/ui/ledger_reader.json` to match;
      `test_ledger_reader` checks the two agree.

## Review log

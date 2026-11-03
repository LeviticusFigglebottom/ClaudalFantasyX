---
id: M5-A3P-1707
title: "Request (staging): mount the ledger page in Ch17 B05 (LedgerReader.mount before ch17_the_ledger plays)"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice)"
depends_on: [M5-A3P-1706]
reviewer: ui
milestone: M5
request-from: ui
---
## Goal
B05's ledger page (M5-A3P-1706) is built and listens to the scene's own sequencer. The Ch17 staging (M5-A3P-1001)
needs to mount it when it plays `ch17_the_ledger`.

## Acceptance criteria
- [x] Before `ch17_the_ledger` starts: `LedgerReader.mount(<the zone or cutscene host>, <its CutsceneSequencer>)`,
      the same sequencer the scene's CutsceneHoldGate is set up on. The page frees itself when the scene finishes.
- [x] Nothing else is needed. The scene's `#narration` entries and `<<event hold_input turn_page>>` gates drive it as
      written. If the line ids or the prompt change, change `game/data/ui/ledger_reader.json` to match;
      `test_ledger_reader` checks the two agree.

## Done (slice-polish, 2026-11-03)
- ch17.json's `ledger` beat runs `{"zone": "mount_ledger"}` between `place: Cabin` and `play: ch17_the_ledger`.
- `Ch17Zone.mount_ledger()` calls `LedgerReader.mount(self, story.sequencer)`, the sequencer the HoldGate is set up on.
  The reader closes on that scene's `finished`.
- Both files are act1-chapters' (M5-A3P-1001). The change is one flow step and one method, and is logged for them.
- test_ch17_thread asserts that the hatch mounts exactly one page and that the scene writes on it. ch17 3/0,
  ledger 3/0.

## Review log

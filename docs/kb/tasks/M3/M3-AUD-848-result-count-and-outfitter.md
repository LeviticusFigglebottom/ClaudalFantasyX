---
id: M3-AUD-848
title: "UI sounds: the battle result's count-up and the Reefball outfitter (and the queue's other screens checked)"
role: audio
status: review
owner_session: "audio (cloud session_01Wmj8xaLtwcqiS3qwC6PciW, branch claude/audio)"
reviewer: ui
depends_on: [M3-AUD-832]
milestone: M3
request-from: lead
---
## Goal
The Lead (10-27, 21:42), item 3: sounds for ui-menus' new screens: the Lattice unlock, the result screen's count-up,
the outfitter and shrine travel, if not done.

## Acceptance criteria
- [x] Already done, checked:
      - the Lattice unlock (`ui_lattice_unlock` on LatticeMenu, M3-AUD-15);
      - shrine travel (M3-AUD-832, `pending` until claude/ui merges).
- [x] The result's count-up (BattleResultPanel, claude/ui's count_sec 0.6):
      - `ui_count_run` is a quick run of tiny bar ticks climbing D-A-E and speeding up, at −8 dB;
      - `ui_count_done` is two soft bars a fifth apart, at −4 dB;
      - both play on `is_counting()` changing, with the choice's cursor and confirm. Until the UI track's count-up
        lands, the read fails harmlessly.
- [x] The Reefball outfitter (ReefballOutfitterMenu, `pending`):
      - it opens and closes, and the cursor moves;
      - a buy is the wallet falling (`ui_buy`); a piece put on, swapped or taken off is its rows changing
        (`ui_equip`); a refusal is the status line (`ui_error`).
      - `ui_buy` now ranks above `ui_equip`, so a buy that also wears is heard as the buy. No other screen buys and
        equips in one frame.
- [x] Tests: test_screen_audio has stand-ins for both. `screen_audio` 10/0, `audio` 167/0, `menu` 238/0;
      validate_data 0/0.
- [ ] When claude/ui merges: drop `pending` on ReefballOutfitterMenu and smoke-test both on the real classes.

## Review log

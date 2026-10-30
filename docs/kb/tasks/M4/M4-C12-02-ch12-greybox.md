---
id: M4-C12-02
title: Ch12 "The Cold Road" greybox (ch12/keth_pass, ch12/quellan, ch12/cloudloom) before the beat sheet
role: cinematics
status: todo
owner_session: act1-chapters (claude/act1-chapters)
depends_on: [M4-C11-02]
reviewer: environment
milestone: M4
request-from: lead
---
## Goal
Ch12's geography from act_outline.md (Ch12) and the colour script's `ch12` (a cold 09:00, woven reds the only warm
notes, white stone under open sky in Cloudloom, no ice in the temple), so the story slots in when the beat sheet
(M4-C12-01) lands.

## Done (act1-chapters, 2026-10-27)
- `tools/act1/ch12_greybox.py` (sharing Ch10's and Ch11's builders): **Keth Pass**, three switchback flights (ramps)
  along a cliff with the pass-cords on the drop side, the knotted post (`knot_post`), the Ram's shelf under the
  seeping Lit Age wall (RamArena), the saddle (`cold_ledge`); **Quellan**, the street, houses, the inn with its red
  banner (`inn_door`), the well, the road up north; **Cloudloom**, the stair up, the open-roofed weaving-hall with its
  rows of keth and an aisle, Hesk's dais (`hesk`, before it: no step-up).
- `Ch12Zone`; three scenes; `locations.json` rows; `chapters/ch12.json` (the chapter becomes 12; every way there and
  back); flags `ch12_started`, `ch12_reached_quellan`, `ch12_reached_cloudloom`; `loc/ch12.csv` imported.
- `tests/integration/test_ch12_thread.gd`, `test_ch12_walkable.gd`.

## Next
- The beat sheet's story; the Avalanche Ram (creatures) and its encounter with sim bands.

## Review log

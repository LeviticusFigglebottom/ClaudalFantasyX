---
id: M3-ENV-1228
title: "Request (env-art): the Ch4 derelict at night grades near-black: D01, D06 and F05 read as nothing (ch04/brightwater_ferry)"
role: environment
status: review
owner_session: "env-art (claude/env-art, 2026-10-29)"
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
ADR 0041 (docs/kb/qa/act1_playthrough_ch04_ch09.md, act1-chapters' playthrough stills): the Ch4 derelict at night grades near-black: D01, D06 and F05 read as nothing (ch04/brightwater_ferry). The story cameras
are aimed at their subjects; the grade or the lights leave nothing to see. For env-art.

## Acceptance criteria
- [x] The listed shots show their subjects (self-render `tools/act1/cutscene_stills` for the zone's visit).

## Notes (env-art, 2026-10-29; 025854a6, 4629dfa6)
- **Cause:** the derelict has no lamp (a dead ship) and the low eastern moon is behind her topsides and transom from every
  ferry camera; env-art's earlier sky fill (M3-ENV-746) lit only her deck.
- **Fix** (`tools/act1/ch04_ferry_dressing.py`, `DERELICT_HULL_FILL_AT`): the same cold, shadowless moon fill (#9DB4D6),
  weaker, just outboard of her ferry side (three, 0.9) and off-centre astern of her transom (1.6), so her hull and the
  name-board read as pale dead timber. No lamp, no warm light.
- **Viewed** (`tools/act1/cutscene_stills`, `ch04/brightwater_ferry`; and player-eye frames): D01 now shows the deckhouse,
  its steps and her red trim; the transom and the name-board read from astern (its marks clear, a soft glint, no hot spot).
  `ch04_ferry_derelict` and `ch04_ferry_deck` drift 0.014 / 0.012 (her ferry-side rail shows between the hulls).
- **Camera side (act1-chapters'):** D06 still frames the rail 1.7 m over the board, and F05 frames mostly rigging against
  the night sky. Their subjects are lit now; re-aim D06 at the board (-9.24, 0.85, 21.04) as your notes planned.
- **PC-QUEUE:** judge the night read on the real GPU.

## Review log

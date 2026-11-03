---
id: M3-BPR-450
title: "FAST-TRACK: every status is obvious on the character (on-body look and an icon over the head)"
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: [M3-BPR-424]
milestone: M3
reviewer: rendering
request-from: lead
---
## Goal
The human's playtest (11-03): status effects must be OBVIOUS on the character. Each of the 21 statuses gets a
distinct on-body look (a tint/overlay pattern, a looping aura, or a prop) in the palette, readable at battle
distance and colour-blind safe by shape and motion as well as colour, plus its icon over the head (over the feet of a
tall body) for as long as it lasts.

## Acceptance criteria
- [x] game/data/vfx/battle/status_looks.json: a look per status; palette swatches; no two alike (tested).
- [x] BattleStatusLooks (game/vfx/battle/battle_status_looks.gd): listens only; shows and removes looks as statuses
      come and go; Doom shows its count; nothing on a fallen fighter.
- [x] 21 icons, assets/vfx/battle/status_icons/*.svg from tools/vfx/status_icons.py (circle = beneficial, rounded
      square = harmful, a glyph per status, a down-arrow tab on the breaks).
- [x] tests/unit/test_battle_status_looks.gd.
- [x] Contact sheet (tools/vfx/status_look_sheet.tscn) of every status on a hero and a foe, viewed (two passes,
      tuned from each).
- [ ] PC-QUEUE: the looks on the GPU at 1080p.

## Notes
- The icon set goes to ui-menus for the help panel (M3-UI-212).
- docs/kb/tech/battle_status_looks.md.

## Review log

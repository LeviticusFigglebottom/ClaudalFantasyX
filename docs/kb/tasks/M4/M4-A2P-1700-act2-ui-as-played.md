---
id: M4-A2P-1700
title: "Act II UI as played, Ch10-Ch13: zone titles, objective cards, Where-to-next, shops, inns, the Vowbound calls; 100% and 130%, pad"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: qa
milestone: M4
request-from: lead
---
## Goal
The Lead's 2026-10-30 pass. Ch10-Ch13 are mounted. Walk their UI as it plays, at 100% and 130% text and on the pad,
and fix what is found.

## Acceptance criteria
- [x] Every Ch10-Ch13 location's area title card fits on screen, at both sizes.
- [x] Every Ch10-Ch13 objective line, main and side, fits its panel. A main line shows in its zone (and on demand:
      the Where-to-next card).
- [x] Quellan's and Ansedra's shops and inns walk with the pad (Buy, every stock row, a purchase, Rest, Leave), open
      and closed, with nothing cut short.
- [x] Asha's battle menu with the six Vowbound bound by Ch13: six Call rows, each reached by the pad and on screen.
- [x] tests/unit/test_act2_ui_as_played.gd (5 tests).

## Notes
- 2026-10-30 ui-menus, found and fixed:
  - **An inn's refusal was cut to one line.** "The door is barred. No rooms for…" at 130%: the status kept the one
    line it was built with. It now gets the column down to the help line (TownMenu._fit_desc).
  - **Quellan's and Ansedra's Rest lines were cut at 130%.** Three paragraphs needed 365 px and the inn panel had
    326. The inn panel is now 618 tall (was 558) and its line's cap is 400 (`shop_menu.json` `inn_menu`).
  - **Renders viewed:** inn_menu at 100% (Haluna) and at 130% (Quellan, open and closed).
- Checked clean: the area titles, every objective line, the shops' stock, and Asha's six Call rows.

## Review log

---
id: M5-A3P-1702
title: "Act III UI: the Kite's revisits (act3_ch18 §4): Oruvel on the chart, Ansedra listed but closed to heretics"
role: ui
status: review
owner_session: claude/ui (ui-menus)
depends_on: []
reviewer: progression
milestone: M5
request-from: lead
---
## Goal
ADR 0207 and the Lead's 23:26 note ("the Kite map and flight"): bring the Kite's chart up to act3_ch18's revisit list.
Oruvel, the home quarter, can be flown back to. Ansedra is on the chart, but the party were declared heretics in Ch14,
so the Kite can't land there, and the list says why rather than hiding the place.

## Acceptance criteria
- [x] `game/data/world/kite.json`: destination `oruvel` (ch01/oruvel, ScaleHull) and `ansedra` (ch13/ansedra,
      Moorings), with the new optional `refused_flag` and `refused_key` fields.
- [x] KiteMapModel.refusal(id): the refused line when the destination's `refused_flag` is set ("" otherwise).
      `fly()` refuses such a destination.
- [x] KiteMapMenu: a refused row is greyed, with its reason on the right ("Closed to heretics", `KITE_CLOSED_HERETICS`
      in kite.csv).
- [x] tests/unit/test_kite_map.gd (13/0): the shipped chart lists Oruvel and refuses Ansedra to heretics.
- [x] Shot `kite_map` rendered with Act III flags into scratch and viewed. No baseline was written; the manifest's own
      flags are unchanged.

## Notes
Positions are provisional, the same as the rest of the chart.

## Review log

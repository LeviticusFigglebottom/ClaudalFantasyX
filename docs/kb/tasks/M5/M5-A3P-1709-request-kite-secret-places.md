---
id: M5-A3P-1709
title: "Request (progression, design): the Kite's secret places for coordinate search (SPEC §6.6; act3_ch18 §9)"
role: progression
status: todo
owner_session: ""
depends_on: []
reviewer: ui
milestone: M5
request-from: ui
---
## Goal
SPEC §6.6 gives the Kite "a world-map menu to fly between unlocked locations, plus coordinate-search secret
locations", and act3_ch18 §9 asks Design for the secret coordinates. The menu is built (M3-UI-205, M5-A3P-1702):
"Search the chart" names a square, and a secret found there joins the list. But `game/data/world/kite.json`
`secrets` is empty, so every search says nothing is there.

## Acceptance criteria
- [ ] Each secret place has a row in kite.json `secrets`:
  - `id`, `region` and `location_id` (a locations.json location with a scene);
  - `spawn`, `found_flag` (declared in flags.tres), `cell` (e.g. "F2"), and `at` within that cell;
  - `name_key`, if its location's name shouldn't show.
- [ ] Each one needs a reason to look there: a clue in a codex record, a bark or an NPC line that names the square
      or the place.
- [ ] ui-menus adds nothing. The menu reads the rows as they are, and test_kite_map covers the search.

## Review log

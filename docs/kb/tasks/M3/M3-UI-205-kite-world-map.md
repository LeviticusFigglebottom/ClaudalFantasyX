---
id: M3-UI-205
title: "The Kite's world map: places by name, a chart, flying with a question first, and searching for secret places"
role: ui
status: blocked
blocked-by: ADR 0041
owner_session: claude/ui (ui-menus)
reviewer: design
depends_on: []
milestone: M3
---
## Goal
SPEC §6.6 gives Act III a Kite (act_outline.md Ch18), the late-game way across Maresh's sea. It needs a world-map menu. The Lead allowed it to start early (2026-10-27, 22:50 list). It should do three things:
- list where the Kite can land;
- show those places on a chart;
- fly there, asking first.

It should also let the player search the chart for hidden places.

## Acceptance criteria
- [x] Data: `game/data/world/kite.json` (open flag, chart grid, regions, destinations gated by flags, secrets found by searching a cell). Validator `check_kite`, tested by `tools/tests/test_kite_validate.py`.
- [x] KiteMapModel (node-free): lists the places, flies, and searches. KiteMapMenu (a FieldSubmenu) plus KiteChart. Here is marked and can't be chosen. Fly asks first, with Stay under the cursor.
- [x] Every string goes through `game/data/loc/kite.csv`. Layout lives in `game/data/ui/kite_map.json`.
- [x] Input parity: keyboard, pad and mouse for flying, searching and Cancel (`test_input_parity_kite_map.gd`).
- [x] Pseudo-loc walk and aspect audit (list, question, search).
- [x] Shot `kite_map`: its RENDER-REQUEST is in the live log.
- [ ] Baseline approved once the render server renders it.
- [x] Wired into the field menu behind `kite_flying` (the Lead, 2026-10-27 23:37): a row after Map, the panel a row taller while it shows, a flight closing the menu; `test_field_menu_kite.gd`; shot `field_menu_kite` (RENDER-REQUEST in the live log).
- [x] Act II's places (act1-chapters' zones): Reedhollow, Lowlight, Quellan and Hollowmere, each on its arrival flag. Ansedra stays off, since the party are heretics there after Ch14.
- [ ] Design places Act III's secret places in `secrets`, and Act III's towns as their zones land.

## Notes
- The four Act I destinations (Haluna, Pemakar, Tamsule, Corrow) stand in so the page can be tested and shot. Their chart positions are a first guess; Design moves them.
- Docs: `docs/kb/tech/ui.md` "The Kite's world map".

## Review log
- 2026-10-28, ui-menus: **paused (ADR 0041, the human's refocus on Act I at final quality).** What is built stays on claude/ui and merges as is; nothing is reverted. Resume when a new ADR lifts the pause.

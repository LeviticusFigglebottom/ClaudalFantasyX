---
id: M3-UI-206
title: "Act II area maps: every Ch10-16 greybox zone on the field menu's map and the route"
role: ui
status: blocked
blocked-by: ADR 0041
owner_session: claude/ui (ui-menus)
reviewer: design
depends_on: [M4-C10-02, M4-C11-02, M4-C12-02, M4-C13-02, M4-C14-02]
milestone: M3
---
## Goal
The Lead routed this on 2026-10-27 at 23:37: area maps for act1-chapters' Act II greybox zones. claude/ui merged claude/act1-chapters (4d2e25cf) to build against its zones, flags and names.

## Acceptance criteria
- [x] `zone_maps.json` has all fifteen zones, each with:
  - shape hints for the Act II `Water`/`Bed` convention and the high floors;
  - bounds;
  - POIs from spawns, marks, actors and triggers. Their names are spoiler-safe and live in `game/data/loc/maps_act2.csv`.
- [x] The route runs on from Corrow through Ch16 (30 stops).
- [x] A layout's own `ramps` draw as pads, so the flights join their landings.
- [x] `test_zone_map` checks each zone: ground, walls, POIs inside, named, known glyphs, on the route. `test_zone_map_pois.py` checks that each source agrees and each hint names a block. Pseudo-loc covers three map shots.
- [x] Shots `field_menu_map_keth_pass`, `field_menu_map_lowlight` and `field_menu_map_ansedra` are added; the RENDER-REQUEST is in the live log.
- [ ] The baselines are approved once rendered.
- [ ] Act II objectives (objectives.json rows) wait on the beat sheets (M4-C10-01 onward) and the chapters' story flags.

## Notes
- **POIs follow layout points.** When act1-chapters moves a spawn or mark, `test_zone_map_pois.py` names the POI to move.
- **Rebuilding the data.** It was authored with a one-off script; edit `zone_maps.json` directly from now on.

## Review log
- 2026-10-28, ui-menus: **paused (ADR 0041, the human's refocus on Act I at final quality).** What is built stays on claude/ui and merges as is; nothing is reverted. Resume when a new ADR lifts the pause.

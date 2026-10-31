---
id: M5-A3P-1021
title: "Request (act1-chapters): what act2-plan's Act III flows played that the owned Ch17–Ch21 flows don't yet"
role: cinematics
status: todo
owner_session: ""
depends_on: [M5-A3P-1001, M5-A3P-1004, M5-A3P-1007, M5-A3P-1011, M5-A3P-1015]
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
act1-chapters own every chapter's levels and flows, Ch10–Ch21 and the Ending (the Lead, 2026-10-31; ownership.md
2f9cf3af). act2-plan's own Ch18–Ch21 staging and flow data stay out. This lists what those flows did that the owned
flows at 2f9cf3af don't yet, so nothing in the scripts goes unplayed. The scripts, their loc and the objective text
are on integration from claude/act2-plan. My last flow versions are in claude/act2-plan's history before the clean cut,
as a reference only (`git show adb39df55:game/data/flow/chapters/ch18.json` and so on).

## Scenes no flow, layout, encounter or menu plays yet
Each is one scene file (dlgc: the first node's title is the file's stem), so a trigger's `{"dialogue": id}` plays it.
- **Ch17 at Hollowmere:** `ch17_dock_master_points` (B03, the dock-master points at the last berth),
  `ch17_after_the_blank_page` (B06, after the ledger), the hull's `ch17_hull_tool_rack` and `ch17_hull_chart_wall`
  (split out of `ch17_hull_sails`, which your a3 comment waits on as M5-A3P-1202), and the barks split out of
  `ch17_bark_lookout`: `ch17_bark_tally_keeper` (the clerk), `ch17_bark_chandler` (the vendor), `ch17_bark_pell_windmills`
  (overheard) and `ch17_bark_ysolde_asleep` (at the dock-master's table after B11).
- **Ch18:** the heirloom errands, one scene each, in the zones `kite_log.json` names (`ch18_heirloom_rhen` at
  Hollowmere's berths, `_liss` at the dock-master's table, `_toma` and `_kerrid` at Corrow, `_pell` at Reedhollow by the
  clutch, `_ysolde` on the Kite's deck, `_asha` at Haluna, which waits on M5-A3P-1019); `ch18_child_older` (K06, the
  child at Reedhollow, optional); `ch18_backs_to_the_water` (K07's night on the deck); `ch18_revisit_oruvel` (waits on
  M5-A3P-1018).
- **Ch20:** `ch20_bark_vowbound_fights` (the six Vowbound's fight lines: an encounter's `barks`, combat M5-A3P-1013).
- **The Ending:** `ending_the_dark_sea`, `ending_beach_rite` (Haluna's rite, M5-A3P-1019) and `ending_first_lamp`.
- **Ch17's hand-off to the Kite:** M5-A3P-1020.

## Objective rows (the text is in game/data/loc/ch17..ch21.csv)
These were my rows, keyed to my flows' flags and POIs. Take what fits your flags and POIs, and drop the rest along
with their OBJ_ text, or tell me in my live log and I'll reword it:
```json
{"id": "hm_drydock", "line_key": "OBJ_CH17_DRYDOCK", "requires": ["ch17_started"], "until": "ch17_saw_the_hull", "zone": "ch17/hollowmere", "target": {"zone": "ch17/hollowmere", "poi": "drydock"}},
{"id": "hm_hull", "line_key": "OBJ_CH17_HULL", "requires": ["ch17_saw_the_hull"], "until": "ch17_read_the_ledger", "zone": "ch17/hollowmere", "target": {"zone": "ch17/hollowmere", "poi": "dace_hull"}},
{"id": "hm_choice", "line_key": "OBJ_CH17_CHOICE", "requires": ["ch17_read_the_ledger"], "until": "ch17_chose_the_unbinding", "zone": "ch17/hollowmere", "target": {"zone": "ch17/hollowmere", "poi": "dace_hull"}},
{"id": "hm_lamp", "line_key": "OBJ_CH17_LAMP", "requires": ["ch17_chose_the_unbinding"], "until": "ch17_first_lamp_lit", "zone": "ch17/hollowmere", "target": {"zone": "ch17/hollowmere", "poi": "dace_hull"}},
{"id": "hm_table", "line_key": "OBJ_CH17_TABLE", "requires": ["ch17_first_lamp_lit"], "until": "ch17_verse_begun", "zone": "ch17/hollowmere", "target": {"zone": "ch17/hollowmere", "poi": "house"}},
{"id": "hm_board", "line_key": "OBJ_CH17_BOARD", "requires": ["ch17_verse_begun"], "until": "ch17_complete", "zone": "ch17/hollowmere", "target": {"zone": "ch17/hollowmere", "poi": "dace_hull"}},
{"id": "hm_side_berth", "line_key": "OBJ_CH17_SIDE_BERTH", "requires": ["ch17_read_the_ledger"], "until": "ch17_first_berth", "zone": "ch17/hollowmere", "side": true, "target": {"zone": "ch17/hollowmere", "poi": "first_berth"}},
{"id": "k_chart", "line_key": "OBJ_CH18_CHART", "requires": ["ch18_started"], "until": "ch18_world_open", "zone": "ch18/kite", "target": {"zone": "ch18/kite", "poi": "chart"}},
{"id": "k_reedhollow", "line_key": "OBJ_CH18_REEDHOLLOW", "requires": ["ch18_world_open"], "until": "ch18_pell_named"},
{"id": "r_teach", "line_key": "OBJ_CH18_TEACH", "requires": ["ch18_pell_named"], "until": "ch18_learned_farewell_tide", "zone": "ch10/reedhollow", "target": {"zone": "ch10/reedhollow", "poi": "shore"}},
{"id": "r_side_heirloom", "line_key": "OBJ_CH18_SIDE_REED_SPEAR", "requires": ["ch18_pell_named"], "until": "ch18_heirloom_pell", "zone": "ch10/reedhollow", "side": true, "target": {"zone": "ch10/reedhollow", "poi": "clutch"}},
{"id": "k_side_parcel", "line_key": "OBJ_CH18_SIDE_PARCEL", "requires": ["ch18_world_open"], "until": "ch18_heirloom_ysolde", "zone": "ch18/kite", "side": true},
{"id": "i_vigil", "line_key": "OBJ_CH19_VIGIL", "requires": ["ch19_started"], "until": "ch19_vigil", "zone": "ch19/iskarra"},
{"id": "i_hitch", "line_key": "OBJ_CH19_HITCH", "requires": ["ch19_vigil"], "until": "ch19_learned_the_hitch", "zone": "ch19/iskarra"},
{"id": "i_spire", "line_key": "OBJ_CH19_SPIRE", "requires": ["ch19_learned_the_hitch"], "until": "ch19_abiding_beaten", "zone": "ch19/iskarra"},
{"id": "i_side_words", "line_key": "OBJ_CH19_SIDE_WORDS", "requires": ["ch19_learned_the_hitch"], "until": "ch19_words_whole", "zone": "ch19/iskarra", "side": true},
{"id": "s_engine", "line_key": "OBJ_CH19_ENGINE", "requires": ["ch19_abiding_beaten"], "until": "ch19_engine_stopped", "zone": "ch19/iskarra_spire"},
{"id": "u_down", "line_key": "OBJ_CH20_DOWN", "requires": ["ch20_started"], "until": "ch20_ethren_released"},
{"id": "u_cage", "line_key": "OBJ_CH20_CAGE", "requires": ["ch20_ethren_released"], "until": "ch20_cage_broken"},
{"id": "h_centre", "line_key": "OBJ_CH21_CENTRE", "requires": ["ch21_started"], "until": "ch21_kesh_fought"}
```

## Acceptance criteria
- Every scene above is played by a flow, trigger, encounter or menu, or is listed here as dropped, with a reason.
- Act III's chapters show an objective line in the field menu.

## Review log

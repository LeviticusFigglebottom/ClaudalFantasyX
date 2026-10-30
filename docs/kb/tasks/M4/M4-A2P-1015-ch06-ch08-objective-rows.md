---
id: M4-A2P-1015
title: "Request (act1-chapters): the Ch6 and Ch8 objective rows; the text is written (OBJ_CH06_*, OBJ_CH08_*)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
The Lead asked story to write the Ch6 and Ch8 objective text, and act1-chapters to add the rows. Until now
`game/data/flow/objectives.json` had no row for either chapter, so the field said OBJ_NONE across the Brine Shoals,
Corrow and Coilspire. The text is already in `game/data/loc/ch06.csv` and `ch08.csv` (appended, on claude/act2-plan).
Below are the rows, in story order. Every flag, trigger and POI comes from `game/data/flow/chapters/ch06.json`,
`ch08.json` and the zone layouts. Story owns the wording; act1-chapters owns the flags, order and targets, so change
those freely and tell story if a line no longer fits.

Place them in story order: the Ch6 rows go after `a_side_quench` (Ch5); the Ch8 rows go after the Ch7 `g_*` rows and
before `c_landing` (Ch9).

```json
{"id": "s_shoals", "line_key": "OBJ_CH06_SHOALS", "requires": ["ch06_arrived"], "until": "ch06_inquisitor_yielded", "zone": "ch06/brine_shoals", "target": {"zone": "ch06/brine_shoals", "poi": "last_ridge"}},
{"id": "s_channel", "line_key": "OBJ_CH06_CHANNEL", "requires": ["ch06_camp_made"], "until": "ch06_done", "zone": "ch06/brine_shoals", "target": {"zone": "ch06/brine_shoals", "poi": "channel"}},
{"id": "s_side_tideline", "line_key": "OBJ_CH06_SIDE_TIDELINE", "requires": ["ch06_camp_made"], "until": "ch06_saw_lamp_buried", "zone": "ch06/brine_shoals", "side": true, "target": {"zone": "ch06/brine_shoals", "poi": "tideline"}},
{"id": "k_wall_head", "line_key": "OBJ_CH08_WALL_HEAD", "requires": ["ch08_arrived_corrow"], "until": "ch08_met_ivo", "zone": "ch08/corrow"},
{"id": "k_wall_gate", "line_key": "OBJ_CH08_WALL_GATE", "requires": ["ch08_met_ivo"], "until": "ch08_beacon_opened", "zone": "ch08/corrow", "target": {"zone": "ch08/corrow", "poi": "wall_gate"}},
{"id": "k_side_stair", "line_key": "OBJ_CH08_SIDE_STAIR", "requires": ["ch08_met_ivo"], "until": "ch08_saw_the_stair", "zone": "ch08/corrow", "side": true, "target": {"zone": "ch08/corrow", "poi": "fisher_stair"}},
{"id": "q_path", "line_key": "OBJ_CH08_PATH", "requires": ["ch08_met_ivo"], "until": "ch08_entered_coilspire", "zone": "ch08/coilspire", "target": {"zone": "ch08/coilspire", "poi": "spire_door"}},
{"id": "q_side_hearth", "line_key": "OBJ_CH08_SIDE_HEARTH", "requires": ["ch08_met_ivo"], "until": "ch08_entered_coilspire", "zone": "ch08/coilspire", "side": true, "target": {"zone": "ch08/coilspire", "poi": "keepers_hut"}},
{"id": "q_flues", "line_key": "OBJ_CH08_FLUES", "requires": ["ch08_entered_coilspire"], "until": "ch08_flame_at_crown", "zone": "ch08/coilspire"},
{"id": "q_crown", "line_key": "OBJ_CH08_CROWN", "requires": ["ch08_flame_at_crown"], "until": "ch08_virel_bound", "zone": "ch08/coilspire"},
{"id": "q_beacon", "line_key": "OBJ_CH08_BEACON", "requires": ["ch08_virel_bound"], "until": "ch08_beacon_opened", "zone": "ch08/coilspire"}
```

### Notes
- **Targets left open:**
  - `k_wall_head`: there is no wall-head POI in `ch08/corrow`, though `MAP_POI_K_WALL_HEAD` exists in loc. The Ivo trigger is at (14.9, 2.4).
  - `q_flues`, `q_crown`, `q_beacon`: `ch08/coilspire` lists no tier or crown POI, though `MAP_POI_Q_SECOND_TIER`, `_FOURTH_TIER` and `_CROWN` exist in loc. The crown trigger is at (308.5, 159.1) and the great key at (308, 162).
  - If ui adds those POIs, point the rows at them.
- **No rows for the Ch8 night (the stair holds, the Reach, the wall falling, the cut rope).** Every step there runs from `arrive` with no walking, so the line would never be read.
- **Side rows, not main:**
  - `k_side_stair`: the stair look is a 20-second wordless insert, off the line to the wall-gate. Its line names no one and says nothing about who held the stair (act1_ch08 rule 3).
  - `q_side_hearth`: Fenn's Keeping Flame is optional (act1_ch08 §4).
- **Voice:** these match the Act I lines (OBJ_P_*, OBJ_T_*, OBJ_C_*): plain imperatives with one concrete thing from the place. The burned lamp's line says only where Liss is, never why (act1_ch06 B09: nobody says whose name).
- **test_qa_threads:** `ch08_flame_at_crown` is set by the flue puzzle (`ch08_field.json`), not by the thread. If the thread check flags it, add it to `qa_known.json` "unraised" with that reason, or raise it in the thread.

## Acceptance criteria
- [ ] The rows are in `objectives.json`; `python3 tools/validate_data.py` is clean.
- [ ] Godot `--filter=objective` and `--filter=qa_threads` are green.
- [ ] Walking Ch6 and Ch8, each line names what is next, and none shows over a scripted stretch.

## Review log

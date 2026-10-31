---
id: M5-A3P-1004
title: "Request (staging + flow): Ch18: the Kite zone, the K01–K23 shots, the marks, and the flow with its revisits"
role: cinematics
status: doing
owner_session: "act1-chapters"
depends_on: [M5-A3P-1003, M5-A3P-1001]
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
The Ch18 scripts are in `game/data/dialogue/ch18/` (M5-A3P-1003). Beats: docs/kb/story/act3/act3_ch18.md §2 (K01–K08), §4 (the
revisits, Haluna's lifting), §5 (the heirlooms). File-to-beat map: drafts README "Files by beat".

## What the scripts name
- **Zones:**
  - `ch18/kite`: new. It is the deck, the chart table and the stern rail, and it hosts K01–K02, K07 and K08.
  - Act I/II zones revisited: `ch01/oruvel`, `ch02/haluna`, `ch05/pemakar`, `ch07/tamsule`, `ch08/corrow`, `ch10/reedhollow`, `ch12/quellan` and `ch17/hollowmere`. Ansedra is seen from the air only.
- **Shots:** K01–K23. `ch10/reedhollow` has no K-ids, so there is no collision (drafts README decision 1).
- **Marks:** `chart_table clutch clutch_stone clutch_stone_b gull_ring ivo_stone kell_stall kell_stall_b kite_wheel pell_gate platform_edge_child shore_edge shore_line shore_line_crowd shore_teach shore_teach_b stair_foot stern_rail village_back`.
- **Held inputs:** a `ch18_field.json` `prompts` map. The loc rows are in `game/data/loc/ch18.csv`.
  - `lift_one`, `lift_two` and `lift_three` → FIELD_PROMPT_CH18_LIFT_ONE/_TWO/_THREE.
  - `turn_back` → FIELD_PROMPT_CH18_TURN_BACK.
- **Flow** (`ch18.json`):
  - The critical path:
    - K01 `ch18_maiden_flight` sets `ch18_started`;
    - K02 `ch18_the_chart_table` sets `ch18_world_open` and opens the world map;
    - K03–K04 `ch18_through_the_gate`;
    - K05 `ch18_farewell_tide_taught`;
    - K07 `ch18_night_aboard`;
    - K08 `ch18_iskarra` sets `ch18_complete`.
  - K06 `ch18_child_older` is optional and needs `ch10_child_asked`.
  - Offered while the world is open:
    - the seven `ch18_revisit_*` scenes;
    - `ch18_backs_to_the_water` (Haluna, flagged optional);
    - the seven heirloom nodes in `ch18_heirloom_rhen.dlg`, each at its own place. `ch18_heirloom_pell` is gated on `ch18_pell_named`.
- **Objective rows:** story writes the text once the flags and POIs exist.

## Acceptance criteria
- [ ] The shots, marks and the `ch18/kite` zone exist, and no Ch18 scene warns about an unknown shot or mark.
- [ ] The flow plays the critical path in order and offers the revisits and heirlooms; Godot `act3` stays green.

## Notes
- **act1-chapters, 2026-10-31 (the flow half, ADR 0207):**
  - **The new `ch18/kite` zone:**
    - its greybox comes from `tools/act3/ch18_greybox.py`: the deck, wheel, mast, chart table and rails;
    - spawns `Deck` and `ChartTable`; marks `chart_table`, `kite_wheel`, `stern_rail`;
    - `Ch18Zone` holds the three lift inputs (`ch18_field.json`);
    - a `locations.json` row and `LOCATION_CH18_KITE`.
  - **The flow** (`chapters/ch18.json`):
    - K01 `ch18_maiden_flight` on boarding (Hollowmere's `aboard` now hands on to the Kite);
    - K02: the chart table's interact plays `ch18_the_chart_table` (`ch18_world_open`);
    - **the courses:** until Design's Kite world map exists, these are interactables round the table
      (`course_*`, `FIELD_PROMPT_CH18_COURSE_*`). Reedhollow, Hollowmere, Pemakar, Tamsule, Corrow and Quellan
      hand off to their zones; Ansedra plays from the air; Iskarra waits on the night;
    - **Reedhollow** (`ch10.json`): through the gate, then the farewell-tide, taught (K03–K05; Ch10Zone holds
      `turn_back`), with `a3_to_kite` back aboard;
    - K07 `ch18_night_aboard` on the first return aboard after the farewell-tide;
    - K08 `ch18_iskarra` from its course sets `ch18_complete`. Ch19's hand-off waits on `ch19/iskarra_spire`
      (M5-A3P-1007).
  - **The revisits** (§4), each once (`ch18_revisit_<town>_seen`):
    - Pemakar, Tamsule and Corrow play on landing and go back aboard (their layouts are env-art-b's generated
      ones, so they get no trigger);
    - Quellan and Hollowmere play on landing and offer `a3_to_kite`;
    - Ansedra plays from the air.
  - **Not done:**
    - Oruvel and Haluna: Ch1–Ch3 zones, M5-A3P-1201 to slice-polish;
    - K06 `ch18_child_older` (optional; it needs a place for the child at Reedhollow);
    - the heirloom errands (nodes of one file, M5-A3P-1200; Design's rewards);
    - the shots K01–K23 and the town marks (staging);
    - the world map (Design);
    - objective rows (story).
  - Tests: `test_ch18_thread` (the critical path, a landing town, a trigger town and Ansedra), `test_ch17_thread`,
    and the ch05, ch07, ch08 and ch10 threads all pass.

## Review log

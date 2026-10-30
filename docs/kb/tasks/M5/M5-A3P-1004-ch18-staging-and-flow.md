---
id: M5-A3P-1004
title: "Request (staging + flow): Ch18: the Kite zone, the K01–K23 shots, the marks, and the flow with its revisits"
role: cinematics
status: todo
owner_session: ""
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

## Review log

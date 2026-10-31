---
id: M5-A3P-1004
title: "Request (staging + flow): Ch18: the Kite zone, the K01–K23 shots, the marks, and the flow with its revisits"
role: cinematics
status: doing
owner_session: "claude/act2-plan (supplementing act1-chapters/cinematics, the Lead 2026-10-30 23:26; ADR 0207)"
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
    - the seven heirloom scenes `ch18_heirloom_<hero>.dlg` (one file each, at its own place). `ch18_heirloom_pell` is gated on `ch18_pell_named`.
- **Objective rows:** story writes the text once the flags and POIs exist.

## Acceptance criteria
- [ ] The shots, marks and the `ch18/kite` zone exist, and no Ch18 scene warns about an unknown shot or mark.
- [ ] The flow plays the critical path in order and offers the revisits and heirlooms; Godot `act3` stays green.

## Done so far (act2-plan, supplementing): the critical path
- **The Kite zone `ch18/kite`:**
  - `tools/act1/ch18_greybox.py` (new) builds the deck with the wheel, chart table, rails, engine hatch, masts and sails.
  - It adds the marks, shots K01–K04, K13, K14, K22 and K23, and 4 triggers: the chart, Iskarra, Ysolde's heirloom, and Ansedra from the air.
  - The night aboard is a light variant.
  - Also new: `Ch18Zone`, `kite.tscn`, the `locations.json` row and `LOCATION_CH18_KITE`.
- **Reedhollow (`reedhollow_act3()` in `tools/act1/ch10_greybox.py`):**
  - marks (the clutch's stone, the shore teaching, the child's platform, the sea, the lagoon);
  - Owa and the name-carver as stand-in actors;
  - shots K05–K12;
  - three Ch18-gated triggers: the farewell-tide, the child, and Pell's heirloom;
  - Ch18's day light as a variant.
  - Ch10's content is unchanged.
- **Held inputs:** `Ch05Zone` has an optional `CutsceneHoldGate` (`hold_field_path`). It is set on the Kite, Reedhollow and Hollowmere scenes, and every Act III prompt is in `game/data/flow/act3_field.json`. This replaces Ch17's own field file.
- **Flow:** `game/data/flow/chapters/ch18.json`:
  - the Kite: K01 on arrival; K02 at the chart (sets `kite_flying`, so the world map opens); K07 on the arrival after the farewell-tide; K08 at the chart → the end card until Ch19's Iskarra;
  - Reedhollow's Act III block: K03–K04 on arrival; K05 on the shore → back aboard; K06 optional.
  - Ch17's boarding now goes to the Kite.
- **Test:** `tests/integration/test_ch18_thread.gd` covers the critical path and the child's gate.

## Done since (the revisits)
- **K07 and K08 on one arrival.** The night aboard, the rest, then Iskarra at the chart table in the morning. Nobody is left ashore with no way back to the deck. The revisits are offered between K02 and K05.
- **Hollowmere:** the dock-master at work (`ch18_revisit`), Dace's hooks at the rack, and Tobin's drawings on the table. Ch17's hull interactables are now blocked by `ch17_complete`.
- **Corrow** (its hand-kept layout, appended): from `ch18_started`, daylight, the low town drained, and Marra and her child at the stair head. Also `ch18_revisit`, Toma's and Kerrid's heirlooms, `ivo_stone`, `stair_foot`, and K21.
- **Tamsule** (gull ring, K20), **Pemakar** (Garo at the forge, K19) and **Quellan** (`quellan_act3()` in `tools/act1/ch12_greybox.py`): one `ch18_revisit` each.
- `ch18.json` has a block for each of those zones (ChapterRegistry: chapter 18).
- `test_ch18_thread` (5 cases) covers them. The Ch5, Ch7, Ch8, Ch10 and Ch12 threads are unchanged and green.

## Still to do here
- **Oruvel:** M5-A3P-1018 (the post-storm look, no Kell, a Kite destination).
- **Haluna:** M5-A3P-1019 (a HalunaStory hook).
- **Known gap:** the older zones' own field barks (Tamsule's Tidecup-week barks, for example) may still play on a Ch18 visit where their flags allow. Each zone's owner can gate them with `blocked_by_flag: ch18_started` when it next touches the zone.

## Review log

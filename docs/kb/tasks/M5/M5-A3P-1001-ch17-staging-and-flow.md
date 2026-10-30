---
id: M5-A3P-1001
title: "Request (staging + flow): Ch17 at Hollowmere: the D01–D18 shots, the marks, and a chapter flow that plays the scenes"
role: cinematics
status: todo
owner_session: ""
depends_on: [M5-A3P-1000]
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
The Ch17 scripts are in `game/data/dialogue/ch17/` (M5-A3P-1000). Every scene is located in `ch17/hollowmere`, the
zone Ch15 already uses. Beat order and modes: docs/kb/story/act3/act3_ch17.md §2. File-to-beat map: drafts README "Files by beat".

## What the scripts name
- **Shots:** D01–D18. These are not H-ids: `ch17/hollowmere` already has H01–H16 from the greybox and Ch15 (drafts README decision 1).
- **Marks:** `berth_walk cabin_seat cabin_seat_b deck_centre deck_rail deck_rail_b engine_bench engine_bench_b fathers_door fathers_table first_berth first_berth_b`.
- **Anims:** `climb clutch give hand_on hold_rope lay_out look_at nod pick_up point seat seat_burner_seat sleep_over touch turn_collar`.
- **Held inputs** (`<<event hold_input …>>`): a `ch17_field.json` `prompts` map, like `ch09_field.json`:
  - `turn_page` → FIELD_PROMPT_CH17_TURN_PAGE;
  - `hold_steady` → FIELD_PROMPT_CH17_HOLD_STEADY;
  - `turn_collar` → FIELD_PROMPT_CH17_TURN_COLLAR;
  - `seat_it` → FIELD_PROMPT_CH17_SEAT_IT.
  - The loc rows are in `game/data/loc/ch17.csv`.
- **Flow:** `game/data/flow/chapters/ch17.json`, in this order:
  - B01 `ch17_pulled_from_the_sea` (arrive, sets `ch17_started`);
  - B03 `ch17_dock_master_points`;
  - B04 `ch17_hull_sails` (three interactables);
  - B05 `ch17_the_ledger`;
  - B06 `ch17_after_the_blank_page`;
  - B07 `ch17_first_berth` (optional);
  - B08 `ch17_the_choice`;
  - B09 `ch17_bark_kesh_chosen` (from the Vowbound menu: a Combat/UI hook, decision 6);
  - B10 `ch17_the_first_lamp`;
  - B11 `ch17_ysoldes_table`;
  - B02/B12 barks `ch17_bark_lookout`.
  - `ch17_complete` is set when the player boards the hull.
  - The hand-off from Ch16's swept-away goes to `ch17/hollowmere` at the sea.
- **Objective rows:** story writes their text once the flow's flags and POIs exist. Ask in the act2-plan live log.

## Acceptance criteria
- [ ] Each shot and mark exists, so the cutscene player raises no unknown-shot or unknown-mark warning on any Ch17 scene.
- [ ] The Ch17 flow plays the scenes in beat order; the Godot `act3` and `dialogue` tests stay green.

## Review log

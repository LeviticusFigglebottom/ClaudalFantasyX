---
id: M5-A3P-1001
title: "Request (staging + flow): Ch17 at Hollowmere: the D01–D18 shots, the marks, and a chapter flow that plays the scenes"
role: cinematics
status: doing
owner_session: "act1-chapters"
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

## Notes
- **act1-chapters, 2026-10-31 (the flow half, ADR 0207):**
  - **The shared zone:** Hollowmere stays Ch15's in `chapters.json`'s first match. `Ch17Zone` points the zone's
    `chapter_path` at the new `chapters/ch17.json` once `ch16_act_two_complete` is set, and adds Ch9's held
    input for the four prompts (`game/data/flow/ch17_field.json`, as ch09's). `chapter_flow_check` now accepts a
    trigger's beat from any chapter file that lists the zone (tools test added). Ch16's swept-away goes on to
    `ch17/hollowmere` Dock.
  - **The flow, in beat order:**
    - B01 `ch17_pulled_from_the_sea` on arrival (chapter 17);
    - B03 `ch17_dock_master_points` on the gangway (`a3_berths`, placed at `Berths`);
    - B04 `ch17_hull_sails` from the walk's end, then aboard by the ladder (`a3_board` → `HullDeck`);
    - B05–B06: the hatch plays the ledger in the cabin, then dusk on the deck;
    - B07 `ch17_first_berth` at Tobin's post (optional);
    - B08, B10, B11: "Rest" on the deck plays the choice, then the first lamp in the engine bay, then Ysolde's
      table (`Fathers`);
    - B12: the lookout's bark, then boarding the hull (`a3_aboard`) sets `ch17_complete`. Ch18's hand-off waits
      on `ch18/kite` (M5-A3P-1004);
    - B09 is the Vowbound menu's hook (Combat/UI).
  - **The layout** (env-art-b's coordinates, M5-A3P-1500): a gangway from the dock's east end to the first berth,
    the walk along the berths' heads, Tobin's berth deck, and floors for the hull's deck, cabin and engine bay.
    All of it is hidden until `ch17_started`; then the dock's east bound opens. Ch15's barks and ship close at
    `ch15_complete`.
  - **Marks:** all twelve the scripts name (`cabin_seat(_b)`, `deck_centre`, `deck_rail(_b)`,
    `engine_bench(_b)`, `fathers_table`, `first_berth(_b)`, `berth_walk`, and the existing `fathers_door`), with
    spawns `Berths`, `HullDeck`, `Cabin`, `EngineBay` and `Fathers`.
  - **Not done:**
    - the D01–D18 shots (staging, slice-polish's as in Act II);
    - five barks and two hull interactables that are nodes inside other files (M5-A3P-1200 asks story to split
      them);
    - objective rows (story writes their text).
  - Tests: `test_ch17_thread` (Ch15's visit unchanged; Ch17 in order) and `test_ch14_16_walkable` (the dock to the
    berths, Tobin's post and the berth walk, through env-art-b's kit colliders); ch14_16 and the tools'
    chapter-flow test pass.
  - **env-art-b:** the walk is in, so the berths' and hull's kit collision can follow. The gangway runs
    (60, 0) → (88.15, −0.42); the berth walk runs from there to (79.65, −15.14), 3.6 m wide; boarding is by
    `place` until your hatch ramp exists.

## Review log

---
id: M5-A3P-1001
title: "Request (staging + flow): Ch17 at Hollowmere: the D01–D18 shots, the marks, and a chapter flow that plays the scenes"
role: cinematics
status: review
owner_session: "claude/act2-plan (supplementing act1-chapters/cinematics, the Lead 2026-10-30 23:26; ADR 0207)"
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

## Done (act2-plan, supplementing; the owner tracks keep the paths and the review)
- **Shared zones (engine, small):**
  - `ChapterRegistry.zone()` now takes the story's chapter. Among the chapter files that have a zone, it uses the first whose chapter is the current one or later, else the first. Hollowmere is Ch15's in Ch15 and Ch17's from chapter 16 on.
  - `ZoneStory` passes `Game.state.chapter`.
  - Test: `tests/unit/test_chapter_registry.gd`.
  - `tools/chapter_flow_check.py` now checks a layout's triggers against every file's beats for the zone.
  - No zone was in two files before, so Act I and Act II behave as they did.
- **Greybox:**
  - In `tools/act1/ch15_16_greybox.py`, `hollowmere_drydock()` builds the jetty, the quay, the first berth and Dace's hull (deck, cabin, engine housing, tool rack, masts, sails). It also adds the dock-master's table.
  - `hollowmere_act3()` adds the spawns `Quay` and `ShipDeck`, 21 marks, 4 stand-in actors (shown or hidden by variant), shots D01–D18, a follow volume, 16 triggers, and 4 light variants (noon, dusk, night, morning).
  - Ch15's own content and staging are unchanged.
- **Held inputs:** `Ch17Zone` has a `CutsceneHoldGate`, as Ch9 does; `game/data/flow/ch17_field.json` maps the prompts.
- **Flow:** `game/data/flow/chapters/ch17.json`, registered in `chapters.json`:
  - arrive rows: the sea, a mid-chapter return, and the default;
  - beats B03, B05–B06, B07, B08 (night, then the rest and the morning), B10, B11 and boarding;
  - barks on triggers.
  - The exit is the end card until Ch18's Kite zone (M5-A3P-1004).
  - New flag: `ch17_night`.
- **Objectives:** 7 rows (`hm_*`), with their text and 3 POIs (`drydock`, `dace_hull`, `first_berth`) in `zone_maps.json`. The text is in `loc/ch17.csv`.
- **Test:** `tests/integration/test_ch17_thread.gd` checks:
  - out of Ch16, Hollowmere is Ch17's;
  - Ch15 still gets its own;
  - the chapter runs from the sea to boarding.

## Open
- **The Ch16 → Ch17 hand-off:** Ch16's `ch16_swept_away` has no flow step yet (M4-A2P-1012). It should end in `{"go": {"location": "ch17/hollowmere", "spawn": "ShipDeck"}}`.
- **B09** (Kesh's call bark) waits on a Vowbound-menu hook.
- **Missing music and sound:** the cues are M5-A3P-1002. Headless, the scenes warn about them.

## Review log

---
id: M3-HER-1130
title: "Tests that leave nodes in the scene tree (the runner frees and reports them; owners free their own)"
role: qa
status: doing
owner_session: "integration-qa (hero-integration track, session_01PzF7Jc4XVQdTWcaYUyCjPB)"
reviewer: lead
depends_on: []
milestone: M3
request-from: lead
---
## Goal
A test that leaves a node under the current scene can break every later test. One field zone left by
test_hero_stairs failed ~30 tests in big13. Since c895c542+ the runner frees whatever a test leaves there and prints a
`LEAK <file>::<test>: ...` line. The summary reads "Tests: N run, M failed, K left nodes in the tree". It reports and
doesn't fail yet, so no track's suite goes red overnight.

## Acceptance criteria
- [x] The full list of leaking tests, by owner, with a request to each owner (each test frees what it and its
      before_each add, or queue_frees it).
- [ ] When the list is empty, the runner fails a leak (one line in tests/run_tests.gd), so none come back.

## The list (full suite on lead/gate-big17 @ 1a986abf, 2026-10-29: 3241 run, 59 tests leave nodes)
Each test below leaves these nodes under the current scene when it returns. The runner frees them and prints `LEAK`.
Fix: free them at the end of the test, or keep them in an array that a `_done()` frees. Owners are by subject.
Since 10-28: creatures' 13 (test_creature_actor) and act1-chapters' are all gone.

### battle-presentation (9)
- `test_battle_boss_vfx.gd::test_data_names_swatches_effects_skills_and_the_haluna_flood`: BattleSandbox
- `test_battle_controller.gd::test_berserk_and_confused_party_turns_are_announced_and_play_themselves`: BattleSandbox
- `test_battle_controller.gd::test_capture_states_run_on_fixture_data_not_live_balance`: BattleSandbox
- `test_battle_controller.gd::test_fixture_overrides_never_touch_the_shared_tables`: BattleSandbox
- `test_fighter_actor.gd::test_a_scene_spec_shows_the_actor_instead_of_the_primitive`: tester_1
- `test_fighter_actor.gd::test_petrify_and_ko_reach_every_surface`: tester_1
- `test_fighter_actor.gd::test_an_actor_with_a_ko_clip_does_not_sink`: tester_1
- `test_fighter_actor.gd::test_a_missing_scene_falls_back_to_the_primitive`: tester_1
- `test_fighter_actor.gd::test_a_plain_spec_is_unchanged`: tester_1

### creatures-b (1)
- `test_creature_bosses_act1.gd::test_every_act1_vowbound_skill_and_finisher_has_its_clip`: Ilun, Kahre, Virel

### env-art (1)
- `test_zone_kit_dressing.gd::test_the_quick_reject_keeps_the_clip_exact`: BrineShoals

### ui-menus (48)
- `test_act_card.gd::test_act_two_is_loc_keyed_on_black`: ActCard
- `test_act_card.gd::test_act_three_closes_act_two`: ActCard
- `test_act_card.gd::test_an_unknown_act_shows_nothing`: ActCard
- `test_act_card.gd::test_a_caption_is_one_line`: ActCard
- `test_act_card.gd::test_reduced_motion_does_not_rise`: ActCard
- `test_act_card.gd::test_the_act_card_event_shows_it`: @Node@694, ActCard
- `test_act_card.gd::test_open_in_puts_it_on_its_own_layer`: @Node@704
- `test_area_title_card.gd::test_it_cards_the_location_once_then_fades`: AreaTitleCard, AreaTitleCard2, AreaTitleCard3, AreaTitleCard4
- `test_area_title_card.gd::test_test_rooms_and_unknown_scenes_get_none`: AreaTitleCard, AreaTitleCard2
- `test_area_title_card.gd::test_a_menu_ends_it_and_reduced_motion_does_not_rise`: AreaTitleCard
- `test_battle_vowbound_hud.gd::test_bound_ids_follow_each_rows_flag`: BattleSandbox
- `test_character_names.gd::test_the_dialogue_box_names_him`: DialogueBox
- `test_dialogue_assist.gd::test_auto_advance_waits_while_paused_or_the_backlog_is_open`: @CanvasLayer@141055
- `test_dialogue_assist.gd::test_the_backlog_action_opens_the_page_only_while_the_box_is_up`: @CanvasLayer@141091, @CanvasLayer@141104
- `test_dialogue_assist.gd::test_the_page_opens_at_the_latest_line_and_scrolls`: @CanvasLayer@141122
- `test_dialogue_assist.gd::test_an_empty_backlog_says_so`: @CanvasLayer@141156
- `test_hold_prompt.gd::test_it_names_the_key_and_the_verb`: HoldPrompt
- `test_hold_prompt.gd::test_it_has_no_meter_and_letting_go_only_breathes`: HoldPrompt
- `test_hold_prompt.gd::test_the_gate_shows_it_for_the_whole_gate`: @Node@172445, @Node@172454
- `test_input_parity_dialogue.gd::test_the_backlog_opens_scrolls_and_closes_with_each_device`: @CanvasLayer@179297, @CanvasLayer@179331, @CanvasLayer@179365
- `test_interact_prompt.gd::test_it_fades_in_with_the_verb_and_the_key_then_out`: @Area3D@198140, InteractPrompt
- `test_interact_prompt.gd::test_an_interactable_with_no_verb_gets_the_default`: @Area3D@198146, InteractPrompt
- `test_interact_prompt.gd::test_the_keycap_follows_the_last_device`: @Area3D@198152, InteractPrompt
- `test_interact_prompt.gd::test_it_hides_while_a_menu_pauses_the_tree`: @Area3D@198158, InteractPrompt
- `test_interact_prompt.gd::test_placement_floats_over_the_point_or_docks`: @Area3D@198164, InteractPrompt
- `test_objective_hud.gd::test_it_shows_once_when_the_field_first_takes_input_then_fades`: ObjectiveHud
- `test_objective_hud.gd::test_the_line_has_height_and_wraps_inside_the_panel`: ObjectiveHud
- `test_objective_hud.gd::test_a_new_objective_shows_and_on_demand_shows_again`: ObjectiveHud
- `test_objective_hud.gd::test_it_hides_in_cutscenes_and_menus_and_waits_for_them`: ObjectiveHud
- `test_objective_hud.gd::test_the_action_is_remappable`: ObjectiveHud
- `test_objective_hud.gd::test_the_target_is_the_poi_in_this_zone_only`: ObjectiveHud
- `test_objective_hud.gd::test_the_cue_marks_on_screen_and_points_from_the_edge`: ObjectiveHud
- `test_shrine_services.gd::test_a_save_shrine_payload_rests_attunes_and_opens_the_save_menu`: @Node@237677
- `test_shrine_services.gd::test_the_road_is_offered_after_the_save_menu_and_the_shrine_is_kept`: @Node@237792
- `test_shrine_services.gd::test_other_payloads_and_unlisted_ids_do_nothing`: @Node@237796
- `test_shrine_services.gd::test_it_hears_field_interactions_on_the_bus`: @Node@237889
- `test_shrine_travel.gd::test_after_the_save_menu_the_other_shrines_are_offered_by_name`: @Node@237915
- `test_shrine_travel.gd::test_choosing_asks_first_and_go_travels`: @Node@237958
- `test_shrine_travel.gd::test_a_refused_trip_says_so_and_keeps_the_list`: @Node@237989
- `test_shrine_travel.gd::test_stay_closes_and_goes_nowhere`: @Node@238014
- `test_shrine_travel.gd::test_nowhere_to_go_offers_nothing`: @Node@238017
- `test_shrine_travel.gd::test_a_load_offers_no_road`: @Node@238042
- `test_swell_input_panels.gd::test_every_grade_has_its_word`: BattleSandbox
- `test_text_fit_probe.gd::test_text_past_its_sibling_panel_fails`: @Control@245472
- `test_text_fit_probe.gd::test_a_small_panel_over_a_wide_title_s_centre_is_not_its_box`: @Control@245475
- `test_tutorial_tips.gd::test_the_card_shows_one_tip_reads_then_the_next`: TipCard
- `test_ui_flair.gd::test_a_titled_page_draws_its_rule_and_nudges_the_cursor_row`: @Control@246529
- `test_ui_flair.gd::test_the_caustic_backdrop_fills_its_parent_and_stills_under_reduced_motion`: @Control@246561

## Review log

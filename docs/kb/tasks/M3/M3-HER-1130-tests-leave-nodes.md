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

## The list (full suite on claude/hero-integration @ eaefe445, 2026-10-28)
Each test below leaves these nodes under the current scene when it returns. Fix: free them at the end of the
test, or keep them in an array and free it in a `_done()` each test calls. A `before_each` never sees the previous
test's nodes, because the runner makes a new instance per test (the hero tests had exactly this bug, fixed in
this commit). Owners, from the files' history:

### creatures
- `test_creature_actor.gd::test_every_creature_row_names_a_scene_with_its_clips`: Stormgull, Wallcrab, FlueMoth, UndertowsReach, VeinSparker, WallPolyp, WreckCrab, SquallWing, TideCrawler, RaidHound, ShoalSkipper, CinderMatron, SlagTortoise, Ashwing, Scuttler, SparWraith, SailLeech, BottleHermit, Glassfry, OilSlug, TowerLimpet, Drownbell, Hullgnaw, ReefCrab, LanternEel, SpawnPolyp, GullHarrier, MangroveDrowner, LampEngine, AvalancheRam, Wakefin
- `test_creature_actor.gd::test_an_action_plays_its_clip_and_the_actor_idles_again`: ReefCrab
- `test_creature_actor.gd::test_ko_holds_its_pose_and_a_revive_returns_to_idle`: ReefCrab
- `test_creature_actor.gd::test_petrify_freezes_and_refuses_clips`: ReefCrab
- `test_creature_actor.gd::test_a_creature_without_phases_or_parts_ignores_them`: ReefCrab
- `test_creature_actor.gd::test_the_stand_in_hands_ko_and_stone_to_the_creature`: reef_crab_1, lantern_eel_1
- `test_creature_actor.gd::test_the_drownbells_rim_breaks_and_mends`: Drownbell
- `test_creature_actor.gd::test_the_flood_phase_sinks_the_bell_and_idles_on_its_flood_clip`: Drownbell, (unnamed Node3D)
- `test_creature_actor.gd::test_phase_nodes_hide_at_once_or_after_the_clip`: CinderMatron, Hullgnaw, (unnamed Node3D), SparWraith
- `test_creature_actor.gd::test_a_phase_plays_its_own_strikes`: UndertowsReach
- `test_creature_actor.gd::test_the_mangrove_drowner_uproots_and_strikes_risen`: MangroveDrowner
- `test_creature_actor.gd::test_the_lamp_engine_opens_its_rings_and_strikes_open`: LampEngine
- `test_creature_actor.gd::test_the_avalanche_ram_charges_bellows_and_lies_down`: AvalancheRam
- `test_creature_actor.gd::test_the_wakefin_circles_cuts_dives_and_floats_belly_up`: Wakefin
- `test_creature_actor.gd::test_hits_rotate_their_variants_and_a_phase_keeps_its_own`: ReefCrab, UndertowsReach
- `test_creature_actor.gd::test_an_idling_creature_fidgets_now_and_then`: ReefCrab, (unnamed Node3D), (unnamed Node3D)
- `test_creature_actor.gd::test_a_portrait_shows_an_enemy_with_a_model_and_nothing_otherwise`: CreaturePortrait
- `test_creature_actor.gd::test_a_hit_snaps_onto_its_struck_pose`: ReefCrab

### ui-menus
- `test_objective_hud.gd::test_it_shows_once_when_the_field_first_takes_input_then_fades`: ObjectiveHud
- `test_objective_hud.gd::test_the_line_has_height_and_wraps_inside_the_panel`: ObjectiveHud
- `test_objective_hud.gd::test_a_new_objective_shows_and_on_demand_shows_again`: ObjectiveHud
- `test_objective_hud.gd::test_it_hides_in_cutscenes_and_menus_and_waits_for_them`: ObjectiveHud
- `test_objective_hud.gd::test_the_action_is_remappable`: ObjectiveHud
- `test_objective_hud.gd::test_the_target_is_the_poi_in_this_zone_only`: ObjectiveHud
- `test_objective_hud.gd::test_the_cue_marks_on_screen_and_points_from_the_edge`: ObjectiveHud
- `test_interact_prompt.gd::test_it_fades_in_with_the_verb_and_the_key_then_out`: (unnamed Area3D), InteractPrompt
- `test_interact_prompt.gd::test_an_interactable_with_no_verb_gets_the_default`: (unnamed Area3D), InteractPrompt
- `test_interact_prompt.gd::test_the_keycap_follows_the_last_device`: (unnamed Area3D), InteractPrompt
- `test_interact_prompt.gd::test_it_hides_while_a_menu_pauses_the_tree`: (unnamed Area3D), InteractPrompt
- `test_interact_prompt.gd::test_placement_floats_over_the_point_or_docks`: (unnamed Area3D), InteractPrompt
- `test_dialogue_assist.gd::test_auto_advance_waits_while_paused_or_the_backlog_is_open`: (unnamed CanvasLayer)
- `test_dialogue_assist.gd::test_the_backlog_action_opens_the_page_only_while_the_box_is_up`: (unnamed CanvasLayer), (unnamed CanvasLayer)
- `test_dialogue_assist.gd::test_the_page_opens_at_the_latest_line_and_scrolls`: (unnamed CanvasLayer)
- `test_dialogue_assist.gd::test_an_empty_backlog_says_so`: (unnamed CanvasLayer)
- `test_area_title_card.gd::test_it_cards_the_location_once_then_fades`: AreaTitleCard, AreaTitleCard2, AreaTitleCard3, AreaTitleCard4
- `test_area_title_card.gd::test_test_rooms_and_unknown_scenes_get_none`: AreaTitleCard, AreaTitleCard2
- `test_area_title_card.gd::test_a_menu_ends_it_and_reduced_motion_does_not_rise`: AreaTitleCard
- `test_ui_flair.gd::test_a_titled_page_draws_its_rule_and_nudges_the_cursor_row`: (unnamed Control)
- `test_ui_flair.gd::test_the_caustic_backdrop_fills_its_parent_and_stills_under_reduced_motion`: (unnamed Control)
- `test_text_fit_probe.gd::test_text_past_its_sibling_panel_fails`: (unnamed Control)
- `test_text_fit_probe.gd::test_a_small_panel_over_a_wide_title_s_centre_is_not_its_box`: (unnamed Control)
- `test_tutorial_tips.gd::test_the_card_shows_one_tip_reads_then_the_next`: TipCard
- `test_swell_input_panels.gd::test_every_grade_has_its_word`: BattleSandbox
- `test_input_parity_dialogue.gd::test_the_backlog_opens_scrolls_and_closes_with_each_device`: (unnamed CanvasLayer), (unnamed CanvasLayer), (unnamed CanvasLayer)
- `test_battle_vowbound_hud.gd::test_bound_ids_follow_each_rows_flag`: BattleSandbox
- `test_fighter_actor.gd::test_a_scene_spec_shows_the_actor_instead_of_the_primitive`: tester_1
- `test_fighter_actor.gd::test_petrify_and_ko_reach_every_surface`: tester_1
- `test_fighter_actor.gd::test_an_actor_with_a_ko_clip_does_not_sink`: tester_1
- `test_fighter_actor.gd::test_a_missing_scene_falls_back_to_the_primitive`: tester_1
- `test_fighter_actor.gd::test_a_plain_spec_is_unchanged`: tester_1

### act1-chapters
- `test_act_card.gd::test_act_two_is_loc_keyed_on_black`: ActCard
- `test_act_card.gd::test_an_unknown_act_shows_nothing`: ActCard
- `test_act_card.gd::test_a_caption_is_one_line`: ActCard
- `test_act_card.gd::test_reduced_motion_does_not_rise`: ActCard
- `test_act_card.gd::test_the_act_card_event_shows_it`: (unnamed Node), ActCard
- `test_act_card.gd::test_open_in_puts_it_on_its_own_layer`: (unnamed Node)
- `test_hold_prompt.gd::test_it_names_the_key_and_the_verb`: HoldPrompt
- `test_hold_prompt.gd::test_it_has_no_meter_and_letting_go_only_breathes`: HoldPrompt
- `test_hold_prompt.gd::test_the_gate_shows_it_for_the_whole_gate`: (unnamed Node), (unnamed Node)
- `test_character_names.gd::test_the_dialogue_box_names_him`: DialogueBox

### battle-presentation (combat rows: battle_controller; rendering: battle_boss_vfx)
- `test_battle_controller.gd::test_berserk_and_confused_party_turns_are_announced_and_play_themselves`: BattleSandbox
- `test_battle_controller.gd::test_capture_states_run_on_fixture_data_not_live_balance`: BattleSandbox
- `test_battle_controller.gd::test_fixture_overrides_never_touch_the_shared_tables`: BattleSandbox
- `test_battle_boss_vfx.gd::test_data_names_swatches_effects_skills_and_the_haluna_flood`: BattleSandbox

The hero layer's own (test_hero_foot_ik, test_hero_battle_actor, test_hero_battle_pops) are fixed. test_hero_stairs
was the zone behind big13's cascade (eaefe445).

## Review log

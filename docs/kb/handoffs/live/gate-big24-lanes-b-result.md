# gate-big24 lanes B result

sha 797b02cc0ee1352bee84467d20dddb5cbe07baa7

res://tests/integration/test_act1_route.gd 3 run, 0 failed
res://tests/integration/test_causeway_route.gd 5 run, 1 failed
res://tests/integration/test_ch06_thread.gd 5 run, 0 failed
res://tests/integration/test_ch08_coilspire_walkable.gd 4 run, 0 failed
res://tests/integration/test_ch08_thread.gd 6 run, 0 failed
res://tests/integration/test_cutscene_directives.gd 2 run, 0 failed
res://tests/integration/test_fp_thread.gd 2 run, 0 failed
res://tests/integration/test_haluna_town.gd 2 run, 0 failed
res://tests/integration/test_qa_threads.gd 1 run, 0 failed
res://tests/integration/test_zone_story.gd 18 run, 0 failed
res://tests/unit/test_ashcrown_audio.gd 3 run, 0 failed
res://tests/unit/test_audio_menu.gd 4 run, 0 failed
res://tests/unit/test_audio_runtime.gd 11 run, 0 failed
res://tests/unit/test_battle_screen_spread.gd 2 run, 0 failed
res://tests/unit/test_battle_stings.gd 7 run, 0 failed
res://tests/unit/test_ch08_coilspire_camera.gd 2 run, 0 failed
res://tests/unit/test_creature_actor.gd 31 run, 0 failed
res://tests/unit/test_creature_bosses_act1.gd 8 run, 0 failed
res://tests/unit/test_crowd_villagers.gd 13 run, 0 failed
res://tests/unit/test_cutscene_grade.gd 3 run, 0 failed
res://tests/unit/test_cutscene_replay.gd 3 run, 0 failed
res://tests/unit/test_debug_overlay.gd 14 run, 0 failed
res://tests/unit/test_field_menu.gd 29 run, 0 failed
res://tests/unit/test_footstep_contacts_audio.gd 8 run, 0 failed
res://tests/unit/test_haluna_footstep_surfaces.gd 2 run, 0 failed
res://tests/unit/test_life_audio.gd 14 run, 0 failed
res://tests/unit/test_menu_motion.gd 8 run, 0 failed
res://tests/unit/test_prewarm_zone_feed.gd 4 run, 0 failed
res://tests/unit/test_read_panel.gd 13 run, 0 failed
res://tests/unit/test_resident_loads.gd 9 run, 1 failed
res://tests/unit/test_scene_router_swap.gd 17 run, 0 failed
res://tests/unit/test_villager_routines.gd 19 run, 0 failed
res://tests/unit/test_voice_audio.gd 12 run, 0 failed
res://tests/unit/test_zone_kit_dressing.gd 10 run, 0 failed
res://tests/unit/test_zone_map.gd 22 run, 0 failed

## FAILURE lines

### res://tests/integration/test_causeway_route.gd
- FAILURE test_causeway_route.gd::test_the_route_after_the_harrier_meets_two_or_three_fights: at least 2 fights (206 m walk)

### res://tests/unit/test_resident_loads.gd
- FAILURE test_resident_loads.gd::test_each_zone_s_villager_actors_are_listed: haluna.tscn lists res://assets/characters/villagers/shopkeeper/shopkeeper_actor.tscn (rerun tools/loading/scene_loads.gd)
- FAILURE test_resident_loads.gd::test_each_zone_s_villager_actors_are_listed: haluna.tscn lists res://assets/characters/villagers/smith/smith_actor.tscn (rerun tools/loading/scene_loads.gd)
- FAILURE test_resident_loads.gd::test_each_zone_s_villager_actors_are_listed: haluna.tscn lists res://assets/characters/villagers/innkeeper/innkeeper_actor.tscn (rerun tools/loading/scene_loads.gd)

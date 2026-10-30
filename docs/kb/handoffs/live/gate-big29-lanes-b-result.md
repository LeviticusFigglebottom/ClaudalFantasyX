# gate-big29 lanes B result

sha 43af4e0c7d7df7a8003566e71d88beb8ebdb8f7b

res://tests/integration/test_footsteps_jog.gd 3 run, 0 failed
res://tests/integration/test_shrine_audio.gd 4 run, 0 failed
res://tests/unit/test_ashcrown_audio.gd 3 run, 0 failed
res://tests/unit/test_audio_live_hooks.gd 2 run, 0 failed
res://tests/unit/test_audio_reverb.gd 5 run, 0 failed
res://tests/unit/test_battle_audio.gd 22 run, 0 failed
res://tests/unit/test_choreo_audio.gd 17 run, 0 failed
res://tests/unit/test_crowd_villagers.gd 18 run, 0 failed
res://tests/unit/test_cutscene_face_per_actor.gd 2 run, 1 failed
res://tests/unit/test_cutscene_sound.gd 3 run, 0 failed
res://tests/unit/test_field_hud_legibility.gd 3 run, 0 failed
res://tests/unit/test_flags.gd 2 run, 0 failed
res://tests/unit/test_footstep_contacts_audio.gd 8 run, 0 failed
res://tests/unit/test_haluna_footstep_surfaces.gd 2 run, 0 failed
res://tests/unit/test_input_parity_glyphs.gd 7 run, 0 failed
res://tests/unit/test_menu_motion.gd 8 run, 0 failed
res://tests/unit/test_prop_audio.gd 2 run, 0 failed
res://tests/unit/test_pseudo_locale.gd 9 run, 0 failed
res://tests/unit/test_save_music.gd 1 run, 0 failed
res://tests/unit/test_tutorial_tips.gd 9 run, 0 failed
res://tests/unit/test_villager_snaps.gd 2 run, 0 failed
res://tests/unit/test_zone_return.gd 9 run, 0 failed

## FAILURE lines

### res://tests/unit/test_cutscene_face_per_actor.gd
- FAILURE test_cutscene_face_per_actor.gd::test_his_shipped_pose_table_is_characters: expected <{
- (helper's summary of the multi-line assert "the copy matches", which compares SHIPPED with SOURCE:) the shipped
  game/data/cutscene/sefir_face_poses.json differs from its source game/levels/_tests/characters/sefir/sefir_face_poses.json
  in two poses. The shipped `sad` is brow_inner_up 0.60, lid_close 0.28, mouth_press 0.12, and the source's is 0.35, 0.20,
  with no mouth_press. The shipped `tender` is brow_inner_up 0.35, mouth_smile 0.35, lid_close 0.22, cheek_raise 0.15, and
  the source's is 0.22, 0.22, 0.18, with no cheek_raise. Everything else matches.

# GATE lead/gate-big14 @ 8707ff90 (+ the PC's Shell Shrine GI rebake 8f6fd29f): results (PC gate runner, 2026-10-28)

- `out/<id>.png` is the WSL2 lavapipe render of every failing or new shot (302). `sheets/` has contact sheets:
  - `new_NN.jpg`: the 121 shots without a baseline, 6 to a sheet.
  - `drift_NN.jpg`: BASE | OUT | DIFF for the 181 drifts, 3 to a sheet, largest RMSE first.
  - The full diff PNGs stay on the PC (/root/keep_gate-big14-shots/out/diff).
- `compare.txt` lists every RMSE; `blender_diffs.txt` is the Blender step's log.
- The run used a fresh `.godot` import (exit 0 and the DONE line) and 2 shards. Blender ran after the suite, on the jobs changed since `claude/undertow-lead-handoff-ze8rrn` (608db549).

## Summary: FAIL (the Godot suite is being re-run; everything else is final)

| Step | Result |
|---|---|
| Shell Shrine GI | **Rebaked on this tree** (`bake_shrine_gi.tscn`, both states OK at ~1.5 s and ~930 KB, then `gi_inputs.py --write`). test_shrine_gi_bake passes. Commit 8f6fd29f, the first on this branch. |
| validate_data, audio, taskboard, gdlint, gdformat, manifest | ok |
| tools unittests | 1527 run (50 skipped), **6 failing units** (below) |
| Godot suite | **Re-running.** The first run listed 15 FAILs (below) and was then cut off by the PC's 2400 s step timeout inside `test_qa_threads` (`test_every_thread_plays_through_clean`), a long playthrough. The tests after it, coverage and the boot smoke never ran. Now re-running with a 3 h step timeout; this README and pc-gpu.md get the result. |
| Blender (77 jobs changed) | **75 identical, 2 DIFF** (below) |
| Screenshots | **523 compared, 302 failed** = 121 without a baseline + 181 over the RMSE limit. All 523 captured, **no SCRIPT ERROR at shutdown** (big12's life_audio error is gone) |
| Wall | lane B 6672 s (523 shots), Blender 1852 s, lane A ~45 min until the timeout |

### Tools failures (6 units)

- `test_arenas` reproducibility, `ash_terrace_lanternfall`: the committed scene uses `kits/pemakar/votive_lamp.glb`, the generator gives `kits/haluna/lamp_flame.glb`. Known red (env-art, M3-ENV-1306).
- `test_screenshots`: the 121 shots without a baseline; the first is `kerrid_front`.
- `test_pemakar_kit` `test_every_target_is_inside_its_budget_with_a_lod_chain`: 34 targets, the test expects 32 (owner: env-art-b).
- `test_zone_dressing_ch01`:
  - `ov_zone_dressing.py`'s layout is stale ("rerun the generator").
  - `ou_zone_dressing.py` and `wake_zone_dressing.py` raise `ZeroDivisionError` in `stairwell()` (`range(round(12.0 / strip))`).
  - Owner: env-art.
- `test_zone_map_pois` `test_every_poi_sits_where_its_source_is`: `ch04/haluna_wake/neme_house (spawn:NemeDoor)` and others are not where their source is (owner: ui-menus or act1-chapters).
- `test_hero_clips`:
  - `test_committed_libraries_rebuild_byte_for_byte`: asha's clip library doesn't rebuild byte for byte (a keyframe at 0.266667 vs 0.2).
  - `test_every_pending_clip_is_called_and_not_built`: a requested clip is no longer called.
  - Owner: characters; the grounded-run FAST-TRACK touched these.

### Godot failures listed before the timeout (15; messages with the rerun)

test_battle_act1_ability_vfx (every Act I skill has its own effect), test_battle_party_stand_ins (Liss's capsule wrapper), test_battle_result_motion, test_creature_portraits (as big12), test_field_audio (change rows and live hooks), test_hero_field_snaps (no hero body snaps in any zone), test_title_reveal (the reveal ends inside boot_title's settle frames), test_villager_routines ×3 (the wake villagers ride inside their cutscene actors; a layer added in a zone's ready; Oruvel's Kell comes alive), test_act1_cutscene_walks (every Act I cutscene walk stays on the floor), test_fp_prologue (a vigil takes its body when its hero has one), test_qa_capsules ×2 (no zone shows an unknown capsule; every foe and Vowbound has a body), test_qa_save_shrines (every shrine saves and loads back where it stands).

### Blender DIFFs (2)

- `assets/environments/kits/haluna/kirru_roost.glb`: kirru_roost-lod1.POSITION (committed 06403c78 vs rebuilt cbda5fa9). Owner: env-art.
- `assets/creatures/avalanche_ram/avalanche_ram.glb`: avalanche_ram.POSITION (committed 6549c8a9 vs rebuilt 8d990e15). The same on claude/creatures and creatures-b heads; the rebuild is the same on all three. The committed .glb no longer matches its source (maybe built on a CPU without AVX2, as in M2-CHR-11). Owner: creatures.

## The human's four FAST-TRACKS on the real GPU (RX 9070 XT, High, 2560×1440)

How it was run:
- big14 + the rebake, imported on Windows. `slice_sweep --walk=res://tools/gpu_bench/playtest_walk.json` (gpu/act1-qa-1), stills every 3 s, `ui_accept` tapped every 1.5 s to take dialogue as a player would.
- The walk: New Game → the Prologue → its hand-off to Haluna; then Ch1 and Ch2 as F8 starts them; runs from behind and from the side; then the first fight.
- `gpu_playtest/` has the sheets, the walk's CSV and its budget lines.

1. **The Prologue's opening buildings in colour: yes.** Domes, blue bands and banners are in colour on the GPU (walk_p01). Still to fix: a hard-edged, bright-green rectangle in the water next to the vigil terrace.
2. **The beach scene (Rhen in the shallows, Asha at his side): partly.**
   - The close-up on Asha reads well.
   - The wide shots show Asha kneeling at the left and Toma standing, but **Rhen is not in frame**.
   - Four lines ("I'm Asha. That's Toma…", "Toma Okeru,", "To Asha. Who is very glad…", "Later. You're shaking.") are framed on **empty sky**. Probably meant as Rhen's view lying on his back, but no face enters it; an orange blur touches one frame edge.
   - Owners: slice-polish and hero-integration (walk_p03).
3. **The party following, spaced, at the start: partly.**
   - After the cutscene the objective is "Follow Asha and Toma up the beach", and they walk ahead, spaced, to the village gate.
   - **Rhen himself is not on screen**: the field camera starts over the shallows facing the beach, with no player in frame, also from the Village spawn (haluna_start_no_rhen.jpg). He may still be lying in the shallows pose, or the camera may be framing the wrong target.
   - Owner: hero-integration.
4. **The run (no arm or leg flop): looks grounded in the stills I could check.**
   - In Ch1, Rhen runs on the Underway floor with feet planted and arms down (ch01_run_frame.jpg).
   - The run carried him into the Glassfry fight, as the zone intends.
   - Stills can't prove the gait: a moving capture is the next step.

**Frame-time budget (ADR 0029/0037), warm second run:** every scene change is over its 1000 ms hidden-frame budget:

| Scene change | Worst hidden frame |
|---|---|
| New Game → the Prologue | 3025 ms (4058 ms on the first run) |
| Ch2 / Haluna | 2017 ms |
| the first fight | 1669 ms |
| Ch1 | 1276 ms |

The title passed warm (385 ms; 1718 ms on the first run). Visible frames are all within 50 ms. Hitches over 33 ms in the dwells: 9 in the Prologue, 14 in Ch1 and 8 in the first fight on the first run. The rows are in act1_gpu_qa.md.

## What the PC saw in the drifts and new shots (lavapipe; the GPU look is in act1_gpu_qa.md)

- **Fixed since big12 (my pass-A findings):**
  - slice_verse_steps is now the textured shrine stage (was white pillars).
  - slice_causeway_harrier_view is reframed down the causeway.
  - battle_arena_wall_head and battle_ch08_stair_hold have textured battlements and the sea.
  - battle_boss_intro_reach has a dressed wall, sea and roofs.
  - iskarra_p01 has the Prologue colour pass: coloured domes and banners, figures in the plaza.
- **Re-dressed or re-modelled:**
  - The Hullgnaw and Drownbell intros are reframed (the Drownbell into the sun).
  - The Bottle Hermit has a new detailed model.
  - Battle dialogue now shows speaker portraits.
- **slice_beach_h05_asha / h06_toma (the human's beach FAST-TRACK, 0.29):**
  - The new frame shows Asha kneeling at the left and Toma standing with his spear.
  - **Rhen, lying in the shallows, is not in the frame.** If the pose moved him out of the shot, the camera needs to follow; for slice-polish and hero-integration to check.
- **New shots that read wrong:**
  - zone_wake_h02: the camera is inside a black wall.
  - zone_wake_h08: the camera is against a shell-covered surface.
  - Both are Ch4 wake camera placements (owner: env-art).
- **New arenas with capsule stand-ins:**
  - battle_arena_drowned_choir_ring, battle_arena_iskarra_spire_crown, battle_arena_undertow_cage, battle_arena_undertow_heart.
  - battle_arena_keth_seep_terrace (a drift) still has one too.

### No baseline (new shots, out PNG only): 121

- **Places (31):** first_verse_stage_v01, first_verse_stage_v02, brightwater_landing_f01, brightwater_landing_f06, ch07_tamsule_mouth, ch07_tamsule_market, ch07_tamsule_gantry, ch05_pemakar_weir, ch05_pemakar_harbour_day, ch09_corrow_landing, ch09_corrow_rocks, ch08_corrow_flood, ch08_corrow_lake, ch08_coilspire_gate, ch08_coilspire_storm, ch08_corrow_storm, ch05_ashcrown_causeway, ch05_ashcrown_forecourt, ch05_ashcrown_crown, ch05_ashcrown_tiers, ch05_ashcrown_court, ch04_haluna_wake_feast, ch04_haluna_wake_lane, ch01_oruvel_storm, ch01_drop, ch01_bell_room, ch01_scale_hull, ch01_kell_stall, ch01_net_pen, ch01_hullgnaw_rises, ch01_going_under

- **Named NPCs (18):** moll_front, moll_three_quarter, moll_profile, moll_face, moll_face_yield, moll_clip_yield, moll_silhouette_vs_toma, stillguard_a_front, stillguard_a_three_quarter, stillguard_a_face, stillguard_b_front, stillguard_b_clip_level_spear, stillguard_d_three_quarter, stillguard_d_clip_shield_up, stillguard_lineup, stillguard_b_face, stillguard_c_front, stillguard_c_face

- **Kit rows (10):** kitrow_ansedra_court_hall, kitrow_ansedra_basin_stacks, kitrow_keth_cloudloom_house, kitrow_keth_road_details, kitrow_lowlight_nave_bays, kitrow_lowlight_vey_details, kitrow_fen_roost_cord, kitrow_fen_reedhollow_walks, kitrow_quellan_inn_well_dais, kitrow_vey_gallery_walk_bench

- **Zones (20):** zone_oruvel_o01, zone_oruvel_o07, zone_oruvel_o09, zone_oruvel_o12, zone_oruvel_o16, zone_underway_u01, zone_underway_u03, zone_underway_u06, zone_underway_u07, zone_underway_u08, zone_wake_h02, zone_wake_h04, zone_wake_h07, zone_wake_h09, zone_wake_h12, zone_wake_h13, zone_wake_h08, zone_wake_c01, zone_oruvel_storm_o12, zone_oruvel_storm_o16

- **Creatures (12):** creature_ilun, creature_kahre, creature_virel, creature_nhoa, creature_hesk, creature_ethren, creature_ilun_held, creature_kahre_held, creature_virel_held, creature_hesk_held, creature_nhoa_held, creature_ethren_held

- **Heroes and party (9):** kerrid_front, kerrid_back, kerrid_three_quarter, kerrid_face, kerrid_face_stylized, kerrid_silhouette_lineup, kerrid_clip_collar_haul, kerrid_battle_idle, kerrid_battle_attack

- **Battle arenas (7):** battle_arena_drowned_choir_ring, battle_arena_iskarra_spire_crown, battle_arena_undertow_cage, battle_arena_undertow_heart, battle_arena_undertow_heart_letting, battle_arena_ashcrown_forecourt_day, battle_arena_ashcrown_anvil_court

- **Other (5):** hollowmere_m01_dace_hull, hollowmere_m02_raft_city_dusk, kite_k01_moored, kite_map, menu_glyphs

- **Menus (4):** field_menu_kite, field_menu_map_keth_pass, field_menu_map_lowlight, field_menu_map_ansedra

- **Battle UI and actors (3):** battle_ch08_intercept, battle_ch08_counter, battle_ch08_withdraw

- **Slice cutscene shots (2):** slice_neme_table, slice_prologue_p01

### Over the limit (drift): 181

- **Heroes and party (43):** ysolde_silhouette_lineup 0.053, asha_clip_offer_hand 0.046, asha_extreme_pose 0.046, asha_clip_bow_palms_flat 0.046, asha_clip_kneel_over_rhen 0.045, asha_clip_laugh 0.045, asha_clip_turn 0.041, asha_clip_walk 0.038, toma_battle_attack 0.038, field_hero_party 0.037, toma_clip_turn 0.037, asha_clip_walk_cycle 0.037, asha_clip_run 0.036, asha_battle_attack 0.036, asha_battle_victory 0.035, toma_battle_victory 0.035, toma_clip_talk 0.034, toma_battle_idle 0.033, toma_battle_ko 0.030, asha_sleeve_s4 0.028, asha_sleeve_s0 0.028, asha_clip_face_west 0.028, asha_battle_idle 0.028, asha_battle_ko 0.027, asha_q34 0.024, toma_clip_stack_bowls 0.022, toma_clip_walk 0.021, field_hero_gait_strip 0.021, toma_front 0.018, asha_front 0.017, rhen_face_neutral 0.015, rhen_face_smile 0.015, asha_face_stylized_compare 0.014, asha_smile_variant_compare 0.014, liss_face 0.013, toma_q34 0.012, toma_back 0.011, rhen_battle_finisher 0.010, liss_face_stylized 0.010, sefir_silhouette_lineup 0.010, toma_clip_walk_cycle 0.009, toma_face_neutral 0.009, toma_face_smile 0.009

- **Battle UI and actors (24):** battle_ch08_stair_hold 0.168, battle_heroes_finisher 0.149, battle_heroes_attack 0.088, battle_heroes_cast 0.084, battle_vowbound_out 0.075, battle_heroes_hit 0.067, battle_opening_banner 0.059, battle_heroes_victory 0.059, battle_heroes_idle 0.059, battle_heroes_ko 0.055, battle_victory 0.032, battle_swell_brace 0.030, battle_statuses 0.029, battle_statuses_colorblind 0.029, battle_hud_preview 0.028, battle_hud_16x10 0.028, battle_swell_chant 0.027, battle_hud_21x9 0.026, battle_read_panel 0.025, battle_swell_modes 0.023, battle_swap_menu 0.023, battle_swell_ring 0.023, battle_vowbound_call 0.021, battle_swell_glyph 0.018

- **Battle arenas (24):** battle_arena_wall_head 0.168, battle_arena_keth_seep_terrace 0.159, battle_arena_seawall_stairhead_surge 0.084, battle_arena_route 0.070, battle_arena_tideline 0.058, battle_arena_underway 0.052, battle_arena_derelict 0.047, battle_arena_raft 0.046, battle_arena_terrace 0.046, battle_arena_shoals 0.045, battle_arena_camp 0.043, battle_arena_ansedra_lagoon_escape 0.043, battle_arena_causeway 0.040, battle_arena_lowlight_engine_hall 0.029, battle_arena_causeway_route_afternoon 0.027, battle_arena_seawall_stairhead_storm 0.023, battle_arena_causeway_disc_sunset 0.022, battle_arena_seawall_stairhead_hoist 0.019, battle_arena_underway_tower 0.017, battle_arena_coilspire_tier_landing 0.014, battle_arena_coilspire_headland_path 0.013, battle_arena_oruvel_raft_morning 0.012, battle_arena_ash_terrace_lanternfall 0.011, battle_arena_tideline_dawn 0.010

- **Creatures (23):** creature_bottle_hermit 0.175, creature_mangrove_drowner_risen 0.146, creature_mangrove_drowner 0.143, creature_shoal_skipper 0.099, creature_spar_wraith 0.089, creature_drownbell_rim_broken 0.088, creature_raid_hound 0.088, creature_drownbell 0.083, creature_oil_slug 0.082, creature_drownbell_toll 0.081, creature_undertows_reach 0.080, creature_hullgnaw 0.067, creature_sail_leech 0.046, creature_slag_tortoise 0.045, creature_ridge_lynx 0.044, creature_scree_crawler 0.044, creature_fen_leech 0.038, creature_cinder_matron 0.036, creature_vein_sparker 0.031, creature_glass_skate 0.028, creature_portraits 0.023, creature_gallery_ray 0.013, creature_flue_moth 0.010

- **Places (19):** iskarra_p01_plaza_dusk 0.163, iskarra_i03_broken_tower 0.158, ch09_corrow_strand 0.141, iskarra_i02_gate_from_the_plaza 0.121, ch05_pemakar_harbour 0.109, ch01_underway_gallery 0.094, ch08_corrow_arrival 0.077, haluna_h07_chapel_court 0.026, ch01_o07_name_board 0.026, ch06_brine_road 0.026, ch01_o10_gull 0.025, haluna_h10_dock_night 0.022, ch06_brine_camp 0.022, ch09_corrow_road 0.020, shrine_s01_approach 0.017, oruvel_o07_name_board 0.017, brightwater_b02_awning 0.011, ch01_underway_crown 0.009, ch08_corrow_stair 0.009

- **Battle choreo (11):** battle_choreo_toll 0.081, battle_choreo_summon 0.073, battle_choreo_vowbound_rise 0.048, battle_choreo_ko 0.033, battle_choreo_lamp_dive 0.029, battle_choreo_hit 0.027, battle_choreo_swap 0.026, battle_choreo_support 0.025, battle_choreo_read 0.024, battle_choreo_cast 0.023, battle_choreo_melee 0.018

- **Other (10):** boot_title 0.070, hero_cutscene_turn_strip 0.042, drownbell_flood 0.042, dialogue_continue 0.031, coilspire_k01_headland_path 0.022, brine_b05_barge_channel 0.021, equip_menu 0.021, revenant_tells_reflection_off 0.010, revenant_tells_reflection 0.010, ashcrown_a04_anvil_hall 0.009

- **Slice cutscene shots (8):** slice_beach_h05_asha 0.294, slice_beach_h06_toma 0.294, slice_causeway_harrier_view 0.236, slice_verse_steps 0.184, slice_prologue_vigil_line 0.116, slice_verse_hall 0.027, slice_dock_night_yes 0.021, slice_causeway_head 0.013

- **Menus (7):** items_menu 0.042, shop_menu_sell 0.034, shop_menu_buy 0.033, save_shrine_field 0.031, items_menu_key 0.028, field_menu_codex 0.012, items_menu_use 0.011

- **Boss intros (7):** battle_boss_intro_drownbell 0.222, battle_boss_intro_hullgnaw 0.162, battle_boss_intro_reach 0.161, battle_boss_intro_matron 0.080, battle_boss_intro_hermit 0.048, battle_boss_intro_wraith 0.036, battle_boss_intro_inquisitor 0.028

- **Wildlife (3):** wildlife_zone_brine_wrecks 0.018, wildlife_zone_brine_flats 0.015, wildlife_zone_underway_crown 0.008

- **NPCs and villagers (2):** npc_haluna_chapel 0.077, npc_wake_feast 0.042



# Act I hero-motion coverage audit (M3-HER-1132)

**What this is:** every in-engine cutscene the game plays (the prologue, Haluna's, and every Act I chapter's `play`
steps: 79 scenes) run headless on its own zone's stage by `tests/integration/test_qa_cutscene_motion_audit.gd`. Each
`@anim` cue is sorted by what the actor really does. Re-run it with
`godot --headless --path . res://tests/run_tests.tscn -- --filter=qa_cutscene_motion_audit` (one `AUDIT` line per
scene); it reports and doesn't fail. Run on claude/hero-integration @ 0449b943 (big12 plus this track), 2026-10-28.

- **real:** the clip plays on the actor's body or rig (or a built clip stands in for it), or it's a `look_at` turn.
- **mark:** a placeholder clip mark: the actor glides onto a spot instead of performing (CutsceneStage.clip_marks).
- **none:** nothing happens. The actor is a capsule, or its rig has no such clip, and the cue is skipped silently.

## Totals
- 244 `@anim` cues: **70 real, 3 mark, 171 none.** About 70 % of Act I's staged
  gestures don't play yet. Bodies walk, turn and face (the hero layer), but the story gestures (sit, kneel,
  laugh, hand over, haul, fold a boat…) are skipped.
- **15 scenes** stage no `@anim` and have no capsules or placeholders (lines, walks and camera only):
  ch02_nemes_table, ch02_low_tide, ch03_dock_at_night, ch01_the_drop, ch01_gauge_wheel, ch01_scale_hull, ch01_gulls, ch01_bridge_gone, ch04_the_wake, ch05_pemakar_after, ch05_dawn_gate, ch06_channel_dawn, ch08_run_back, ch08_stair_look, ch08_binding.
- **Heroes:** every hero gap except two is already requested from characters in
  `assets_src/characters/requested_clips.json` (**M3-CHR-1000**). Not requested: **liss `haul_rope`** (ch08_hoist)
  and **pell `storm_call`** (ch08_stranger_on_wall). See M3-HER-1133.
- **Act I's people (NPCs):** 29 actors are missing 60 clips. They're capsules (models: M3-HER-1125), and
  no request lists their clips. See **M3-HER-1133** (characters), and **M3-HER-1134** for the Cinder Matron's two
  (creatures).
- **Clip marks** (glides in place of a clip): ch09_the_ebbing's asha `stand_gilt`, `pole_out`, `pole_in`. All three
  are in M3-CHR-1000, so the marks go when the clips land.
- **Placeholder cue features** (not motion: `@vfx drift=/rate=/motion=`, `@sfx at=`, `@camera grade=`): 19 scenes,
  added to **M3-HER-1123**.

## Per scene (only the scenes with a gap)
| Scene | Zone | real | mark | none | Capsules it names | Hero clips missing (M3-CHR-1000) | NPC clips missing (M3-HER-1133/1134) | Placeholder cues |
|---|---|---|---|---|---|---|---|---|
| prologue_dead_city | prologue | 2 | 0 | 0 | — | — | — | — |
| ch02_girl_on_the_beach | haluna | 13 | 0 | 0 | — | — | — | @vfx drift=, @camera grade= |
| ch01_bell_room | oruvel_underway | 1 | 0 | 0 | — | — | — | — |
| ch01_low_lights | oruvel_underway | 0 | 0 | 1 | — | rhen/touch_cord | — | @vfx drift=, @vfx rate= |
| ch01_current_shaft | oruvel_underway | 0 | 0 | 1 | — | rhen/clip_on | — | — |
| ch01_going_under | oruvel | 0 | 0 | 0 | — | — | — | @vfx drift= |
| ch01_kell_stall | oruvel | 1 | 0 | 5 | — | rhen/laugh, rhen/pocket_tin, rhen/trim_wicks | kell/take_scissors, kell/trim_wicks | — |
| ch01_the_rising | oruvel | 0 | 0 | 1 | — | — | kell/light_beacon | — |
| ch01_scuttlers | oruvel | 0 | 0 | 0 | — | — | — | @vfx drift= |
| ch01_net_pen | oruvel | 0 | 0 | 0 | pen_child | — | — | — |
| ch01_hullgnaw_rises | oruvel | 0 | 0 | 0 | — | — | — | @vfx drift= |
| ch04_lamps_to_the_wall | haluna_wake | 0 | 0 | 1 | neme | — | neme/carry_food | — |
| ch04_wake_neme | haluna_wake | 0 | 0 | 1 | neme | — | neme/clear_plates | @sfx at= |
| ch04_shell_is_set | haluna_wake | 0 | 0 | 5 | neme, osu | asha/touch_arm, rhen/put_down_plate, toma/follow | neme/laugh_breaks, osu/set_shell | @sfx at= |
| ch04_dock_in_the_dark | haluna_wake | 0 | 0 | 8 | — | asha/hold_out_cake, asha/look_out_to_sea, asha/sit_beside, rhen/look_back, rhen/look_out_to_sea, rhen/sit_dock_edge, rhen/take_cake, toma/sit_post | — | — |
| ch04_the_ink | haluna_wake | 0 | 0 | 4 | — | rhen/hold_lamp, ysolde/cap_ink, ysolde/ink_shell, ysolde/move_lamp | — | @sfx at= |
| ch04_long_way_round | haluna_wake | 0 | 0 | 4 | neme | asha/look_at_fingertip, asha/touch_shell, rhen/look_back | neme/watch | @camera grade= |
| ch04_name_board | brightwater_ferry | 0 | 0 | 2 | — | rhen/lift_name_board, rhen/prise_name_board | — | @vfx drift=, @vfx rate= |
| ch04_under_way | brightwater_ferry | 0 | 0 | 3 | passenger_child | asha/hold_out_forearm, toma/unroll_ink_kit | passenger_child/place_leaf_boat | — |
| ch04_gangplank | brightwater_ferry | 0 | 0 | 2 | — | ysolde/present_appointment, ysolde/turn_to_gangplank | — | — |
| ch04_seventh_terrace | brightwater_ferry | 0 | 0 | 1 | — | rhen/jump_gap | — | @vfx drift=, @vfx rate= |
| ch04_spar_wraith | brightwater_ferry | 0 | 0 | 0 | spar_wraith | — | — | @vfx drift=, @vfx rate= |
| ch05_ferry_comes_in | pemakar | 1 | 0 | 3 | ferryman | asha/touch_forearm, ysolde/read_letter | ferryman/carry_name_board | — |
| ch05_smiths_question | pemakar | 0 | 0 | 7 | garo | rhen/fold_boat | garo/fold_boat, garo/laugh, garo/nod, garo/take_boat | — |
| ch05_lanternfall_boats | pemakar | 0 | 0 | 8 | boat_seller, elder | asha/float_boat, rhen/float_boat, rhen/hand_away, rhen/hand_to_tin, rhen/light_seller_wick, rhen/procession_walk | boat_seller/give_boat, elder/give_boat | @vfx drift=, @vfx rate= |
| ch05_lanternfall_weir | pemakar | 5 | 0 | 5 | weir_child | kerrid/catch_collar, rhen/slip, rhen/walk_backwards | weir_child/lean_out, weir_child/slip | — |
| ch05_inn_gate | pemakar | 1 | 0 | 4 | — | kerrid/set_bowl_down, kerrid/shake_head, rhen/eat_on_step, rhen/give_bowl | — | — |
| ch05_kahre | ashcrown | 2 | 0 | 7 | kerrid, matron, tender | asha/face_crown_sing, rhen/brace, rhen/grin, toma/laugh, ysolde/walk_past | matron/bank, tender/open_chamber | @vfx motion=, @vfx rate= |
| ch05_kerrid_steps_up | ashcrown | 0 | 0 | 1 | kerrid | kerrid/unsling_cleaver | — | — |
| ch05_crown_pavilion | ashcrown | 0 | 0 | 1 | tender | — | tender/open_pavilion | — |
| ch05_matron_wakes | ashcrown | 0 | 0 | 2 | kerrid, matron | kerrid/unsling_cleaver | matron/unfold | — |
| ch06_barge | brine_shoals | 8 | 0 | 23 | clerk, inquisitor, kerrid, stillguard_a, stillguard_b, stillguard_c, wright_child_a, wright_child_b, wrights | asha/bow_palms_flat, kerrid/hold_rib_on_shoulder, sefir/bow_from_barge, toma/kneel_palms_flat, toma/shield_up | clerk/iron_into_water, inquisitor/kneel, reed_a/pole_barge, reed_b/pole_barge, reed_c/pole_barge, reed_d/pole_barge, stillguard_a/kneel_palms_flat, stillguard_a/level_spear, stillguard_b/kneel_palms_flat, stillguard_b/level_spear, stillguard_c/kneel_palms_flat, stillguard_c/let_go, wright_child_a/crawl_out, wright_child_b/crawl_out | — |
| ch06_after_barge | brine_shoals | 2 | 0 | 0 | wrights | — | — | — |
| ch06_liss_lantern | brine_shoals | 2 | 0 | 0 | — | — | — | — |
| ch06_ridge_camp | brine_shoals | 0 | 0 | 1 | kerrid | kerrid/stand_watch_seaward | — | — |
| ch06_midday | brine_shoals | 0 | 0 | 5 | kerrid | asha/sit, kerrid/stand_apart, rhen/take, toma/sit, ysolde/sit | — | — |
| ch06_smoke | brine_shoals | 0 | 0 | 1 | — | toma/stop | — | — |
| ch06_raid | brine_shoals | 2 | 0 | 7 | hound | liss/collide, rhen/throw_sail, toma/shield_up | clerk/heat_iron, stillguard_a/walk_torch, stillguard_b/walk_torch, stillguard_c/hold_arm | — |
| ch06_burned_lamp | brine_shoals | 0 | 0 | 5 | liss | liss/dig_sand, liss/flatten_sand, liss/set_in_hole, liss/stand, rhen/sit | — | @vfx drift= |
| ch07_into_tamsule | tamsule | 1 | 0 | 0 | liss | — | — | — |
| ch07_tavi | tamsule | 2 | 0 | 5 | tavi | — | tavi/grab_shoulders, tavi/half_laugh, tavi/laugh, tavi/tie_band, tavi/untie_band | — |
| ch07_leaving_tamsule | tamsule | 1 | 0 | 0 | — | — | — | — |
| ch07_after_the_bell | tamsule_bell_galleries | 1 | 0 | 6 | liss, oruvel_diver_1, oruvel_diver_2, poolkeeper, tavi | asha/hand_jacket, rhen/catch_breath, rhen/untie_band | poolkeeper/chalk_slate, tavi/catch_breath, tavi/stop_hand | — |
| ch07_galleries | tamsule_bell_galleries | 4 | 0 | 1 | liss | ysolde/turn_page | — | — |
| ch07_naming | tamsule_bell_galleries | 1 | 0 | 0 | — | — | — | — |
| ch07_empty_moorings | tamsule_bell_galleries | 1 | 0 | 3 | kerrid, tavi | asha/kneel_touch_ring, rhen/tie_band, rhen/untie_band | — | — |
| ch08_wall_falls | corrow | 1 | 0 | 1 | kerrid | kerrid/catch_collar | — | @sfx at= |
| ch08_captain | corrow | 0 | 0 | 2 | kerrid | kerrid/push_climber | marra/look_back | — |
| ch08_the_reach | corrow | 0 | 0 | 1 | — | toma/shield_up | — | — |
| ch08_stranger_on_wall | corrow | 1 | 0 | 3 | — | asha/hands_half_raised, asha/kneel_hum, pell/storm_call | — | @sfx at= |
| ch08_hoist | corrow | 2 | 0 | 3 | liss | liss/drive_pin, liss/haul_rope, toma/haul_rope | — | — |
| ch08_first_down | corrow | 0 | 0 | 1 | hobb | toma/shield_up | — | — |
| ch08_landfall | corrow | 0 | 0 | 0 | kerrid, townsfolk_a, townsfolk_b | — | — | — |
| ch08_okeru | corrow | 3 | 0 | 3 | — | toma/laugh | ivo/hug_lift, ivo/kneel_palms_flat | — |
| ch08_wall_gate | corrow | 0 | 0 | 1 | gatekeeper | — | gatekeeper/open_gate | — |
| ch08_cut_rope | corrow | 2 | 0 | 5 | kerrid, liss, officer, stillguard_a | liss/coil_rope, toma/look_away | officer/hatchet_blow, stillguard_a/shake_head | — |
| ch08_keeping_flame | coilspire | 1 | 0 | 4 | fenn | asha/feed_fire | fenn/feed_fire, fenn/hand_driftwood | — |
| ch08_spire_door | coilspire | 2 | 0 | 1 | liss, tender | toma/present_papers | — | — |
| ch08_stuck_key | coilspire | 0 | 0 | 3 | liss | liss/charcoal_rubbing, liss/ease_key, toma/strain_key | — | — |
| ch08_storm_against_wind | coilspire | 0 | 0 | 2 | fenn, liss, tender | — | fenn/hand_key, tender/palms_level | — |
| ch08_beacon_opened | coilspire | 0 | 0 | 1 | — | asha/turn_great_key | — | — |
| ch09_strand | corrow_night | 0 | 0 | 1 | marra | — | marra/hold_hands | @vfx drift=, @vfx rate= |
| ch09_the_ebbing | corrow_night | 2 | 3 | 5 | fenn, kerrid_stair, pell, tender | asha/lower_staff, asha/pole_in, asha/pole_out, asha/raise_staff, asha/stand_gilt, asha/turn_on_raft, toma/hand_on_spear | tender/paint_gilt | @vfx drift=, @vfx rate= |
| ch09_the_road_out | corrow_night | 5 | 0 | 0 | kerrid, liss, pell | — | — | — |

# GATE lead/gate-big12 @ 8a28be17: the failing and new shots (PC gate runner, 2026-10-27)

- `<id>_out.png` is the WSL2 lavapipe render. `<id>_diff.png` is compare.py's diff against big12's committed
  baselines (there is none for a shot without a baseline). Every one of the 31 shots without a baseline has an out PNG.
  `compare.txt` lists every RMSE. `blender_diffs.txt` is the Blender step's log.
- The run used a fresh `.godot` import (complete: exit 0 and the final DONE line) and 2 shards. Blender ran after the suite
  (base `claude/undertow-lead-handoff-ze8rrn`).

## Summary: FAIL (2 Godot failures as in the cloud, 3 tools failures, drift and 31 new shots for the Lead to view)

| Step | Result |
|---|---|
| validate_data, audio, taskboard, gdlint, gdformat, manifest | ok |
| tools unittests | 1186 run, **3 failures** (below) |
| Godot suite | **2820 run, 2 failed** (= the cloud; below) |
| Coverage gate, boot smoke | **not reached**: ci_local stops at the Godot failures |
| Blender (28 jobs changed since ze8rrn) | **28/28 identical**, 0 uncovered: asha, rhen, toma, sefir, ysolde, the 9 villagers, 10 kits, 4 creatures, wildlife_insect |
| Screenshots | **341 compared, 111 failed** = 31 without a baseline + 80 over the RMSE limit. All 341 captured. |
| Wall | lanes A+B 51 min (lane B 3067 s), Blender 1007 s, lane A re-run 12 min |

**Lane A:** the tools failures stopped ci_local before the Godot suite. The PC re-ran lane A on the same checkout with
only the tools step made non-fatal (a local copy of ci_local, not committed). That run gave the Godot results below.

### Godot failures (2, the same as the cloud's)

- `test_creature_portraits.gd::test_every_manifest_creature_exists_with_a_provenance_row`: creatures.json rows
  mangrove_drowner, lamp_engine, avalanche_ram and wakefin "have a portrait in the manifest" (the four new creatures).
- `test_footsteps_slice_zones.gd::test_the_causeway_is_stone_with_a_tidepool`: "expected <water> got <stone> in the tidepool".

### Tools failures (3)

- `test_screenshots.test_repo_manifest_is_valid_and_baselined`: the first id without a baseline is `ch04_ferry_deck`.
  There are 31 such shots (listed below; the out PNGs are here).
- `test_iskarra.test_the_vigils_stand_on_the_paving`: `3 not greater than or equal to 7` (only 3 vigils found on the paving).
- `test_shrine_gi_bake.test_the_bake_is_not_stale`: the Shell Shrine's GI inputs changed. Rebaked on this tree:
  `gpu/shrine-gi-big12` (the test passes there).

### `SCRIPT ERROR: Trying to cast a freed object` at shutdown (19 shots; big11 had 11)

The error is always `LifeAudio.advance (res://game/audio/life_audio.gd:124)`, printed after "Capture: 1 shot(s),
0 failed". Every capture is ok, but capture.sh exits 1. The shots are: ch04_ferry_deck, ch04_ferry_derelict,
ch06_brine_camp, ch06_brine_road, npc_haluna_chapel/dock/lane/market, npc_stage_field, npc_wake_feast,
slice_beach_h05_asha, slice_beach_h06_toma, slice_causeway_harrier_view, slice_causeway_head,
slice_haluna_villagers_village, wildlife_stage, and wildlife_zone_brine_flats/brine_wrecks/underway_crown.

## The 111 failing shots

### No baseline (31 new shots; out PNG only)

asha_battle_ko, asha_battle_victory, rhen_battle_finisher, rhen_battle_ko, rhen_battle_victory, toma_battle_ko,
toma_battle_victory, battle_arena_wall_head, battle_boss_intro_reach, battle_ch08_stair_hold, ch04_ferry_deck,
ch04_ferry_derelict, ch07_bell_galleries, ch07_bell_moorings, ch08_coilspire_hall, ch08_coilspire_path, ch09_corrow_road,
ch09_corrow_strand, creature_avalanche_ram, creature_lamp_engine, creature_lamp_engine_opened, creature_wakefin,
iskarra_p01_plaza_dusk, iskarra_i02_gate_from_the_plaza, iskarra_i03_broken_tower, slice_beach_h05_asha,
slice_beach_h06_toma, slice_causeway_harrier_view, slice_causeway_head, slice_haluna_villagers_village, slice_verse_steps.

(The Lead expected 41. The manifest at 8a28be17 has 341 shots and 31 of them lack a baseline.)

### Newly failing: passed on big11 (57)

The Blender rebuilds of asha, rhen and toma are identical, so these drifts come from the Godot side (materials, rig or
scene code). Notes are from viewing the out PNGs next to the baselines:

- **Asha (21):** asha_front 0.0177, asha_q34 0.0143, asha_profile 0.0164, asha_sleeve_s0/s4 0.0095,
  asha_face_stylized_compare 0.0099, asha_smile_variant_compare 0.0098, asha_extreme_pose 0.0564, and the clips
  kneel_over_rhen 0.0566, walk 0.0497, offer_hand **0.0771**, face_west 0.0317, laugh 0.0570, run 0.0604,
  walk_cycle 0.0619, turn 0.0542, plus asha_battle_idle 0.0321 and asha_battle_attack 0.0457. The front views barely move.
  In offer_hand the skirt now flares out in a wide bell to the floor; in the baseline the underskirt was a rigid tube
  (M1-QA-09's finding). This is the characters track's to judge.
- **Toma (11):** toma_front 0.0139, toma_back 0.0086, toma_face_neutral/smile 0.0118, toma_clip_walk 0.0190,
  toma_clip_talk 0.0301, toma_clip_turn 0.0315, toma_battle_idle 0.0272, toma_battle_attack 0.0235.
- **Rhen (2):** rhen_clip_take_hand 0.0142, rhen_clip_kneel 0.0148 (barely visible).
- **Strips and lineups (5):** hero_cutscene_turn_strip 0.0435, field_hero_party 0.0339, field_hero_gait_strip 0.0164,
  sefir_silhouette_lineup 0.0091, ysolde_silhouette_lineup 0.0417.
- **Battle UI (17, ~0.04-0.05 each):** battle_hud_preview, battle_swap_menu, battle_statuses(+_colorblind), battle_read_panel,
  battle_swell_ring/modes/glyph, battle_vowbound_call/out, battle_hud_21x9/16x10, and choreo cast/support/summon/
  vowbound_rise/lamp_dive (lamp_dive 0.1005). In battle_hud_preview the UI is the same; the heroes change.
- **creature_portraits 0.0566:** the grid has the four new creatures, so the layout changes (4 rows, not 3).
- **Places (3):** haluna_h01_village_from_sea 0.0218 (new boats at the shore), haluna_h04_dock 0.0108,
  shrine_s01_approach 0.0230 (driftwood and debris on the islet).
- **Dialogue (2):** slice_prologue_vigil_line **0.1017** (the dialogue box is wider and sits lower; the heroes have changed),
  dialogue_voice_over 0.0404 (new jars in the lane, and a wider box).

### Repeats of big11's failures (23; RMSE big11 -> big12)

- **Arenas re-dressed, the drift grew:** battle_arena_camp 0.0099 -> **0.1093** (the whole camp is rebuilt: the beach,
  wrecks and smoke), battle_arena_shoals 0.0101 -> **0.0966** (re-dressed with wrecks and debris), battle_arena_route
  0.0227 -> 0.0501, battle_arena_causeway_route_afternoon 0.0238 -> 0.0383, battle_arena_underway 0.0115 -> 0.0140,
  battle_arena_underway_tower 0.0127 -> 0.0140, battle_arena_tideline_dawn 0.0081 -> 0.0103.
- **Arenas, the drift shrank:** tideline 0.0477 -> 0.0102, raft 0.0140 -> 0.0095, oruvel_raft_morning 0.0151 -> 0.0098,
  causeway_disc_sunset 0.0100 -> 0.0081.
- **battle_boss_intro_inquisitor 0.0517 -> 0.1642:** the camp arena behind it (a cobbled beach and a wreck).
- **Choreo and swell:** melee 0.0116 -> 0.1090, hit 0.0581 -> 0.0978, ko 0.0100 -> 0.0867, swap 0.0091 -> 0.0459,
  read 0.0105 -> 0.0433, toll 0.0109 -> 0.0171, swell_chant 0.0085 -> 0.0422, swell_brace 0.0138 -> 0.0444,
  battle_opening_banner 0.0160 -> 0.0420.
- **Villagers, the drift shrank:** npc_haluna_dock 0.0620 -> 0.0115, npc_haluna_lane 0.1160 -> 0.0112.

### Passing now (failed on big11: 20)

battle_arena_causeway, battle_arena_derelict(+_deck_night), battle_arena_terrace, battle_arena_ash_terrace_lanternfall,
the boss intros hullgnaw/matron/wraith/drownbell, ch06_brine_road, npc_haluna_market/chapel, wildlife_zone_brine_flats/
brine_wrecks, settings_accessibility, field_objective_line/interact_prompt/area_title/tip_card, and dialogue_continue.

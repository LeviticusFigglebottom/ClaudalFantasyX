# Act I mix pass: loudness at every music hand-over (2026-10-30)

The Lead's 10-30 item, on 7dc3ab41 (merged into claude/audio at a34edb9a). `tools/audio/act1_mix_pass.py` pairs every
music change the player hears in Act I and measures both sides as the deck plays them: the cue's file, or the stack
of its `start_stems`, plus the row's `volume_db`. The pairs are:
- a cutscene's `@music` cues in order;
- the cutscene's last cue -> the zone its `location:` resumes;
- every zone -> the regular battle cue and back;
- a chapter's zones -> each of its boss cues and back.

## Result
- **Before:** 81 hand-overs, 6 over 3 LU. All 6 were Ch8's three-stem cues. `seawall_hold` and `undertows_reach` start
  on their first stem alone, at -19.3 and -19.5 LUFS, because their full stacks are set to -16. So the fall from the
  -16 zone loops was 3.3 to 3.5 LU, and so was the rise when the Reach's cutscene handed back to the seawall.
- **Fix (data only, music.json):** `volume_db` +1.0 on `undertows_reach` and `undertow_reach`, +0.5 on `seawall_hold`.
  Each first stem now sits 2.5 to 2.8 LU under the zones. The full stacks reach -15.1 and -15.6, with true peaks
  under the master limiter's ceiling except for brief drum peaks. The two-stem seawall cue peaks at -0.3 dBTP, and the
  limiter (threshold -1.5) takes those down.
- **After:** 81 hand-overs, 0 over 3 LU. The largest remaining steps are the Cinder Matron at 2.1 and the Drownbell at
  1.8, each softer than its zone. They open with a boss intro sting over the change, so they stay as they are.
- **Beds under the music:** `act1_loop_check.py` shows 41 files and 0 problems; every bed is about 10 LU under its zone music.
- **Not measured here:** the dialogue duck (Music -4 dB under a line) and the battle duck (Ambience -3 dB) are fixed
  mix rules. Hearing the hand-overs on real speakers is in the PC-QUEUE.

## Every hand-over (after the fix)
| Chapter | Hand-over | From | LUFS | To | LUFS | Step (LU) |
|---|---|---|---|---|---|---|
| ch01 | cutscene (ch01_current_shaft) | `rhen_current_hum` | -15.9 | `oruvel_raft` | -16.0 | -0.1 |
| ch01 | cutscene -> field (ch01_current_shaft) | `oruvel_raft` | -16.0 | `lamp_diver` | -16.0 | -0.0 |
| ch01 | cutscene -> field (ch01_going_under) | `going_under` | -16.0 | `oruvel` | -16.0 | -0.0 |
| ch01 | cutscene -> field (ch01_hullgnaw_rises) | `hullgnaw` | -16.1 | `oruvel` | -16.0 | 0.1 |
| ch01 | cutscene -> field (ch01_scale_hull) | `oruvel_raft` | -16.0 | `oruvel` | -16.0 | 0.0 |
| ch01 | cutscene -> field (ch01_the_drop) | `oruvel_underway` | -16.0 | `lamp_diver` | -16.0 | 0.0 |
| ch01 | cutscene -> field (ch01_the_rising) | `undertow_rising` | -17.7 | `oruvel` | -16.0 | 1.7 |
| ch01 | field <-> battle | `lamp_diver` | -16.0 | `battle_standard_v2` | -16.1 | -0.0 |
| ch01 | field <-> battle | `oruvel` | -16.0 | `battle_standard_v2` | -16.1 | -0.0 |
| ch01 | field <-> boss (ch01_hullgnaw) | `lamp_diver` | -16.0 | `hullgnaw` | -16.1 | -0.0 |
| ch01 | field <-> boss (ch01_hullgnaw) | `oruvel` | -16.0 | `hullgnaw` | -16.1 | -0.1 |
| ch02 | cutscene -> field (ch02_girl_on_the_beach) | `haluna_dawn` | -16.0 | `haluna_village` | -16.0 | 0.0 |
| ch02 | cutscene -> field (ch02_low_tide) | `saltgrass_causeway` | -16.1 | `haluna_village` | -16.0 | 0.1 |
| ch02 | field <-> battle | `haluna_village` | -16.0 | `battle_standard_v2` | -16.1 | -0.1 |
| ch03 | cutscene (ch03_the_first_verse) | `shell_shrine_interior` | -16.0 | `hush_first_verse` | -16.0 | -0.1 |
| ch03 | cutscene -> field (ch03_the_first_verse) | `hush_first_verse` | -16.0 | `shell_shrine_interior` | -16.0 | 0.1 |
| ch03 | field <-> battle | `saltgrass_causeway` | -16.1 | `battle_standard_v2` | -16.1 | 0.1 |
| ch03 | field <-> battle | `shell_shrine_interior` | -16.0 | `battle_standard_v2` | -16.1 | -0.1 |
| ch04 | cutscene (ch04_shell_is_set) | `haluna_wake` | -16.1 | `the_long_way_round` | -16.0 | 0.1 |
| ch04 | cutscene -> field (ch04_dock_in_the_dark) | `hearer_hum` | -16.1 | `haluna_night` | -16.0 | 0.1 |
| ch04 | cutscene -> field (ch04_gangplank) | `ysolde_theme` | -16.0 | `brightwater_ferry` | -16.0 | -0.0 |
| ch04 | cutscene -> field (ch04_long_way_round) | `haluna_dawn` | -16.0 | `haluna_night` | -16.0 | 0.0 |
| ch04 | cutscene -> field (ch04_name_board) | `name_board_home` | -16.1 | `brightwater_ferry` | -16.0 | 0.0 |
| ch04 | cutscene -> field (ch04_shell_is_set) | `the_long_way_round` | -16.0 | `haluna_night` | -16.0 | -0.0 |
| ch04 | cutscene -> field (ch04_spar_wraith) | `spar_wraith` | -16.1 | `brightwater_ferry` | -16.0 | 0.0 |
| ch04 | cutscene -> field (ch04_the_ink) | `ysolde_theme` | -16.0 | `haluna_night` | -16.0 | 0.0 |
| ch04 | cutscene -> field (ch04_the_wake) | `haluna_wake` | -16.1 | `haluna_night` | -16.0 | 0.1 |
| ch04 | cutscene -> field (ch04_under_way) | `brightwater_crossing` | -16.0 | `brightwater_ferry` | -16.0 | 0.0 |
| ch04 | field <-> battle | `brightwater_ferry` | -16.0 | `battle_standard_v2` | -16.1 | -0.0 |
| ch04 | field <-> battle | `haluna_night` | -16.0 | `battle_standard_v2` | -16.1 | -0.1 |
| ch04 | field <-> boss (ch04_spar_wraith) | `brightwater_ferry` | -16.0 | `spar_wraith` | -16.1 | -0.0 |
| ch04 | field <-> boss (ch04_spar_wraith) | `haluna_night` | -16.0 | `spar_wraith` | -16.1 | -0.1 |
| ch05 | cutscene -> field (ch05_crown_pavilion) | `ashcrown_trial` | -16.0 | `ashcrown` | -16.0 | 0.0 |
| ch05 | cutscene -> field (ch05_ferry_comes_in) | `pemakar_terraces` | -16.1 | `terraces_of_ash` | -16.1 | 0.0 |
| ch05 | cutscene -> field (ch05_inn_gate) | `lanternfall` | -16.0 | `terraces_of_ash` | -16.1 | -0.1 |
| ch05 | cutscene -> field (ch05_kahre) | `hush_second_verse` | -16.0 | `ashcrown` | -16.0 | -0.0 |
| ch05 | cutscene -> field (ch05_lanternfall_weir) | `kerrid_stair` | -16.1 | `terraces_of_ash` | -16.1 | -0.0 |
| ch05 | field <-> battle | `ashcrown` | -16.0 | `battle_standard_v2` | -16.1 | -0.1 |
| ch05 | field <-> battle | `terraces_of_ash` | -16.1 | `battle_standard_v2` | -16.1 | -0.0 |
| ch05 | field <-> boss (ch05_cinder_matron) | `ashcrown` | -16.0 | `cinder_matron` | -18.1 | -2.1 |
| ch05 | field <-> boss (ch05_cinder_matron) | `terraces_of_ash` | -16.1 | `cinder_matron` | -18.1 | -2.0 |
| ch06 | cutscene -> field (ch06_after_barge) | `liss_theme` | -16.1 | `brine_shoals` | -16.0 | 0.0 |
| ch06 | cutscene -> field (ch06_barge) | `sefir_theme` | -16.0 | `brine_shoals` | -16.0 | -0.1 |
| ch06 | cutscene -> field (ch06_raid) | `raid` | -16.1 | `brine_shoals` | -16.0 | 0.1 |
| ch06 | cutscene -> field (ch06_ridge_camp) | `shoals_dusk` | -16.0 | `brine_shoals` | -16.0 | 0.0 |
| ch06 | field <-> battle | `brine_shoals` | -16.0 | `battle_standard_v2` | -16.1 | -0.0 |
| ch06 | field <-> boss (ch06_inquisitor) | `brine_shoals` | -16.0 | `stillguard_inquisitor` | -16.1 | -0.0 |
| ch07 | cutscene -> field (ch07_after_the_bell) | `tidecup_after` | -16.0 | `tamsule_bell_galleries` | -16.0 | 0.0 |
| ch07 | cutscene -> field (ch07_empty_moorings) | `oruvel_theme` | -16.0 | `tamsule_bell_galleries` | -16.0 | 0.0 |
| ch07 | cutscene -> field (ch07_galleries) | `tidecup_crowd` | -16.1 | `tamsule_bell_galleries` | -16.0 | 0.1 |
| ch07 | cutscene -> field (ch07_into_tamsule) | `tamsule_port` | -16.0 | `tamsule` | -16.0 | 0.0 |
| ch07 | cutscene -> field (ch07_leaving_tamsule) | `tidecup_after` | -16.0 | `tamsule` | -16.0 | 0.0 |
| ch07 | cutscene -> field (ch07_tavi) | `tavi_kell` | -16.1 | `tamsule` | -16.0 | 0.1 |
| ch07 | field <-> battle | `tamsule` | -16.0 | `battle_standard_v2` | -16.1 | -0.0 |
| ch07 | field <-> battle | `tamsule_bell_galleries` | -16.0 | `battle_standard_v2` | -16.1 | -0.1 |
| ch07 | field <-> battle | `tidecup_match` | -16.0 | `battle_standard_v2` | -16.1 | -0.0 |
| ch08 | cutscene -> field (ch08_beacon_opened) | `undertow_rising` | -17.7 | `coilspire` | -16.0 | 1.7 |
| ch08 | cutscene -> field (ch08_binding) | `virel_bound` | -16.0 | `coilspire` | -16.0 | -0.0 |
| ch08 | cutscene -> field (ch08_cut_rope) | `corrow_aftermath` | -16.0 | `corrow_seawall` | -16.1 | -0.0 |
| ch08 | cutscene -> field (ch08_first_down) | `seawall_hold` | -18.8 | `corrow_seawall` | -16.1 | 2.8 |
| ch08 | cutscene -> field (ch08_landfall) | `corrow_day` | -16.1 | `corrow_seawall` | -16.1 | 0.0 |
| ch08 | cutscene -> field (ch08_run_back) | `undertow_rising` | -17.7 | `corrow_seawall` | -16.1 | 1.7 |
| ch08 | cutscene -> field (ch08_spire_door) | `coilspire_flues` | -16.0 | `coilspire` | -16.0 | 0.0 |
| ch08 | cutscene -> field (ch08_the_reach) | `undertow_reach` | -18.5 | `corrow_seawall` | -16.1 | 2.5 |
| ch08 | field <-> battle | `coilspire` | -16.0 | `battle_standard_v2` | -16.1 | -0.0 |
| ch08 | field <-> battle | `corrow_seawall` | -16.1 | `battle_standard_v2` | -16.1 | -0.0 |
| ch08 | field <-> boss (ch08_stair_hold_1) | `coilspire` | -16.0 | `seawall_hold` | -18.8 | -2.8 |
| ch08 | field <-> boss (ch08_stair_hold_1) | `corrow_seawall` | -16.1 | `seawall_hold` | -18.8 | -2.8 |
| ch08 | field <-> boss (ch08_stair_hold_2) | `coilspire` | -16.0 | `seawall_hold_rope` | -17.6 | -1.5 |
| ch08 | field <-> boss (ch08_stair_hold_2) | `corrow_seawall` | -16.1 | `seawall_hold_rope` | -17.6 | -1.5 |
| ch08 | field <-> boss (ch08_stair_hold_3) | `coilspire` | -16.0 | `seawall_hold_last` | -16.1 | -0.1 |
| ch08 | field <-> boss (ch08_stair_hold_3) | `corrow_seawall` | -16.1 | `seawall_hold_last` | -16.1 | -0.1 |
| ch08 | field <-> boss (undertows_reach) | `coilspire` | -16.0 | `undertows_reach` | -18.5 | -2.5 |
| ch08 | field <-> boss (undertows_reach) | `corrow_seawall` | -16.1 | `undertows_reach` | -18.5 | -2.5 |
| ch09 | cutscene (ch09_the_ebbing) | `corrow_night` | -16.0 | `the_ebbing` | -16.0 | 0.0 |
| ch09 | cutscene (ch09_the_ebbing) | `the_ebbing` | -16.0 | `corrow_night` | -16.0 | -0.0 |
| ch09 | cutscene (ch09_the_road_out) | `dawn_road` | -16.0 | `hush_first_verse` | -16.0 | -0.0 |
| ch09 | cutscene -> field (ch09_the_road_out) | `hush_first_verse` | -16.0 | `corrow_night` | -16.0 | 0.0 |
| ch09 | field <-> battle | `corrow_night` | -16.0 | `battle_standard_v2` | -16.1 | -0.0 |
| prologue | field <-> battle | `prologue_dusk` | -16.0 | `battle_standard_v2` | -16.1 | -0.1 |
| prologue | field <-> boss (drownbell) | `prologue_dusk` | -16.0 | `drownbell` | -17.8 | -1.8 |

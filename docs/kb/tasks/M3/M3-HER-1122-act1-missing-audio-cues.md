---
id: M3-HER-1122
title: "Act I cutscenes call sounds and music that don't exist yet (request to audio)"
role: audio
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: qa
---
## Goal
The integration-qa playthrough guards (M3-HER-1121) drive every Act I thread headless. The sequencer warns, and plays
silence, for every `@sfx` and `@music` cue whose id has no file and no stand-in. The slice (prologue, Haluna, the
first verse) is clean; all of these are Act I.

## The ids (from the threads' runs on 2026-10-27)
- **Sounds (68):** anvil_crack, asha_hum_lullaby, barge_pole, beacon_lamp_gutter, beacon_roar, bell_crowd_roar, bell_hum_rise, bell_room_drip, brine_iron_hiss, camp_burn, chit_stamp, coast_bells, column_weep, crowd_on_stair, crowd_up, crowd_warm, crown_bell, current_song, derelict_wheel_turning, flue_key_free, gangplank, gate_bar, gulls_far, harbour_lap, hatch_burst, hatchet_rope, hearth_crackle, hearth_settle, hoist_block, hullgnaw_ribs_creak, ink_brush, kite_torn, lintel_gull_cry, lookout_call, matron_bank, mooring_ring, name_board_prise, neme_humming, pell_storm_note, plume_crackle, plume_thunder, raft_lashing_snap, raft_pole, raid_hound_bay, rain_easing, reach_grips, reach_rises, sail_pulled, sails_luff_and_fall, salvage_cut, scale_weigh, shell_set, shield_dropped, shingle_kneel, spire_door, splash, staff_bell_shells, stillguard_hum, stone_falls, surf_storm, tether_run, tide_ambience, undertow_wall_roar, wake_lamps_out, wall_breach, watchers_pin, weir_spill, wind_landward
- **Music (29):** ashcrown_trial, brightwater_crossing, corrow_aftermath, corrow_night, dawn_road, going_under, haluna_wake, hearer_hum, hush_second_verse, kerrid_stair, lanternfall, liss_theme, name_board_home, oruvel_raft, oruvel_theme, oruvel_underway, pemakar_terraces, raid, rhen_current_hum, seawall_hold, shoals_dusk, tamsule_port, tavi_kell, the_long_way_round, tidecup_after, tidecup_crowd, undertow_rising, virel_bound, ysolde_theme

## Acceptance criteria
- [ ] Each id gets a synthesised original cue or a stand-in mapping (sequencer.json `music_stand_ins` for music).
- [ ] The two rows for M3-HER-1122 leave tests/integration/qa_known.json, and test_qa_threads passes without them.

## Review log

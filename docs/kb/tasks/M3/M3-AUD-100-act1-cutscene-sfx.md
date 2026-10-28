---
id: M3-AUD-100
title: "Request: 68 Act I cutscene sounds the .dlg files cue are not built (they play as silence)"
role: audio
status: todo
owner_session: ""
depends_on: []
reviewer: cinematics
milestone: M3
request-from: cinematics
---
## Goal
The human's "primitive moments" re-audit (slice-polish, 2026-10-27, after big11) checked every `@sfx <id>` in the
game's `.dlg` files. The sequencer plays audio's `sfx*.json` row when one exists (M2-FP-118, `CutsceneSound`), else
`assets/audio/sfx/<id>.ogg`. **68 of 69 cued ids have neither**, so those beats are silent and log "no sound". The
M2 slice (prologue, Ch2, Ch3) is clean: its only cue, `drownbell_toll`, exists. Every missing one is in Act I:

- **ch01** (11): `beacon_lamp_gutter` (ch01_going_under); `bell_room_drip` (ch01_bell_room); `chit_stamp` (ch01_scale_hull); `hullgnaw_ribs_creak` (ch01_hullgnaw_rises); `lintel_gull_cry` (ch01_gulls); `raft_lashing_snap` (ch01_bridge_gone); `salvage_cut` (ch01_gauge_wheel); `scale_weigh` (ch01_scale_hull); `splash` (ch01_bark_roof_dive); `tether_run` (ch01_the_drop); `undertow_wall_roar` (ch01_going_under, ch01_the_rising)
- **ch04** (9): `derelict_wheel_turning` (ch04_seventh_terrace); `gangplank` (ch04_gangplank, ch04_seventh_terrace); `ink_brush` (ch04_the_ink); `lookout_call` (ch04_seventh_terrace); `name_board_prise` (ch04_name_board); `neme_humming` (ch04_wake_neme); `sails_luff_and_fall` (ch04_name_board, ch04_spar_wraith); `shell_set` (ch04_shell_is_set); `wake_lamps_out` (ch04_lamps_to_the_wall)
- **ch05** (6): `anvil_crack` (ch05_matron_wakes); `crown_bell` (ch05_lanternfall_boats); `matron_bank` (ch05_kahre); `plume_crackle` (ch05_bark_forge_child); `plume_thunder` (ch05_bark_forge_child, ch05_kahre); `weir_spill` (ch05_lanternfall_weir)
- **ch06** (8): `barge_pole` (ch06_barge); `brine_iron_hiss` (ch06_barge); `camp_burn` (ch06_smoke); `hatch_burst` (ch06_raid); `raid_hound_bay` (ch06_raid); `sail_pulled` (ch06_raid); `stillguard_hum` (ch06_raid); `tide_ambience` (ch06_burned_lamp)
- **ch07** (6): `bell_crowd_roar` (ch07_leaving_tamsule); `bell_hum_rise` (ch07_galleries); `column_weep` (ch07_naming); `crowd_up` (ch07_naming); `crowd_warm` (ch07_after_the_bell); `mooring_ring` (ch07_empty_moorings)
- **ch08** (24): `asha_hum_lullaby` (ch08_stranger_on_wall); `beacon_roar` (ch08_beacon_opened); `coast_bells` (ch08_beacon_opened); `crowd_on_stair` (ch08_first_down); `current_song` (ch08_wall_falls); `flue_key_free` (ch08_stuck_key); `gate_bar` (ch08_wall_gate); `gulls_far` (ch08_landfall); `hatchet_rope` (ch08_cut_rope); `hearth_crackle` (ch08_keeping_flame); `hearth_settle` (ch08_keeping_flame); `hoist_block` (ch08_hoist); `kite_torn` (ch08_run_back); `pell_storm_note` (ch08_stranger_on_wall); `rain_easing` (ch08_cut_rope); `reach_grips` (ch08_the_reach); `reach_rises` (ch08_the_reach); `shield_dropped` (ch08_okeru); `spire_door` (ch08_spire_door); `stone_falls` (ch08_wall_falls); `surf_storm` (ch08_captain); `wall_breach` (ch08_wall_falls); `watchers_pin` (ch08_hoist); `wind_landward` (ch08_run_back, ch08_storm_against_wind)
- **ch09** (4): `harbour_lap` (ch09_the_ebbing, ch09_toma); `raft_pole` (ch09_the_ebbing); `shingle_kneel` (ch09_the_ebbing); `staff_bell_shells` (ch09_the_ebbing)

## Acceptance criteria
- [ ] Each id gets a row in an `sfx*.json` table (preferred: the bus, variation and cooldown come with it; the
  cue's `at=` then plays it positionally) or an `assets/audio/sfx/<id>.ogg`, with PROVENANCE.
- [ ] Ch1's 11 come first (Ch1 is the next chapter the M2 switch opens), then Ch4 onward in chapter order.
- [ ] A tools test that fails on a cued id with no sound.

## Notes
- Chapter owners: Ch1 is slice-polish's, Ch4+ act1-chapters'. If an id should be renamed to an existing row, say
  so in the review log and the owner edits the `.dlg`.

## Review log

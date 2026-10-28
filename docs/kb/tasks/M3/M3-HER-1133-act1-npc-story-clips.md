---
id: M3-HER-1133
title: "Request (characters): Act I's people have no story clips (their @anim cues are skipped), plus two hero clips nobody requested"
role: character
status: todo
owner_session: ""
reviewer: cinematics
depends_on: [M3-HER-1125]
milestone: M3
request-from: qa
---
## Goal
The Act I hero-motion audit (docs/kb/qa/act1_hero_motion_audit.md, M3-HER-1132) runs every cutscene and sorts each
`@anim` cue. The heroes' missing story clips are already requested (M3-CHR-1000, requested_clips.json). Two hero clips
and every clip Act I's people use aren't requested anywhere:

**Heroes, not in requested_clips.json:**
- **liss** `haul_rope` (ch08_hoist)
- **pell** `storm_call` (ch08_stranger_on_wall)

**Act I's people.** Each is a capsule today (their models are M3-HER-1125's inventory). The cues below do nothing
until the person has a rig with the clip:
- **boat_seller**: `give_boat` (ch05_lanternfall_boats)
- **clerk**: `heat_iron` (ch06_raid), `iron_into_water` (ch06_barge)
- **elder**: `give_boat` (ch05_lanternfall_boats)
- **fenn**: `feed_fire` (ch08_keeping_flame), `hand_driftwood` (ch08_keeping_flame), `hand_key` (ch08_storm_against_wind)
- **ferryman**: `carry_name_board` (ch05_ferry_comes_in)
- **garo**: `fold_boat` (ch05_smiths_question), `laugh` (ch05_smiths_question), `nod` (ch05_smiths_question), `take_boat` (ch05_smiths_question)
- **gatekeeper**: `open_gate` (ch08_wall_gate)
- **inquisitor**: `kneel` (ch06_barge)
- **ivo**: `hug_lift` (ch08_okeru), `kneel_palms_flat` (ch08_okeru)
- **kell**: `light_beacon` (ch01_the_rising), `take_scissors` (ch01_kell_stall), `trim_wicks` (ch01_kell_stall)
- **marra**: `hold_hands` (ch09_strand), `look_back` (ch08_captain)
- **neme**: `carry_food` (ch04_lamps_to_the_wall), `clear_plates` (ch04_wake_neme), `laugh_breaks` (ch04_shell_is_set), `watch` (ch04_long_way_round)
- **officer**: `hatchet_blow` (ch08_cut_rope)
- **osu**: `set_shell` (ch04_shell_is_set)
- **passenger_child**: `place_leaf_boat` (ch04_under_way)
- **poolkeeper**: `chalk_slate` (ch07_after_the_bell)
- **reed_a**: `pole_barge` (ch06_barge)
- **reed_b**: `pole_barge` (ch06_barge)
- **reed_c**: `pole_barge` (ch06_barge)
- **reed_d**: `pole_barge` (ch06_barge)
- **stillguard_a**: `kneel_palms_flat` (ch06_barge), `level_spear` (ch06_barge), `shake_head` (ch08_cut_rope), `walk_torch` (ch06_raid)
- **stillguard_b**: `kneel_palms_flat` (ch06_barge), `level_spear` (ch06_barge), `walk_torch` (ch06_raid)
- **stillguard_c**: `hold_arm` (ch06_raid), `kneel_palms_flat` (ch06_barge), `let_go` (ch06_barge)
- **tavi**: `catch_breath` (ch07_after_the_bell), `grab_shoulders` (ch07_tavi), `half_laugh` (ch07_tavi), `laugh` (ch07_tavi), `stop_hand` (ch07_after_the_bell), `tie_band` (ch07_tavi), `untie_band` (ch07_tavi)
- **tender**: `open_chamber` (ch05_kahre), `open_pavilion` (ch05_crown_pavilion), `paint_gilt` (ch09_the_ebbing), `palms_level` (ch08_storm_against_wind)
- **weir_child**: `lean_out` (ch05_lanternfall_weir), `slip` (ch05_lanternfall_weir)
- **wright_child_a**: `crawl_out` (ch06_barge)
- **wright_child_b**: `crawl_out` (ch06_barge)

## Acceptance criteria
- [ ] liss `haul_rope` and pell `storm_call` are added to requested_clips.json (M3-CHR-1000), or built.
- [ ] A plan for the people's clips: built per person, or a shared set (`give_r`, `take_r`, `laugh_standing` and
      `kneel_palms_flat` already exist in requested_clips.json "shared") that act1-chapters' scripts call instead.
- [ ] Re-run the audit (`--filter=qa_cutscene_motion_audit`): the "none" count falls as each lands.

## Review log

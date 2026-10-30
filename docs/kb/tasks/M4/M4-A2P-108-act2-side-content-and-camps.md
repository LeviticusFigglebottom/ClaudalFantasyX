---
id: M4-A2P-108
title: "Act II side content: two optional errands or lore finds per chapter, and one camp conversation per chapter"
role: narrative
status: review
owner_session: "act2 story track (claude/act2-plan, ADR 0205)"
depends_on: [M4-A2P-001, M4-A2P-007]
reviewer: lead
milestone: M4
request-from: lead
---
## Goal
The Lead's 2026-10-30 request: small, sincere optional content for each Act II zone, tied to the pilgrimage, plus a camp or rest conversation per chapter that grows a companion's arc toward the cost of ending the cycle (pillar 6).

## What's written (21 scripts, `game/data/dialogue/ch1N/`; each sets its own flag, declared in flags.tres)
| Ch | Errands and finds | Camp |
|---|---|---|
| 10 | `ch10_side_the_three_nets` (needs `ch10_drowner_defeated`, `ch10_reached_reedhollow`), `ch10_find_guardian_strap` | `ch10_camp_what_you_carry`: Rhen and Pell (the blank shell; Kell's wick, unlit) |
| 11 | `ch11_side_the_altar_lamp` (`ch11_reached_lowlight`), `ch11_find_lampmakers_plate` | `ch11_camp_she_sounded_glad`: Asha and Pell (`ch11_nhoa_bound`) |
| 12 | `ch12_side_the_boys_knot` (`ch12_reached_quellan`), `ch12_side_dorros_cord` (`ch12_ram_felled`) | `ch12_camp_the_end_of_the_road`: Toma and Ysolde (`ch12_ysolde_confessed`) |
| 13 | `ch13_side_the_leaning_flame` (`ch13_wedding_announced`), `ch13_find_velamir_register` | `ch13_camp_twenty_four_years`: Ysolde and Asha (`ch13_ethren_bound`) |
| 14 | `ch14_side_the_oar_pin`, `ch14_side_six_lamps` (both B01, before the vows) | `ch14_camp_the_whole_of_him`: Liss and Rhen (`ch14_complete`) |
| 15 | `ch15_side_the_current_phrase` (`ch15_reached_hollowmere`), `ch15_side_the_tally_hull` (`ch15_toma_confessed`) | `ch15_camp_the_bottom_step`: Toma and Kerrid (`ch15_kerrid_revealed`) |
| 16 | `ch16_side_the_fallen_cairn`, `ch16_find_the_counting_stone` | `ch16_camp_coming_up`: Asha and Rhen (the last wade night, before the Choir) |

The flag in brackets after each script is when it may first run. The chapter flow checks it; each script's header comment says the same.

## Acceptance criteria
- [x] `.dlg` with `#line:` ids. dlgc compiles them into `dialogue.csv`. Every spoken line has a speaker and an emotion.
- [x] No new `@anim`, `@sfx` or `@camera` cues: dialogue only, so nothing joins the pending lists. Cinematics may stage them later.
- [x] dlgc --check, validate_data (banned terms included), and Godot `act2_dialogue` (every path, all flags unset and all set) and `dialogue` 86/0 are clean.
- [ ] **Chapters/towns (request):** place the interactables and NPC actors, and add the camp rest points.
- [ ] **ui-menus (request):** add the errands as `side` rows in `game/data/flow/objectives.json`, with `OBJ_SIDE_*` loc keys. Each row's `until` is the flag the script sets.
- [ ] ADR 0041 §3's final bar.

## Notes
- **Facts kept (bible and scripts):**
  - Imra never reached Ansedra: she was struck at Corrow in 1001. So the Archive register shows an earlier, unnamed Velamir.
  - Kell's wick stays unlit and is never paid off: E7 is Act III's.
  - Nothing says what the Hush does before Ch16 B05.
  - The current-song is Hollowmere's, never Dace's.
  - Toma's 1003 camp is not Liss's.
- **Ch14:** act_outline says "no side scene", so its two items are moments in B01's hour before the vows, not detours.

## Review log

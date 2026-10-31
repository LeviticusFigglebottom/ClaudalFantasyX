---
id: M5-A3P-1015
title: "Request (staging + flow): Ch21 in the heart (HT01–HT22) and the Ending (E01–E13), with its flow and credits"
role: cinematics
status: review
owner_session: "act1-chapters"
depends_on: [M5-A3P-1014]
reviewer: narrative
milestone: M5
request-from: narrative
---
## Goal
The scripts are in `game/data/dialogue/ch21/` and `ending/` (M5-A3P-1014). Beats: docs/kb/story/beats/act3_ending.md;
file-to-beat map: drafts README "Files by beat" (H01–H09, R1, E1–E7).

## What the scripts name
- **Zones:**
  - `ch21/heart`: new; HT01–HT22 (not H-ids, which read as beat names). Mark: `arms_length`.
  - The Ending: the Kite deck (`ch18/kite`), the Haluna dock and beach (`ch02/haluna`), and Oruvel (`ch01/oruvel`); E01–E13.
  - Marks: `by_asha kite_rail kite_rail_b kite_wheel rhen_shoulder where_dace_stood`.
- **Held input:** `take_the_strain` (`ending_the_kite_comes_down`, Liss bringing the Kite down by hand) → FIELD_PROMPT_ENDING_TAKE_THE_STRAIN, in an ending field data `prompts` map.
- **Flow:**
  - Ch21:
    - H01 `ch21_the_last_layer` → H02 `ch21_two_lamps`;
    - H03 `ch21_kesh` → the fight `ch21_kesh` → `ch21_kesh_release`;
    - R1 `ch21_seven_bands`;
    - H04 the Warden phase `ch21_sefir_warden`, started by the flow after R1;
    - H05 `ch21_he_takes_the_heart` → the fight `ch21_sefir_heart`;
    - H06 → `ch21_sefir_letting`;
    - H07 `ch21_the_letting`;
    - H08 `ch21_sefir_lets_go`;
    - H09 `ch21_great_unbinding` sets `ch21_unbound`.
  - Then E1–E7 in order:
    - `ending_imra`, `ending_rest_hands`;
    - `ending_dace`, `ending_rest_where_he_stood`;
    - `ending_kerrid`, `ending_rest_empty_place`;
    - `ending_the_kite_comes_down`, `ending_nothing_comes`;
    - `ending_the_dark_sea`, `ending_beach_rite`;
    - `ending_first_lamp` (after the credits: the post-credits lamp).
- **Inserts:** T-08 (the hitch, in H02 and E3) and T-09 (Tobin's lamp dark, in E4) are optional inserts with no line (drafts README decision 16).

## Acceptance criteria
- [ ] The zone, shots and marks exist, and the flow runs H01 → E7 with the credits before `ending_first_lamp`. Godot `act3` stays green.

## Notes (act1-chapters, the Act III chapters track, 2026-10-31)
- **Zone:** `ch21/heart` (Ch05Zone, from `tools/act3/ch21_greybox.py`):
  - the last layer's walk;
  - the heart's floor round the two lamps (light columns inside a ring; `arms_length` where Rhen stops);
  - the Kite at rest;
  - the dark Choir-stone (R1: a save, `heart_choir_stone`);
  - the battle floor.
  - **Shots:** HT01–HT02 on the walk; HT03–HT22 round the lamps, outside the ring.
- **Flow (`chapters/ch21.json`):**
  - H01 on arrival.
  - The heart's mouth plays H02, then H03 and the fight `ch21_kesh`; the return plays her release (`ch21_kesh_released`)
    and R1.
  - Stepping onto the battle floor starts the Warden (decision 13).
  - Each return plays the next: H05 and the heart phase; the Letting scene and its fight; H08 and H09
    (`ch21_unbound`), then it goes to the Kite.
  - The Cage's return (Ch20 U08) now goes down to the heart.
- **The Ending (`chapters/ending.json`, read by Ch18Zone once `ch21_unbound` is set):**
  - E1 and its rest on arrival.
  - E2 at `where_dace_stood`; E3 at the rail.
  - E4 at the wheel: the held input `take_the_strain` (ch18_field.json), then `ending_nothing_comes`. It sets
    `ending_landed` and goes to `ch02/haluna` DockNight.
  - The Kite's courses close after the Unbinding.
  - **Marks and shots on the Kite:** E01–E10; `by_asha kite_rail kite_rail_b kite_wheel rhen_shoulder
    where_dace_stood`, plus the `@vfx at=` ids.
- **Open, requested in M5-A3P-1203:** E5 (Haluna, slice-polish), E6 (the credits' beach-rite vignette, Cinematics' scene)
  and E7 (the credits' `next_scene` into Oruvel, UI and slice-polish).
- **Other open items:**
  - R1's optional per-member lines (`ch21_bands_*`) need the party standing as talkable actors in the heart, like the
    Act I camps.
  - H09's montage places (`iskarra_columns`, `tamsule_bell` and others) are inserts in other zones, so they warn
    here.
  - T-08 and T-09 are optional inserts with no line (decision 16).
- **Tests:** `test_ch21_thread.gd`, 3 tests: Ch20 down to the heart; H01–H09; the Ending aboard the Kite to Haluna.
  `test_ch21_walkable.gd`: the last layer to the lamps and the Choir-stone.

## Review log

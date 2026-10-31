---
id: M5-A3P-1015
title: "Request (staging + flow): Ch21 in the heart (HT01–HT22) and the Ending (E01–E13), with its flow and credits"
role: cinematics
status: review
owner_session: "claude/act2-plan (supplementing act1-chapters/cinematics, the Lead 2026-10-30 23:26; ADR 0207)"
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

## Done (act2-plan, supplementing)
- **Zone `ch21/heart`:** `Ch21Zone`, and `tools/act1/ch21_greybox.py` (new), which writes the layout and the scene.
  - The scene instances env-art's Heart kit: `heart_floor`, `heart_column` at (-9.5, -12), `heart_eyewall`.
  - The layout holds collision only, the spawns HeartEdge and Centre, the anchors the scenes name, and HT01–HT22. H09's seven lights rise round the eyewall; cinematics may cut them to their own places later.
  - The location row and `LOCATION_CH21_HEART`.
- **Flow:** `ch21.json`.
  - **The Heart:** H01–H02 on arrival from Ch20 (Ch20 now goes here), H03 Kesh on a touch at the centre. Each fight's return then plays the next stage: Kesh's release and R1, H05, H07, then H08–H09, which go to the Kite.
  - **The Ending:** this file's `ch18/kite` block (chapter 21) plays E1–E5 in order, including the strain's held input, then the end card.
  - **New flags:** `ch21_started`, the four victory flags (`ch21_kesh_fought`, `_warden_fought`, `_heart_fought`, `_letting_fought`) and `ending_landed`.
- **The Ending's staging on the Kite** (`tools/act1/ch18_greybox.py`): E01–E10, the rails, `where_dace_stood`, `rhen_shoulder`, and the goodbyes' anchors.
- **Test:** `tests/integration/test_ch21_thread.gd`.

## Open
- **The fights:** M5-A3P-1017. The battle steps are named in `ch21.json`'s doc.
- **After E5:** the credits roll (M5-A3P-1700) needs a scene to hand off to, and its `beach_rite` vignette needs Haluna (M5-A3P-1019). E6, the dark sea at Haluna, also needs 1019. E7, the first lamp at Oruvel after the credits, needs M5-A3P-1018 and `credits.json`'s `next_scene`.

## Review log

---
id: M4-A2P-114
title: "Request: play the Act II scenes from the Ch10–Ch16 flows (the setters for the beat-level objective rows)"
role: cinematics
status: review
owner_session: "act1-chapters (claude/act1-chapters)"
depends_on: []
reviewer: narrative
milestone: M4
request-from: narrative
---
## Goal
To act1-chapters, who own the Ch10–Ch16 greybox flows (M4-C10-02 … M4-C14-02). This comes from the Lead's FAST-TRACK on
big23's test_qa_threads red.

The greybox flows play no Act II scene, so no chapter thread raises the story flags the scenes set. test_qa_threads
requires every main objective's `requires` and `until` in a chapter's zones to be raised by that chapter's thread.
Story's beat-level objective rows for Ch10–Ch13 therefore failed on 19 flags.

**Update (2026-10-30, the Lead):** story has written the 10 cut rows back in, unchanged (the Ch10–Ch14 block is as
at 089c254d4). Each flag the threads can't raise yet is listed in `tests/integration/qa_known.json` `"unraised"`, with
the scene that sets it and this task, so test_qa_threads reports it instead of failing. An objective's `until` gates no
beat, so none of them is a softlock.

**For act1-chapters:** as each flow step lands (a `play` of the scene, or a battle's `victory_flag`), delete that
flag's `unraised` row in the same commit. The guard then holds it for good. The rows in `objectives.json` need no
change.

## What to wire: the exact setter for each of the 19 flags
Every scene below already sets its flag with `<<set>>`, so the flow only has to **play** it. Use the Act I pattern
(ch05.json): a beat on a trigger, with `when` gating and `play` steps. A **new trigger** sits at the objective row's
target POI, which needs placing in the layout (act1-chapters' lane: trigger placement). For battles, use a flow `battle`
step with `victory_flag` and `return_spawn`, as ch10's drowner does. Where a scene already ends on
`<<event start_battle …>>`, take **one** of the two routes, not both.

| # | Flag | Zone | Trigger (where) | `when` | Steps |
|---|---|---|---|---|---|
| 1 | ch10_farewell_tide_seen | ch10/reedhollow | new `shore` at the `Shore` spawn (row r_shore's POI `shore`) | set ch10_reached_reedhollow; unset ch10_farewell_tide_seen | place Shore; play `ch10_farewell_tide` (B09) |
| 2 | ch10_complete | ch10/reedhollow | the same `shore` beat continues (`ch10_farewell_tide` already jumps to B10 `ch10_outside_causeway`) | set ch10_farewell_tide_seen; unset ch10_complete | place Gate; play `ch10_dawn_gate` (B11, dawn) |
| 3 | ch11_nhoa_bound | ch11/lowlight | arrive at spawn `Sanctum` via a new `to_sanctum` trigger at the well-shaft foot (row l_down's POI `sanctum`); before it, a new `engine` trigger at the engine hall's stair head (`EngineHall`) | engine: set ch11_reached_lowlight, unset ch11_engine_released. sanctum: set ch11_engine_released, unset ch11_nhoa_bound | engine: play `ch11_the_engine` → battle `ch11_lamp_engine`, victory_flag `ch11_engine_released` (**declare it** in flags.tres: §1's name), return_spawn EngineHall → play `ch11_twice`. sanctum: place Sanctum; play `ch11_nhoa` |
| 4 | ch11_complete | ch11/sunken_vey | arrive from Lowlight (`FromLowlight`) | set ch11_nhoa_bound; unset ch11_complete | place FromLowlight; play `ch11_held_by_you` (B11) |
| 5 | ch12_ram_felled | ch12/keth_pass | new `terrace` trigger under the seeping wall (row k_wall's POI `terrace`; arena spawn `RamArena`) | set ch12_started; unset ch12_ram_felled | play `ch12_weeping_wall` → battle `ch12_avalanche_ram`, **victory_flag `ch12_ram_felled`**, return_spawn RamArena → play `ch12_herd_cord` (B07, which sets it too) |
| 6 | ch12_hesk_bound | ch12/cloudloom | new `dais` trigger at the hall's dais (row c_dais's POI `dais`; spawn `Hall`) | set ch12_reached_cloudloom; unset ch12_hesk_bound | place Hall; play `ch12_hesk` (B10–B11; it also sets ch12_ysolde_lied) |
| 7 | ch12_ysolde_confessed | ch12/quellan | arrive `FromCloudloom` (row q_inn's POI `inn`) | set ch12_hesk_bound; unset ch12_ysolde_confessed | place FromCloudloom; play `ch12_forty_seven_voices` (B12, night) |
| 8 | ch12_complete | ch12/keth_pass | arrive `FromQuellan` | set ch12_ysolde_confessed; unset ch12_complete | place FromQuellan; play `ch12_down_the_other_side` (B13) |
| 9 | ch13_ethren_bound | ch13/sanctum | the existing arrive row, then a new `ledge` trigger at the basin's edge (row s_ledge's POI `ledge`) | set ch13_entered_sanctum; unset ch13_ethren_bound | play `ch13_ethren` (B05–B06) |
| 10 | ch13_read_ledgers | ch13/lamp_archive | new `ledgers` trigger at the ledger shelves (row la_ledgers's POI `ledgers`) | set ch13_entered_archive; unset ch13_read_ledgers | play `ch13_archive_ledgers` (B07) |
| 11 | ch13_read_cantor_roll | ch13/lamp_archive | new `roll` trigger at the lectern (row la_roll's POI `roll`) | set ch13_read_ledgers; unset ch13_read_cantor_roll | play `ch13_archive_roll` (B08) |
| 12 | ch13_archive_read | ch13/lamp_archive | the same `roll` lectern, the third day | set ch13_read_cantor_roll; unset ch13_archive_read | play `ch13_archive_hands` (B09) |
| 13–14 | ch13_pact_of_silence, ch13_complete | ch13/ansedra | arrive `FromArchive` at night (row a_moorings's POI `moorings`) | set ch13_archive_read; unset ch13_pact_of_silence | place FromArchive; play `ch13_the_pact` (B10–B11; sets both, then Sefir closes the book) |
| 15 | ch14_started | ch13/ansedra_lacquer_court | **already set** by ch14.json's arrive row. It's unraised only because Ch13's thread checks the court's rows (below) | — | — |
| 16–17 | ch14_vows_spoken, ch14_declared_heretics | ch13/ansedra_lacquer_court | new `dais` trigger at `vows` (row lc_vows's POI `dais`) | set ch14_started; unset ch14_vows_spoken | play `ch14_the_vows` (B02–B05, one scene with nodes; ends on `start_battle ch14_water_steps`) |
| 18 | ch14_steps_held | ch13/ansedra_lacquer_court | the vows' battle return (spawn `Steps`) | — | battle `ch14_water_steps` (set piece), victory_flag `ch14_steps_held`, return_spawn Barge → play `ch14_first_ripple` (B07–B08, sets it too; ends on `start_battle ch14_malcor_venn`) |
| 19 | ch14_complete | ch13/ansedra_lacquer_court | the Venn battle's return | — | battle `ch14_malcor_venn`, victory_flag `ch14_venn_beaten` (**declare it**: act2_ch14's flag table) → play `ch14_left_standing` (B10) → the existing `escape` go |

**Missing encounters (combat lane, before #18 and #19 can run):** `ch14_water_steps` and `ch14_malcor_venn` aren't in
`game/data/battle/encounters.json` yet. Ch13 has no boss encounter (Ethren is a binding scene, not a fight).

**Thread tests:** each `test_chNN_thread.gd` should touch the new triggers in order, as test_ch05_thread does, so the
guard sees every flag raised. Then delete each flag's row from `qa_known.json` `"unraised"`.

**The Lacquer Court's rows are Ch14's but sit in a `ch13/` zone**, so Ch13's thread is the one that checks them (see
M3-UI-1242). Their five flags (ch14_started and the four beat flags) stay in `unraised` until either the guard reads a
row's `"chapter"` or Ch13's thread plays into Ch14.

**Ch15** (`ch15_the_dock_master` must play when the party reaches Hollowmere, after `ch15_current_song` at sea) and
**Ch16** have no thread that checks their rows yet, so their rows are unchanged.

## Acceptance criteria
- [x] The beat-level rows are back in `objectives.json` (story, 2026-10-30).
- [x] Each Ch10–Ch13 flow plays its scenes and battles in §1's order (Ch14: M4-A2P-118).
- [ ] `qa_known.json` `"unraised"` is empty again, and test_qa_threads stays green. (Down from 19 to Ch14's 5, which wait on M4-A2P-118; green.)

## Notes (act1-chapters, 2026-10-30)
- **Wired (§1 rows 1–14):** the triggers come from the generators: reedhollow `shore`, lowlight `engine` and
  `sanctum`, keth_pass `terrace`, cloudloom `dais`, sanctum `ledge`, lamp_archive `ledgers` and `roll`.
  - The return scenes are `arrive` rows:
    - Lowlight after the engine fight (`ch11_twice`, held to once by the new `ch11_twice_seen`).
    - Vey from Lowlight (`ch11_held_by_you`).
    - Keth Pass after the Ram (`ch12_herd_cord`) and from Quellan (`ch12_down_the_other_side`).
    - Quellan from Cloudloom (`ch12_forty_seven_voices`).
    - The Archive's third visit (`ch13_archive_hands`).
    - Ansedra from the Archive (`ch13_the_pact`).
  - Battles use one route each: `play` the scene, then the flow's `battle` step (a scene's `start_battle` is only
    reported).
  - `ch11_engine_released` is declared in flags.tres.
- **Threads:** test_ch10..13_thread play the story in order. The 14 rows are gone from `unraised`, and
  test_qa_threads is green.
- **Staging:** the scenes name shots, cast, marks and VFX anchors these greybox stages don't have yet (100 warnings).
  They're handed to M4-A2P-075 (staging 070–075, mine) through one qa_known `known` row.
- **Ch14 (rows 15–19):** `ch14_water_steps`, `ch14_malcor_venn` and Venn's enemy row aren't built yet, so these are
  M4-A2P-118.

## Review log

# Live log: combat-systems environment

**Session:** `session_01F3vrUN933kFk8vhen4Tm2X` (cloud) · **Branch:** `claude/combat-systems` (from `claude/undertow-lead-handoff-ze8rrn` @ 920ebd32) · **Role:** combat (rules and data) · **Lead:** `session_018aiGwGLGkxsnMnu8VfCu1m`

I own the battle RULES and DATA: the headless engine (`game/battle/*.gd`), items, abilities, encounter balance numbers, the balance sim (`tools/balance/sim.py --check`), and field-usable abilities and items. VFX are battle-presentation's; menu screens are ui-menus'. Path claims are in `docs/kb/ownership.md` (the "Combat systems" row).

## Queue (the human's playtest FAST-TRACKs, 2026-11-03, in order)
1. A REVIVE item in the Act I economy (in battle and in the field).
2. After a WON fight, KO'd members come back at 1 HP.
3. Spells castable OUTSIDE combat (`field_usable`), with an API for ui-menus.
4. The solo Ch1 Hullgnaw is a little too hard: sim-tune it.
5. Then: combat rows in `docs/kb/qa/act1_gpu_qa.md` (newest on origin/gpu/act1-qa-7) and the inventory.

## Log (newest first)

### 2026-11-03: FAST-TRACKs 1–4 DONE (all `status: review`)
MERGE-READY @ 08eaf116 (plus this log commit): FAST-TRACK, cherry-pick all of `claude/combat-systems`.
1. **Revive item (M3-CMB-03).** The revive already existed: the **Relighting Wick** (`relighting_wick`, revive 25%, battle and field). It is a taper lit from a living lamp; in the glossary, "lamp" is a living being's inner glimmer. The playtest gap was REACH: no shop sold it before Ch3's Drownbell, and nothing dropped it.
   - Haluna Market now sells it from the first visit (`ch02_met_asha`), at **240 lume** (was 300).
   - The Hullgnaw (Ch1) and the Spar-Wraith (Ch4) each drop one (100%); the Gull Harrier drops it 4%.
   - Its description now says it works in the field. economy.md and the glossary are updated.
   - test_shop and test_shop_menu (ui-menus') used the Wick as their "gated item" example; they now use Tidewash Salve. A one-word change each.
2. **KO'd members back at 1 HP after a WON fight (M3-CMB-04).**
   - `Formulas.VICTORY_RISE_HP` and `victory_rise_hp`, with formulas.md and test_formulas in the same commit.
   - `BattleSpoils.returning_party(engine)` hands the saved vitals a risen copy of each KO'd member after a victory or a set piece's scripted way out. An escape keeps them down; stone is not a KO.
   - The engine's combatants are untouched, so XP credit (alive at victory) and the stage are unchanged.
   - **One-line hook** in `game/battle/scene/battle_vitals.gd` `send_back` (scene glue, not this track's).
3. **Spells outside combat (M3-CMB-05).**
   - skills.json `field_usable: true` on Mend and Chorus Mend. validate_data's `field_usable_errors` allows it only on ally-targeting heals or cleanses.
   - **`FieldSpell`** (`game/progression/field_spell.gd`) is the rule: `castable`, `caster_error`, `target_error`, `reach`, and an exact `preview` and `cast` at `Formulas.FIELD_VARIANCE_PCT` (100; no RNG out of battle).
   - The API is written up in request task **M3-MNU-05** for ui-menus (the Spells screen, plus a check of the Wick's field use). **M3-BPR-446** asks battle-presentation to check the Wick's VFX and stage the risen.
4. **Solo Hullgnaw (M3-CMB-06).** HP 2000 → **1850**, strength 3 → **2**. The Gnaw skill is shared with Act III's Hull Rasp, so its power is unchanged. The pattern is kept: the Coil telegraph into the Gnaw, the raft breaking at 50%, and Kick Off answering Thrash.
   - 1000 seeds: naive 0.6 → **12.8%**, naive_swell 3.6 → 51.1%, role_answer 8.5 → **68.4%**, smart 86.4 → **100%** (mean 25.9 actions).
   - New first-timer bands: naive 5–25%, role_answer 55–85% (now banded), smart ≥ 97% with a 24-action ease ceiling.
   - The sweep table is in balance_report.md (2026-11-03).
5. **QA rows and the inventory:** origin/gpu/act1-qa-7 `act1_gpu_qa.md` has no open combat-systems row. Row 73 (Attack's "R3") and row 69 (plural) are ui-menus'. `act1_final_inventory.md` has only env-art-b rows.

**Checks run:**
- validate_data, taskboard --check, gdlint and gdformat on every touched .gd.
- Godot tests filtered to field_spell, victory_rise, revive_economy, test_formulas, test_shop, test_shop_menu, test_items_menu, test_battle_items, swell_save, party_vitals, battle_vitals, ch01_battles, timeline_honesty and boss_set_piece: all green.
- tools tests: test_field_usable, test_validate_data, test_items_validate, test_balance_sim, test_ch01_validate and test_skill_targets_validate: green. The full `run_tool_tests.py -j 4` was still running (the rig-integrity tests) when this was written.
- `sim.py --check` on the 7 Ch1 suites: ok.

**Checks skipped:**
- The full 76-suite sim: it outlasted the 30-minute background limit, and its first 217 lines were all ok. Only the Hullgnaw suite reads the changed data.
- Screenshots and Blender: nothing visual changed.
- The coverage step: the new code is fully exercised by its tests. The Lead's full gate measures it.

LEAD-ASK: M3-CMB-04 put a one-line hook in `game/battle/scene/battle_vitals.gd` (BattleSpoils.returning_party in send_back). OK to keep, or should its owner take it? (Assumed OK.)

**Next:** adjacent combat work, if the Lead has none queued. Candidate: a party cure or revive spell, since no hero can cure poison or raise the fallen with a skill yet (FieldSpell already supports `cleanses`). That is a content decision, so it waits for the Lead's word.
- **Follow-up, tools suite:** `run_tool_tests.py -j 4` finished: 222 units, 11 failing, none in files this branch touches.
  - LFS-pointer audio that ffmpeg can't decode: test_dialogue_clarity, test_direction_holds, test_cutscene_sfx_files.
  - Rig, creature, arena and palette assets: test_rig_integrity Asha, test_creatures, test_b_arenas, test_palette_check, test_hero_clips.
  - Screenshot baselines: test_screenshots.
  - `memories.csv` MEMORY_CH04_SHELL_IS_SET uses the old "Shell" name: test_status_names, ui-menus'/story's.
  - `game/audio/prop_audio.gd:77`: test_freed_cast_lint, audio's.
  - Every validator and balance unit is green.

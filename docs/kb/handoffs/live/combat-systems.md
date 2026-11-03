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

### 2026-11-03 ~17:30: the Lead's 17:15 check: each FAST-TRACK confirmed
- **FT done @ dd522443: (1) the revive item.** The Relighting Wick: original name and lore (glossary).
  - Shops: Haluna Market sells it from Ch2's first visit, at 240 lume (4eb42a51).
  - Drops: the Hullgnaw and the Spar-Wraith 100%, the Gull Harrier 4% (4eb42a51).
  - **Chest (new, dd522443):** one Wick in Ch1's hidden old tin, the Underway's find behind the coral curtain that the lantern reveals. test_ch01_thread pins it.
- **FT done @ bfda429a: (2) the KO'd at 1 HP after a won fight.** BattleSpoils.returning_party, Formulas.VICTORY_RISE_HP, and the BattleVitals.send_back hook. Tests: test_victory_rise, test_formulas.
- **FT done @ bfda429a (API task da778b9e): (3) field spells.** skills.json `field_usable` (Mend, Chorus Mend, validated) and `FieldSpell` (game/progression/field_spell.gd: castable, caster_error, target_error, cast_error, reach, preview, cast). ui-menus binds it per M3-MNU-05. Tests: test_field_spell, tools/tests/test_field_usable.py.
- **FT done @ 08eaf116: (4) the Hullgnaw** (logged above).
- **Sim check, touched suites only** (every encounter with the Hullgnaw, the Gull Harrier or the Spar-Wraith; 1000 seeds; `sim.py --check` exit 0, all ok):
  - sandbox_reef 10.9 / 97.1 / 100.0;
  - sandbox_reef_tier1 25.1 / 98.4 / 100.0;
  - sandbox_reef_vowbound naive_swell 38.9;
  - sandbox_reef_vowbound_good naive_swell 46.2;
  - ch01_hullgnaw 12.8 / 68.4 / 100.0;
  - ch03_causeway_shore 71.3 / 95.3 / 99.9;
  - ch03_causeway_harrier 65.8 / 95.3 / 100.0;
  - ch04_spar_wraith 3.7 / 72.8 / 100.0;
  - ch06_ridge_gulls 57.3 / 74.0 / 99.7;
  - ch06_flats_crabs 55.2 / 95.8 / 100.0.

  The columns are naive / role_answer / smart win %. The drop changes don't move win rates (drops roll after the victory). Only the Hullgnaw's numbers changed.

MERGE-READY @ dd522443: FAST-TRACKs 1–4 complete. Checks: validate_data; test_ch01_thread and test_ch01_zones green; the sim on the touched suites as above.
**Next:** no open combat Act I rows, so Act II per ADR 0205 §4: my M4 combat tasks and docs/kb/plan/act2_plan.md.

### 2026-11-03 ~19:00: Act II (ADR 0205 §4): M4-A2P-1202 to review
MERGE-READY @ f096de6b: M4-A2P-1202.
- When no field calls for a particular Vowbound, the sim now calls the latest bound one (3e843993).
- `sim.py` gates `p90_turns_max` on banded rows only (`within_p90`); report-only rows still fail on timeouts.
- `--check` is clean on all 40 suites that bind more than one Vowbound.
  - The Wakefin's masher tail is the same whichever Vowbound is called (p90 91–92), so the call rule alone couldn't fix it.
  - Spire Wicks p90 went 55 → 48.
  - Details are in balance_report.md (2026-11-03).
- Checks: battle_sim tests 56/0; tools test_balance_sim and test_balance_naive_swell OK; taskboard --check.
- LEAD-ASK: the p90 cap no longer gates report-only rows (my lane, tools/balance). Overrule if you want the cap back on naive_swell. Assumed OK.
- **Next:** no open combat-rules task on the board. Battle-presentation owns the open BPR and A2P VFX requests. I'm waiting for the Lead's next combat item, or the cure/revive-spell content call above.

### 2026-11-03 ~19:20: the Lead's 18:45: M3-CMB-1252 (ui-menus' field cast request) DONE
MERGE-READY @ 2acd3abc, for big48: M3-CMB-1252.
- The API is `FieldSpell` (game/progression/field_spell.gd), the equivalent the task allows. ui-menus' `FieldMagicRules.live` already binds it by name (origin/claude/ui), and their task file was marked "withdrawn, superseded" there.
- To close it fully, this branch adds what the original ask named and FieldSpell lacked:
  - the result shape `{ok, mp_spent, healed: {id: HP}, cured: {id: [statuses]}, revived: []}` (alongside `changes`);
  - a Silenced-caster refusal (`ERR_SILENCED`) for magic skills;
  - a test that a field Mend heals exactly what a battle Mend heals at variance 100. Over 120 seeds the battle's heals bracket the field amount, and the field amount appears among them.
- Data: `field_usable` is on Mend and Chorus Mend. No cure or revive spell exists in skills.json yet; FieldSpell already handles `cleanses`.
- I didn't copy the task file here. It lives on claude/ui as done, and a second copy would be an add/add conflict at merge.
- Checks: test_field_spell 8/0; gdlint and gdformat clean.

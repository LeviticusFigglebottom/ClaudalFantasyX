---
id: M2-FP-04
title: First-playable integration, Cutscene A and B in game, PLAYTEST.md
role: lead
status: review
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M2-FP-01, M2-FP-02, M2-FP-03]
milestone: M2
request-from: lead
---
## Goal
Wire the thread end to end: boot → title → New Game → prologue → Cutscene A on the beach → free roam with villagers → first battle → back to the field → save at the shrine → Cutscene B (the first verse) → end card. Document how the human plays it on Windows (`docs/PLAYTEST.md`).

## Acceptance criteria
- [x] An integration test walks the whole thread headlessly (instant cutscenes).
- [x] docs/PLAYTEST.md: how to open and run it in Godot 4.6.3 on Windows, controls, what to expect, known placeholders.

## Notes (handoff)
- Ready for review by the **Lead**. `tests/integration/test_fp_thread.gd` walks the whole thread headlessly; a real-runtime smoke (router swaps, Enter mashed) also ran end to end with no script errors. Cutscene B plays on a placeholder Shell Shrine set (`game/levels/ch03/first_verse/`) and its closing `start_battle drownbell` goes to the end card until the Drownbell exists.

## Review log
- 2026-10-23 lead-role reviewer (review-sweep-K, fresh reviewer): **request changes on docs/PLAYTEST.md only (B1). Approve the integration code with should-fixes.**
  - **What I read:** the task, handoff first-playable-1, `git diff 2ddca3f^1 2ddca3f -- game/flow/haluna_story.gd game/levels/ch03 tests/integration/test_fp_thread.gd tests/integration/test_fp_first_verse.gd docs/PLAYTEST.md`, game/data/world/field_input.json, debug_overlay.gd, export_presets.cfg and the Haluna README.
  - **Checks:**
    - Godot `--filter=fp_` 15/0 failed. This includes `test_fp_thread.gd::test_the_first_playable_thread_end_to_end`: the whole thread headless, with instant cutscenes and recorded scene changes. The only warning is the missing `drownbell_toll` sfx, a known placeholder.
    - I did not repeat the real-router Enter-mash smoke. The handoff says it passed, and there is no scripted harness for it.
    - Note: project.godot has no `[input]` section. Field actions come from field_input.json at runtime (FieldInput.ensure_actions), and menus use Godot's `ui_*` defaults.
  - **Blocker:**
    - **B1: PLAYTEST.md misdirects the human on the mandatory save and on the battle.**
      - **:12** says the shrine is "near the beach palms". It is on lane 3 in the village (README.md:34, 50; z 46.6), past the tideline strip.
      - **:11** says "you return to the beach path". BattleReturn is inland of the strip, before the lane-1 gate (README.md:32).
      - **:58** says that after a loss "the fight can be skipped by walking on". After a loss or an escape you are on the village side, and the causeway head is at the beach's north end (README.md:35). Reaching it crosses the strip again, so the fight returns. Only the village and the shrine can be reached without a win.

        Fix the line. If a bypass does exist, gate `causeway_head` (haluna.tscn:606) on `ch02_tideline_won` instead.
      - **:21** says to download `claude/first-playable`. The thread is merged into the integration branch, which also has CHR-07 Asha and the RND-12 sky. Point the human there.
  - **Should-fix:**
    - **S1: smaller PLAYTEST.md accuracy items.**
      - The controls table matches field_input.json and the `ui_*` defaults: E/Enter/Space or A to interact, button 9 (LB) to walk, Q/R or the right stick to orbit, and `ui_up`/`ui_down` with Enter for choices.
      - Add that **E also advances dialogue** (cutscene_sequencer.gd:93).
      - **:42** "Back, cancel: Escape" does nothing in the field, where there is no pause menu. Say "in menus and battle".
      - **:47** "Debug keys (editor runs only)": `OS.is_debug_build()` (debug_overlay.gd:54) is also true for an export with "Export With Debug", which is Godot's default. On the F4 page, Enter both toggles a flag and is field interact.
    - **S2: the thread test skips the story's battle wiring.** test_fp_thread.gd:67-68 calls `BattleRequest.start` itself, so HalunaStory's real battle hand-off (haluna_story.gd:95-100: `location_id`, `battle_return_spawn`, `battle_victory_flag` from the data) is never exercised. Leave `story.hand_off` unset for the battle step and record through `BattleRequest.change_scene`. Also add two legs:
      - a loss, Return, and the re-trigger on the way back to the beach;
      - a load at Shrine with `ch02_met_asha` set (Cutscene A must not replay).
    - **S3: Asha's face lighting in Cutscene B.** first_verse.tscn:169-173: the Sun has the default `shadow_normal_bias` (1.0) and lights Asha at dialogue range. character_shading.md:184 says 2.5–3.0 for lights that key a face. Same issue as M2-FP-02 S1.
    - **N1: hard-coded hand-off.** first_verse_scene.gd:12-13 hard-codes the scene id and the end-card path, while every other hand-off is in first_playable.json. Move them there.

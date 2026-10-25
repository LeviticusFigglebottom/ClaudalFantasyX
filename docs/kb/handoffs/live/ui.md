# Live log: ui environment

UI track (cloud session session_01NyuYPSZn7o7gYirTvz4zjs), branch `claude/ui`, started from `claude/undertow-lead-handoff-423ixt` at 92bd0f4 on 2026-10-24. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE; the integration branch is `claude/undertow-lead-handoff-423ixt`.

## Queue (from the Lead, 2026-10-24)
1. M2-UI-03: Swell input panels for Asha (chant), Toma (brace), Ysolde (glyph); revisit the 7-row root menu. **Review** (reviewer lead).
2. Lead decision on M2-UI-05: hide the Call row until a Vowbound is bound. **Done** (5eda83b; ADR 0030 amendment).
3. M2-UI-06: shop and inn menus for Haluna. **Skipped: m2-slice had already done it** (eeb3737 on claude/m2-slice, in review, with Haluna's keepers placed in e5ba263). This track's claim is reverted.
4. UI polish pass for the slice: **M2-UI-09, review** (reviewer lead). Also took **M2-UI-08** (Art's fixes, filed on claude/env-art): review, reviewer character.
5. Gaps the m2-slice playthrough files under role ui. **None filed yet:** m2-slice's playthrough (handoff cinematics-7) filed only M2-FP-20 and M2-FP-21, both its own. Its ui review request (M2-FP-12) is already approved and done.
6. (Found on claude/characters) **M2-UI-07**, the hero actor hook: **hook done and pushed (08c872c)**. It is **blocked** on M2-CHR-06's scenes reaching the integration branch; after that it needs three `"scene"` lines in battle_sandbox.json and shot re-approval.

## Now (Lead queue of 15:13 and 15:46)
- **Lead queue of 17:40 (items 1–7), status at 20:45:**
  1. **Lip sync on reveal times (M2-CHR-10 UI notes): done** and on claude/ui (cherry-picked after the big7 merge). The mouth rests through a comma pause; test `test_the_mouth_rests_while_the_reveal_lingers_at_a_comma`.
  2. **M2-UI-07: review** (reviewer character). Heroes are their battle actor scenes. 27 battle shots were re-approved after viewing; two captures were pixel-identical. Two tests updated, including one line in the Creatures track's `test_creature_actor.gd` (see the task file).
  3. **Pseudo-localisation (M2-UI-28): review**, merged.
     - `--pseudo-loc`, `HYMN_PSEUDO_LOC=1` or F10 in the debug overlay.
     - `tests/unit/test_pseudo_loc_screens.gd` walks every screen at 100 % and 130 %.
     - Filed **M2-MNU-11** (Menus: Status and Customize overflow at 130 %) and **M2-FP-29** (cutscene choices should follow the text size).
  4. **Resolution and aspect audit (M2-UI-29): review**, merged.
     - `UiFrame.centre` for menus and HUD `"pin"`s.
     - New shots battle_hud_/field_menu_ 16x10 and 21x9.
     - Filed **M2-ARC-09** (the dialogue box at 21:9 is 2260 px wide).
     - Merge note: the Swell hint and pause help both shrink toward 100 % (M2-UI-29) and then wrap upward (M2-UI-28).
  5. **Subtitles (M2-UI-30): review.**
  6. **Act I maps and objectives (M3-UI-04): review**, merged.
  7. **Reefball HUD (M3-UI-01): waits for big8.**
- **Cross-track gap, for the Lead and Audio:** after big7, `validate_data` has 14 errors and `test_voice_audio` fails. voices.json has no rows for m2-slice's new speakers (boatman, crowd, fenn, ferryman, ferrymaster, garo, hobb, ione, marra, poolkeeper, stillguard, tavi, tender, townsfolk). claude/audio already has them; the gap closes when audio reaches integration. The Menus track has told Audio as well.
- **Merge note:** after merging claude/ui, run `godot --import`; there are new class_names (UiFrame, TextFitProbe, PseudoLoc).
- **M3-UI-01 (Reefball HUD): review, held for big8.** It lives on local branch `ui/reefball-big8` @ fb685ac1 (= worktree-agent-a7467349dde9740ca), which is claude/ui 1b0d5eb2 plus the merge of `origin/lead/gate-big8` (6624f237) plus the HUD.
  - **The HUD:** `game/ui/reefball/` (ReefballHud, ReefballHudController, side panel and drop view), with `reefball_hud.json` and `reefball_hud.csv`. Shots `reefball_hud_choice` and `reefball_hud_goal` were viewed and approved; reefball filter 67/0, battle 615/0, pseudo 21/0, aspect 13/0.
  - **Also on that branch, needed for the big8 + claude/ui merge:**
    - hero-integration's proposed choreo test hunks, ported verbatim: big8's battle-presentation tests assume capsule heroes;
    - a TextFitProbe fix: big8's Lattice Whole board button made a false overflow on the page title.
  - **Requests filed:** M3-RBL-201 (combat: preview() fields for the HUD).
  - **Id collision, for the Lead:** big8 renumbers the bestiary-portrait task to `M2-UI-28-bestiary-creature-portrait.md`, but claude/ui's M2-UI-28 is pseudo-localisation; on claude/ui the portrait task is still `M2-UI-26-bestiary-creature-portrait.md`. Suggestion: give the portrait **M2-UI-201** at the big8 merge and drop the other two copies.
  - **Next step once big8 is on integration:** merge integration into claude/ui, then `git merge ui/reefball-big8`, keeping claude/ui's battle baselines and recapturing them. If this container is gone, recreate it: merge integration into claude/ui and redo M3-UI-01 from the task file's notes.
- **MERGE-READY @ 2bd80fe5** (supersedes 62d38cad):
  - **What changed:** integration (M3-CMB-02, M2-ARC-12) is merged into claude/ui.
  - **Conflicts:**
    - `field_encounters.gd`: M2-MNU-08's rate refresh and M2-FP-28's kept meters are both kept. A kept meter now saves its `rate_pct` and rescales on return; test `test_a_kept_meter_rescales_to_the_rate_on_return`.
    - Battle baselines: 23 recaptured on top of the merge, then viewed and re-approved (two captures pixel-identical).
  - **Full suite:** 2176 run, 1 failed (`test_voice_audio`, the voices gap).
  - **M3-UI-01 (Reefball HUD):** a worktree agent is building it on top of lead/gate-big8. It reaches claude/ui only after big8 lands on integration.
- **Superseded MERGE-READY @ 62d38cad** (handoff and live-log commits since are docs only):
  - **Items:**
    - M2-UI-07 hero actor scenes, with the KO-clip no-sink fix from hero-integration;
    - M2-UI-28 pseudo-loc;
    - M2-UI-29 aspect audit;
    - M2-UI-30 subtitles;
    - M3-UI-04 Act I maps;
    - M2-AUD-08 value-step tick;
    - M2-UI-26 bestiary creature portrait;
    - M3-C05-07 Matron Crust cues;
    - M3-C09-05 Ch9 HoldPrompt / ActCard / CharacterNames;
    - the lip sync on reveal times.
  - **Requests filed:** M2-MNU-11, M2-FP-29, M2-ARC-09, M3-CRE-201, M3-C09-201.
  - **Checks run:**
    - gdlint and gdformat are clean;
    - `taskboard --check` is OK;
    - `validate_data` has only the 14 known voices errors;
    - the full Godot suite is 2167 run, 1 failed: `test_voice_audio`, the same voices gap.
    - **Shots:** the 31 battle shots were captured twice, pixel-identical, and 27 re-approved after viewing. The agents approved bestiary_menu, cutscene_hold_prompt, cutscene_act_card and the four aspect shots; I viewed them after merging.
  - **Checks skipped:** the full screenshot manifest (the Lead runs it), Blender (no Blender sources touched), and coverage (no core `game/battle/` or `game/progression/` code).
  - **After merging:** run `godot --import` for the new class_names.
  - **Next step:** the hero-integration stand_ins repoint, once claude/hero-integration is on integration.
- **Id blocks (Lead, 21:00):** this track's new task ids are 200–299 (any prefix, e.g. M2-UI-210), new ADRs 0110–0119, and handoffs are named `<date>-<role>-ui-<n>.md`.
- **Since 20:45:**
  - **M2-AUD-08: review.** It is M3-UI-02's Audio page plus a `SettingsPage` sound hook in ui_sfx.json, so each value step ticks.
  - **Claimed (fe4f2bd0):** M2-UI-26 (the bestiary creature portrait; not the input parity task, which shares the id), M3-C05-07 (the Matron's Crust hook) and M3-C09-05 (Ch9 UI). Two worktree agents are on them.
- **17:20:** claude/ui fast-forwarded to claude/menus @ 6f192c17. That includes everything above, the Menus track's Memories gallery, m2-slice d034c31d and the integration branch. The Menus track's full suite there: 1913 run, 0 failed.
  - **Queue:** all UI items are done or in review.
  - **Blocked:** M2-UI-07 (M2-CHR-06 is not on integration yet) and M3-UI-01 (no Reefball engine). **Lead: please queue more.**
  - **Agreed with the Menus track:** they take a key-items view in Items and a Lattice overview. A field-menu save row is a design change for the Lead (saving is shrine-only today).
- **MERGE-READY @ d741a39a:**
  - **Items:**
    - M2-UI-26, input parity (all screens);
    - M2-UI-27, dialogue reveal pauses and `time_of_char`;
    - M3-UI-02, the Audio page;
    - M3-UI-03, the lore codex;
    - with claude/menus @ b5a92596 merged (its swap-test fix, Formation, m2-slice d034c31d).
  - **Checks run:**
    - full Godot suite **1848 run, 0 failed** (log check clean);
    - tools unittest 552 OK on b5a92596 (no `tools/` change since);
    - validate_data, taskboard, gdlint and gdformat clean;
    - shots for each item, viewed and approved.
  - **Checks skipped:** the full manifest, Blender and coverage (nothing in core `game/battle/` or `game/progression/` changed). The Lead runs them at merge.
  - **The battle pause's mouse way in:** Cancel at the command root opens it (in BattlePause).
  - **Test infrastructure:** parity tests clear stray screens and park the pointer before they start (`InputDriver.clear_screen`), because the runner has no after_each.
- **M2-UI-26, the input parity audit (review, reviewer lead):** every screen has a keys, pad and mouse parity test (`tests/unit/test_input_parity_*.gd`, `InputDriver`, `ParityHost`).
  - **Shared fixes (ADR 0036):** the `UiInput` autoload (mouse cancel, held right click for skip, pad defaults everywhere, last device). MenuPage: wheel, hover only from pointer motion, a dimmed page ignores hover.
  - **Fixed along the way:**
    - shop count steppers;
    - save menu hover and wheel;
    - Controls listening;
    - Lattice drag pan, wheel zoom and pad shoulders for Page Up/Down;
    - mouse targeting and Swell play in battle;
    - click to advance dialogue;
    - choice hover;
    - device-following glyphs.
  - **Other owners to accept these hooks:**
    - Systems: `game/ui/save/`;
    - Architect: `dialogue_box.gd`;
    - m2-slice: `cutscene_choices.gd`;
    - the Menus track has merged its part.
    - Request **M2-FP-28** is filed for the Ch1 tutorial lines.
  - **Lead decisions needed:**
    1. Done: Cancel at the command root opens the battle pause. Say if you'd rather have a corner button.
    2. `battle_controller.gd` is at exactly 1000 lines.
- **M2-UI-27, the dialogue reveal pauses (review):** pauses at punctuation live in `text_box.json`, scaled by the text speed and skipped on fast-forward and instant text. **For M2-CHR-10's lip sync:** `DialogueBox.time_of_char(i)` and `reveal_duration()`; switch from i/cps to them. The player's text speed now reaches the box (part of M2-ARC-07).
- **M3-UI-02, the Audio page (review):** re-approve `settings_hub` after claude/audio merges.
- **M3-UI-03, the lore codex:** in progress in a worktree agent.
- **M3-UI-01, the Reefball HUD:** filed, blocked on M3-RBL-01.
- **`test_scene_router_swap`:** fixed by the Menus track (an injected clock). It is merged here and passes.
- **Note:** sending messages to the Lead's session fails (it needs a trusted device), so this file is the channel.

### Earlier this session
- **Lead gate rules from 14:14 apply** (scoped checks per item; one full Godot suite per batch in the background; the Lead runs the full manifest and Blender at merge).
- **MERGE-READY @ 4d8798c7:**
  - **Items:** M2-UI-16..24 and the battle_pause Controls row.
  - **Includes:** the integration branch, m2-slice and menus as of 14:20.
  - **Checks run:**
    - full Godot suite **1716 run, 0 failed** (log check clean);
    - tools unittest **544 OK** (3 skipped);
    - validate_data 0/0, taskboard --check, gdlint and gdformat clean;
    - the shots for each item, viewed and approved.
  - **Checks skipped (Lead runs at merge):** the full screenshot manifest, Blender (no Blender source touched) and coverage (the M2-UI-23 battle edits are in `game/battle/scene/`, which coverage excludes).
- **Done this batch, all status review (reviewer lead):**
  - **M2-UI-16/17/19:** objectives, the objective line, the destination cue. Since the last line:
    - the field menu root shows the objective (an Objective block);
    - fixed the line drawing empty (a trimming Label asked for no height);
    - shot `field_objective_line` approved.
  - **M2-UI-18:** the zone map, merged with the Menus track's party pages. The root has ten rows: Map comes after Swell.
  - **M2-UI-20:** the field interaction prompt. A keycap (key, or pad button after pad use) plus the interactable's `prompt_key` verb over the nearest interactable. `FieldHud.attach(self)` is now the one UI line in FieldController (Systems' file; one line changed).
  - **M2-UI-21:** area title cards, once per change of place. The title screen resets them.
  - **M2-UI-22:** title screen (worktree agent). An original drawn logotype, light shafts and motes over the caustics, and a debug-only build label. **Removed boot's placeholder Label** in `game/core/boot.gd`/`.tscn` (Architect's files; please accept).
  - **M2-UI-23:** Battle speed (0.75 to 2x; presentation only, the engine and Swell windows untouched) and Vowbound call length (Full/Short/Off) (worktree agent).
    - **No call cinematic exists yet:** request task **M2-BPR-08** for combat.
    - **Expect a conflict with claude/battle-presentation's M2-BPR-03:** it adds the same `battle_speed` row and loc keys. Keep one copy of the six `SET_BATTLE_SPEED*` rows.
  - **M2-UI-24:** first-time tips. Data-driven, saved per journey by seen flags, with an Accessibility **Tips** off switch. There are four slice tips, and `validate_data` checks them.
  - **M2-UI-13 addendum:** `battle_pause` on the Controls page (the Menus track's ask).
- **Fixes found by the full gate:**
  - **Field shot drivers moved to `game/levels/_tests/ui_shots/`:** they load `_tests` scenes, and `test_release_excludes_tests` failed. The Menus track reported it too.
  - **`test_town_services` leak:** a FieldController left behind by a test opened a second shop.
- **M2-UI-25 (review, merged at 19838a8d):** the dialogue box's continue glyph, backlog (L / pad Y) and auto-advance setting (Off by default). UI-owned in `game/ui/dialogue_assist/`.
  - **One line added to `dialogue_box.gd`** (Architect's file; please accept). Nothing of M2-ARC-06/07 is done there.
  - **Shots:** `dialogue_continue` and `dialogue_backlog` are new; `settings_accessibility` is re-approved (11 rows).
- **MERGE-READY @ 19838a8d:**
  - **Items:** M2-UI-25 on top of the 4d8798c7 batch.
  - **Checks run:**
    - full Godot suite **1728 run, 0 failed** (log check clean);
    - validate_data, taskboard, gdlint and gdformat clean;
    - shots `dialogue_continue`, `dialogue_backlog` and `settings_accessibility` viewed and approved.
  - **Checks skipped:**
    - the tools unittest rerun, because M2-UI-25 changed nothing under `tools/` (its release-excludes and loc-literal tests passed in the agent's run);
    - the full manifest, Blender and coverage, which the Lead runs at merge.
- **Blocked:**
  - **M2-UI-07:** claude/characters (M2-CHR-06) is still not on the integration branch.
  - **M3-UI-01 (Reefball HUD):** no Reefball engine on any branch yet.

## Exact next step
- When big8 is on integration, merge integration into claude/ui, then merge `ui/reefball-big8`. Recapture the battle shots, then view and re-approve them.
- When claude/hero-integration is on integration, repoint the hero `stand_ins` at the `*_battle_actor.tscn` wrappers and re-approve the battle shots.
- When M3-CRE-201 lands, drop the temporary model registration in `test_battle_part_cues.gd`.
- Otherwise, pick M3 UI work from `python3 tools/taskboard.py --role ui`.

## Un-pushed state
- Local branch `ui/reefball-big8` @ fb685ac1 (M3-UI-01 on top of the big8 gate). It cannot be pushed to claude/ui before big8 is on integration; see above.

## STATE AT HANDOVER (2026-10-25)

UI track, branch `claude/ui`; the integration branch is `claude/undertow-lead-handoff-423ixt`. Nothing is running: no subagents and no background jobs.

### Done and merge-ready
- **claude/ui @ 2bd80fe5 is MERGE-READY.** Every commit after it is docs or handoff only. The full Godot suite is 2176 run, 1 failed: `test_voice_audio` (voices.json lacks 14 m2-slice speakers; claude/audio has the fix, and big8 already carries it).
- **In review on claude/ui:**
  - M2-UI-07 (hero actor scenes in battle);
  - M2-UI-26 input parity, and M2-UI-26 bestiary creature portrait (two tasks share this id; see Open questions);
  - M2-UI-27, M2-UI-28 (pseudo-loc), M2-UI-29 (aspect), M2-UI-30 (subtitles);
  - M3-UI-02 (Audio page), M3-UI-03 (codex), M3-UI-04 (Act I maps);
  - M2-AUD-08, M3-C05-07 (Matron Crust cues), M3-C09-05 (Ch9 HoldPrompt / ActCard / CharacterNames);
  - M2-UI-03 and M2-UI-08 to M2-UI-25 from earlier.
- **After merging claude/ui:** run `godot --import`. New class_names: UiFrame, TextFitProbe, PseudoLoc, HoldPrompt, ActCard, CharacterNames, BattlePartCues, BestiaryPortraitSlot.

### In progress (not on claude/ui yet)
- **M3-UI-01, the Reefball HUD: done, status review (reviewer lead), but built on top of `origin/lead/gate-big8`.**
  - **Where it lives:**
    - as a patch on claude/ui: `docs/kb/handoffs/live/patches/ui-reefball-big8.patch` (4 commits, `git format-patch --binary`);
    - the same commits on local branch `ui/reefball-big8` @ fb685ac1, which is gone once this container is.
  - **How the patch was checked:** it applies with `git am --3way` onto the big8 merge commit (`6624f237`: claude/ui 1b0d5eb2 merged with gate-big8) and gives a byte-identical tree.
  - **The 4 commits:**
    1. the HUD: `game/ui/reefball/`, `game/data/ui/reefball_hud.json`, `game/data/loc/reefball_hud.csv` plus one project.godot translations entry, tests, and the shots `reefball_hud_choice` and `reefball_hud_goal`;
    2. the M3-RBL-201 request (and M3-MNU-201, which commit 4 removes);
    3. hero-integration's choreo test hunks, ported verbatim;
    4. a TextFitProbe fix plus `tests/unit/test_text_fit_probe.gd`.
  - **Gates on that branch:** reefball 67/0, battle 615/0, pseudo 21/0, aspect 13/0, input_parity 55/0, validate_data 0 errors.

### Exact next steps, in priority order
1. **When big8 is on integration:**
   - Merge integration into claude/ui. Resolve conflicts as below.
     - PNG baselines: take ours.
     - `baselines.json` and `shots.json`: JSON union by key or id.
     - `balance_report.md`: keep both sides, or regenerate it.
   - Run `git am --3way docs/kb/handoffs/live/patches/ui-reefball-big8.patch`. If it conflicts, apply the patch per file, or redo the work from the M3-UI-01 task notes.
   - Recapture every `battle*` shot and `drownbell_flood` twice. Check the two runs are pixel-identical, view them, then re-approve.
   - Run the full suite, then write MERGE-READY.
2. **The bestiary-portrait task id:** big8 renames it to `M2-UI-28-bestiary-creature-portrait.md`, which collides with pseudo-loc's M2-UI-28. Give it **M2-UI-201** and delete the other copies (the M2-UI-26 and M2-UI-28 portrait files).
3. **When claude/hero-integration is on integration:**
   - Point `battle_sandbox.json` stand_ins rhen, asha and toma at `res://game/hero_motion/battle/<hero>_battle_actor.tscn`. The diff is `docs/kb/tech/hero_battle_proposed.patch` on that branch; its set_ko and test hunks are already in.
   - Re-approve the battle shots after viewing them.
4. **When M3-CRE-201 lands** (cinder_matron's `model` in enemies.json): drop the temporary `CreatureModels` registration in `tests/unit/test_battle_part_cues.gd`, and check the Ch5 boss shot.
5. **When M3-C09-09 lands** (the `act_card` event): M3-C09-201 (cinematics) wires `ActCard.listen(seq)`.
6. **Then:** M3 UI work from `python3 tools/taskboard.py --role ui`, and the reviews of the tasks above.

### Open questions (for the Lead)
- Duplicate ids:
  - M2-UI-26 (input parity, and the bestiary portrait);
  - M2-UI-28 (pseudo-loc, and the portrait as renamed in big8).
- M3-RBL-201 (combat): fields in the Reefball engine's `preview()` that the HUD wants (who contests, fetches, stakes_key), and whether `strokes_left` may go below 0.
- Speaker names are all gold, not one colour per hero: no four palette colours stay distinct under every colour-vision type (M2-UI-30 notes).

### Known bugs and gaps
- `test_voice_audio` and validate_data's 14 voice errors. Fixed by claude/audio and in big8.
- `test_shrine_audio::test_the_zone_plays_the_shrine_cue` fails when run alone (no `flush_pending`). Fixed on claude/audio.
- M3-C05-07 does nothing in play until M3-CRE-201 lands.
- The ActCard is not shown at B11 until M3-C09-201 lands.
- Pell has no `characters.json` row yet (M3-C09-07); a raw id would show once he joins a party.
- The dialogue box is 2260 px wide at 21:9 (M2-ARC-09, architect).
- Status and Customize overflow at 130 % text (M2-MNU-11, menus).
- Cutscene choices do not follow the text size (M2-FP-29).

### Gotchas
- **Re-import after a merge:** after any merge that adds class_names, run `godot --import`. Otherwise scripts fail with "Identifier not declared", and a test run before the import is meaningless.
- **Don't change files during a run:** capture and the test suite read the working tree live. A merge or a data edit during a run mixes versions, and `AudioData.table` caches JSON at startup.
- **Heroes are models now:** battle_controller.gd is at 990 of its 1000-line cap, so put new battle-scene logic in helpers. Tests that want a primitive should build Ysolde, who is still a capsule.
- **`tools/dev/merge_union.py`** crashes on binaries. Resolve the PNGs first.
- **The Lead can't be messaged directly:** send_message to the Lead fails with `elevated_session_untrusted_device`, so this file is the channel.

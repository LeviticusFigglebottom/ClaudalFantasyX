# Live log: ui environment

UI track (cloud session session_01NyuYPSZn7o7gYirTvz4zjs), branch `claude/ui`, started from `claude/undertow-lead-handoff-423ixt` at 92bd0f4 on 2026-10-24. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE; the integration branch is `claude/undertow-lead-handoff-423ixt`.

## Queue (from the Lead, 2026-10-24)
1. M2-UI-03: Swell input panels for Asha (chant), Toma (brace), Ysolde (glyph); revisit the 7-row root menu. **Review** (reviewer lead).
2. Lead decision on M2-UI-05: hide the Call row until a Vowbound is bound. **Done** (5eda83b; ADR 0030 amendment).
3. M2-UI-06: shop and inn menus for Haluna. **Skipped: m2-slice had already done it** (eeb3737 on claude/m2-slice, in review, with Haluna's keepers placed in e5ba263). This track's claim is reverted.
4. UI polish pass for the slice: **M2-UI-09, review** (reviewer lead). Also took **M2-UI-08** (Art's fixes, filed on claude/env-art): review, reviewer character.
5. Gaps the m2-slice playthrough files under role ui. **None filed yet:** m2-slice's playthrough (handoff cinematics-7) filed only M2-FP-20 and M2-FP-21, both its own. Its ui review request (M2-FP-12) is already approved and done.
6. (Found on claude/characters) **M2-UI-07**, the hero actor hook: **hook done and pushed (08c872c)**. It is **blocked** on M2-CHR-06's scenes reaching the integration branch; after that it needs three `"scene"` lines in battle_sandbox.json and shot re-approval.

## Now (Lead queue of 15:13: input parity first, then M2-UI-07, the Reefball HUD and M3 UI)
- **M2-UI-26, the input parity audit (doing):**
  - **Shared fixes, ADR 0036:**
    - A `UiInput` autoload: right click and the mouse's back button mean Cancel everywhere; pad A and B exist in every scene, not only after boot; it tracks the last device.
    - MenuPage: the wheel works on every list, and a hover counts only when the pointer moved.
    - The `InputDriver` test helper.
  - **Done with tests for all three devices:**
    - title and Settings hub;
    - Settings pages (the Controls page now stops listening on a right click);
    - shop and inn (new ‹ ×N › mouse steppers for the count);
    - save and load (hover, wheel and the dialog-choice hover, in Systems' `game/ui/save/`; **Systems: please accept**; this also fixes M2-ARC-06's hover bug).
  - **In progress (worktree agents):**
    - the field menu family: the map, the bestiary, and the Menus track's Items, Equip, Lattice and Status;
    - battle (commands, targeting, Swell inputs, pause), dialogue, choices, backlog and glyph switching.
- **M3-UI-02, the Audio settings page (review):** the Audio track's volume rows (`master_volume` etc., on claude/audio) get their own page. The hub shows it only when the rows exist. **After claude/audio merges, re-approve `settings_hub`.**
- **M3-UI-03, the lore codex:** in progress in a worktree agent.
- **M3-UI-01, the Reefball HUD:** filed, blocked on M3-RBL-01.
- **Suggestion for the Lead:** SPEC §6.11's party formation menu is a field-menu party page, so it fits the Menus track (its queue is empty).

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
    - **No call cinematic exists yet:** request task **M2-BPR-07** for combat.
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
- Merge the three agent branches as they report (field-menu parity, battle/dialogue parity, codex). Run the full Godot suite in the background, then write the MERGE-READY line.
- M2-UI-07 when claude/characters is on integration (Lead batch big7).

## Un-pushed state
- None.

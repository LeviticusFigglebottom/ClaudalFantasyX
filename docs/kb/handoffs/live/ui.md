# Live log: ui environment

UI track (cloud session session_01NyuYPSZn7o7gYirTvz4zjs), branch `claude/ui`, started from `claude/undertow-lead-handoff-423ixt` at 92bd0f4 on 2026-10-24. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE; the integration branch is `claude/undertow-lead-handoff-423ixt`.

## Queue (from the Lead, 2026-10-24)
1. M2-UI-03: Swell input panels for Asha (chant), Toma (brace), Ysolde (glyph); revisit the 7-row root menu. **Review** (reviewer lead).
2. Lead decision on M2-UI-05: hide the Call row until a Vowbound is bound. **Done** (5eda83b; ADR 0030 amendment).
3. M2-UI-06: shop and inn menus for Haluna. **Skipped: m2-slice had already done it** (eeb3737 on claude/m2-slice, in review, with Haluna's keepers placed in e5ba263). This track's claim is reverted.
4. UI polish pass for the slice: **M2-UI-09, review** (reviewer lead). Also took **M2-UI-08** (Art's fixes, filed on claude/env-art): review, reviewer character.
5. Gaps the m2-slice playthrough files under role ui. **None filed yet:** m2-slice's playthrough (handoff cinematics-7) filed only M2-FP-20 and M2-FP-21, both its own. Its ui review request (M2-FP-12) is already approved and done.
6. (Found on claude/characters) **M2-UI-07**, the hero actor hook: **hook done and pushed (08c872c)**. It is **blocked** on M2-CHR-06's scenes reaching the integration branch; after that it needs three `"scene"` lines in battle_sandbox.json and shot re-approval.

## Now
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
- **In progress:** M2-UI-25, the dialogue box's continue glyph, backlog and auto-advance, in a worktree agent. These are UI-owned pieces in `game/ui/dialogue_assist/`, attached by one line in DialogueBox (Architect's file).
- **Blocked:**
  - **M2-UI-07:** claude/characters (M2-CHR-06) is still not on the integration branch.
  - **M3-UI-01 (Reefball HUD):** no Reefball engine on any branch yet.

## Exact next step
- Merge the M2-UI-25 agent branch when it reports. Then write the MERGE-READY line, and ask the Lead for more queue: after M2-UI-25 only the two blocked items remain.

## Un-pushed state
- None.

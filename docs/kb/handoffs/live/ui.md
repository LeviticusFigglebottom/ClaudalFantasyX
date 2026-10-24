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
- **MERGE-READY @ 81910b52: ci_local exit 0, 1586 tests, 91 shots** (full run, every shot, own HYMN_LOG_DIR). It includes the integration branch at cf999e0a and m2-slice at 386643c3. Coverage battle 99.95% / progression 96.69%. The Blender step was SKIPPED: no pinned Blender in this container, and this branch touches no Blender source.
- **In progress, the human's top priority:** objectives, the objective line, the destination cue (M2-UI-16/17/19, done on the local branch `ui/objectives`) and the zone map (M2-UI-18, done in a worktree agent). They are merging into claude/ui with claude/menus (the Menus track's nine-row field menu). The next MERGE-READY line follows after a full gate.
- **Queued after it (Lead, intro audit):**
  1. A field interaction prompt.
  2. First-time tutorial prompts.
  3. The title screen.
  4. Area title cards.
  5. Dialogue box: a continue glyph, a backlog and auto-advance.
  6. Settings: battle speed and summon-cinematic length.
  Also add `battle_pause` to the Controls page (from the Menus track).
- **The Lead's queue top-up (11:00) is done apart from M2-UI-07,** which waits on claude/characters. All in review:
  - **Item 1, M2-UI-08:** Art's two colour fixes (done earlier).
  - **Item 2, the accessibility audit, one task per item:**
    - **M2-UI-11:** the colour-blind palette. The old orange `#F08A24` was *less* distinct than red under deuteranopia: 0.085 Oklab from the Swell amber. The new `#D15E1F` reaches 0.177 at 4.6:1 contrast. Regression test with CVD matrices; new shot `battle_statuses_colorblind`. Reviewer character; **art/ui.md §9 needs updating by Art.**
    - **M2-UI-12:** text speed and subtitle backing on the Accessibility page, with query methods for the box. **M2-ARC-07 filed** for Architect's dialogue box to read them; text size there is M2-ARC-06.
    - **M2-UI-13:** a Controls page (a worktree agent's work, merged), for keyboard and pad remapping with swap-on-conflict. Escape or B always backs out, and Cancel can never be unbound. It saves to `[controls]`, and **one line in `game/core/boot.gd`** applies the saved bindings (Architect's file: please accept). **Behaviour change:** pad A and B now confirm and cancel in menus; Godot ships those actions with no pad buttons.
    - **M2-UI-14:** hold to confirm (`timing_assist` "hold"). Reviewer combat, because `swell_input.gd` changed.
  - **Item 3, M2-UI-15:** a pseudo-locale render test and a no-hard-coded-string check (the codebase was clean). Fixes: the hub help line now wraps, and the shop and inn lines size to their text. **The shop's sell description and refusal line were already cut off in English.**
- **The human asked directly for UI flair:** M2-UI-10 / ADR 0033, in review with Art. The m2-slice merge (c2d03e29) is pushed.
- **Gates at the last push:**
  - Full suite **1578 run, 0 failed**, log check clean.
  - Coverage battle 99.95% / progression 96.69% (within baseline); tools unittest 519 OK.
  - validate_data 0/0, lint and format clean, manifest 91 shots.
  - Shots viewed and approved this round: `battle_statuses_colorblind`, `settings_accessibility` (six rows), `settings_controls`, `settings_hub` (three rows), and `shop_menu_buy`, `shop_menu_sell`, `inn_menu`.
- **Only M2-UI-07 remains in the queue. Lead: please queue more.**

## Exact next step
- When claude/characters is on the integration branch, merge it here and finish M2-UI-07: add the three `"scene"` lines to battle_sandbox.json `stand_ins`, capture the battle shots twice to check the idle animation keeps them stable, then view and re-approve them.

## Un-pushed state
- None.

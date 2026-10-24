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
- **Merged `origin/claude/m2-slice` (bf18e854, which contains 24894292) into claude/ui at the Lead's request.**
  - **Graphics page:** kept both sides. It is a `SettingsPage` (M2-UI-09), and m2-slice's M1-UI-11 "Applying" veil now runs through two new SettingsPage hooks: `is_busy()` swallows input and blocks close while the veil is up, and `_change(delta)` lets a preset change go behind the veil. The model keeps m2-slice's warm-up tracking on top of `SettingsPageModel`. The json keeps both `hub` and `apply`.
  - **strings.csv:** `merge_union.py`, then I dropped the two old texts it appended again (BESTIARY_HELP and TITLE_HELP_SETTINGS keep this branch's rewording). shots.json and baselines.json were merged by union.
  - **Gates:** validate_data 0/0; gdlint and gdformat clean; filtered runs (graphics 54, settings 46, title 16, menu 125, ui_ 46) all 0 failed; full suite **1552 run, 0 failed**, log check clean. Coverage was not re-run: my side of the merge touched no battle or progression code.
  - **Shots:** `boot_title`, `settings_hub`, `settings_accessibility`, `field_menu` and `bestiary_menu` are unchanged by the merge (rmse 0). m2-slice's `shop_menu_buy`, `shop_menu_sell` and `inn_menu` moved only because they now draw in the ADR 0033 theme; I viewed and re-approved them.
- **The human asked directly for more flair in the menus and theme.** Done as **M2-UI-10** (ADR 0033), in review with reviewer character (Art):
  - Panel glint, corner ticks and tide lines.
  - A lamplit cursor whose row nudges right.
  - Gold header rules.
  - Caustic backdrops behind the full-screen menus.
  - All of it is theme data. 21 baselines were re-approved after viewing them (every battle shot, menus, title, save dialog, Drownbell). The Settings hub and pages also had a zero-size anchoring bug, now fixed.
- **Lead queue top-up (2026-10-24 11:00):**
  1. M2-UI-08: **already done**, in review (reviewer character).
  2. Accessibility audit and fixes: **next**. One task per item: colour-blind timeline and status chips, dialogue text size and speed, a subtitle background, full control remapping, and hold-to-confirm for timing inputs.
  3. Localization-readiness pass: a pseudo-locale render test, and a tools test for strings without a loc key.
  4. M2-UI-07 after the claude/characters merge.
- **Review-ready:** M2-UI-03, M2-UI-08, M2-UI-09, M2-UI-10, and ADR 0030's amendment.
- **Gates at the last push:** full suite 1483/0, godot_log_check clean.

## Exact next step
- Wait for a new queue from the Lead.
- When M2-CHR-06 merges, finish M2-UI-07: add the three `"scene"` lines and re-approve the battle shots after viewing them, checking that the idle animation gives stable captures.

## Un-pushed state
- None.

# Live log: ui environment

UI track (cloud session session_01NyuYPSZn7o7gYirTvz4zjs), branch `claude/ui`, started from `claude/undertow-lead-handoff-423ixt` at 92bd0f4 on 2026-10-24. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE; the integration branch is `claude/undertow-lead-handoff-423ixt`.

## Queue (from the Lead, 2026-10-24)
1. M2-UI-03: Swell input panels for Asha (chant), Toma (brace), Ysolde (glyph); revisit the 7-row root menu. **Review** (reviewer lead).
2. Lead decision on M2-UI-05: hide the Call row until a Vowbound is bound. **Done** (5eda83b; ADR 0030 amendment).
3. M2-UI-06: shop and inn menus for Haluna. **Skipped: m2-slice had already done it** (eeb3737 on claude/m2-slice, in review, with Haluna's keepers placed in e5ba263). This track's claim is reverted.
4. UI polish pass for the slice: **M2-UI-09, review** (reviewer lead). Also took **M2-UI-08** (Art's fixes, filed on claude/env-art): review, reviewer character.
5. Gaps the m2-slice playthrough files under role ui. **Next.**

## Now
- **Review-ready:** M2-UI-03 (handoff ui-7), M2-UI-08 and M2-UI-09 (handoff ui-8). ADR 0030's amendment records the Call-row decision.
- **The Lead's merge run should include these shots:**
  - New: `battle_swell_chant`, `battle_swell_brace`, `battle_swell_glyph`, `settings_hub`, `settings_accessibility`.
  - Re-approved: `battle_statuses`, `battle_vowbound_call`, `battle_opening_banner`, `battle_swell_ring`, `field_menu`, `field_menu_swell_modes`, `bestiary_menu`.
- **M2-UI-09 in one line:** a Settings hub (Graphics, Accessibility) from the title and the field menu; an Accessibility page (text size, reduced motion, palette, timing assist); and text size and palette applied to every UI-owned menu (`UiSettings.follow`).
- **Filed M2-ARC-06** (architect): the save menu and the dialogue box should follow UiSettings and match the help-line style. It includes a hover bug in the save dialog.
- **For m2-slice:** the Graphics page is now reachable in the field (field menu → Settings), so M1-UI-11's preset fade matters in play.
- **M2-UI-06 overlap:** m2-slice had built the shop and inn before this track's claim reached GitHub, and a worktree agent here built a parallel version. That version was dropped unmerged. Its ideas, worth porting onto m2-slice's menus later:
  - Equipment rows show who wears the item, the slot, its abilities, and each stat against what that hero wears now.
  - A refused deal shows only the deal line.
  - Up/Down change the count by 10, and the mouse wheel changes it too.
  - The inn says plainly that it does not save, and Rest is greyed out with its reason before anything is chosen.
- **Two queue items remained after item 3; now only item 5 is left** (plus M2-UI-07 when its scenes land).

## Exact next step
- Queue item 5: read claude/m2-slice for tasks or playthrough notes filed under role ui, and take them. If none, ask the Lead for more queue (through this file).

## Un-pushed state
- None.

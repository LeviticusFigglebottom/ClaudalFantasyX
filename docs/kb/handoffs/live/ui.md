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
- **The queue is empty apart from blocked work. Lead: please queue more.**
- **Review-ready:**
  - M2-UI-03 (handoff ui-7) and M2-UI-09 (handoff ui-8), reviewer lead.
  - M2-UI-08 (handoff ui-8), reviewer character.
  - ADR 0030's amendment.
- **Blocked:** M2-UI-07 (the hook is done; the specs wait on M2-CHR-06's merge).
- **The Lead's merge run should include these shots:**
  - New: `battle_swell_chant`, `battle_swell_brace`, `battle_swell_glyph`, `settings_hub`, `settings_accessibility`.
  - Re-approved: `battle_statuses`, `battle_vowbound_call`, `battle_opening_banner`, `battle_swell_ring`, `field_menu`, `field_menu_swell_modes`, `bestiary_menu`.
- **Merge notes:**
  - claude/ui carries copies of M2-UI-07 (from claude/characters) and M2-UI-08 (from claude/env-art), with this track's status and notes. Take claude/ui's version of those two files.
  - M2-UI-06 is m2-slice's; this branch has the integration branch's copy.
  - **strings.csv:** this branch appended 21 keys (HUD_SWELL_*, FIELD_MENU_SETTINGS*, SET_MENU_*, GFX_VALUE_*_FMT) and reworded BESTIARY_HELP and TITLE_HELP_SETTINGS. Use `tools/dev/merge_union.py` against m2-slice's shop keys.
  - **hymn_theme.tres was regenerated** (the new HelpDimLabel). If another branch also regenerated it, rebuild from the merged theme.json instead of picking a side.
- **Filed M2-ARC-06** (architect): the save menu and the dialogue box should follow UiSettings and the shared help style. It includes a save-dialog hover bug.
- **For m2-slice:** the Graphics page is now reachable in the field (field menu → Settings), so M1-UI-11's fade matters in play.
- **UI-06 port ideas** (from this track's dropped parallel build), for whoever next touches m2-slice's shop and inn:
  - Equipment rows show who wears the item, the slot, its abilities, and each stat against what that hero wears now.
  - A refused deal shows only the deal line.
  - Up/Down change the count by 10, and the mouse wheel changes it too.
  - The inn says plainly that it does not save, and Rest is greyed out with its reason before anything is chosen.

## Exact next step
- Wait for a new queue from the Lead.
- When M2-CHR-06 merges, finish M2-UI-07: add the three `"scene"` lines and re-approve the battle shots after viewing them, checking that the idle animation gives stable captures.

## Un-pushed state
- None.

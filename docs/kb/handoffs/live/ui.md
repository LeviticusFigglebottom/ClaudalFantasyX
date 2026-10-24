# Live log: ui environment

UI track (cloud session session_01NyuYPSZn7o7gYirTvz4zjs), branch `claude/ui`, started from `claude/undertow-lead-handoff-423ixt` at 92bd0f4 on 2026-10-24. **This environment owns this file** (CLAUDE.md §7a). The Lead is session_019iimsngAgPLEram1wcbLpE; the integration branch is `claude/undertow-lead-handoff-423ixt`.

## Queue (from the Lead, 2026-10-24)
1. M2-UI-03: Swell input panels for Asha (chant), Toma (brace), Ysolde (glyph); revisit the 7-row root menu. **Review** (reviewer lead).
2. Lead decision on M2-UI-05: hide the Call row until a Vowbound is bound. **Done** (5eda83b; ADR 0030 amendment).
3. M2-UI-06: shop and inn menus for Haluna. **Skipped: m2-slice had already done it** (eeb3737 on claude/m2-slice, in review, with Haluna's keepers placed in e5ba263). This track's claim is reverted.
4. UI polish pass for the slice (typography, spacing, controller/keyboard navigation, text size, screenshots).
5. Gaps the m2-slice playthrough files under role ui.

## Now
- **M2-UI-03 is review-ready** (handoff 2026-10-24-ui-7). Gates: full suite 1445/0, coverage battle 99.95% / progression 96.52%. Shots: 3 new (`battle_swell_chant`, `battle_swell_brace`, `battle_swell_glyph`) and 4 re-approved on purpose (`battle_statuses`, `battle_vowbound_call`, `battle_opening_banner`, `battle_swell_ring`): Asha/Toma/Ysolde now have gauges and Swell rows. **Please run those shots in the merge run.**
- **The brace rule changed slightly** (`SwellBrace.release` in the lead-in only lets go; formulas.md § Swell). It is outside formulas.gd, so test_formulas is untouched.
- **M2-UI-06 overlap:** m2-slice had built the shop and inn before this track's claim reached GitHub, and a worktree agent here built a parallel version. That version was dropped unmerged. Its ideas, worth porting onto m2-slice's menus in the polish pass or a follow-up:
  - Equipment rows show who wears the item, the slot, its abilities, and each stat against what that hero wears now.
  - A refused deal shows only the deal line; it used to show "Lume: 360 → -20".
  - Up/Down change the count by 10, and the mouse wheel changes it too.
  - The inn says plainly that it does not save, and Rest is greyed out with its reason before anything is chosen.
  - Check that m2-slice's live shop reads story flags through a reader that stays alive. The agent's own version freed its `GameFlagAccess` at once; m2-slice's `flag_reader.gd` fix covers this.
- Merged the integration branch (cd4e425) at 365b3df. Its emitter prebuild moves particles, so I re-approved `battle_opening_banner` (now also showing the gauges), `battle_vowbound_call` and the three new Swell shots, after viewing them.

## Exact next step
- Queue item 4 (polish pass). Two items remain after it (4 and 5).

## Un-pushed state
- None.

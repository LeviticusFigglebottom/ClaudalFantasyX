---
id: M2-UI-03
title: HUD panels for Asha's chant, Toma's brace and Ysolde's glyph
role: ui
status: review
owner_session: "claude/ui"
reviewer: lead
depends_on: [M2-CMB-01]
milestone: M2
request-from: combat
---
## Goal
M2-CMB-01 gave Asha, Toma and Ysolde their own Swell inputs (SPEC §6.2: unique, short, cancelable), as Node-free logic: `SwellChant`, `SwellBrace` and `SwellGlyph` (formulas.md § Swell). The engine, the tests and the simulator fill and unleash them, but the HUD draws only Rhen's ring, so `SwellRingView.DRAWN_KINDS` keeps their gauges and Swell rows hidden for now (battle_ctb.md "Swell", the HUD gate).

## Acceptance criteria
- [x] A panel per kind, drawn over the input's state the way `SwellRingView` draws a `SwellTimingRing` (it never decides anything): the chant's notes and the button each asks for (`expected_button`, `note_time`), the brace's blows and counter (`impact_time`, `counter_time`, `holding`), and the glyph's strokes and time left (`strokes`, `expected_button`, `time_to_peak`). Grades read by shape, not hue alone. Reduced motion keeps the timing.
- [x] Each kind is added to `SwellRingView.DRAWN_KINDS` (or its successor) once its panel lands, which turns that hero's gauge and Swell row on. Re-approve the battle shots that then show the new gauges.
- [x] `BattleController._commit_skill` opens the right panel for the input kind (it already builds any kind through `SwellInput.create`, and `SwellInputKeys` already feeds directions and releases). The hint lines use the rows' `help_key` (loc keys already exist: `SWELL_INPUT_CHANT_HELP`, `SWELL_INPUT_BRACE_HELP`, `SWELL_INPUT_GLYPH_HELP`).
- [x] `BattleMenus.grade_text` names the new grades (`braced`, `traced`, `swift`); they read as Miss today.
- [x] A short float or toast on `BattleSwell.mode_unlocked` ("Tether unlocked"), so an unlock through play is seen (pillar 5).

## Notes
- Input APIs and grade tables: formulas.md § Swell; tests in `tests/unit/test_swell_inputs.gd`.
- The timing-assist setting (M2-UI-01) should apply to these inputs' rows too (`good_sec`, `window_sec`, `swift_sec`).
- **From review sweep M (filed by M2-NIT-03, combat):**
  - **Brace lead-in** (M2-CMB-01 S5, swell_brace.gd:81-96). The technique is chosen with ui_accept, so the brace opens on a press the menu has already used, and the first blow can land before the player presses again. Make the lead-in long enough to press again, or count an accept still held when the brace opens as `holding`.
  - **Land before the slice review** (M2-ARC-01 S3). Gauges hidden by `DRAWN_KINDS` (Asha, Toma, Ysolde) still fill and save. If this task lands after the slice has been played, the first visible gauge may already be full.
  - Shallows Verse is now power 4 (balance_report.md, 2026-10-23 M2-NIT-03), so the chant's grades decide whether it beats a Chorus Mend. Make the panel's perfect feedback carry that weight.

## Implementation notes (claude/ui, 2026-10-24)
- **Panels.** `SwellRingView` is the panel for every kind: title, figure, one pip per grade, the last grade in words (top right), the hint and the assist tag. It draws Rhen's lamp itself and hands the other kinds to `SwellChantDraw`, `SwellBraceDraw` and `SwellGlyphDraw` (game/ui/battle/). They draw only. Details: tech/ui.md § Swell input panels.
  - Chant: notes scroll onto a gold line as direction arrows, inside the good/perfect window band. Brace: blows, counter and playhead on a track, and a hold shield with "Holding" / "Not holding". Glyph: the whole glyph with traced, missed, current and later strokes, and a time bar with the Swift notch.
  - Grades read by shape: best = halo diamond, earned = filled diamond, miss = cross; the finishing step (counter, swift) waits as a circle.
- **Wiring.** `DRAWN_KINDS` lists all four kinds. The controller picks the hint by kind (`SwellRingView.hint_key`) and connects `mode_unlocked` to `SwellModeRows.announce` ("Tether unlocked" float). It also calls `SwellInputKeys.carry_held` when an input opens. Net +2 controller lines (997/1000).
- **Brace lead-in (M2-NIT-03).** Both fixes: a release during the lead-in only lets go (`SwellBrace.release`, formulas.md § Swell), and an accept still held when the brace opens starts the hold.
- **Grade words.** `BattleMenus.grade_text` reads `SwellRingView.grade_key`: Braced, Traced, Swift.
- **Seven-row root.** `commands.max_rows` 6 → 7. Asha with a bag and Ilun bound has seven rows (Attack, Swell, Skills, Call Ilun, Items, Escape, Swap), and the root grows upward from the same foot (top at y 684), so nothing scrolls out of sight. Regrouping was rejected: Swap must stay last and visible (pillar 4), and folding Escape or Items into a sub-page costs a press in every battle.
- **Timing assist** already applied to every kind (`UiSettings.timing_input`). The chant and brace panels draw the window band, so "wide" is visible.
- **Data.** battle_hud.json `swell_ring` metrics; battle_fixtures.json gains frozen rows for shallows_verse, return_tide and written_light, plus fixtures `swell_chant`, `swell_brace` and `swell_glyph`; 12 loc keys.
- **Tests.** `tests/unit/test_swell_input_panels.gd` (11); `test_swell_inputs.gd` adds the lead-in release and carry_held tests and now asserts that every kind is drawn. Two tests that reached Skills by pressing ui_down now select the row (Asha has a Swell row).
- **Shots.**
  - New: `battle_swell_chant`, `battle_swell_brace`, `battle_swell_glyph`.
  - Re-approved after viewing: `battle_statuses` (Ysolde's root gains Swell; the script now selects Skills), `battle_vowbound_call` (Asha's root gains Swell), `battle_opening_banner` (Asha's and Toma's gauges, part-filled by the ambush), and `battle_swell_ring` (the "Perfect" callout).
  - The other battle shots pass under the 0.008 limit with Asha's empty gauge.

## Review log

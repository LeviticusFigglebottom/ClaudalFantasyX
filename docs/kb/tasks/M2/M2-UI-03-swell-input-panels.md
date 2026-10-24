---
id: M2-UI-03
title: HUD panels for Asha's chant, Toma's brace and Ysolde's glyph
role: ui
status: doing
owner_session: "claude/ui"
depends_on: [M2-CMB-01]
milestone: M2
request-from: combat
---
## Goal
M2-CMB-01 gave Asha, Toma and Ysolde their own Swell inputs (SPEC §6.2: unique, short, cancelable), as Node-free logic: `SwellChant`, `SwellBrace` and `SwellGlyph` (formulas.md § Swell). The engine, the tests and the simulator fill and unleash them, but the HUD draws only Rhen's ring, so `SwellRingView.DRAWN_KINDS` keeps their gauges and Swell rows hidden for now (battle_ctb.md "Swell", the HUD gate).

## Acceptance criteria
- [ ] A panel per kind, drawn over the input's state the way `SwellRingView` draws a `SwellTimingRing` (it never decides anything): the chant's notes and the button each asks for (`expected_button`, `note_time`), the brace's blows and counter (`impact_time`, `counter_time`, `holding`), and the glyph's strokes and time left (`strokes`, `expected_button`, `time_to_peak`). Grades read by shape, not hue alone. Reduced motion keeps the timing.
- [ ] Each kind is added to `SwellRingView.DRAWN_KINDS` (or its successor) once its panel lands, which turns that hero's gauge and Swell row on. Re-approve the battle shots that then show the new gauges.
- [ ] `BattleController._commit_skill` opens the right panel for the input kind (it already builds any kind through `SwellInput.create`, and `SwellInputKeys` already feeds directions and releases). The hint lines use the rows' `help_key` (loc keys already exist: `SWELL_INPUT_CHANT_HELP`, `SWELL_INPUT_BRACE_HELP`, `SWELL_INPUT_GLYPH_HELP`).
- [ ] `BattleMenus.grade_text` names the new grades (`braced`, `traced`, `swift`); they read as Miss today.
- [ ] A short float or toast on `BattleSwell.mode_unlocked` ("Tether unlocked"), so an unlock through play is seen (pillar 5).

## Notes
- Input APIs and grade tables: formulas.md § Swell; tests in `tests/unit/test_swell_inputs.gd`.
- The timing-assist setting (M2-UI-01) should apply to these inputs' rows too (`good_sec`, `window_sec`, `swift_sec`).
- **From review sweep M (filed by M2-NIT-03, combat):**
  - **Brace lead-in** (M2-CMB-01 S5, swell_brace.gd:81-96). The technique is chosen with ui_accept, so the brace opens on a press the menu has already used, and the first blow can land before the player presses again. Make the lead-in long enough to press again, or count an accept still held when the brace opens as `holding`.
  - **Land before the slice review** (M2-ARC-01 S3). Gauges hidden by `DRAWN_KINDS` (Asha, Toma, Ysolde) still fill and save. If this task lands after the slice has been played, the first visible gauge may already be full.
  - Shallows Verse is now power 4 (balance_report.md, 2026-10-23 M2-NIT-03), so the chant's grades decide whether it beats a Chorus Mend. Make the panel's perfect feedback carry that weight.

## Review log

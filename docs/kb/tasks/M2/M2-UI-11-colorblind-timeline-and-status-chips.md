---
id: M2-UI-11
title: Accessibility audit (1/5): the colour-blind palette on the timeline and status chips
role: ui
status: review
owner_session: "claude/ui"
reviewer: character
depends_on: [M1-UI-02]
milestone: M2
request-from: lead
---
## Goal
SPEC §6.11 asks for colour-blind-friendly UI options. The `palette` setting (standard / colorblind, M1-UI-02) exists. Audit whether it really reaches the turn timeline's chips and the status glyphs, fix what doesn't, and prove it with a test and a shot.

## Acceptance criteria
- [x] Under the colorblind palette, every timeline chip (ally, enemy, ghost, current, skipped, Doom) and every status glyph draws from the overridden roles, and still reads by shape (the edge shapes, the backings, the silhouettes).
- [x] A test walks the chips and glyphs under both palettes; ally and enemy, and buff and ailment, stay distinct under a deuteranopia simulation (contrast check on the simulated colours).
- [x] A shot of the statuses fixture under the colorblind palette (`battle_statuses_colorblind`), viewed and approved.

## Implementation notes (claude/ui, 2026-10-24)
- **Reach:** every timeline chip colour (ally and enemy fills, enemy names, target marks) and every status glyph (buff `focus`, ailment `danger`) is a theme role, and `BattleHud.apply_settings` swaps the theme live. No code path hard-codes a colour (audited: timeline_chip.gd, turn_timeline.gd, status_glyph.gd). The chip identity tints are the heroes' own colours, not team coding.
- **Finding:** the old colour-blind `danger`, `#F08A24` (art/ui.md §9), made things worse than the standard red. Under simulated deuteranopia it sat 0.085 (Oklab) from the amber Swell gauge and 0.098 from the green HP bar. The standard red scores 0.139.
- **Fix:** I searched colours with at least 4.5:1 contrast on `panel_low` for the best worst-case distance from focus, HP, heal, Swell, text and MP, under deuteranopia, protanopia and normal vision. `#D15E1F` (burnt orange, darker than the Swell amber) reaches 0.177 at 4.6:1. Shapes still carry every distinction.
- **Tests:** `tests/unit/test_colorblind_palette.gd` uses the Machado 2009 matrices and Oklab. It checks a worst case ≥ 0.15 and ≥ the standard palette's, text contrast ≥ 4.5, and the capture fixture's settings. `test_ui_settings.gd` now expects `#D15E1F`.
- **Shot:** `battle_statuses_colorblind`, viewed and approved. It is the statuses fixture with `"ui_settings": {"palette": "colorblind"}`, replaying the statuses script. A fixture can now set the capture's settings and borrow another fixture's script: `BattleFixture.capture_settings` and `script_of`, with no new controller lines.
- **For Art (reviewer):** art/ui.md §9 still says `#F08A24`. Please update it to `#D15E1F` or propose another colour that passes the test.

## Review log

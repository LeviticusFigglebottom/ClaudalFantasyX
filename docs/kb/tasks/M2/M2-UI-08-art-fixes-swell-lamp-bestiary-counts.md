---
id: M2-UI-08
title: "Art fixes from M2-ART-01: the Swell lamp at rest and the bestiary's defeat counts"
role: ui
status: review
owner_session: "claude/ui"
reviewer: character
depends_on: [M2-ART-01]
milestone: M2
request-from: character
---
## Goal
M2-ART-01 accepted deviations 8–12 (art/ui.md §10) with two small fixes. Both are colour roles in UI code. No layout changes.

## Acceptance criteria
- [x] **The Swell lamp at rest reads as an ember, not mud.** In `battle_swell_ring` (frozen 0.2 s before a peak, so near rest) the lamp core measures `#4A4231` (Oklab L 0.38, C 0.03): `gauge_back` (translucent `night_sky`) lerped 25% toward `ui_swell`; the translucency over the blue panel greys the hue. The halo measures `#474B4B`, a grey ring: `ui_swell` at alpha 0.25 × 0.55 over the blue panel. Fix both in `SwellRingView._draw_ring` without changing the timing cue:
  - The core lerps from a **dark warm** toward `swell`, not from the translucent `gauge_back`: for example `swell` darkened in value (× 0.3, alpha 1). At rest it should measure Oklab hue 60–90° with C ≥ 0.05.
  - The halo's alpha follows the **flare only** (0 at rest), not `brightness()`, so no grey ring shows between beats. At the peak it is unchanged.
  - Reduced motion and the flicker are unchanged.
- [x] **Bestiary defeat counts are not `ui_focus`.** `BestiaryMenu` sets `right_role = &"focus"` for a Read foe, so "×1" and "×4" measure `#65CCC8` (`ui_focus`). Use `&"text"` (`ui_line_white`) for a Read foe and keep `&"text_dim"` for an unread one. `ui_focus` means cursor, focus and current actor (art/ui.md §1), and a teal count competes with the cursor row.
- [x] Re-approve the `battle_swell_ring` and `bestiary_menu` baselines and attach before/after crops. Name Art (character) as the reviewer.

## Notes
- Art spec: docs/kb/art/ui.md §10.2 and §10.3. The evidence is in M2-ART-01's Review log.
- Not asked: the opening banner, the Read panel and the Swell page rows pass as they are.

## Implementation notes (claude/ui, 2026-10-24)
- **Lamp core:** `SwellRingView.lamp_core(b)` lerps from an opaque ember to `swell`. The ember is `swell` darkened to `lamp_core_value` 0.3 of its value (battle_hud.json `swell_ring`). At the peak it is `swell`, as before.
- **Halo:** its alpha now follows `flare()` (the beat's flare only), so it is 0 at rest. Its radius and the peak are unchanged, and so are the timing, the flicker and reduced motion.
- **Bestiary:** a Read foe's count is `text`; an unread one stays `text_dim`.
- **Measured at 720p, `battle_swell_ring` (lamp centre, 0.2 s before the second peak):** the core went from `#4A4231` to `#7B5D26` (warm, Oklab hue about 75°, C about 0.07). That frame sits inside the 0.3 s flare, so a faint halo still shows by design; it is 0 at rest (test).
- **Tests:** `test_swell_input_panels.gd::test_the_lamp_at_rest_is_an_ember_and_has_no_halo` checks the Oklab hue 60–90° and C ≥ 0.05 at rest, and the halo at 0. `test_bestiary_menu.gd` checks the count roles.
- **Baselines:** `battle_swell_ring` and `bestiary_menu` re-approved after viewing (they passed at 0.0019 and 0.0039 before re-approval). Crops are not attached: there are no reference images in the repo (CLAUDE.md §2), and the measurements above stand in for them.

## Review log

---
id: M2-UI-08
title: "Art fixes from M2-ART-01: the Swell lamp at rest and the bestiary's defeat counts"
role: ui
status: doing
owner_session: "claude/ui"
depends_on: [M2-ART-01]
milestone: M2
request-from: character
---
## Goal
M2-ART-01 accepted deviations 8–12 (art/ui.md §10) with two small fixes. Both are colour roles in UI code. No layout changes.

## Acceptance criteria
- [ ] **The Swell lamp at rest reads as an ember, not mud.** In `battle_swell_ring` (frozen 0.2 s before a peak, so near rest) the lamp core measures `#4A4231` (Oklab L 0.38, C 0.03): `gauge_back` (translucent `night_sky`) lerped 25% toward `ui_swell`; the translucency over the blue panel greys the hue. The halo measures `#474B4B`, a grey ring: `ui_swell` at alpha 0.25 × 0.55 over the blue panel. Fix both in `SwellRingView._draw_ring` without changing the timing cue:
  - The core lerps from a **dark warm** toward `swell`, not from the translucent `gauge_back`: for example `swell` darkened in value (× 0.3, alpha 1). At rest it should measure Oklab hue 60–90° with C ≥ 0.05.
  - The halo's alpha follows the **flare only** (0 at rest), not `brightness()`, so no grey ring shows between beats. At the peak it is unchanged.
  - Reduced motion and the flicker are unchanged.
- [ ] **Bestiary defeat counts are not `ui_focus`.** `BestiaryMenu` sets `right_role = &"focus"` for a Read foe, so "×1" and "×4" measure `#65CCC8` (`ui_focus`). Use `&"text"` (`ui_line_white`) for a Read foe and keep `&"text_dim"` for an unread one. `ui_focus` means cursor, focus and current actor (art/ui.md §1), and a teal count competes with the cursor row.
- [ ] Re-approve the `battle_swell_ring` and `bestiary_menu` baselines and attach before/after crops. Name Art (character) as the reviewer.

## Notes
- Art spec: docs/kb/art/ui.md §10.2 and §10.3. The evidence is in M2-ART-01's Review log.
- Not asked: the opening banner, the Read panel and the Swell page rows pass as they are.

## Review log

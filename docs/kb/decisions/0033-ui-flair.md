# 0033 — UI flair: faint ornament on panels, a lamplit cursor, header rules and caustic backdrops

- **Status:** accepted (the human asked for it directly, 2026-10-24); Art to review the values
- **Date:** 2026-10-24
- **Roles affected:** UI (theme, menus), Art (art/ui.md owner), every role whose screens use the theme
- **Author role:** UI

## Context
The human looked at the menus and asked for the general menus and UI theme to "have flair and not look so plain". art/ui.md's thesis is "nothing is decorative unless it also carries information", and §3 allows one ornament per chamfered corner. Both rules held the UI to bare panels and a flat cursor. The human's direction outranks the art rule, but the art rules that serve clarity and the IP guardrail still hold: gold discipline (lines only, at most 2% of the screen), no drop shadows behind panels, readable text first, reduced motion, and nothing pixel-copied from the inspiring game's windows.

## Decision
Add a small, original vocabulary of faint ornament built from the existing motifs: lamplight, the tide-notch and water. All of it is theme data (theme.json → hymn_theme.tres), so Art can tune or switch off each piece without code:
1. **Panels** (`TideNotchStyleBox`):
   - A gold **surface glint** under the top frame, faded at both ends (`glint_span_pct`).
   - Gold **corner ticks** on the two square corners (`corner_tick_px`; 0 turns them off).
   - On panels at least 120 px tall, two faint **tide lines** that sway in the bottom margin (`tide_*`), kept below the last row so they never cross text.
2. **The cursor** (`CursorStyleBox`, the theme's `cursor` stylebox):
   - A raised fill lit from the left and fading to the right, with a focus wash over the first half.
   - The 2 px gold frame and the focus glow stay (art/ui.md §2).
   - The row under the cursor **nudges** its text right by `cursor_nudge_px` (6). It slides with the cursor and snaps under reduced motion.
   - A left "wick" bar exists but is off (`cursor_wick_px` 0), because the lamp mote already marks the row.
3. **Header rules** (`OrnamentRule`): a gold line with a lamp-node diamond that fades out toward a small hollow diamond. It sits under every titled MenuPage header and under the field menu's and bestiary's banner titles.
4. **Caustic backdrops** (`CausticBackdrop`, `menu_caustics.gdshader`): slow, drifting lamplight-through-water lines behind full-screen menus (field menu, bestiary, Settings hub and pages), at `caustic` alpha 0.24.
   - It is still under reduced motion.
   - Its phase comes from its own elapsed time, so `--fixed-fps` captures stay deterministic.

## Consequences
- Every screen that uses the theme changed. 21 baselines were re-approved after viewing them (battle, menus, title, save dialog, Drownbell).
- **Fixed on the way:** the Settings hub and the settings pages (including the old Graphics page) anchored themselves to zero size, so their dimming backdrop never covered the screen. They now use `set_anchors_and_offsets_preset`.
- **art/ui.md §1 and §3 now have an exception.** Art (the character role) should review the values and fold them into art/ui.md, or ask for any piece to be toned down or turned off (all of it is data).
- Gold stays within discipline: the glint, ticks and rules are 1 px lines, and the only gold fills are the 4 px rule diamonds.

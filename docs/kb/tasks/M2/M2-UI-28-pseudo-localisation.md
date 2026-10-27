---
id: M2-UI-28
title: Localisation readiness. A debug pseudo-locale, every screen walked in it at 100% and 130% text, and the fixes
role: ui
status: review
reviewer: lead
owner_session: "claude/ui"
depends_on: [M2-UI-15, M2-UI-26]
milestone: M2
request-from: lead
---
## Goal
Find every label that would overflow or be cut in a longer language, before there is a translation, and fix the ones UI owns.

## Acceptance criteria
- [x] **A debug pseudo-localisation mode.** `PseudoLoc` (`game/core/debug/pseudo_loc.gd`, data `game/data/debug/pseudo_loc.json`) builds a translation for `en_XA` from every loc CSV.
  - Every string is about 40% longer, accented and bracketed: "Settings" becomes "[Šéţţîñĝš ····]".
  - `{placeholders}`, `%`-formats, BBCode tags and newlines are kept.
  - Godot's built-in pseudolocalization works headless, but it accents `{placeholders}` and BBCode, so it was not used.
- [x] **Turning it on:** `--pseudo-loc` or `HYMN_PSEUDO_LOC=1` at launch (UiInput applies it before the first scene), and **F10** in the debug overlay. Debug builds only: release strips `game/core/debug/`, nothing outside it names the class, and `enable()` refuses outside a debug build.
- [x] **The screen walk:** `tests/unit/test_pseudo_loc_screens.gd`, with one test per screen group, each at 100% and 130% text on the 1920 x 1080 reference. The overflow helper is `tests/text_fit_probe.gd`.
  - **The rule:**
    - Glyphs past their panel, a clipping ancestor or the screen **fail**.
    - Text cut with no sign of it **fails**.
    - An ellipsis is a **warning**, printed for review.
    - The full rule is in docs/kb/tech/ui.md "Pseudo-localisation".
- [x] `test_pseudo_locale.gd` (M2-UI-15) now tests the generator, the switch and the release guard. Its menu walks moved into the screen walk.
- [x] **Fixes for what failed** (below). No screenshot moved: 22 shots were captured and compared, all at RMSE 0, and no baseline was updated.

## Findings per screen

Each entry gives the result at 100% and 130%, then what was done about it. Warnings are ellipses, which never fail the test.

- **Title** fits.
  - **Settings hub, Graphics, Audio** fit.
  - **Accessibility and Controls:** the help line ellipsizes at 130% (it needs 2 lines and has 1). Warning.
  - **Memories gallery:** chapter titles ellipsize at 130%. Warning.
- **Field menu**
  - **Failed:** the Swell heroes help line ran 24 px past the panel at 130%. **Fixed:** the help line wraps upward (`HudLayout.wrap_upward`).
  - The root row "Return to the path" ellipsizes at 130%. Warning.
- **Party pages** (the Menus track's)
  - **Items, hero picker.**
    - **Failed:** the header "Salt Tonic: for whom?" ran 20 px past the page at 130%. **Fixed:** MenuPage headers now ellipsize (a warning).
    - "Asha (fallen)" ellipsizes. Warning.
  - **Lattice and Formation.**
    - **Failed:** the help line ran 95 px (Lattice) and 319 px (Formation) past the panel at 130%. **Fixed:** the FieldSubmenu help line wraps upward. This is a one-line change in `field_submenu.gd` and covers every party page and the battle pause.
    - Lattice: "Wake it (1 Ability Facet)" and a node name ellipsize at 130%. Warning.
  - **Status.** **Failed, not fixed:** the gear's ability line runs 6 px past the panel at 130%. Its column rect is wider than the panel there. Request **M2-MNU-11**, and listed in the test's `KNOWN`.
  - **Equip and Customize.**
    - **Failed, not fixed:** in Customize, the change list clips 3 px of its last line at 130% (`_changes` clips with no sign). Request **M2-MNU-11**, listed in `KNOWN`.
    - Stat names ("Magic Defense", even at 100%), gear names and the "Customize ..." header ellipsize. Warnings, listed in the request.
- **Map** (Haluna, Shell Shrine) fits.
- **Bestiary.** **Failed:** the stat grid at 130% pushed the page panel 126 px past the bestiary's frame. **Fixed:** `EnemyPageView.max_width`, so the grid drops to two pairs a row, then one, when four do not fit. The Read panel uses it too. The page now grows 17 px taller inside its frame (a "grew" warning).
- **Codex** fits.
- **Shop and inn.**
  - **Failed:** they **did not follow the text size at all**: 130% looked like 100%. **Fixed:** `UiSettings.follow` in `TownMenu._ready`.
  - **Failed:** after that fix, the help line ran 68 px past the panel at 130%. **Fixed:** it wraps upward.
  - The item description ellipsizes at its two-line cap, the refusal status at one line and the inn's description at five lines (130%). Warnings.
- **Save and load** (Systems) fit. They do not follow the text size; M2-ARC-06 already asks for that.
- **Dialogue box** fits all 600+ compiled lines with their speakers. It does not follow the text size; M2-ARC-07 already asks for that.
  - **Backlog** fits.
  - **Cutscene choices** fit every compiled choice set. They do not follow the text size. Request **M2-FP-1001** (filed as M2-FP-29).
- **Field HUD:** the objective line (every objective), tip card (every tip), interaction prompt (every verb) and area title (every location) fit.
- **Battle:** every capture state (command menu and pages, target, Read panel, result panel, Swell panels, Vowbound) and the pause.
  - **Failed:** the Swell input panels' hint ran past the 480 px panel even at 100%. The English "Confirm: strike as the ring meets the lamp · Cancel: back" did too, before the first beat. **Fixed:** the hint wraps upward.
  - **Failed:** the battle pause's help line ran 41 px past at 100%. **Fixed:** FieldSubmenu wrap.
  - The help line ellipsizes its third line (statuses at 130%, the Vowbound call at both). Warning.

## Requests filed
- **M2-MNU-11** (Menus track): the Status ability line and the Customize change list at 130%, plus the ellipsis list for review.
- **M2-FP-1001** (m2-slice, cinematics; filed as M2-FP-29): CutsceneChoices should follow `UiSettings` text size.
- Already open, unchanged: **M2-ARC-06** (save menu) and **M2-ARC-07** (dialogue box) follow the text size.

## Files outside UI ownership
- **Systems** (`game/core/debug/**`, `game/data/debug/**`):
  - New `pseudo_loc.gd` and `pseudo_loc.json`. They are debug tools, so they live where release strips them.
  - `debug_overlay.gd`: the F10 action and its help line (additive).
  - `debug_overlay.json`: one action row.
- **Menus track** (`game/ui/menus/field_submenu.gd`): one line, the help label goes through `HudLayout.wrap_upward`.

## Checks
- gdlint and gdformat: clean.
- `validate_data`: 0 errors. `taskboard --check`: clean. `unittest test_loc_literals`: OK.
- Godot tests, filtered:
  - `pseudo`: 19/0. `input_parity`: 50/0. `battle`: 448/0. `menu`: 214/0.
  - `field_menu`: 24/0. `shop`: 27/0. `inn`: 10/0. `town`: 6/0. `bestiary`: 29/0. `read`: 41/0.
  - `swell`: 148/0. `hud`: 54/0. `debug_overlay`: 12/0. `title`: 28/0. `ui_`: 46/0. `loc`: 57/0.
- Screenshots, captured and compared at RMSE 0, none updated:
  - Field menu: `field_menu`, `field_menu_swell_modes`.
  - Shop and inn: `shop_menu_buy`, `shop_menu_sell`, `inn_menu`.
  - `bestiary_menu`.
  - Battle: `battle_read_panel`, `battle_swell_ring`, `battle_swell_chant`, `battle_swell_brace`, `battle_swell_glyph`, `battle_pause`, `battle_hud_preview`.
  - Party pages: `formation_menu`, `lattice_menu`, `lattice_menu_activate`, `items_menu`, `items_menu_use`, `status_menu`, `equip_menu`, `equip_customize`, `memories_menu`.

## Review log

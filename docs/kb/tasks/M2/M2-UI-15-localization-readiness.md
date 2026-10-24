---
id: M2-UI-15
title: Localization readiness: a pseudo-locale render test and a no-hardcoded-string check
role: ui
status: review
owner_session: "claude/ui"
reviewer: lead
depends_on: [M2-UI-09]
milestone: M2
request-from: lead
---
## Goal
SPEC M7 needs a localization-ready string table. Prove the UI survives longer and accented translations, and keep player-facing strings on loc keys.

## Acceptance criteria
- [x] A pseudo-locale (`xx`, generated from strings.csv by a tool: accented letters, about 35% longer, wrapped in brackets) is loaded in tests. Every menu (field menu, bestiary, settings pages, title, battle HUD pages, shop and inn) is built under it, and each Label's text fits its rect or is set to wrap or ellipsize, with no silent overflow.
- [x] A tools unittest scans game/ui and game/battle/scene for player-facing literals (`.text = "..."`, `tr()` on a non-key, `set_help("...")`) and fails on any not on an allow-list.
- [x] The fixes the two checks find.

## Implementation notes (claude/ui, 2026-10-24)
- **Pseudo-locale:** `tests/unit/test_pseudo_locale.gd` builds `xx` from strings.csv at test time. Each string is accented, padded about 35% longer and bracketed, with `{placeholders}` and %-formats kept. There is no generated file to keep in sync. Under it the test builds:
  - every menu through its capture driver: the field menu (root and Swell modes), bestiary, settings hub, Accessibility page, shop (buy and sell) and inn;
  - six battle HUD states: player preview, swap menu, Read panel, chant, brace and the Vowbound call.
  A visible Label fails if it is wider (one line) or taller (wrapped) than its rect with no ellipsis, clip or line limit. Labels sized by a Container are skipped, because their container grows; the shots show those.
- **No-hard-coded-string check:** `tools/tests/test_loc_literals.py` scans every .gd under game/ for literals reaching `.text`, the help/hint/header/note/banner setters, `tr()`, `pop_info()` and the row `label`/`right` fields. Loc keys, ids and formats, and `&""`/`^""` literals pass. **The codebase was already clean**; the test includes a seeded offender to prove it catches one.
- **Fixes the checks found:**
  - The Settings hub's help line did not wrap. It now wraps and ellipsizes, as does the settings pages' help line.
  - The shop and inn description and status lines had fixed heights. **In English the sell page's two-line description was already one pixel too tall for its box**, and the refusal line needed 84 px of a 72 px box. The description is now as tall as its text, up to the data cap (`desc.height`), with the status `status.gap` under it (87 px, two lines). Both ellipsize as a last resort for long translations.
  - `shop_menu_buy`, `shop_menu_sell` and `inn_menu` were re-approved after viewing; every line now shows whole.
  - The town menu's help line uses `HelpDimLabel`.

## Review log

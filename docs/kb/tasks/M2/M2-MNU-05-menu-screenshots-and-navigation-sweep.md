---
id: M2-MNU-05
title: Screenshots, navigation and accessibility sweep over the new menus
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-01, M2-MNU-02, M2-MNU-03, M2-MNU-04]
milestone: M2
request-from: lead
reviewer: qa
---
## Goal
Every new screen has an approved baseline (viewed), works on keyboard, controller and mouse, and follows UiSettings (text size, palette, reduced motion).

## Acceptance criteria
- [x] A baseline per new screen, viewed before approval; `field_menu` re-approved for its nine rows.
- [x] A test per screen that drives it with ui_* actions only.
- [x] Text size 130%, each palette and reduced motion checked on each screen.

## Notes
- **Baselines (all viewed before approval):** `battle_pause`, `items_menu`, `items_menu_use`, `status_menu`, `lattice_menu`, `lattice_menu_activate`, `equip_menu`, `equip_customize`; `field_menu` and `field_menu_swell_modes` re-approved for the nine-row root.
- **Input:** each page's test file drives it with ui_up/down/left/right/accept/cancel and page_up/page_down events only, plus mouse hover/click (test_items_menu, test_status_menu, test_lattice_menu, test_equip_menu, test_battle_pause, test_field_menu_party_pages).
- **Accessibility sweep:** every new screen rendered at text 130% and with the colorblind palette by a throwaway driver (not committed) and viewed. Palette: correct everywhere (all colours are theme roles). 130%: field menu root truncated "Return to the path" (root widened, cost_width 0); Lattice side panel text ran over its key and the confirm (now flows by measured height; test at 1.0/1.15/1.3); Equip stat rows overlapped, the Customize header clipped into the next panel and the refusal ellipsized (row pitch follows the line height, headers ellipsize, refusals wrap; test at 1.3). Items, Status and the pause were already clean. Reduced motion: every page gives its MenuPages reduced_motion and the Lattice camera/pulses stop; the caustic backdrop is still under it (ADR 0033).
- **Gates:** see the MERGE-READY line in docs/kb/handoffs/live/menus.md (full tools/ci_local.sh).

## Review log

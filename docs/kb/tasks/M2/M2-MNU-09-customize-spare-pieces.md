---
id: M2-MNU-09
title: Customize on spare (unworn) pieces
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-02]
milestone: M2
request-from: lead
reviewer: progression
---
## Goal
Customize works only on worn pieces. Let the Equip page customize any owned piece, worn or not.

## Acceptance criteria
- [x] Spare pieces reachable for Customize; preview and refusals as for worn ones.
- [x] Tests; screenshots unchanged or re-approved after viewing.

## Notes
- **Done (2026-10-24, worktree agent off claude/menus 73f59505):** on the Equip page's PIECES level each spare piece with an empty slot gets a "· Customize" row ("N empty"); Confirm or a click opens the existing RECIPES level for its first empty slot (same preview, refusals in words, two-Confirm craft); Cancel and a craft return to PIECES on that piece. Worn pieces stay on GEAR's ability rows. No rule changes. Files: `game/ui/menus/equip/equip_menu.gd`, `equip_menu_model.gd` (`KIND_CUSTOMIZE`, `customize_row`, `customize_desc`), `game/data/loc/menus_equip.csv` (3 keys; Pieces help now "Confirm: wear it or Customize"), `tests/unit/test_equip_menu.gd` (+3 tests, one updated), `docs/kb/tech/ui.md`.
- **Screenshots:** `equip_menu` changed (the spare Coral-Bitten Hooks now show "· Customize  1 empty", new help line); viewed and re-approved. `equip_customize` unchanged (rmse 0).
- **Gates:** see the commit report (format, lint, validate_data, taskboard, --filter=equip / parity / field_menu, compare).

## Review log

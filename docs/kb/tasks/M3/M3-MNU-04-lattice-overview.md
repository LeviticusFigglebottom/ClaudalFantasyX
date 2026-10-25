---
id: M3-MNU-04
title: Lattice overview: the whole board at a glance
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-01]
milestone: M3
request-from: ui
reviewer: progression
---
## Goal
The Lattice page follows the cursor; there is no way to see the whole board and every hero on it at once (pillar 5, growth you can see).

## Acceptance criteria
- [x] An overview mode (a key toggles it) that fits the whole board, shows every hero's position and woken nodes, and returns to the cursor view on the same node.
- [x] Keyboard, mouse and pad parity; reduced motion honoured; screenshot viewed; tests.

## Notes
- 2026-10-24 (menus worktree):
  - **Toggle:** the action `lattice_overview` (M / pad X; lattice_menu.json `overview`) and a framed title-bar button whose label names the binding.
  - **Remappable:** a controls.json row, a `ControlsModel` ensure line, and `CTRL_ACT_LATTICE_OVERVIEW` in menus_lattice.csv.
  - **Camera:** `LatticeBoardView.fit_zoom` / `set_overview` reuse the M2-UI-26 zoom and pan (clamped), with a snap under reduced motion.
  - **Words:** hero name tags and woken-by initials are drawn in view space (`LatticeMenuModel.woken_initials`).
  - **Behaviour:** the cursor, side panel and actions are unchanged; a wheel turn or drag ends the overview; toggling back returns to the cursor view on the same node.
- Shots: new `lattice_overview`. `lattice_menu` and `lattice_menu_activate` were re-approved for the new title-bar button (viewed). Compare passes at RMSE 0.00000.
- Tests: 4 new tests in test_lattice_menu.gd and test_input_parity_lattice_overview.gd (keys, pad, mouse).
- Gates: listed in the commit report.

## Review log

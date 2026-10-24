---
id: M2-MNU-01
title: The Lattice board menu (view, travel, activate, preview each node)
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M1-PRG-01]
milestone: M2
request-from: lead
reviewer: progression
---
## Goal
The Lattice exists only as headless logic (`game/progression/lattice_*.gd`); the player cannot see or use it. SPEC §10.2 M2 asks for "a first Lattice section", pillar 5 for growth you can see, pillar 4 for knowing what an action costs. Build the field menu's Lattice page over the existing `LatticeProgress` rules (no new rules).

## Acceptance criteria
- [x] Reached from the field menu's Lattice row; a hero switcher (each joined hero's board view).
- [x] The 87-node standard section drawn from `lattice_standard.json` (nodes, edges, regions, gates, starts), in an ORIGINAL look (SPEC §2: no echo of the inspiring game's node board; see tools/banned_terms.txt).
- [x] Travel with movement points: step to a neighbour, or pick any node and walk the cheapest path (`cheapest_path`), the cost shown before committing.
- [x] Activate the node you stand on with its Facet; open an adjacent gate with its Key; every refusal said in words (`activate_error`, `open_gate_error`, `ERR_*`).
- [x] Each node's effect, its Facet and count held, and who activated it, shown for the node under the cursor before committing.
- [x] Saves through `LatticeProgress.save_into` (refused while the tables are broken).
- [x] Keyboard, controller and mouse; UiSettings honoured; screenshots; tests.

## Notes
- 2026-10-24 (menus worktree): built over the existing rules, with no new rules and nothing in game/progression touched.
  - `LatticeMenuModel` (Node-free): words, plans (action, path, cost, left, refusal) and actions. It saves through `PartySheet.save_lattice()` and refuses everything while the tables are broken.
  - `LatticeMenu` (FieldSubmenu): board, side panel, key, status line and a two-row confirm.
  - `LatticeBoardView` (`_draw`): lozenge gems, gate plates with a boom, gold rigging edges, lamp glow, hero ring, teal cursor, path and cost tag.
  - `LatticeLegend`: the key, drawn with the board's own shapes.
  - Capture driver `LatticeMenuShot`.
  - Layout: game/data/ui/lattice_menu.json. Words: game/data/loc/menus_lattice.csv.
  - docs/kb/tech/ui.md § Lattice page (M2-MNU-01), including how the look differs from the inspiring game's board.
- Shots: `lattice_menu` (the path and its cost) and `lattice_menu_activate` (the confirm to wake Kick Off the Wall). Baselines are approved, and compare passes at RMSE 0.00000.
- Gates:
  - gdformat and gdlint clean on the whole tree.
  - validate_data: 0 errors.
  - taskboard --check passes.
  - Godot tests: `--filter=lattice` 49/0 (12 new in test_lattice_menu.gd); `--filter=field_menu` 19/0.
  - No coverage step: game/battle and game/progression were not touched.
- 2026-10-24, M2-MNU-05 sweep fix: the side panel flows by measured height, so text sizes up to 130% no longer overlap. The key's rows wrap and the key shrinks or hides before reaching the foot, and the confirm keeps a gap above it at 100%. A new test checks that no rects intersect at 1.0, 1.15 and 1.3. Both baselines were re-approved: the key sits 9 px (1080p) higher. Gates: `--filter=lattice` 50/0, `--filter=field_menu` 19/0, compare 2/2 at RMSE 0.00000, lint, format, validate_data and taskboard clean. I checked the page at 130% in scratch renders that are not committed.
- Left for later:
  - The board has no zoom-out or overview mode, and the page has no mouse-drag pan (the camera follows the cursor).
  - A closed gate that is not adjacent offers no "walk next to it".

## Review log

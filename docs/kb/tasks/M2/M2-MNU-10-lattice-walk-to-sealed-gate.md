---
id: M2-MNU-10
title: Lattice: a sealed gate away from the hero offers to walk there
role: ui
status: review
owner_session: "menus (claude/menus)"
depends_on: [M2-MNU-01]
milestone: M2
request-from: lead
reviewer: progression
---
## Goal
Choosing a sealed gate that is not next to the hero only says to stand beside it. Offer to walk to the cheapest neighbour of the gate first (cost shown), then open it.

## Acceptance criteria
- [x] The plan names the walk and its cost; no new rules (cheapest_path, open_gate_error).
- [x] Tests.

## Notes
- 2026-10-24 (menus worktree): `LatticeMenuModel._plan_walk_to_gate`. A far sealed gate plans an ACT_WALK to its cheapest reachable neighbour, using `cheapest_path` and `path_cost` (the sum of `entry_cost`), with `beside` naming that neighbour.
  - The plan line gives the cost and the movement left, plus whether the Key is held. The confirm reads "Walk beside the gate (N movement)".
  - Once the hero stands beside the gate, the next Confirm opens it through the existing open plan.
  - Refusals in words: no way (`LATTICE_MENU_GATE_NO_WAY`) and too far (`LATTICE_MENU_GATE_TOO_FAR_FMT`). The 8 new keys are in menus_lattice.csv.
  - No new rules; game/progression untouched.
- Tests: 3 new tests in test_lattice_menu.gd (the model plan and act for the far gate; the no-Key and no-way refusals; keyboard Confirm walking and then opening), and the old not-adjacent assertion updated.
- Gates:
  - gdformat and gdlint clean.
  - validate_data: 0 errors.
  - taskboard --check passes.
  - Godot tests: `--filter=lattice` 57/0, `--filter=parity` 25/0, `--filter=field_menu` 24/0.
  - Screenshot compare: `lattice_menu` and `lattice_menu_activate` unchanged (RMSE 0.00000), so no re-approval was needed.
- docs/kb/tech/ui.md section Lattice page has a new "A far sealed gate (M2-MNU-10)" bullet.

## Review log

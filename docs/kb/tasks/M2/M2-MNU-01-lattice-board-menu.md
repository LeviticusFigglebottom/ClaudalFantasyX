---
id: M2-MNU-01
title: The Lattice board menu (view, travel, activate, preview each node)
role: ui
status: doing
owner_session: "menus (claude/menus)"
depends_on: [M1-PRG-01]
milestone: M2
request-from: lead
reviewer: progression
---
## Goal
The Lattice exists only as headless logic (`game/progression/lattice_*.gd`); the player cannot see or use it. SPEC §10.2 M2 asks for "a first Lattice section", pillar 5 for growth you can see, pillar 4 for knowing what an action costs. Build the field menu's Lattice page over the existing `LatticeProgress` rules (no new rules).

## Acceptance criteria
- [ ] Reached from the field menu's Lattice row; a hero switcher (each joined hero's board view).
- [ ] The 87-node standard section drawn from `lattice_standard.json` (nodes, edges, regions, gates, starts), in an ORIGINAL look (SPEC §2: no echo of the inspiring game's node board; see tools/banned_terms.txt).
- [ ] Travel with movement points: step to a neighbour, or pick any node and walk the cheapest path (`cheapest_path`), the cost shown before committing.
- [ ] Activate the node you stand on with its Facet; open an adjacent gate with its Key; every refusal said in words (`activate_error`, `open_gate_error`, `ERR_*`).
- [ ] Each node's effect, its Facet and count held, and who activated it, shown for the node under the cursor before committing.
- [ ] Saves through `LatticeProgress.save_into` (refused while the tables are broken).
- [ ] Keyboard, controller and mouse; UiSettings honoured; screenshots; tests.

## Notes

## Review log
